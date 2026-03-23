"""Activity tracker: parse git log for commits, track lines, files, test creation, docs."""

import json
import os
import subprocess
from datetime import datetime
from collections import Counter


def _run_git(repo_path: str, args: list) -> str:
    """Run a git command and return stdout."""
    result = subprocess.run(
        ["git", "-C", repo_path] + args,
        capture_output=True, text=True, timeout=60,
    )
    return result.stdout.strip()


def get_git_user(repo_path: str) -> str:
    """Get the current git user."""
    name = _run_git(repo_path, ["config", "user.name"])
    email = _run_git(repo_path, ["config", "user.email"])
    return f"{name} <{email}>"


def parse_commits(repo_path: str, max_commits: int = 5000) -> list:
    """Parse git log for commits with metadata."""
    separator = "---SPARKLE_SEP---"
    fmt = f"%H{separator}%an{separator}%ae{separator}%aI{separator}%s"

    raw = _run_git(repo_path, [
        "log", f"--format={fmt}", "--numstat", f"-n{max_commits}"
    ])

    if not raw:
        return []

    commits = []
    current = None
    current_files = []
    current_added = 0
    current_deleted = 0

    for line in raw.split("\n"):
        if separator in line:
            if current is not None:
                current["files"] = current_files
                current["files_changed"] = len(current_files)
                current["lines_added"] = current_added
                current["lines_deleted"] = current_deleted
                commits.append(current)

            parts = line.split(separator)
            if len(parts) >= 5:
                current = {
                    "hash": parts[0],
                    "author_name": parts[1],
                    "author_email": parts[2],
                    "date": parts[3],
                    "message": parts[4],
                }
                current_files = []
                current_added = 0
                current_deleted = 0
        elif line.strip() and current is not None:
            tab_parts = line.split("\t")
            if len(tab_parts) >= 3:
                ins = int(tab_parts[0]) if tab_parts[0] != "-" else 0
                dels = int(tab_parts[1]) if tab_parts[1] != "-" else 0
                current_files.append(tab_parts[2])
                current_added += ins
                current_deleted += dels

    if current is not None:
        current["files"] = current_files
        current["files_changed"] = len(current_files)
        current["lines_added"] = current_added
        current["lines_deleted"] = current_deleted
        commits.append(current)

    return commits


def classify_commit(commit: dict) -> dict:
    """Classify a commit for XP bonuses."""
    message = commit["message"].lower()
    files = commit.get("files", [])

    tags = set()

    # Test file detection
    test_files = [f for f in files if "test" in f.lower() or "spec" in f.lower() or f.endswith("_test.py") or f.endswith(".test.js")]
    if test_files:
        tags.add("tests")

    # Documentation
    doc_files = [f for f in files if f.lower().endswith(".md") or "readme" in f.lower() or "doc" in f.lower() or "changelog" in f.lower()]
    if doc_files:
        tags.add("docs")

    # Bug fix
    if any(kw in message for kw in ["fix", "bug", "patch", "hotfix", "resolve"]):
        tags.add("bugfix")

    # Feature
    if any(kw in message for kw in ["feat", "feature", "add", "implement", "new"]):
        tags.add("feature")

    # Refactor
    if any(kw in message for kw in ["refactor", "clean", "restructure", "reorganize"]):
        tags.add("refactor")

    # Languages in files
    extensions = set()
    for f in files:
        _, ext = os.path.splitext(f)
        if ext:
            extensions.add(ext.lower())

    commit["tags"] = tags
    commit["extensions"] = extensions
    commit["has_tests"] = "tests" in tags
    commit["has_docs"] = "docs" in tags
    commit["is_bugfix"] = "bugfix" in tags
    commit["is_feature"] = "feature" in tags

    return commit


def get_language_count(commits: list) -> int:
    """Count unique programming languages across all commits."""
    all_exts = set()
    code_exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".kt", ".swift", ".go",
                 ".rs", ".rb", ".php", ".c", ".cpp", ".h", ".cs", ".scala", ".r",
                 ".lua", ".dart", ".vue", ".svelte", ".zig", ".nim", ".ex", ".exs",
                 ".erl", ".hs", ".ml", ".clj", ".sh", ".sql"}
    for c in commits:
        for ext in c.get("extensions", set()):
            if ext in code_exts:
                all_exts.add(ext)
    return len(all_exts)


def count_commits_in_window(commits: list, hours: int = 1) -> int:
    """Find max commits within a sliding time window."""
    if not commits:
        return 0

    dates = []
    for c in commits:
        try:
            dates.append(datetime.fromisoformat(c["date"]))
        except (ValueError, KeyError):
            pass

    dates.sort()
    max_count = 1

    for i, d in enumerate(dates):
        count = 1
        for j in range(i + 1, len(dates)):
            if (dates[j] - d).total_seconds() <= hours * 3600:
                count += 1
            else:
                break
        max_count = max(max_count, count)

    return max_count
