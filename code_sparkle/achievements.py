"""Achievement system: 30+ achievements from git activity."""

from datetime import datetime
from collections import Counter


# Achievement definitions: (id, name, description, check_function_name)
ACHIEVEMENT_DEFS = [
    # Commit milestones
    ("first_blood", "First Blood", "Make your first commit", "check_first_blood"),
    ("ten_commits", "Getting Started", "Reach 10 commits", "check_commit_count"),
    ("fifty_commits", "Committed", "Reach 50 commits", "check_commit_count"),
    ("century", "Century", "Reach 100 commits", "check_commit_count"),
    ("five_hundred", "Half Thousand", "Reach 500 commits", "check_commit_count"),
    ("thousand", "Thousand Club", "Reach 1,000 commits", "check_commit_count"),

    # Bug fixing
    ("bug_squasher", "Bug Squasher", "Fix 10 bugs (commits with 'fix' in message)", "check_bugfix_count"),
    ("exterminator", "Exterminator", "Fix 50 bugs", "check_bugfix_count"),

    # Testing
    ("test_writer", "Test Writer", "Add test files in 5 commits", "check_test_count"),
    ("test_champion", "Test Champion", "Add test files in 25 commits", "check_test_count"),

    # Documentation
    ("doc_hero", "Documentation Hero", "Update docs/README in 5 commits", "check_doc_count"),
    ("doc_legend", "Documentation Legend", "Update docs in 25 commits", "check_doc_count"),

    # Time patterns
    ("night_owl", "Night Owl", "Make 10 commits between 10pm-4am", "check_night_commits"),
    ("early_bird", "Early Bird", "Make 10 commits between 5am-8am", "check_morning_commits"),
    ("weekend_warrior", "Weekend Warrior", "Make 20 commits on weekends", "check_weekend_commits"),

    # Speed
    ("speed_demon", "Speed Demon", "3 commits in 1 hour", "check_speed"),
    ("turbo_coder", "Turbo Coder", "5 commits in 1 hour", "check_speed"),

    # Polyglot
    ("bilingual", "Bilingual", "Commit code in 2+ languages", "check_languages"),
    ("polyglot", "Polyglot", "Commit code in 5+ languages", "check_languages"),
    ("hyperglot", "Hyperglot", "Commit code in 10+ languages", "check_languages"),

    # Size
    ("big_bang", "Big Bang", "Single commit with 500+ lines", "check_big_commit"),
    ("atomic", "Atomic Committer", "10 commits with < 10 lines each", "check_small_commits"),

    # Features
    ("feature_factory", "Feature Factory", "Ship 10 features", "check_feature_count"),
    ("innovator", "Innovator", "Ship 25 features", "check_feature_count"),

    # Streaks
    ("streak_3", "On a Roll", "3-day commit streak", "check_streak"),
    ("streak_7", "Streak Master", "7-day commit streak", "check_streak"),
    ("streak_14", "Unstoppable", "14-day commit streak", "check_streak"),
    ("streak_30", "Marathon Coder", "30-day commit streak", "check_streak"),

    # Files
    ("many_files", "Octopus", "Single commit touching 10+ files", "check_many_files"),
    ("refactorer", "Refactorer", "10 refactoring commits", "check_refactor_count"),

    # XP
    ("xp_1k", "Rising Star", "Earn 1,000 XP", "check_xp"),
    ("xp_5k", "Seasoned Dev", "Earn 5,000 XP", "check_xp"),
    ("xp_10k", "XP Master", "Earn 10,000 XP", "check_xp"),
    ("xp_50k", "XP Legend", "Earn 50,000 XP", "check_xp"),
]


def check_achievements(commits: list, total_xp: int, streak_info: dict) -> list:
    """Check all achievements against current state. Returns list of newly earned achievement IDs."""
    earned = []
    state = _build_state(commits, total_xp, streak_info)

    for ach_id, name, desc, check_fn in ACHIEVEMENT_DEFS:
        if _check_achievement(ach_id, state):
            earned.append((ach_id, name, desc))

    return earned


def _build_state(commits: list, total_xp: int, streak_info: dict) -> dict:
    """Build state dict for achievement checking."""
    total = len(commits)
    bugfix_count = sum(1 for c in commits if c.get("is_bugfix"))
    test_count = sum(1 for c in commits if c.get("has_tests"))
    doc_count = sum(1 for c in commits if c.get("has_docs"))
    feature_count = sum(1 for c in commits if c.get("is_feature"))
    refactor_count = sum(1 for c in commits if c.get("tags") and "refactor" in c["tags"])

    night_commits = 0
    morning_commits = 0
    weekend_commits = 0
    max_lines = 0
    small_commits = 0
    max_files = 0
    max_speed = 1

    all_extensions = set()

    for c in commits:
        lines = c.get("lines_added", 0) + c.get("lines_deleted", 0)
        max_lines = max(max_lines, lines)
        if lines < 10:
            small_commits += 1
        max_files = max(max_files, c.get("files_changed", 0))

        for ext in c.get("extensions", set()):
            all_extensions.add(ext)

        try:
            dt = datetime.fromisoformat(c.get("date", ""))
            if dt.hour >= 22 or dt.hour < 4:
                night_commits += 1
            if 5 <= dt.hour <= 8:
                morning_commits += 1
            if dt.weekday() >= 5:
                weekend_commits += 1
        except (ValueError, TypeError):
            pass

    # Speed: max commits in 1 hour window
    from code_sparkle.tracker import count_commits_in_window
    max_speed = count_commits_in_window(commits, hours=1)

    # Language count (code extensions only)
    from code_sparkle.tracker import get_language_count
    lang_count = get_language_count(commits)

    return {
        "total_commits": total,
        "bugfix_count": bugfix_count,
        "test_count": test_count,
        "doc_count": doc_count,
        "feature_count": feature_count,
        "refactor_count": refactor_count,
        "night_commits": night_commits,
        "morning_commits": morning_commits,
        "weekend_commits": weekend_commits,
        "max_lines": max_lines,
        "small_commits": small_commits,
        "max_files": max_files,
        "max_speed": max_speed,
        "lang_count": lang_count,
        "total_xp": total_xp,
        "current_streak": streak_info.get("current_streak", 0),
        "longest_streak": streak_info.get("longest_streak", 0),
    }


def _check_achievement(ach_id: str, state: dict) -> bool:
    """Check if a specific achievement is met."""
    checks = {
        "first_blood": state["total_commits"] >= 1,
        "ten_commits": state["total_commits"] >= 10,
        "fifty_commits": state["total_commits"] >= 50,
        "century": state["total_commits"] >= 100,
        "five_hundred": state["total_commits"] >= 500,
        "thousand": state["total_commits"] >= 1000,
        "bug_squasher": state["bugfix_count"] >= 10,
        "exterminator": state["bugfix_count"] >= 50,
        "test_writer": state["test_count"] >= 5,
        "test_champion": state["test_count"] >= 25,
        "doc_hero": state["doc_count"] >= 5,
        "doc_legend": state["doc_count"] >= 25,
        "night_owl": state["night_commits"] >= 10,
        "early_bird": state["morning_commits"] >= 10,
        "weekend_warrior": state["weekend_commits"] >= 20,
        "speed_demon": state["max_speed"] >= 3,
        "turbo_coder": state["max_speed"] >= 5,
        "bilingual": state["lang_count"] >= 2,
        "polyglot": state["lang_count"] >= 5,
        "hyperglot": state["lang_count"] >= 10,
        "big_bang": state["max_lines"] >= 500,
        "atomic": state["small_commits"] >= 10,
        "feature_factory": state["feature_count"] >= 10,
        "innovator": state["feature_count"] >= 25,
        "streak_3": state["longest_streak"] >= 3,
        "streak_7": state["longest_streak"] >= 7,
        "streak_14": state["longest_streak"] >= 14,
        "streak_30": state["longest_streak"] >= 30,
        "many_files": state["max_files"] >= 10,
        "refactorer": state["refactor_count"] >= 10,
        "xp_1k": state["total_xp"] >= 1000,
        "xp_5k": state["total_xp"] >= 5000,
        "xp_10k": state["total_xp"] >= 10000,
        "xp_50k": state["total_xp"] >= 50000,
    }
    return checks.get(ach_id, False)
