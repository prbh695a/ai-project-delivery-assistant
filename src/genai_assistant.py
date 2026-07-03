from __future__ import annotations

from typing import Any


BLOCKER_KEYWORDS = [
    "blocked",
    "waiting",
    "dependency",
    "access",
    "input",
    "freeze",
    "unclear",
    "not clear",
    "needs review",
    "partially clear",
]


def analyze_project(summary: dict[str, Any]) -> dict[str, Any]:
    """Create deterministic AI-style delivery insights for a project summary.

    This function is intentionally rule-based so the public repository can run
    without sending data to any external AI service. In a real enterprise setup,
    the same normalized ticket payload can be sent to an approved LLM endpoint.
    """
    tickets = summary.get("tickets", [])
    blockers = []
    risks = []
    actions = []

    for ticket in tickets:
        status = str(ticket.get("status", ""))
        priority = str(ticket.get("priority", ""))
        description = str(ticket.get("description", ""))
        text = f"{status} {priority} {description}".lower()

        has_blocker = any(keyword in text for keyword in BLOCKER_KEYWORDS)
        risk_level = "Low"

        if status.lower() in {"blocked", "on hold", "waiting input"} or (
            priority.lower() == "high" and has_blocker
        ):
            risk_level = "High"
        elif priority.lower() in {"high", "medium"} or has_blocker:
            risk_level = "Medium"

        if has_blocker or status.lower() in {"blocked", "on hold", "waiting input"}:
            blockers.append(
                {
                    "ticket": ticket.get("id"),
                    "title": ticket.get("subject"),
                    "reason": description or status,
                    "owner": ticket.get("assignee"),
                }
            )

        risks.append(
            {
                "ticket": ticket.get("id"),
                "title": ticket.get("subject"),
                "risk_level": risk_level,
                "reason": _risk_reason(ticket, has_blocker),
            }
        )

        action = _next_action(ticket, has_blocker)
        if action:
            actions.append(action)

    return {
        "project_id": summary["project_id"],
        "summary": _summary_text(summary, blockers),
        "blockers": blockers,
        "risks": risks,
        "actions": actions,
        "stakeholder_update": _stakeholder_update(summary, blockers, actions),
    }


def render_insights_markdown(insights: list[dict[str, Any]]) -> str:
    parts = ["# AI Delivery Insights", ""]

    for item in insights:
        parts.append(f"## {item['project_id']}")
        parts.append("")
        parts.append("### Delivery summary")
        parts.append(item["summary"])
        parts.append("")

        parts.append("### Blockers")
        if item["blockers"]:
            for blocker in item["blockers"]:
                parts.append(
                    f"- OP#{blocker['ticket']} - {blocker['title']} | Owner: {blocker['owner']} | Reason: {blocker['reason']}"
                )
        else:
            parts.append("- No obvious blockers detected in the sample data.")
        parts.append("")

        parts.append("### Risk classification")
        for risk in item["risks"]:
            parts.append(
                f"- {risk['risk_level']}: OP#{risk['ticket']} - {risk['title']} | {risk['reason']}"
            )
        parts.append("")

        parts.append("### Recommended next actions")
        if item["actions"]:
            for action in item["actions"]:
                parts.append(f"- {action}")
        else:
            parts.append("- Continue normal sprint execution and monitor status changes.")
        parts.append("")

        parts.append("### Stakeholder update draft")
        parts.append(item["stakeholder_update"])
        parts.append("")

    return "\n".join(parts)


def _summary_text(summary: dict[str, Any], blockers: list[dict[str, Any]]) -> str:
    return (
        f"Project {summary['project_id']} has {summary['active_ticket_count']} active ticket(s), "
        f"{summary['closed_ticket_count']} closed ticket(s), and "
        f"{summary['blocked_ticket_count']} blocked ticket(s). "
        f"The latest ticket update is: {summary['latest_ticket_update']}. "
        f"Detected blocker count: {len(blockers)}."
    )


def _stakeholder_update(summary: dict[str, Any], blockers: list[dict[str, Any]], actions: list[str]) -> str:
    if blockers:
        blocker_text = "; ".join(
            f"OP#{blocker['ticket']} ({blocker['title']}) is blocked or at risk due to {blocker['reason']}"
            for blocker in blockers[:3]
        )
    else:
        blocker_text = "No major blocker was detected in the available ticket descriptions"

    action_text = " ".join(actions[:3]) if actions else "Continue monitoring the sprint and update the tracker after the next status change."

    return (
        f"Current project delivery status for {summary['project_id']} requires attention. "
        f"{blocker_text}. Recommended next step: {action_text}"
    )


def _risk_reason(ticket: dict[str, Any], has_blocker: bool) -> str:
    status = str(ticket.get("status", ""))
    priority = str(ticket.get("priority", ""))

    if status.lower() == "blocked":
        return "Ticket is blocked."
    if priority.lower() == "high" and has_blocker:
        return "High-priority item has a dependency or blocker signal."
    if has_blocker:
        return "Ticket description contains dependency, access, freeze, or uncertainty signals."
    return "No major blocker signal detected."


def _next_action(ticket: dict[str, Any], has_blocker: bool) -> str | None:
    ticket_id = ticket.get("id")
    title = ticket.get("subject")
    owner = ticket.get("assignee") or "owner"
    description = str(ticket.get("description", "")).lower()

    if "customer input" in description or "waiting" in description:
        return f"Escalate missing input for OP#{ticket_id} - {title} with {owner}."
    if "access" in description:
        return f"Confirm secure access dependency for OP#{ticket_id} - {title}."
    if "requirement" in description or "unclear" in description or "partially clear" in description:
        return f"Clarify requirement scope for OP#{ticket_id} - {title}."
    if "freeze" in description:
        return f"Confirm API freeze timeline before progressing OP#{ticket_id} - {title}."
    if "review" in description:
        return f"Schedule review and close open feedback for OP#{ticket_id} - {title}."
    if has_blocker:
        return f"Review blocker details for OP#{ticket_id} - {title}."
    return None
