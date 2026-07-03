# Architecture

## Purpose

This use case connects ticket-level execution with project-level reporting using a shared Project ID.

## Logical flow

```text
OpenProject or sample ticket data
        ↓
Python extractor and mapper
        ↓
Project ID grouping
        ↓
Excel summary table named ProjectSyncTable
        ↓
Power Automate
        ↓
SharePoint project tracker
        ↓
AI-assisted status summary
```

## Components

| Component | Responsibility |
|---|---|
| OpenProject client | Reads work packages from OpenProject API when running internally |
| Mapper | Normalizes ticket fields and groups by Project ID |
| Exporter | Creates Excel output with a Power Automate-readable table |
| Power Automate | Reads Excel and updates or creates SharePoint tracker items |
| AI assistant | Creates delivery insights from normalized ticket data |

## Governance principle

OpenProject remains the execution source. SharePoint remains the reporting and management control layer. The Project ID is the traceability key between the two systems.

The repository uses a deterministic rule-based assistant for the public demo so no data is sent to an external AI service. In an enterprise setup, the normalized ticket payload can be sent to an approved GenAI endpoint if governance permits it.
