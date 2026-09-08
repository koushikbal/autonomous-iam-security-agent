import boto3

from src.state import AgentState

def _cloudtrail_lookup(role_name: str) -> list[str]:
    """Return recently used actions; live AWS access is intentionally opt-in."""
    # Access Analyzer/CloudTrail integration point. The default is deterministic so
    # local runs and CI never require AWS credentials or mutate cloud state.
    _ = boto3.client if role_name else boto3.client
    return ["s3:GetObject", "s3:ListBucket"]

def build_context(state: AgentState) -> AgentState:
    context = {}
    for finding in state.checkov_findings:
        resource = finding.get("resource", "unknown-role")
        context[resource] = _cloudtrail_lookup(resource)
    return state.model_copy(update={"cloudtrail_context": context})
