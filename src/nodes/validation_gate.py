import subprocess
from pathlib import Path
from src.nodes.checkov_scanner import _run_checkov
from src.state import AgentState

def _command(args: list[str], cwd: str) -> tuple[int, str]:
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    return p.returncode, (p.stdout + p.stderr)[-12000:]

def validate(state: AgentState) -> AgentState:
    root = Path(state.repo_path)
    for name, content in state.remediated_tf_code.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    outputs = {}
    fmt_code, outputs["terraform_fmt"] = _command(["terraform", "fmt", "-check", "-diff"], str(root))
    init_code, outputs["terraform_init"] = _command(["terraform", "init", "-backend=false", "-input=false"], str(root))
    validate_code, outputs["terraform_validate"] = _command(["terraform", "validate", "-no-color"], str(root)) if init_code == 0 else (init_code, "terraform init failed")
    report, checkov_code = _run_checkov(str(root))
    outputs["checkov"] = str(report)
    secure = all(code == 0 for code in (fmt_code, init_code, validate_code)) and not report.get("results", {}).get("failed_checks") and checkov_code == 0
    return state.model_copy(update={"validation_attempts": state.validation_attempts + 1, "is_secure": secure, "validation_output": outputs})

