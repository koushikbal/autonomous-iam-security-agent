import json
import subprocess
from pathlib import Path
from src.state import AgentState

IAM_CHECK_PREFIXES = ("CKV_AWS_1", "CKV_AWS_108", "CKV_AWS_109", "CKV_AWS_110", "CKV_AWS_111", "CKV_AWS_288", "CKV_AWS_287", "CKV_AWS_63")

def _run_checkov(path: str) -> tuple[dict, int]:
    result = subprocess.run(["checkov", "-d", path, "-o", "json"], capture_output=True, text=True, check=False)
    if not result.stdout.strip():
        return {}, result.returncode
    try:
        return json.loads(result.stdout), result.returncode
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Checkov returned invalid JSON: {exc}") from exc

def scan(state: AgentState) -> AgentState:
    root = Path(state.repo_path)
    tf = {str(p.relative_to(root)): p.read_text(encoding="utf-8") for p in root.rglob("*.tf")}
    report, _ = _run_checkov(str(root))
    findings = []
    for item in report.get("results", {}).get("failed_checks", []):
        check_id = item.get("check_id", "")
        if check_id.startswith(IAM_CHECK_PREFIXES) or "iam" in item.get("check_name", "").lower():
            findings.append(item)
    return state.model_copy(update={"raw_tf_code": tf, "checkov_findings": findings})

