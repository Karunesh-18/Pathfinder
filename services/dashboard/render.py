"""render.py — chart_render stand-in.

Per ARCHITECTURE.md Section 03, card 08, `chart_render` turns the
DashboardViewModel into the skill-radar / timeline visuals the brief asks
for. This prototype is a backend script with no frontend built anywhere in
this project — there's nothing to render a chart library into yet — so
this produces a plain-text approximation instead: a bar per skill for the
radar, and separate completed/remaining sections for the timeline. Good
enough for a by-eye sanity check; a real chart_render would hand this same
DashboardViewModel to a charting library or frontend component instead.
"""

from __future__ import annotations

from dashboard_schema import DashboardViewModel

_BAR_WIDTH = 20


def _bar(value: int, max_value: int = 3) -> str:
    filled = round((value / max_value) * _BAR_WIDTH) if max_value else 0
    return "#" * filled + "-" * (_BAR_WIDTH - filled)


def render_text(dashboard: DashboardViewModel) -> str:
    lines: list[str] = []
    lines.append(f"Dashboard for learner {dashboard.learner_id}  (target role: {dashboard.target_role})")

    lines.append("")
    lines.append("SKILL RADAR (current vs. required)")
    lines.append("-" * 60)
    for point in dashboard.skill_radar:
        lines.append(
            f"  {point.skill:<22s} [{_bar(point.current_value)}] "
            f"{point.current_level:<12s} -> need {point.required_level}"
        )

    lines.append("")
    lines.append("COMPLETED")
    lines.append("-" * 60)
    if dashboard.completed_history:
        for h in dashboard.completed_history:
            lines.append(f"  [x] {h.title} ({h.provider})  {h.estimated_hours:.0f}h")
    else:
        lines.append("  (nothing completed yet)")

    lines.append("")
    lines.append("REMAINING TIMELINE")
    lines.append("-" * 60)
    if dashboard.remaining_timeline:
        for step in dashboard.remaining_timeline:
            marker = " *MILESTONE*" if step.milestone else ""
            lines.append(
                f"  [ ] step {step.step_index}: {step.title} ({step.provider})  "
                f"cum {step.cumulative_hours:.0f}h, ~week {step.estimated_completion_week}{marker}"
            )
    else:
        lines.append("  (plan complete — nothing remaining)")

    lines.append("")
    lines.append("NEXT RECOMMENDED ACTION")
    lines.append("-" * 60)
    if dashboard.next_action:
        na = dashboard.next_action
        lines.append(f"  step {na.step_index}: {na.title} ({na.provider}) -> addresses {na.skill_gap_addressed}")
    else:
        lines.append("  Plan complete - no further action needed.")

    lines.append("")
    lines.append("SUMMARY")
    lines.append("-" * 60)
    s = dashboard.summary
    lines.append(
        f"  {s.completed_courses} course(s) done, {s.remaining_steps} remaining  |  "
        f"{s.completed_hours:.0f}h done / {s.remaining_hours:.0f}h remaining "
        f"({s.overall_progress_pct:.1f}% overall)  |  ~{s.weeks_remaining} weeks to finish"
    )

    return "\n".join(lines)
