# Power Automate Flow

This flow assumes Python has already generated `project_sync_summary.xlsx` with a table named `ProjectSyncTable`.

## Flow overview

```text
1. Trigger manually or on schedule
2. List rows present in Excel table
3. Initialize exception variable
4. Apply to each Excel row
5. Read Project ID
6. Get SharePoint project tracker items
7. Filter matching SharePoint row
8. If one match exists, update item
9. If no match exists, create item or record exception
10. If duplicate exists, record exception
11. Send exception summary
```

## Excel input columns

- Project ID
- Active Ticket Count
- Closed Ticket Count
- Blocked Ticket Count
- Latest Ticket Update
- Linked OpenProject Tickets
- Last Synced

## SharePoint tracker columns

Recommended columns:

| SharePoint column | Type | Updated by |
|---|---|---|
| Name or Project ID | Single line text | Power Automate or manual |
| Project Name | Single line text | Manual |
| Manual Status | Choice | Manual |
| Active Ticket Count | Number | Power Automate |
| Closed Ticket Count | Number | Power Automate |
| Blocked Ticket Count | Number | Power Automate |
| Latest Ticket Update | Multiple lines text | Power Automate |
| Linked OpenProject Tickets | Multiple lines text | Power Automate |
| Last Synced | Date/time | Power Automate |

Do not overwrite manual fields such as management status, owner, target date, or business comment.

## Key expressions

### Compose Project ID

Use this inside `Apply to each` over Excel rows:

```text
trim(items('Apply_to_each')?['Project ID'])
```

### Filter array condition

If your SharePoint internal column for Project ID is `Name`:

```text
@equals(trim(item()?['Name']), outputs('Compose_Project_ID'))
```

Replace `Name` with your SharePoint internal column name if different.

### Count matching SharePoint items

```text
length(body('Filter_array'))
```

### Get SharePoint item ID for Update item

Add a Compose action called `Compose_SP_Item_ID` using the Expression tab:

```text
first(body('Filter_array'))?['ID']
```

Then in `Update item > Id`, use:

```text
int(outputs('Compose_SP_Item_ID'))
```

If the Compose output literally shows `first(body('Filter_array'))?['ID']`, it was entered as plain text. Delete it and add it through the Expression tab.

## Safe branch logic

| Match count | Action |
|---:|---|
| 1 | Update existing SharePoint item |
| 0 | Create item or append not-found exception |
| >1 | Append duplicate Project ID exception |

Recommended first version:

```text
Apply to each Excel row
    Compose Project ID
    Condition: Project ID empty?
        True: Append missing Project ID exception
        False:
            Get items from SharePoint
            Filter array where SharePoint Project ID equals Compose Project ID
            Condition: length(Filter array) equals 1
                True: Update item
                False:
                    Condition: length(Filter array) equals 0
                        True: Create item or append not-found exception
                        False: Append duplicate Project ID exception
```

## Create item mapping

When no SharePoint row exists and you choose to create one:

| SharePoint field | Power Automate value |
|---|---|
| Title / Name / Project ID | `outputs('Compose_Project_ID')` |
| Active Ticket Count | `if(empty(items('Apply_to_each')?['Active Ticket Count']), 0, int(items('Apply_to_each')?['Active Ticket Count']))` |
| Closed Ticket Count | `if(empty(items('Apply_to_each')?['Closed Ticket Count']), 0, int(items('Apply_to_each')?['Closed Ticket Count']))` |
| Blocked Ticket Count | `if(empty(items('Apply_to_each')?['Blocked Ticket Count']), 0, int(items('Apply_to_each')?['Blocked Ticket Count']))` |
| Latest Ticket Update | `items('Apply_to_each')?['Latest Ticket Update']` |
| Linked OpenProject Tickets | `items('Apply_to_each')?['Linked OpenProject Tickets']` |
| Last Synced | `items('Apply_to_each')?['Last Synced']` |

## Update item mapping

Use the same mappings as Create item, but set `Id` to:

```text
int(outputs('Compose_SP_Item_ID'))
```

## Performance note

For a pilot, `Get items` without an OData filter is acceptable for a small SharePoint list. To reduce warnings, set `Top Count` to `100` or use an OData filter once the flow is stable.
