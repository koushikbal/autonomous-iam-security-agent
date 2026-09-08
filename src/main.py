import argparse
from src.graph import build_graph
from src.state import AgentState

def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous IAM security posture agent")
    parser.add_argument("repo_path", nargs="?", default=".")
    args = parser.parse_args()
    result = build_graph().invoke(AgentState(repo_path=args.repo_path))
    print(f"secure={result['is_secure']} attempts={result['validation_attempts']} pull_request={result.get('pull_request_url')}")

if __name__ == "__main__":
    main()

