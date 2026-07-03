from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any


def extract_ticket(raw_ticket: dict[str, Any], project_id_custom_field: str) -> dict[str, Any]:
    """Normalize one OpenProject work package into a simpler ticket object."""
    links = raw_ticket.get("_links", {})

    return {
        "id": raw_ticket.get("id"),
        "project_id": raw_ticket.get(project_id_custom_field),
        "subject": raw_ticket.get("subject", ""),
        "status": links.get("status", {}).get("title", ""),
        "assignee": links.get("assignee", {}).get("title", ""),
        "priority": links.get("priority", {}).get("title", ""),
        "description": _extract_description(raw_ticket),
        "updated_at": raw_ticket.get("updatedAt", ""),
        "href": links.get("self", {}).get("href", ""),
    }


def ticket_from_csv_row(row: dict[str, str]) -> dict[str, Any]:
    """Normalize one sample CSV row into the same ticket shape used by OpenProject."""
    return {
        "id": row.get("Ticket"),
        "project_id": row.get("Project ID"),
        "subject": row.get("Title", ""),
        "status": row.get("Status", ""),
        "assignee": row.get("Owner", ""),
        "priority": row.get("Priority", ""),
        "description": row.get("Description", ""),
        "updated_at": row.get("Updated At", ""),
        "href": "",
    }


def group_tickets_by_project(tickets: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    """Group tickets by Project ID and collect tickets that cannot be mapped."""
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    exceptions: list[dict[str, Any]] = []

    for ticket in tickets:
        project_id = str(ticket.get("project_id") or "").strip()

        if not project_id:
            exceptions.append(
                {
                    "type": "Missing Project ID",
                    "ticket_id": ticket.get("id"),
                    "subject": ticket.get("subject"),
                }
            )
            continue

        ticket["project_id"] = project_id
        grouped[project_id].append(ticket)

    return dict(grouped), exceptions


def build_project_summary(
    project_id: str,
    tickets: list[dict[str, Any]],
    closed_statuses: list[str],
    blocked_statuses: list[str],
    max_lines: int = 20,
) -> dict[str, Any]:
    """Build one SharePoint/Excel-ready summary row for a Project ID."""
    active_count = 0
    closed_count = 0
    blocked_count = 0
    ticket_lines: list[str] = []

    closed_set = {status.lower() for status in closed_statuses}
    blocked_set = {status.lower() for status in blocked_statuses}

    for ticket in tickets:
        status = str(ticket.get("status", ""))
        status_key = status.lower()

        if status_key in closed_set:
            closed_count += 1
        else:
            active_count += 1

        if status_key in blocked_set:
            blocked_count += 1

        if len(ticket_lines) < max_lines:
            ticket_lines.append(
                f"OP#{ticket['id']} - {ticket['subject']} - {status} - {ticket.get('assignee', '')}"
            )

    latest_ticket = None
    if tickets:
        latest_ticket = sorted(
            tickets,
            key=lambda item: str(item.get("updated_at", "")),
            reverse=True,
        )[0]

    latest_update = ""
    if latest_ticket:
        latest_update = (
            f"OP#{latest_ticket['id']} - "
            f"{latest_ticket['subject']} - "
            f"{latest_ticket['status']} - "
            f"{latest_ticket.get('updated_at', '')}"
        )

    return {
        "project_id": project_id,
        "linked_tickets": "\n".join(ticket_lines),
        "active_ticket_count": active_count,
        "closed_ticket_count": closed_count,
        "blocked_ticket_count": blocked_count,
        "latest_ticket_update": latest_update,
        "last_synced": datetime.now(timezone.utc).isoformat(),
        "tickets": tickets,
    }


def _extract_description(raw_ticket: dict[str, Any]) -> str:
    description = raw_ticket.get("description")
    if isinstance(description, dict):
        return str(description.get("raw") or description.get("html") or "")
    return str(description or "")
