# Missive MCP Server — Use Cases

A comprehensive guide to what's possible when connecting Claude (or any AI assistant) to your Missive workspace via the MCP server. The server exposes 31 tools across conversations, tasks, messages, contacts, analytics, drafts, posts, and more.

---

## Table of Contents

- [Inbox Triage & Prioritisation](#inbox-triage--prioritisation)
- [Conversation Intelligence](#conversation-intelligence)
- [Task Management & Workflow](#task-management--workflow)
- [Drafting & Sending Messages](#drafting--sending-messages)
- [Contact Management](#contact-management)
- [Analytics & Reporting](#analytics--reporting)
- [Team Coordination](#team-coordination)
- [Automations & Integrations](#automations--integrations)

---

## Inbox Triage & Prioritisation

### Daily Inbox Summary
> "Show me what's in my inbox this morning — summarise the subjects and who they're from."

Uses `get_conversations_filtered` (mailbox=inbox) to pull recent conversations, giving you a quick overview without opening Missive.

### Flagged Conversation Review
> "What flagged conversations do I have? Give me a priority list."

Uses `get_conversations_filtered` (mailbox=flagged) to surface conversations you've flagged for follow-up, helping you stay on top of important threads.

### Snoozed Items Check
> "What's coming back from snooze today?"

Uses `get_conversations_filtered` (mailbox=snoozed) to review conversations that are about to resurface.

### Team Inbox Audit
> "Show me all open conversations in the Support team inbox."

Uses `get_conversations_filtered` with a `team_id` to review a specific team's workload.

### Assigned Work Review
> "What conversations are currently assigned to me?"

Uses `get_conversations_filtered` (mailbox=assigned) to show your personal assignment queue.

---

## Conversation Intelligence

### Deep-Dive on a Thread
> "Pull up conversation [ID] — what's the full history and who's involved?"

Uses `get_conversation_details` then `get_conversation_messages` to reconstruct the full picture of a thread including participants, labels, assignment, and message content.

### Summarise a Long Email Thread
> "This conversation has 20+ messages. Can you summarise the key points and any action items?"

Uses `get_conversation_messages` to read through the thread, then AI summarises the discussion, decisions made, and outstanding actions.

### Read Internal Comments
> "What have the team said internally about this conversation?"

Uses `get_conversation_comments` to surface internal notes and task items that team members have left on a conversation — useful for getting context before replying.

### Find a Specific Email
> "I need to find the email with Message-ID abc123@example.com"

Uses `search_messages_by_email_id` to locate a specific message by its email header Message-ID — helpful for debugging delivery issues or cross-referencing with other systems.

### Full Message Inspection
> "Show me the full body and attachments of message [ID]."

Uses `get_message_details` to retrieve complete message content including HTML body, attachment list, and all header fields.

---

## Task Management & Workflow

### Create a Follow-Up Task
> "Create a task to follow up with Acme Corp about their proposal by Friday."

Uses `create_task` with a title, description, and due date timestamp. Can be standalone or attached to a specific conversation as a subtask.

### Assign Work to Team Members
> "Create a task for Sarah to review the Q1 report and assign it to the Marketing team."

Uses `create_task` with `assignee_ids` and `team_id` to delegate work to specific people and teams.

### Create Subtasks on a Conversation
> "Add a checklist item to this conversation: 'Send revised contract to client'."

Uses `create_task` with `conversation_id` and `is_subtask=True` to attach actionable items directly to a conversation thread.

### Update Task Status
> "Mark task [ID] as in progress" or "Close out that task — it's done."

Uses `update_task` to change task state (todo → in_progress → closed), update assignees, change due dates, or modify descriptions.

### Batch Task Creation from Meeting Notes
> "Here are my meeting notes — create tasks for each action item mentioned."

AI parses the meeting notes and uses `create_task` multiple times to generate individual tasks with appropriate titles, descriptions, and assignees.

---

## Drafting & Sending Messages

### Draft an Email Reply
> "Draft a polite reply to this customer asking for more details about their issue."

Uses `create_draft` with `send=False` to compose a draft that appears in Missive for your review before sending.

### Send a Quick Response
> "Send a reply to john@example.com confirming the meeting time."

Uses `create_draft` with `send=True` to compose and immediately send a message.

### Schedule a Message
> "Draft an email to the client but schedule it to send Monday at 9am."

Uses `create_draft` with `send_at` timestamp to queue a message for future delivery — great for working across time zones.

### Review Existing Drafts
> "What drafts are sitting in this conversation?"

Uses `get_conversation_drafts` to list unsent drafts, helping you spot messages that were started but never sent.

### Cancel a Scheduled Send
> "Actually, don't send that scheduled email — delete it."

Uses `delete_draft` to remove a scheduled draft before it goes out.

### Send and Organise
> "Send this reply, assign the conversation to the Sales team, add the 'Enterprise' label, and close it."

Uses `create_draft` with `send=True`, `team_id`, `add_shared_labels`, and `close=True` to handle the full lifecycle in one action.

---

## Contact Management

### Look Up a Contact
> "Find me the contact details for anyone at acme.com."

Uses `list_contacts` with a search term to find matching contacts across your contact books.

### View Full Contact Profile
> "Show me everything we have on file for contact [ID]."

Uses `get_contact` to retrieve full details including name, emails, phones, notes, and group memberships.

### Add a New Contact
> "Add Jane Smith (jane@example.com, +64 21 555 1234) to our main contact book and put her in the VIP group."

Uses `create_contact` with contact details and `memberships_data` to create the contact with group membership in one step.

### Update Contact Details
> "Update John's email to john.new@example.com and add a note that he's our primary point of contact."

Uses `update_contact` to modify contact fields.

### Manage Contact Groups
> "Add this contact to the 'Partners' group" or "Remove them from 'Prospects'."

Uses `add_contact_to_group` and `remove_contact_from_group` to manage group memberships without affecting other groups the contact belongs to.

### Browse Contact Groups
> "What contact groups do we have in our main contact book?"

Uses `list_contact_groups` to show all groups or organisations linked to a contact book.

### Filter Contacts by Group
> "Show me all contacts in the 'Enterprise Clients' group."

Uses `get_contacts_by_group` to list all contacts belonging to a specific group — useful for segmented outreach or reporting.

### Contact Book Overview
> "What contact books do I have access to?"

Uses `list_contact_books` to list all available contact books, useful when you manage multiple books (e.g., personal, shared, team-specific).

### Clean Up Contacts
> "Delete the duplicate contact [ID]."

Uses `delete_contact` to remove contacts that are no longer needed.

---

## Analytics & Reporting

### Generate a Performance Report
> "Pull an analytics report for the Support team for last month."

Uses `create_analytics_report` with date range and team filter, then `get_analytics_report` to retrieve results including conversation volumes, response times, and resolution metrics.

### Custom Team Metrics
> "Calculate our average first reply time for the Sales inbox over the past 2 weeks, broken down by email channel."

Uses `calculate_team_metrics` to analyse conversations and messages for a specific team, producing metrics like:
- Total conversations and reply rates
- Inbound vs outbound message counts
- First reply time averages
- Per-channel breakdowns

This is especially valuable on plans where native analytics filtering is limited.

### Weekly Standup Data
> "Give me the numbers for this week — how many conversations did we handle, what was our response time?"

Uses `create_analytics_report` scoped to the current week to pull key metrics for team standups or check-ins.

### Compare Team Performance
> "How does the Support team's response time compare to Sales this month?"

Run `create_analytics_report` for each team with the same date range, then compare the results side by side.

### Channel Performance Analysis
> "Which email channels are getting the most volume? Break it down for the past 30 days."

Uses `calculate_team_metrics` with `tracked_channels` to see volume and response patterns across different email addresses.

---

## Team Coordination

### List Team Members
> "Who's in our organisation? Show me all users and their roles."

Uses `get_users` to list team members, optionally filtered by organisation — helpful for onboarding or when you need to find someone's user ID for assignments.

### Review Org Structure
> "What organisations and teams do we have set up?"

Uses `list_organizations` and `list_teams` to map out the org structure — useful when setting up new workflows or auditing access.

### Label Management
> "What shared labels are available in our workspace?"

Uses `list_shared_labels` to list all shared labels, useful when building automation rules or deciding how to categorise conversations.

---

## Automations & Integrations

### Post Integration Notifications
> "Post a message into conversation [ID] from our CRM bot saying the deal was marked as won."

Uses `create_post` with custom `username` and `username_icon` to post a formatted notification into a Missive conversation — creating a visible audit trail from external systems.

### Create Conversations from External Events
> "A new support ticket just came in from our web form. Create a conversation for it."

Uses `create_custom_message` with the form data to create a new conversation in a custom channel, complete with sender info and message body.

### Append to Existing Conversations
> "Add this webhook payload as a new message in the existing conversation."

Uses `create_custom_message` with `conversation_id` to thread external system messages into an ongoing conversation.

### Workflow Automation Posts
> "When a task is completed, post an update to the conversation with the task details, remove the 'Pending' label, and add the 'Completed' label."

Uses `create_post` with `add_shared_labels`, `remove_shared_labels`, and formatted markdown content to automate status updates.

### Close and Notify
> "Post a resolution summary to this conversation, assign it to the account manager, and close it."

Uses `create_post` with `markdown` content, `add_assignees`, and `close=True` to wrap up a conversation with full context.

### Reopen and Escalate
> "Reopen this conversation, assign it to the escalations team, and post a note explaining why."

Uses `create_post` with `reopen=True`, `add_assignees`, and `team_id` to bring a closed conversation back with proper context.

---

## Multi-Step Workflow Examples

### End-to-End Customer Onboarding
1. `create_contact` — Add the new customer to your contact book with group membership
2. `create_draft` (send=True) — Send a welcome email
3. `create_task` — Create follow-up tasks for the account manager
4. `create_post` — Post an internal note with onboarding checklist

### Weekly Team Review
1. `create_analytics_report` / `get_analytics_report` — Pull the week's metrics
2. `get_conversations_filtered` (mailbox=flagged) — Check flagged items needing attention
3. `calculate_team_metrics` — Get per-channel breakdowns
4. AI synthesises everything into a summary with recommendations

### Customer Issue Investigation
1. `list_contacts` — Find the customer's contact record
2. `get_conversations_filtered` — Search for related conversations
3. `get_conversation_messages` — Read the full message history
4. `get_conversation_comments` — Check internal team notes
5. `create_task` — Create action items based on findings
6. `create_draft` — Draft a response to the customer

### Monthly Reporting
1. `list_teams` — Get all team IDs
2. `create_analytics_report` for each team — Pull monthly metrics
3. `calculate_team_metrics` for each team — Get detailed channel breakdowns
4. AI compiles a comprehensive monthly report with trends and recommendations

---

## Tool Reference Summary

| Category | Tools | Count |
|----------|-------|-------|
| Conversations | get_conversations, get_conversations_filtered, get_conversation_details, get_conversation_messages, get_conversation_comments | 5 |
| Tasks | create_task, update_task | 2 |
| Messages | get_message_details, search_messages_by_email_id, create_custom_message | 3 |
| Users | get_users | 1 |
| Analytics | create_analytics_report, get_analytics_report, calculate_team_metrics | 3 |
| Drafts | create_draft, get_conversation_drafts, delete_draft | 3 |
| Posts | create_post, get_conversation_posts | 2 |
| Contacts | list_contacts, get_contact, create_contact, update_contact, delete_contact, list_contact_books, list_contact_groups, get_contacts_by_group, add_contact_to_group, remove_contact_from_group | 10 |
| Orgs & Teams | list_organizations, list_teams | 2 |
| Labels | list_shared_labels | 1 |
| **Total** | | **32** |
