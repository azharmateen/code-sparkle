"""XP system: earn XP per commit with bonuses. Level up with titles."""

from dataclasses import dataclass

# XP thresholds for levels
LEVELS = [
    (1, 0, "Beginner"),
    (2, 100, "Apprentice"),
    (3, 300, "Novice"),
    (4, 600, "Junior"),
    (5, 1000, "Developer"),
    (6, 1800, "Skilled Developer"),
    (7, 3000, "Senior Developer"),
    (8, 5000, "Lead Developer"),
    (9, 8000, "Staff Engineer"),
    (10, 12000, "Principal Engineer"),
    (11, 18000, "Architect"),
    (12, 25000, "Senior Architect"),
    (13, 35000, "Distinguished Engineer"),
    (14, 50000, "Fellow"),
    (15, 75000, "Legend"),
    (16, 100000, "Mythical"),
]

# XP values
BASE_XP = 10          # Per commit
LINE_XP = 0.1         # Per line changed (added + deleted)
FILE_XP = 2           # Per file changed
TEST_BONUS = 15       # Bonus for commits with test files
DOC_BONUS = 10        # Bonus for documentation
FEATURE_BONUS = 20    # Bonus for feature commits
BUGFIX_BONUS = 15     # Bonus for bug fixes
REFACTOR_BONUS = 10   # Bonus for refactors
WEEKEND_BONUS = 5     # Bonus for weekend commits
NIGHT_BONUS = 5       # Bonus for night owl commits (10pm-4am)
LARGE_COMMIT = 25     # Bonus for commits with 100+ lines
STREAK_BONUS = 5      # Bonus per day of active streak


def calculate_commit_xp(commit: dict, streak_days: int = 0) -> int:
    """Calculate XP earned for a single commit."""
    xp = BASE_XP

    # Lines changed
    lines = commit.get("lines_added", 0) + commit.get("lines_deleted", 0)
    xp += int(lines * LINE_XP)

    # Files changed
    xp += commit.get("files_changed", 0) * FILE_XP

    # Tag bonuses
    if commit.get("has_tests"):
        xp += TEST_BONUS
    if commit.get("has_docs"):
        xp += DOC_BONUS
    if commit.get("is_feature"):
        xp += FEATURE_BONUS
    if commit.get("is_bugfix"):
        xp += BUGFIX_BONUS
    if commit.get("tags") and "refactor" in commit["tags"]:
        xp += REFACTOR_BONUS

    # Large commit bonus
    if lines >= 100:
        xp += LARGE_COMMIT

    # Weekend bonus
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(commit.get("date", ""))
        if dt.weekday() >= 5:  # Saturday or Sunday
            xp += WEEKEND_BONUS
        if dt.hour >= 22 or dt.hour < 4:  # Night owl
            xp += NIGHT_BONUS
    except (ValueError, TypeError):
        pass

    # Streak bonus
    if streak_days > 0:
        xp += min(streak_days, 30) * STREAK_BONUS  # Cap at 30-day streak bonus

    return max(xp, 1)


def calculate_level(total_xp: int) -> tuple:
    """Calculate level and title from total XP. Returns (level, title, xp_for_next, xp_progress)."""
    current_level = 1
    current_title = "Beginner"
    next_threshold = LEVELS[1][1] if len(LEVELS) > 1 else float("inf")

    for i, (level, threshold, title) in enumerate(LEVELS):
        if total_xp >= threshold:
            current_level = level
            current_title = title
            if i + 1 < len(LEVELS):
                next_threshold = LEVELS[i + 1][1]
            else:
                next_threshold = threshold  # Max level
        else:
            break

    # Progress to next level
    current_threshold = LEVELS[current_level - 1][1] if current_level <= len(LEVELS) else 0
    xp_in_level = total_xp - current_threshold
    xp_needed = next_threshold - current_threshold

    progress = (xp_in_level / xp_needed * 100) if xp_needed > 0 else 100.0

    return current_level, current_title, next_threshold, progress


def format_xp_bar(progress: float, width: int = 20) -> str:
    """Create a text-based progress bar."""
    filled = int(width * progress / 100)
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {progress:.1f}%"
