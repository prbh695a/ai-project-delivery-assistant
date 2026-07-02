# AI Project Delivery Assistant

A proof-of-concept for connecting ticket-level delivery data with project-level reporting.

The use case demonstrates how sprint/project tickets can be extracted, grouped by a common **Project ID**, exported into a management-friendly tracker, synced to SharePoint through Power Automate, and enriched with AI-style delivery insights such as blocker detection, risk classification, next actions, and stakeholder update drafts.

> Public demo note: this repository uses sample and anonymized data only. Do not commit real customer names, internal URLs, API keys, SharePoint links, or production ticket data.

---

## Problem statement

In many engineering teams, sprint execution is managed in a ticketing tool while project status is tracked separately in a management tracker. This creates a gap between:

- what the team is actually working on
- what stakeholders see as project status
- which blockers, risks, and dependencies require action

This prototype uses a shared **Project ID** to connect both views.

```text
OpenProject / ticket system
        ↓
Python extraction and grouping
        ↓
Excel summary with Project ID
        ↓
Power Automate updates SharePoint tracker
        ↓
AI-assisted risk and stakeholder summary
```

---

## Project ID convention

Recommended structure for project work:

```text
PRJ-Year-Type-Stakeholder-Sequence
```

Examples:

```text
PRJ-2026-A-INFRA-002
PRJ-2026-C-TEAM-B-001
PRJ-2026-D-TEST-004
PRJ-2026-E-TEAM-C-006
```

Suggested type values:

| Type | Meaning |
|---|---|
| A | Automation or application-related work |
| C | Change or customer/requester-driven change |
| D | Defect, correction, delivery issue, or testing correction |
| E | Enhancement, improvement, or efficiency topic |

The sample also includes non-project work identifiers for demonstration:

| Prefix | Meaning |
|---|---|
| PRJ | Project-related delivery work |
| OPR | Operational request |
| INFRA | Infrastructure or platform improvement |

---

## Example input

The demo uses sample ticket data like this:

| Ticket | Project ID | Title | Status | Owner | Priority | Description |
|---:|---|---|---|---|---|---|
| 101 | PRJ-2026-C-TEAM-B-001 | Requirement confirmation from Team B before project development can start | Blocked | Jose | High | Waiting for customer input |
| 102 | PRJ-2026-A-INFRA-002 | Pre-development phase infrastructure enhancement before requirement freeze | In Progress | Alex | High | Dependency on secure access |
| 103 | OPR-2026-MAINT-001 | Operational request to add a new type in a maintenance project | Not Started | Leo | Medium | Requirement partially clear |
| 104 | PRJ-2026-D-TEST-004 | Testing phase test plan preparation in progress | Not Started | Max | Medium | Can start after API freeze |
| 201 | INFRA-2026-E-LOGGING-005 | Continuous improvement logging enhancement | In Progress | Jose | Medium | Standard log format needs review |
| 202 | PRJ-2026-E-TEAM-C-006 | UAT in progress for email optimization request from Team C | In Review | Prateek | High | Excel to SharePoint pilot validation |

---

## AI-assisted output examples

The AI layer can produce:

- sprint/project summary
- blocker detection
- risk classification
- stakeholder-ready status update
- next action recommendations

Example stakeholder update:

```text
Current project delivery status requires attention. Requirement confirmation is blocked due to missing customer input. Infrastructure enhancement is in progress, but secure access remains a dependency. The test plan can start only after the API freeze is confirmed.

Recommended next actions are to escalate requirement confirmation, confirm secure access, and clarify the operational maintenance request before sprint planning.
```

---

## Folder Structure

```text
ai-project-delivery-assistant/
│
├── README.md
├── Pipfile
├── .env.example
├── .gitignore
│
├── config/
│   └── config.example.yaml
│
├── sample_data/
│   └── sample_tickets.csv
│
├── src/
│   ├── main.py
│   ├── openproject_client.py
│   ├── mapper.py
│   ├── exporter.py
│   └── genai_assistant.py
│
├── docs/
│   ├── architecture.md
│   ├── power_automate_flow.md
│   └── genai_prompt_template.md
│
├── output/
│   └── .gitkeep
│
└── tests/
    ├── conftest.py
    └── test_mapper.py
```

### Folder Description

| Folder / File | Purpose |
|---|---|
| `README.md` | Main project explanation, use case, setup steps, and demo instructions |
| `Pipfile` | Python dependency and environment management using Pipenv. `Pipfile.lock` is generated locally after `pipenv install`. |
| `.env.example` | Template for environment variables such as API keys and configuration secrets |
| `.gitignore` | Prevents local secrets, cache files, and generated outputs from being committed |
| `config/` | Stores configuration templates such as OpenProject URL, project identifier, custom field name, and sync rules |
| `sample_data/` | Contains anonymized sample ticket data used for demo mode |
| `src/` | Main Python source code for extraction, mapping, Excel export, and AI-style analysis |
| `docs/` | Additional documentation for architecture, Power Automate flow, and GenAI prompt design |
| `output/` | Generated Excel and AI insight files are created here during local execution |
| `tests/` | Unit tests for mapping and ticket grouping logic |

### Main Components

| Component | Description |
|---|---|
| `main.py` | Entry point of the application. Runs demo mode or OpenProject-based extraction and generates output files |
| `openproject_client.py` | Connects to OpenProject API and reads work packages |
| `mapper.py` | Extracts ticket fields, groups tickets by Project ID, and calculates active, closed, and blocked ticket counts |
| `exporter.py` | Creates the Excel output file with a Power Automate-readable table named `ProjectSyncTable` |
| `genai_assistant.py` | Generates AI-style delivery insights such as blocker summary, risk classification, and stakeholder update draft |
| `sample_tickets.csv` | Anonymized demo input showing project, operational, and infrastructure ticket examples |
| `power_automate_flow.md` | Step-by-step guide for syncing the generated Excel output into a SharePoint Project Tracker |

---

## Setup with Pipenv

Install dependencies:

```bash
pipenv install
pipenv install --dev pytest
```

Run the demo with sample data:

```bash
pipenv run python src/main.py --demo
```

This creates:

```text
output/project_sync_summary.xlsx
output/ai_delivery_insights.md
```

Run tests:

```bash
pipenv run pytest
```

---

## Running against OpenProject

Create a local `.env` file based on `.env.example`:

```env
OPENPROJECT_API_KEY=your_api_key_here
```

Copy the example config:

```bash
cp config/config.example.yaml config/config.yaml
```

Update `config/config.yaml` with your internal OpenProject URL, project identifier, and Project ID custom field.

Then run:

```bash
pipenv run python src/main.py
```

For internal company certificates, prefer using a company CA bundle. Do not keep SSL verification disabled in production.

---

## Power Automate integration pattern

The recommended pilot approach is:

```text
Python generates Excel summary
        ↓
Excel file saved in SharePoint / OneDrive
        ↓
Power Automate reads Excel table ProjectSyncTable
        ↓
Power Automate updates or creates SharePoint Project Tracker rows
```

The Excel table name generated by this script is:

```text
ProjectSyncTable
```

See [`docs/power_automate_flow.md`](docs/power_automate_flow.md) for the detailed flow.

---

## Governance and privacy

For public demos:

- use only sample or anonymized data
- do not include real customer names
- do not include internal URLs
- do not include screenshots from internal systems
- do not include API keys, secrets, or real SharePoint links
- use enterprise-approved AI tools for real project data

---

## Possible future improvements

- direct Microsoft Graph update to SharePoint
- Teams exception notification
- automatic missing Project ID report
- dashboard view in Power BI
- enterprise-approved GenAI integration
- automated weekly highlight report generation
# ai-project-delivery-assistant
