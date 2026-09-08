from github import Github
from src.config import get_settings
from src.state import AgentState

def publish(state: AgentState) -> AgentState:
    settings = get_settings()
    if not settings.github_token or not settings.github_repository:
        raise RuntimeError("GITHUB_TOKEN and GITHUB_REPOSITORY are required for publishing")
    gh = Github(settings.github_token)
    repo = gh.get_repo(settings.github_repository)
    base = repo.get_branch(settings.github_base_branch)
    branch = f"security/iam-remediation-{state.validation_attempts}"
    repo.create_git_ref(ref=f"refs/heads/{branch}", sha=base.commit.sha)
    for name, content in state.remediated_tf_code.items():
        try:
            existing = repo.get_contents(name, ref=branch)
            repo.update_file(name, "chore: remediate IAM policy", content, existing.sha, branch=branch)
        except Exception:
            repo.create_file(name, "chore: remediate IAM policy", content, branch=branch)
    report = "# IAM Security Remediation\n\nAll deterministic Terraform and Checkov validation gates passed.\n\n## Findings\n" + "\n".join(f"- `{x.get('check_id')}`: {x.get('check_name', 'IAM finding')}" for x in state.checkov_findings)
    repo.create_file("SECURITY_REMEDIATION.md", "docs: add IAM remediation report", report, branch=branch)
    pr = repo.create_pull(title="chore: remediate excessive IAM permissions", body=report, head=branch, base=settings.github_base_branch)
    return state.model_copy(update={"pull_request_url": pr.html_url})

