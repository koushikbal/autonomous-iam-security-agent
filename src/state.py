from typing import Dict, List
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    repo_path: str
    raw_tf_code: Dict[str, str] = Field(default_factory=dict)
    checkov_findings: List[dict] = Field(default_factory=list)
    cloudtrail_context: Dict[str, List[str]] = Field(default_factory=dict)
    remediated_tf_code: Dict[str, str] = Field(default_factory=dict)
    validation_attempts: int = 0
    is_secure: bool = False
    validation_output: Dict[str, str] = Field(default_factory=dict)
    pull_request_url: str | None = None

