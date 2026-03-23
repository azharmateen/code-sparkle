"""Code Sparkle CLI - Gamify your coding workflow."""

import json
import os
import sys
import click

from code_sparkle.tracker import parse_commits, classify_commit, get_git_user
from code_sparkle.xp import calculate_commit_xp, calculate_level, format_xp_bar
from code_sparkle.achievements import check_achievements, ACHIEVEMENT_DEFS
from code_sparkle.streaks import calculate_streaks, format_streak_display
from code_sparkle.badges import save_badges
from code_sparkle.storage import (
    get_or_create_profile, update_profile_xp, log_activity,
    get_total_xp, get_achievements, unlock_achievement,
    record_streak_day, get_streak_days, get_activity_count,
)


def _sync_repo(repo_path: str) -> dict:
    """Sync git activity for a repo and return current state."""
    repo_path = os.path.abspath(repo_path)
    profile = get_or_create_profile(repo_path)

    # Parse and classify commits
    commits = parse_commits(repo_path)
    classified = [classify_commit(c) for c in commits]

    # Calculate streaks
    streak_info = calculate_streaks(classified)

    # Log new activity and calculate XP
    new_xp = 0
    new_commits = 0
    for c in classified:
        xp = calculate_commit_xp(c, streak_info.get("current_streak", 0))
        was_new = log_activity(
            profile["id"],
            c["hash"],
            c.get("date", ""),
            c.get("message", ""),
            c.get("lines_added", 0),
            c.get("lines_deleted", 0),
            c.get("files_changed", 0),
            json.dumps(c.get("files", [])),
            xp,
        )
        if was_new:
            new_xp += xp
            new_commits += 1

    # Record streak days
    for c in classified:
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(c["date"])
            date_str = dt.strftime("%Y-%m-%d")
            record_streak_day(profile["id"], date_str, 1)
        except (ValueError, KeyError):
            pass

    # Get total XP and level
    total_xp = get_total_xp(profile["id"])
    level, title, next_threshold, progress = calculate_level(total_xp)

    # Update profile
    update_profile_xp(profile["id"], total_xp, level, title)

    # Check achievements
    existing = {a["achievement_id"] for a in get_achievements(profile["id"])}
    earned = check_achievements(classified, total_xp, streak_info)
    new_achievements = []
    for ach_id, name, desc in earned:
        if ach_id not in existing:
            if unlock_achievement(profile["id"], ach_id, name, desc):
                new_achievements.append((ach_id, name, desc))

    return {
        "profile": profile,
        "total_xp": total_xp,
        "level": level,
        "title": title,
        "next_threshold": next_threshold,
        "progress": progress,
        "streak_info": streak_info,
        "new_xp": new_xp,
        "new_commits": new_commits,
        "new_achievements": new_achievements,
        "total_commits": len(classified),
        "total_achievements": len(existing) + len(new_achievements),
        "classified_commits": classified,
    }


@click.group()
@click.version_option(version="1.0.0", prog_name="code-sparkle")
def cli():
    """Code Sparkle - Gamify your coding workflow.

    Earn XP, unlock achievements, and track streaks from your git activity.
    """
    pass


@cli.command()
@click.option("--repo", "-r", default=".", help="Path to git repository")
def status(repo):
    """Show your current level, XP, streak, and recent achievements."""
    repo = os.path.abspath(repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        click.echo(f"Error: {repo} is not a git repository", err=True)
        sys.exit(1)

    click.echo("Syncing git activity...")
    state = _sync_repo(repo)

    click.echo()
    click.echo("=" * 50)
    click.echo("  CODE SPARKLE")
    click.echo("=" * 50)

    # Level and XP
    click.echo(f"\n  Level {state['level']}: {state['title']}")
    click.echo(f"  XP: {state['total_xp']:,} / {state['next_threshold']:,}")
    click.echo(f"  {format_xp_bar(state['progress'])}")

    # Streak
    streak = state["streak_info"]
    if streak["current_streak"] > 0:
        fires = "*" * min(streak["current_streak"], 20)
        click.echo(f"\n  Streak: {streak['current_streak']} days {fires}")
    else:
        click.echo(f"\n  Streak: 0 (commit today to start!)")
    click.echo(f"  Longest: {streak['longest_streak']} days")

    # Stats
    click.echo(f"\n  Total Commits: {state['total_commits']}")
    click.echo(f"  Achievements: {state['total_achievements']}/{len(ACHIEVEMENT_DEFS)}")

    # New stuff
    if state["new_commits"] > 0:
        click.echo(f"\n  NEW: +{state['new_xp']} XP from {state['new_commits']} new commit(s)")

    if state["new_achievements"]:
        click.echo(f"\n  NEW ACHIEVEMENTS UNLOCKED!")
        for _, name, desc in state["new_achievements"]:
            click.echo(f"    [*] {name} - {desc}")

    click.echo("\n" + "=" * 50)


@cli.command()
@click.option("--repo", "-r", default=".", help="Path to git repository")
def achievements(repo):
    """Show all achievements and progress."""
    repo = os.path.abspath(repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        click.echo(f"Error: {repo} is not a git repository", err=True)
        sys.exit(1)

    state = _sync_repo(repo)
    profile = state["profile"]
    unlocked = {a["achievement_id"]: a for a in get_achievements(profile["id"])}

    click.echo()
    click.echo("=" * 60)
    click.echo("  ACHIEVEMENTS")
    click.echo("=" * 60)
    click.echo(f"  Unlocked: {len(unlocked)}/{len(ACHIEVEMENT_DEFS)}")
    click.echo()

    for ach_id, name, desc, _ in ACHIEVEMENT_DEFS:
        if ach_id in unlocked:
            date = unlocked[ach_id]["unlocked_at"][:10]
            click.echo(f"  [DONE] {name}")
            click.echo(f"         {desc} (unlocked {date})")
        else:
            click.echo(f"  [    ] {name}")
            click.echo(f"         {desc}")

    click.echo()


@cli.command()
@click.option("--repo", "-r", default=".", help="Path to git repository")
def streak(repo):
    """Show detailed streak information."""
    repo = os.path.abspath(repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        click.echo(f"Error: {repo} is not a git repository", err=True)
        sys.exit(1)

    state = _sync_repo(repo)
    click.echo(format_streak_display(state["streak_info"]))


@cli.command()
@click.option("--repo", "-r", default=".", help="Path to git repository")
def leaderboard(repo):
    """Show XP leaderboard (multi-repo comparison)."""
    # For single repo, show top contributors by simulated XP
    repo = os.path.abspath(repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        click.echo(f"Error: {repo} is not a git repository", err=True)
        sys.exit(1)

    state = _sync_repo(repo)
    commits = state["classified_commits"]

    # Group by author
    from collections import defaultdict
    author_xp = defaultdict(lambda: {"xp": 0, "commits": 0})
    for c in commits:
        author = c.get("author_name", "Unknown")
        xp = calculate_commit_xp(c)
        author_xp[author]["xp"] += xp
        author_xp[author]["commits"] += 1

    # Sort by XP
    leaderboard_data = sorted(author_xp.items(), key=lambda x: x[1]["xp"], reverse=True)

    click.echo()
    click.echo("=" * 55)
    click.echo("  LEADERBOARD")
    click.echo("=" * 55)
    click.echo()
    click.echo(f"  {'#':<4} {'Developer':<25} {'XP':>8} {'Commits':>8}")
    click.echo("  " + "-" * 50)

    for i, (author, data) in enumerate(leaderboard_data[:20]):
        level, title, _, _ = calculate_level(data["xp"])
        medal = ""
        if i == 0:
            medal = " [1st]"
        elif i == 1:
            medal = " [2nd]"
        elif i == 2:
            medal = " [3rd]"
        click.echo(f"  {i+1:<4} {author[:23]:<25} {data['xp']:>8,} {data['commits']:>8}{medal}")

    click.echo()


@cli.command()
@click.option("--repo", "-r", default=".", help="Path to git repository")
def profile(repo):
    """Show detailed profile and stats."""
    repo = os.path.abspath(repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        click.echo(f"Error: {repo} is not a git repository", err=True)
        sys.exit(1)

    state = _sync_repo(repo)
    user = get_git_user(repo)

    click.echo()
    click.echo("=" * 50)
    click.echo(f"  PROFILE: {user}")
    click.echo("=" * 50)
    click.echo(f"\n  Level {state['level']}: {state['title']}")
    click.echo(f"  Total XP: {state['total_xp']:,}")
    click.echo(f"  {format_xp_bar(state['progress'])}")
    click.echo(f"  Next level at: {state['next_threshold']:,} XP")
    click.echo(f"\n  Commits: {state['total_commits']}")
    click.echo(f"  Achievements: {state['total_achievements']}/{len(ACHIEVEMENT_DEFS)}")
    click.echo(f"  Current Streak: {state['streak_info']['current_streak']} days")
    click.echo(f"  Longest Streak: {state['streak_info']['longest_streak']} days")
    click.echo(f"  Active Days: {state['streak_info']['total_active_days']}")
    click.echo()


@cli.command(name="badges")
@click.option("--repo", "-r", default=".", help="Path to git repository")
@click.option("--output", "-o", default=".", help="Output directory for SVG badges")
def generate_badges(repo, output):
    """Generate SVG badges for your GitHub profile README."""
    repo = os.path.abspath(repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        click.echo(f"Error: {repo} is not a git repository", err=True)
        sys.exit(1)

    state = _sync_repo(repo)
    streak = state["streak_info"]

    saved = save_badges(
        level=state["level"],
        title=state["title"],
        total_xp=state["total_xp"],
        current_streak=streak["current_streak"],
        longest_streak=streak["longest_streak"],
        output_dir=output,
    )

    click.echo("Badges generated:")
    for path in saved:
        click.echo(f"  {path}")
    click.echo("\nAdd to your README.md:")
    click.echo("  ![Level](./level-badge.svg) ![Streak](./streak-badge.svg) ![XP](./xp-badge.svg)")


@cli.command(name="hook")
@click.argument("action", type=click.Choice(["install", "uninstall"]))
@click.option("--repo", "-r", default=".", help="Path to git repository")
def hook(action, repo):
    """Install/uninstall git post-commit hook for automatic tracking."""
    repo = os.path.abspath(repo)
    hooks_dir = os.path.join(repo, ".git", "hooks")

    if not os.path.isdir(hooks_dir):
        click.echo(f"Error: {repo} is not a git repository", err=True)
        sys.exit(1)

    hook_path = os.path.join(hooks_dir, "post-commit")

    if action == "install":
        hook_content = """#!/bin/sh
# Code Sparkle - Auto XP tracking
code-sparkle status --repo "$(git rev-parse --show-toplevel)" 2>/dev/null || true
"""
        with open(hook_path, "w") as f:
            f.write(hook_content)
        os.chmod(hook_path, 0o755)
        click.echo(f"Post-commit hook installed at {hook_path}")
        click.echo("Every commit will now auto-sync your XP and achievements!")

    elif action == "uninstall":
        if os.path.exists(hook_path):
            # Only remove if it's our hook
            with open(hook_path) as f:
                content = f.read()
            if "Code Sparkle" in content:
                os.remove(hook_path)
                click.echo("Post-commit hook removed.")
            else:
                click.echo("Hook exists but wasn't installed by Code Sparkle. Skipping.")
        else:
            click.echo("No post-commit hook found.")


if __name__ == "__main__":
    cli()
