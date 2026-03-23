"""Badge generator: SVG badges for GitHub profile README."""

import os


def generate_level_badge(level: int, title: str, total_xp: int) -> str:
    """Generate an SVG badge showing current level and title."""
    # Color gradient based on level
    colors = {
        1: ("#6c757d", "#adb5bd"),   # Gray
        2: ("#28a745", "#5cb85c"),   # Green
        3: ("#28a745", "#5cb85c"),
        4: ("#17a2b8", "#5bc0de"),   # Teal
        5: ("#007bff", "#5dade2"),   # Blue
        6: ("#007bff", "#5dade2"),
        7: ("#6f42c1", "#9b59b6"),   # Purple
        8: ("#6f42c1", "#9b59b6"),
        9: ("#fd7e14", "#f39c12"),   # Orange
        10: ("#fd7e14", "#f39c12"),
        11: ("#e83e8c", "#e74c3c"),  # Pink/Red
        12: ("#e83e8c", "#e74c3c"),
        13: ("#ffc107", "#f1c40f"),  # Gold
        14: ("#ffc107", "#f1c40f"),
        15: ("#ffc107", "#f1c40f"),
        16: ("#ffc107", "#f1c40f"),
    }
    bg, fg = colors.get(level, ("#6c757d", "#adb5bd"))

    label = f"Level {level}"
    value = title
    label_width = len(label) * 7 + 12
    value_width = len(value) * 7 + 12
    total_width = label_width + value_width

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a"><rect width="{total_width}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#a)">
    <path fill="#555" d="M0 0h{label_width}v20H0z"/>
    <path fill="{bg}" d="M{label_width} 0h{value_width}v20H{label_width}z"/>
    <path fill="url(#b)" d="M0 0h{total_width}v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_width/2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width/2}" y="14">{label}</text>
    <text x="{label_width + value_width/2}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{label_width + value_width/2}" y="14">{value}</text>
  </g>
</svg>"""


def generate_streak_badge(current_streak: int, longest_streak: int) -> str:
    """Generate an SVG badge showing streak info."""
    if current_streak >= 14:
        bg = "#e74c3c"  # Red hot
    elif current_streak >= 7:
        bg = "#fd7e14"  # Orange
    elif current_streak >= 3:
        bg = "#ffc107"  # Yellow
    elif current_streak > 0:
        bg = "#28a745"  # Green
    else:
        bg = "#6c757d"  # Gray

    label = "Streak"
    value = f"{current_streak} days (best: {longest_streak})"
    label_width = len(label) * 7 + 12
    value_width = len(value) * 6.5 + 12
    total_width = int(label_width + value_width)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a"><rect width="{total_width}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#a)">
    <path fill="#555" d="M0 0h{int(label_width)}v20H0z"/>
    <path fill="{bg}" d="M{int(label_width)} 0h{int(value_width)}v20H{int(label_width)}z"/>
    <path fill="url(#b)" d="M0 0h{total_width}v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
    <text x="{int(label_width/2)}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{int(label_width/2)}" y="14">{label}</text>
    <text x="{int(label_width + value_width/2)}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{int(label_width + value_width/2)}" y="14">{value}</text>
  </g>
</svg>"""


def generate_xp_badge(total_xp: int) -> str:
    """Generate an SVG badge showing total XP."""
    if total_xp >= 50000:
        bg = "#ffc107"
    elif total_xp >= 10000:
        bg = "#6f42c1"
    elif total_xp >= 1000:
        bg = "#007bff"
    else:
        bg = "#28a745"

    label = "XP"
    value = f"{total_xp:,}"
    label_width = len(label) * 7 + 12
    value_width = len(value) * 7 + 12
    total_width = label_width + value_width

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="20">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a"><rect width="{total_width}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#a)">
    <path fill="#555" d="M0 0h{label_width}v20H0z"/>
    <path fill="{bg}" d="M{label_width} 0h{value_width}v20H{label_width}z"/>
    <path fill="url(#b)" d="M0 0h{total_width}v20H0z"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">
    <text x="{label_width/2}" y="15" fill="#010101" fill-opacity=".3">{label}</text>
    <text x="{label_width/2}" y="14">{label}</text>
    <text x="{label_width + value_width/2}" y="15" fill="#010101" fill-opacity=".3">{value}</text>
    <text x="{label_width + value_width/2}" y="14">{value}</text>
  </g>
</svg>"""


def save_badges(level: int, title: str, total_xp: int,
                current_streak: int, longest_streak: int,
                output_dir: str = ".") -> list:
    """Save all badges as SVG files."""
    os.makedirs(output_dir, exist_ok=True)
    saved = []

    badges = {
        "level-badge.svg": generate_level_badge(level, title, total_xp),
        "streak-badge.svg": generate_streak_badge(current_streak, longest_streak),
        "xp-badge.svg": generate_xp_badge(total_xp),
    }

    for filename, svg in badges.items():
        path = os.path.join(output_dir, filename)
        with open(path, "w") as f:
            f.write(svg)
        saved.append(os.path.abspath(path))

    return saved
