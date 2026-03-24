# Code Sparkle

[![Built with Claude Code](https://img.shields.io/badge/Built%20with-Claude%20Code-blue?logo=anthropic&logoColor=white)](https://claude.ai/code)


> Gamify your coding workflow: achievements, streaks, XP, and badges from git activity.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Turn every `git commit` into a dopamine hit.** Code Sparkle tracks your git activity, awards XP, unlocks achievements, and maintains streak counters. Think GitHub contribution graph meets RPG leveling.

## Features

- **XP System** - Earn XP per commit with bonuses for tests, docs, features, and bug fixes
- **16 Levels** - From Beginner to Mythical, with titles like "Architect" and "Legend"
- **30+ Achievements** - "Night Owl", "Bug Squasher", "Polyglot", "Speed Demon", and more
- **Streak Tracking** - Daily commit streaks with motivational messages
- **SVG Badges** - Generate badges for your GitHub profile README
- **Leaderboard** - Compare contributors by XP
- **Git Hook** - Auto-track on every commit

## Install

```bash
pip install code-sparkle
```

## Quick Start

```bash
# Check your status (syncs git activity automatically)
code-sparkle status

# View all achievements
code-sparkle achievements

# Check your streak
code-sparkle streak

# See the leaderboard
code-sparkle leaderboard

# Generate badges for your README
code-sparkle badges --output ./badges

# Install auto-tracking hook
code-sparkle hook install
```

## XP Breakdown

| Action | XP |
|--------|-----|
| Each commit | 10 base |
| Lines changed | 0.1 per line |
| Files touched | 2 per file |
| Includes tests | +15 bonus |
| Includes docs | +10 bonus |
| New feature | +20 bonus |
| Bug fix | +15 bonus |
| Weekend commit | +5 bonus |
| Night owl (10pm-4am) | +5 bonus |
| Large commit (100+ lines) | +25 bonus |
| Active streak (per day) | +5 bonus |

## Achievements (30+)

Unlock achievements by coding consistently:

- **First Blood** - Make your first commit
- **Night Owl** - 10 commits between 10pm-4am
- **Weekend Warrior** - 20 weekend commits
- **Speed Demon** - 3 commits in 1 hour
- **Polyglot** - Code in 5+ languages
- **Streak Master** - 7-day commit streak
- **Marathon Coder** - 30-day commit streak
- **Bug Squasher** - Fix 10 bugs
- **Documentation Hero** - Update docs in 5 commits
- ...and many more!

## Badges

Generate SVG badges for your GitHub profile:

```bash
code-sparkle badges --output ./badges
```

Then add to your README:

```markdown
![Level](./badges/level-badge.svg) ![Streak](./badges/streak-badge.svg) ![XP](./badges/xp-badge.svg)
```

## License

MIT
