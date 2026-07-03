from mapper import build_project_summary, group_tickets_by_project, ticket_from_csv_row


def test_group_tickets_by_project_separates_missing_project_id():
    tickets = [
        {"id": 1, "project_id": "PRJ-2026-A-CUSTA", "subject": "Valid"},
        {"id": 2, "project_id": "", "subject": "Missing"},
    ]

    grouped, exceptions = group_tickets_by_project(tickets)

    assert "PRJ-2026-A-CUSTA" in grouped
    assert len(grouped["PRJ-2026-A-CUSTA"]) == 1
    assert len(exceptions) == 1
    assert exceptions[0]["ticket_id"] == 2


def test_build_project_summary_counts_statuses():
    tickets = [
        {"id": 1, "subject": "A", "status": "Blocked", "assignee": "CS", "updated_at": "2026-06-24T09:00:00Z"},
        {"id": 2, "subject": "B", "status": "Closed", "assignee": "Erik", "updated_at": "2026-06-25T09:00:00Z"},
        {"id": 3, "subject": "C", "status": "In Progress", "assignee": "Vinya", "updated_at": "2026-06-26T09:00:00Z"},
    ]

    summary = build_project_summary(
        project_id="PRJ-2026-A-CUSTA",
        tickets=tickets,
        closed_statuses=["Closed"],
        blocked_statuses=["Blocked"],
    )

    assert summary["active_ticket_count"] == 2
    assert summary["closed_ticket_count"] == 1
    assert summary["blocked_ticket_count"] == 1


def test_ticket_from_csv_row_uses_expected_headers():
    row = {
        "Ticket": "101",
        "Project ID": "PRJ-2026-C-TEAM-B-001",
        "Title": "Requirement confirmation",
        "Status": "Blocked",
        "Owner": "Jose",
        "Priority": "High",
        "Description": "Waiting for customer input",
        "Updated At": "2026-06-24T08:30:00Z",
    }

    ticket = ticket_from_csv_row(row)

    assert ticket["id"] == "101"
    assert ticket["project_id"] == "PRJ-2026-C-TEAM-B-001"
    assert ticket["status"] == "Blocked"
