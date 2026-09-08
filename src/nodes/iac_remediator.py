import json
import re
import openai
from src.config import get_settings
from src.state import AgentState

SYSTEM = """You are a senior AWS IAM and Terraform security engineer. Rewrite only the vulnerable Terraform IAM policy resources supplied by the user. Apply least privilege: replace wildcard actions/resources with the smallest actions and ARNs justified by the usage context. Preserve valid Terraform syntax and unrelated resources. Return JSON with a 'files' object mapping filenames to complete Terraform source strings. Do not include markdown fences."""

def _extract_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(text)

def remediate(state: AgentState) -> AgentState:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for remediation")
    prompt = json.dumps({"terraform": state.raw_tf_code, "findings": state.checkov_findings, "recently_used_actions": state.cloudtrail_context})
    openai.api_key = settings.openai_api_key
    response = openai.ChatCompletion.create(
        model=settings.llm_model, temperature=0, response_format={"type": "json_object"},
        messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": prompt}],
    )
    payload = _extract_json(response["choices"][0]["message"]["content"] or "{}")
    files = payload.get("files", {})
    if not files or not all(isinstance(v, str) for v in files.values()):
        raise ValueError("LLM response did not contain valid Terraform files")
    return state.model_copy(update={"remediated_tf_code": files})
