"""Streak tracker: daily commit streaks, weekend bonus, current/longest streak."""

from datetime import datetime, timedelta
from collections import Counter


def calculate_streaks(commits: list) -> dict:
    """Calculate streak information from commit list."""
    if not commits:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_active_days": 0,
            "streaks": [],
        }

    # Get unique dates with commits
    commit_dates = set()
    for c in commits:
        try:
            dt = datetime.fromisoformat(c["date"])
            commit_dates.add(dt.strftime("%Y-%m-%d"))
        except (ValueError, KeyError):
            pass

    if not commit_dates:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_active_days": 0,
            "streaks": [],
        }

    # Sort dates
    sorted_dates = sorted(commit_dates)
    date_objects = [datetime.strptime(d, "%Y-%m-%d") for d in sorted_dates]

    # Find all streaks
    streaks = []
    current_streak_start = date_objects[0]
    current_streak_length = 1

    for i in range(1, len(date_objects)):
        delta = (date_objects[i] - date_objects[i - 1]).days
        if delta == 1:
            current_streak_length += 1
        else:
            streaks.append({
                "start": current_streak_start.strftime("%Y-%m-%d"),
                "end": date_objects[i - 1].strftime("%Y-%m-%d"),
                "length": current_streak_length,
            })
            current_streak_start = date_objects[i]
            current_streak_length = 1

    # Don't forget the last streak
    streaks.append({
        "start": current_streak_start.strftime("%Y-%m-%d"),
        "end": date_objects[-1].strftime("%Y-%m-%d"),
        "length": current_streak_length,
    })

    # Current streak: check if the last commit date is today or yesterday
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    last_streak = streaks[-1]
    if last_streak["end"] == today or last_streak["end"] == yesterday:
        current_streak = last_streak["length"]
        # If yesterday, the streak is still alive but needs today's commit
        if last_streak["end"] == yesterday:
            current_streak = last_streak["length"]  # Still counts
    else:
        current_streak = 0

    longest_streak = max(s["length"] for s in streaks) if streaks else 0

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_active_days": len(commit_dates),
        "streaks": sorted(streaks, key=lambda s: s["length"], reverse=True)[:10],
    }


def format_streak_display(streak_info: dict) -> str:
    """Format streak info for terminal display."""
    lines = []
    lines.append("=" * 50)
    lines.append("  STREAK STATUS")
    lines.append("=" * 50)

    current = streak_info["current_streak"]
    longest = streak_info["longest_streak"]

    # Streak fire visualization
    if current > 0:
        fires = min(current, 30)
        fire_bar = "*" * fires
        lines.append(f"\n  Current Streak: {current} days {fire_bar}")
    else:
        lines.append(f"\n  Current Streak: 0 days (commit today to start!)")

    lines.append(f"  Longest Streak: {longest} days")
    lines.append(f"  Total Active Days: {streak_info['total_active_days']}")

    # Top streaks
    if streak_info["streaks"]:
        lines.append(f"\n  Top Streaks:")
        for i, s in enumerate(streak_info["streaks"][:5]):
            marker = " <-- ACTIVE" if i == 0 and s["length"] == current and current > 0 else ""
            lines.append(f"    {s['length']} days ({s['start']} to {s['end']}){marker}")

    # Motivational message
    if current == 0:
        lines.append("\n  Make a commit today to start a new streak!")
    elif current < 3:
        lines.append(f"\n  Keep going! {3 - current} more day(s) to 'On a Roll' achievement!")
    elif current < 7:
        lines.append(f"\n  Nice streak! {7 - current} more day(s) to 'Streak Master'!")
    elif current < 14:
        lines.append(f"\n  Impressive! {14 - current} more day(s) to 'Unstoppable'!")
    elif current < 30:
        lines.append(f"\n  Incredible! {30 - current} more day(s) to 'Marathon Coder'!")
    else:
        lines.append(f"\n  LEGENDARY {current}-day streak! You are unstoppable!")

    lines.append("\n" + "=" * 50)
    return "\n".join(lines)
