import argparse
import importlib
from pathlib import Path
import re


INLINE_MATH_PATTERN = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)", re.DOTALL)
BLOCK_MATH_PATTERN = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
DOUBLE_SLASH_PATTERN = re.compile(r"(?<!:)//(?!/)([ \t]*)(?=\S)")
LATEX_ROW_BREAK_PATTERN = re.compile(r"\\\\[ \t]*(?=\S)")


def should_promote_to_block_math(content: str) -> bool:
    normalized = content.strip()
    return any(marker in normalized for marker in (r"\begin{", r"\end{", r"\\", r"\tag{", "\n"))


def is_standalone_inline_math(text: str, match: re.Match) -> bool:
    line_start = text.rfind("\n", 0, match.start()) + 1
    line_end = text.find("\n", match.end())
    if line_end == -1:
        line_end = len(text)

    return text[line_start:line_end].strip() == match.group(0).strip()


def normalize_block_math_content(content: str) -> str:
    return LATEX_ROW_BREAK_PATTERN.sub(lambda _: "\\\\\n", content.strip())


def promote_formula_blocks(text: str) -> str:
    def replace(match: re.Match) -> str:
        content = match.group(1).strip()
        if not should_promote_to_block_math(content) and not is_standalone_inline_math(text, match):
            return match.group(0)
        content = normalize_block_math_content(content)
        return f"\n$$\n{content}\n$$\n"

    return INLINE_MATH_PATTERN.sub(replace, text)


def normalize_existing_block_math(text: str) -> str:
    def replace(match: re.Match) -> str:
        content = normalize_block_math_content(match.group(1))
        return f"$$\n{content}\n$$"

    return BLOCK_MATH_PATTERN.sub(replace, text)


def ensure_newline_after_double_slash(text: str) -> str:
    return DOUBLE_SLASH_PATTERN.sub("//\n", text)


def normalize_spacing(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def format_issue_body(body: str) -> str:
    formatted = body.replace("\r\n", "\n")
    formatted = promote_formula_blocks(formatted)
    formatted = normalize_existing_block_math(formatted)
    formatted = ensure_newline_after_double_slash(formatted)
    return normalize_spacing(formatted)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Format GitHub issue content before Gmeek.")
    parser.add_argument("token", nargs="?", help="GitHub token")
    parser.add_argument("repository", nargs="?", help="GitHub repository in owner/name format")
    parser.add_argument("--issue_number", type=int, help="Issue number to format")
    parser.add_argument("--file", help="Local markdown file to format in place")
    return parser.parse_args()


def format_local_file(file_path: str) -> None:
    path = Path(file_path)
    original_body = path.read_text(encoding="utf-8")
    formatted_body = format_issue_body(original_body)

    if formatted_body == original_body:
        print(f"{path} did not require formatting.")
        return

    path.write_text(formatted_body, encoding="utf-8")
    print(f"{path} formatted successfully.")


def main() -> None:
    args = parse_args()

    if args.file:
        format_local_file(args.file)
        return

    if not args.token or not args.repository or args.issue_number is None:
        raise SystemExit("token, repository, and --issue_number are required unless --file is used")

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
