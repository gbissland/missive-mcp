# Missive MCP Server

> **Fork notice**: This is a fork of [Jordanlaubaugh9/missive-mcp](https://github.com/Jordanlaubaugh9/missive-mcp) with significant additions and fixes. The original project provided conversation management, task management, and basic message tools.
>
> **New tools added:**
> - **User management** — list users across organisations
> - **Analytics & reporting** — create and retrieve analytics reports with date/team/user filters
> - **Custom team metrics** — calculate per-channel response times and volumes without requiring a higher plan tier
> - **Drafts & sending** — create, schedule, and delete drafts; send emails/SMS directly
> - **Posts** — create and retrieve posts for integration audit trails
> - **Contacts** — full CRUD, contact books, contact groups, group membership management
> - **Organisations & teams** — list orgs and teams
> - **Shared labels** — list shared labels for conversation tagging
> - **Claude Code support** — configuration instructions for Claude Code alongside Claude Desktop
>
> **API fixes** (Missive API has changed since the original project):
> - Fixed contact groups endpoint — switched from `/contact_books/{id}/groups` to `/v1/contact_groups` with query parameters, matching current Missive API
> - Fixed contacts API response handling — the API now returns arrays instead of objects for contacts; added handling for both formats
> - Fixed contact update payload — API now expects `contacts` as an array with `id` included, not a plain object
> - Fixed conversation pagination — corrected from `before` to `until` parameter for cursor-based pagination
> - Fixed message fetch limit — Missive API max is 10 messages per request, not 50
> - Improved rate limiting — adjusted delays to stay within Missive's 5 requests/sec burst limit

Model Context Protocol (MCP) server for accessing Missive conversations in Claude Desktop and Claude Code.

## 🎯 What This Provides

### **Conversation Management**
- **Get Conversations**: Retrieve recent conversations from your Missive inbox
- **Filtered Conversations**: Get conversations by mailbox (inbox, assigned, closed, flagged, etc.)
- **Conversation Details**: Get detailed information about specific conversations
- **Conversation Messages**: Retrieve messages from any conversation
- **Conversation Comments**: Get comments and tasks from conversations

### **Task Management**
- **Create Tasks**: Create standalone tasks or conversation subtasks
- **Update Tasks**: Modify task details, state, assignees, and due dates

### **Message Operations**
- **Message Details**: Get full message content including attachments
- **Search Messages**: Find messages by email Message-ID
- **Create Messages**: Send messages through custom channels

### **Analytics Reports**
- **Create Analytics Report**: Generate analytics reports with date ranges and filters
- **Get Analytics Report**: Retrieve report results including conversations, messages, response times

### **Drafts & Sending**
- **Create Draft**: Create drafts or send emails/SMS immediately
- **Get Drafts**: Retrieve drafts from conversations
- **Delete Draft**: Delete scheduled drafts

### **Posts (Integration Actions)**
- **Create Post**: Add posts to conversations with conversation management (close, assign, label)
- **Get Posts**: Retrieve posts from conversations

### **Contacts Management**
- **List Contacts**: Search and list contacts with filtering
- **Get Contact**: Get detailed contact information
- **Create Contact**: Create new contacts with group memberships
- **Update Contact**: Update contact details and group memberships
- **Delete Contact**: Remove contacts
- **List Contact Books**: Get available contact books
- **List Contact Groups**: Get groups/organizations in a contact book
- **Get Contacts by Group**: Find all contacts belonging to a specific group
- **Add Contact to Group**: Add a contact to an existing group
- **Remove Contact from Group**: Remove a contact from a group

> **Note**: Contact groups must be created in the Missive UI first. The API supports adding/removing contacts from existing groups, but cannot create new groups.

### **Organizations & Teams**
- **List Organizations**: Get organizations you're part of
- **List Teams**: Get teams with optional organization filter

### **Shared Labels**
- **List Shared Labels**: Get shared labels for tagging conversations

### **Team Metrics (Custom Analytics)**
- **Calculate Team Metrics**: Generate custom analytics for any team inbox by analysing conversation and message data. Useful when native analytics filtering requires a higher plan tier.

> **Looking for inspiration?** See [USE-CASES.md](USE-CASES.md) for detailed scenarios, example prompts, and multi-step workflows you can use with Claude.

### **Security & Integration**
- **Secure Authentication**: Uses your personal Missive API token
- **Claude Integration**: Works seamlessly with Claude Desktop and Claude Code
- **Local Execution**: Runs entirely on your machine for privacy and security

## 📁 Project Structure

```
missive-mcp/
├── local-server/
│   ├── main.py            # MCP server implementation
│   ├── requirements.txt   # Python dependencies
│   └── install.sh         # Automated setup script
├── README.md              # This file
└── LICENSE                # MIT License
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
cd local-server
./install.sh
```

The script will:
- Create a virtual environment
- Install dependencies
- Show you the exact configuration for Claude Desktop

### Option 2: Manual Setup

1. **Create virtual environment:**
   ```bash
   cd local-server
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get your Missive API token:**
   - Go to Missive → Settings → API
   - Create a new API token
   - Copy the token (starts with `missive_pat-...`)

## ⚙️ Claude Desktop Configuration

Add this to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "missive": {
      "command": "/path/to/missive-mcp/local-server/.venv/bin/python",
      "args": ["/path/to/missive-mcp/local-server/main.py"],
      "env": {
        "MISSIVE_API_TOKEN": "YOUR_MISSIVE_API_TOKEN_HERE"
      }
    }
  }
}
```

**Important**:
- Replace `/path/to/missive-mcp/` with the actual path to this project
- Replace `YOUR_MISSIVE_API_TOKEN_HERE` with your actual Missive API token
- On Windows, use `.venv\Scripts\python.exe` instead of `.venv/bin/python`

## ⚙️ Claude Code Configuration

Add this to your Claude Code settings file:

**macOS/Linux**: `~/.claude/settings.json`

```json
{
  "mcpServers": {
    "missive": {
      "command": "/path/to/missive-mcp/local-server/.venv/bin/python",
      "args": ["/path/to/missive-mcp/local-server/main.py"],
      "env": {
        "MISSIVE_API_TOKEN": "YOUR_MISSIVE_API_TOKEN_HERE"
      }
    }
  }
}
```

## ⚙️ Team Metrics Configuration (Optional)

The `calculate_team_metrics` tool can be configured via environment variables for convenience.
Add these to your `env` section in the Claude Desktop/Code config:

```json
{
  "env": {
    "MISSIVE_API_TOKEN": "YOUR_MISSIVE_API_TOKEN_HERE",
    "INTERNAL_DOMAINS": "yourdomain.com,yourdomain.co.nz",
    "TRACKED_CHANNELS": "support@yourdomain.com,sales@yourdomain.com,person@yourdomain.com"
  }
}
```

**Configuration options:**
- `INTERNAL_DOMAINS`: Comma-separated list of your email domains. Used to determine which messages are inbound (from external) vs outbound (from your team).
- `TRACKED_CHANNELS`: Comma-separated list of email addresses to track separately. If not set, all internal addresses will be auto-detected and reported.

**Example usage:**
- "Calculate metrics for team abc123 from 2025-01-01 to 2025-12-31"
- "Show me support team stats for the last month"
- "Get metrics for team xyz from 2025-06-01 to 2025-06-30 with max 1000 conversations"

**⚠️ Missive API rate limits:** The Missive API allows approximately 3 requests per second (180/min). The `calculate_team_metrics` tool accounts for this with built-in delays, but large date ranges with hundreds of conversations will take time to process. For very large historical data pulls (e.g., a full year across thousands of conversations), the MCP tool may timeout — in those cases, a standalone script calling the API directly with checkpoint/resume logic is more appropriate.

## 🧪 Testing

1. **Restart Claude Desktop** completely (quit and reopen)
2. **Test the connection** by asking Claude:
   - "Show me my recent email conversations"
   - "What's in my Missive inbox?"
   - "Get my latest conversations"

## 🔧 How It Works

- **Local execution**: Runs as a local process launched by Claude Desktop
- **Stdio transport**: Uses standard input/output for MCP communication
- **Environment variables**: API token passed securely via environment
- **Direct API calls**: Connects directly to Missive API from your machine

## 🔐 Security Features

- ✅ **No hardcoded tokens**: You provide your own API token
- ✅ **Local processing**: All data stays on your machine
- ✅ **Environment variables**: Secure token storage
- ✅ **Direct API calls**: No intermediary services
- ✅ **Full API access**: Read and write conversations, contacts, drafts, and more

## 🛠 Troubleshooting

### Connection Errors
1. **Check paths**: Ensure the paths in your Claude config are correct
2. **Verify token**: Make sure your Missive API token is valid
3. **Check permissions**: Ensure `main.py` is executable (`chmod +x main.py`)
4. **Python path**: Verify the virtual environment Python path is correct

### Common Issues
- **"spawn ENOENT"**: Wrong Python path in Claude config
- **"nodename nor servname provided"**: Network connectivity issue
- **"Invalid API token"**: Check your Missive API token

### Getting Help
1. Check the Claude Desktop logs for detailed error messages
2. Test your API token with curl:
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        "https://public.missiveapp.com/v1/conversations?inbox=true&limit=5"
   ```

## 🧑‍💻 Development

### Local Testing
```bash
cd local-server
source .venv/bin/activate
MISSIVE_API_TOKEN="your_token" python main.py
```

### Adding Features
The server uses the [FastMCP](https://github.com/jlowin/fastmcp) framework. To add new tools:

1. Add a new function decorated with `@mcp.tool`
2. Use the Missive API documentation: https://learn.missiveapp.com/api-documentation
3. Follow the existing pattern in `main.py`

## 📚 API Reference

This server implements the following MCP tools:

### **Conversation Tools**
- **`get_conversations`**: Get recent conversations from your Missive inbox
- **`get_conversations_filtered`**: Get conversations with filtering (inbox, assigned, closed, flagged, etc.)
- **`get_conversation_details`**: Get detailed information about a specific conversation
- **`get_conversation_messages`**: Get messages from a specific conversation
- **`get_conversation_comments`**: Get comments from a specific conversation

### **Task Management Tools**
- **`create_task`**: Create a new task (standalone or conversation subtask)
- **`update_task`**: Update an existing task (title, description, state, assignees, due date)

### **Message Tools**
- **`get_message_details`**: Get full details of a specific message including body and attachments
- **`search_messages_by_email_id`**: Find messages by email Message-ID header
- **`create_custom_message`**: Create a message in a custom channel

### **User Management Tools**
- **`get_users`**: List users in organizations with optional filtering and pagination

### **Analytics Tools**
- **`create_analytics_report`**: Create an analytics report request with organization, date range, and optional filters (teams, users, mailboxes, labels)
- **`get_analytics_report`**: Retrieve analytics report results by report ID (conversations, messages, response times, resolution times, team/user breakdowns)

### **Drafts Tools**
- **`create_draft`**: Create a draft or send immediately (email/SMS). Supports scheduling, team assignment, labels, and conversation management
- **`get_conversation_drafts`**: Get drafts from a specific conversation
- **`delete_draft`**: Delete a scheduled draft

### **Posts Tools**
- **`create_post`**: Create a post in a conversation with optional actions (close, reopen, assign, label, move to inbox). Recommended for integrations as posts leave an audit trail
- **`get_conversation_posts`**: Get posts from a specific conversation

### **Contacts Tools**
- **`list_contacts`**: List contacts with optional search and contact book filtering
- **`get_contact`**: Get detailed contact information including memberships
- **`create_contact`**: Create a new contact with email, phone, notes, and group memberships
- **`update_contact`**: Update contact details (note: memberships array replaces all existing memberships)
- **`delete_contact`**: Delete a contact
- **`list_contact_books`**: List all contact books you have access to
- **`list_contact_groups`**: List groups or organizations in a contact book
- **`get_contacts_by_group`**: Get all contacts belonging to a specific group
- **`add_contact_to_group`**: Add a contact to an existing group (preserves other memberships)
- **`remove_contact_from_group`**: Remove a contact from a group (preserves other memberships)

### **Organization & Team Tools**
- **`list_organizations`**: List organizations you're part of
- **`list_teams`**: List teams with optional organization filter

### **Shared Labels Tools**
- **`list_shared_labels`**: List shared labels with optional organization filter

### **Example Usage with Claude**
Ask Claude things like:
- "Give me a summary of what's in my inbox this morning"
- "Show me all flagged conversations — what needs my attention?"
- "Summarise the full history of conversation [ID] and list any action items"
- "Draft a polite reply to this customer asking for more details, but don't send it yet"
- "Send an email to john@example.com confirming the meeting, then close the conversation"
- "Create a follow-up task for Friday assigned to the Sales team"
- "Calculate our support team's average first reply time for the past 2 weeks, broken down by channel"
- "Find all contacts in the VIPs group and list their emails"
- "Add Jane Smith to the Priority Clients group"
- "Post an internal note to this conversation saying the issue is resolved, add the 'Completed' label, and close it"

For more detailed scenarios and multi-step workflows, see [USE-CASES.md](USE-CASES.md).

## 🤝 Contributing

Contributions welcome! This project demonstrates:
- FastMCP framework usage
- Secure API token handling
- Claude Desktop integration patterns
- Local MCP server best practices

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Related Projects

- [FastMCP](https://github.com/jlowin/fastmcp) - The MCP framework used
- [Missive API](https://learn.missiveapp.com/api-documentation) - Official API documentation
- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP specification
