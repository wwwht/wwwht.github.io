import argparse
import importlib
import re


INLINE_MATH_PATTERN = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", re.DOTALL)
DOUBLE_SLASH_PATTERN = re.compile(r"(?<!:)//(?!/)([ \t]*)(?=\S)")


def should_promote_to_block_math(content: str) -> bool:
    normalized = content.strip()
    return any(marker in normalized for marker in (r"\begin{", r"\end{", r"\\", "\n"))


def promote_formula_blocks(text: str) -> str:
    def replace(match: re.Match) -> str:
        content = match.group(1).strip()
        if not should_promote_to_block_math(content):
            return match.group(0)
        return f"\n$$\n{content}\n$$\n"

    return INLINE_MATH_PATTERN.sub(replace, text)


def ensure_newline_after_double_slash(text: str) -> str:
    return DOUBLE_SLASH_PATTERN.sub("//\n", text)


def normalize_spacing(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def format_issue_body(body: str) -> str:
    formatted = body.replace("\r\n", "\n")
    formatted = promote_formula_blocks(formatted)
    formatted = ensure_newline_after_double_slash(formatted)
    return normalize_spacing(formatted)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Format GitHub issue content before Gmeek.")
    parser.add_argument("token", help="GitHub token")
    parser.add_argument("repository", help="GitHub repository in owner/name format")
    parser.add_argument("--issue_number", required=True, type=int, help="Issue number to format")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    github_module = importlib.import_module("github")
    github_auth = github_module.Auth.Token(args.token)
    github_client = github_module.Github(auth=github_auth)
    issue = github_client.get_repo(args.repository).get_issue(args.issue_number)
    original_body = issue.body or ""
    formatted_body = format_issue_body(original_body)

    if formatted_body == original_body:
        print(f"Issue #{args.issue_number} did not require formatting.")
        return

    issue.edit(body=formatted_body)
    print(f"Issue #{args.issue_number} formatted successfully.")


if __name__ == "__main__":
    main()
