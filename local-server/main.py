#!/usr/bin/env python3
import os
import json
from datetime import datetime
from typing import Optional, List
import httpx
from fastmcp import FastMCP

# Initialize FastMCP server for local stdio use
mcp = FastMCP("Missive MCP")

# Helper function to get API token
def get_api_token():
    """Get API token from environment variable"""
    api_token = os.getenv("MISSIVE_API_TOKEN")
    if not api_token:
        raise ValueError("MISSIVE_API_TOKEN not set in environment")
    return api_token

# Helper function to format timestamp
def format_timestamp(timestamp):
    """Convert Unix timestamp to readable date"""
    if timestamp:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    return "Not set"

# ============================================================================
# CONVERSATION ENDPOINTS
# ============================================================================

@mcp.tool
async def get_conversations() -> str:
    """Get recent conversations from Missive inbox"""
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/conversations",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"inbox": "true", "limit": 10}
            )
            response.raise_for_status()
            data = response.json()
            
            conversations = data.get("conversations", [])
            if not conversations:
                return "No conversations found in your Missive inbox"
            
            result = "📧 Recent Missive Conversations:\n\n"
            for conv in conversations[:5]:
                subject = conv.get("latest_message_subject", "No subject")
                authors = ", ".join([a.get("name", "Unknown") for a in conv.get("authors", [])])
                result += f"• {subject}\n  From: {authors}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            else:
                return f"Error fetching conversations: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching conversations: {str(e)}"

@mcp.tool
async def get_conversations_filtered(
    mailbox: str = "inbox",
    limit: int = 10,
    team_id: Optional[str] = None
) -> str:
    """Get conversations with filtering options.
    
    Args:
        mailbox: Filter by mailbox (inbox, all, assigned, closed, flagged, trashed, junked, snoozed)
        limit: Number of conversations to return (max 50)
        team_id: Optional team ID to filter by team conversations
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Build parameters based on mailbox type
    params = {"limit": min(limit, 50)}
    
    if mailbox == "inbox":
        params["inbox"] = "true"
    elif mailbox == "all":
        params["all"] = "true"
    elif mailbox == "assigned":
        params["assigned"] = "true"
    elif mailbox == "closed":
        params["closed"] = "true"
    elif mailbox == "flagged":
        params["flagged"] = "true"
    elif mailbox == "trashed":
        params["trashed"] = "true"
    elif mailbox == "junked":
        params["junked"] = "true"
    elif mailbox == "snoozed":
        params["snoozed"] = "true"
    else:
        return f"Error: Invalid mailbox '{mailbox}'. Valid options: inbox, all, assigned, closed, flagged, trashed, junked, snoozed"
    
    if team_id:
        if mailbox == "inbox":
            params = {"team_inbox": team_id, "limit": min(limit, 50)}
        elif mailbox == "closed":
            params = {"team_closed": team_id, "limit": min(limit, 50)}
        elif mailbox == "all":
            params = {"team_all": team_id, "limit": min(limit, 50)}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/conversations",
                headers={"Authorization": f"Bearer {api_token}"},
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            conversations = data.get("conversations", [])
            if not conversations:
                return f"No conversations found in {mailbox} mailbox"
            
            result = f"📧 Conversations from {mailbox.title()} ({len(conversations)} found):\n\n"
            for conv in conversations:
                subject = conv.get("latest_message_subject", "No subject")
                authors = ", ".join([a.get("name", "Unknown") for a in conv.get("authors", [])])
                assignees = conv.get("assignee_names", "Unassigned")
                tasks_count = conv.get("tasks_count", 0)
                
                result += f"• {subject}\n"
                result += f"  From: {authors}\n"
                if assignees:
                    result += f"  Assigned: {assignees}\n"
                if tasks_count > 0:
                    result += f"  Tasks: {tasks_count}\n"
                result += f"  ID: {conv.get('id')}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            else:
                return f"Error fetching conversations: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching conversations: {str(e)}"

@mcp.tool
async def get_conversation_details(conversation_id: str) -> str:
    """Get detailed information about a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation to retrieve
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/conversations/{conversation_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()
            
            conversations = data.get("conversations", [])
            if not conversations:
                return f"Conversation {conversation_id} not found"
            
            conv = conversations[0]
            
            result = f"📧 Conversation Details:\n\n"
            result += f"Subject: {conv.get('latest_message_subject', 'No subject')}\n"
            result += f"ID: {conv.get('id')}\n"
            
            # Authors
            authors = conv.get("authors", [])
            if authors:
                result += f"Authors: {', '.join([a.get('name', 'Unknown') for a in authors])}\n"
            
            # Assignees
            assignees = conv.get("assignee_names", "")
            if assignees:
                result += f"Assigned to: {assignees}\n"
            
            # Team
            team = conv.get("team")
            if team:
                result += f"Team: {team.get('name')}\n"
            
            # Organization
            org = conv.get("organization")
            if org:
                result += f"Organization: {org.get('name')}\n"
            
            # Counts
            result += f"Messages: {conv.get('messages_count', 0)}\n"
            result += f"Tasks: {conv.get('tasks_count', 0)} ({conv.get('completed_tasks_count', 0)} completed)\n"
            result += f"Attachments: {conv.get('attachments_count', 0)}\n"
            result += f"Drafts: {conv.get('drafts_count', 0)}\n"
            
            # Status
            users = conv.get("users", [])
            if users:
                user = users[0]
                status = []
                if user.get("assigned"): status.append("assigned")
                if user.get("closed"): status.append("closed")
                if user.get("archived"): status.append("archived")
                if user.get("flagged"): status.append("flagged")
                if user.get("snoozed"): status.append("snoozed")
                if user.get("trashed"): status.append("trashed")
                if user.get("junked"): status.append("junked")
                
                if status:
                    result += f"Status: {', '.join(status)}\n"
            
            # Shared labels
            shared_labels = conv.get("shared_label_names", "")
            if shared_labels:
                result += f"Labels: {shared_labels}\n"
            
            # Last activity
            last_activity = conv.get("last_activity_at")
            if last_activity:
                result += f"Last activity: {format_timestamp(last_activity)}\n"
            
            # URLs
            result += f"\nWeb URL: {conv.get('web_url', 'N/A')}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Conversation {conversation_id} not found"
            else:
                return f"Error fetching conversation: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching conversation: {str(e)}"

@mcp.tool
async def get_conversation_messages(conversation_id: str, limit: int = 5) -> str:
    """Get messages from a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        limit: Number of messages to return (max 10)
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/conversations/{conversation_id}/messages",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"limit": min(limit, 10)}
            )
            response.raise_for_status()
            data = response.json()
            
            messages = data.get("messages", [])
            if not messages:
                return f"No messages found in conversation {conversation_id}"
            
            result = f"💬 Messages in Conversation ({len(messages)} found):\n\n"
            
            for i, msg in enumerate(messages, 1):
                result += f"{i}. {msg.get('subject', 'No subject')}\n"
                
                # From field
                from_field = msg.get("from_field", {})
                if from_field:
                    result += f"   From: {from_field.get('name', 'Unknown')} <{from_field.get('address', 'unknown')}>\n"
                
                # To fields
                to_fields = msg.get("to_fields", [])
                if to_fields:
                    to_names = [f"{t.get('name', 'Unknown')} <{t.get('address', 'unknown')}>" for t in to_fields]
                    result += f"   To: {', '.join(to_names)}\n"
                
                # Preview
                preview = msg.get("preview", "")
                if preview:
                    result += f"   Preview: {preview[:100]}{'...' if len(preview) > 100 else ''}\n"
                
                # Delivered time
                delivered_at = msg.get("delivered_at")
                if delivered_at:
                    result += f"   Delivered: {format_timestamp(delivered_at)}\n"
                
                # Attachments
                attachments = msg.get("attachments", [])
                if attachments:
                    result += f"   Attachments: {len(attachments)} file(s)\n"
                
                result += f"   Message ID: {msg.get('id')}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Conversation {conversation_id} not found"
            else:
                return f"Error fetching messages: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching messages: {str(e)}"

@mcp.tool
async def get_conversation_comments(conversation_id: str, limit: int = 5) -> str:
    """Get comments from a specific conversation.
    
    Args:
        conversation_id: The ID of the conversation
        limit: Number of comments to return (max 10)
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/conversations/{conversation_id}/comments",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"limit": min(limit, 10)}
            )
            response.raise_for_status()
            data = response.json()
            
            comments = data.get("comments", [])
            if not comments:
                return f"No comments found in conversation {conversation_id}"
            
            result = f"💭 Comments in Conversation ({len(comments)} found):\n\n"
            
            for i, comment in enumerate(comments, 1):
                result += f"{i}. {comment.get('body', 'No content')}\n"
                
                # Author
                author = comment.get("author", {})
                if author:
                    result += f"   By: {author.get('name', 'Unknown')} <{author.get('email', 'unknown')}>\n"
                
                # Created time
                created_at = comment.get("created_at")
                if created_at:
                    result += f"   Created: {format_timestamp(created_at)}\n"
                
                # Task info
                task = comment.get("task")
                if task:
                    result += f"   Task: {task.get('description', 'No description')}\n"
                    result += f"   Task State: {task.get('state', 'unknown')}\n"
                    
                    due_at = task.get("due_at")
                    if due_at:
                        result += f"   Due: {format_timestamp(due_at)}\n"
                    
                    assignees = task.get("assignees", [])
                    if assignees:
                        assignee_names = [a.get('name', 'Unknown') for a in assignees]
                        result += f"   Assigned to: {', '.join(assignee_names)}\n"
                
                # Attachment
                attachment = comment.get("attachment")
                if attachment:
                    result += f"   Attachment: {attachment.get('filename', 'Unknown file')}\n"
                
                result += f"   Comment ID: {comment.get('id')}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Conversation {conversation_id} not found"
            else:
                return f"Error fetching comments: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching comments: {str(e)}"

# ============================================================================
# TASK ENDPOINTS
# ============================================================================

@mcp.tool
async def create_task(
    title: str,
    description: str = "",
    organization_id: Optional[str] = None,
    team_id: Optional[str] = None,
    assignee_ids: Optional[List[str]] = None,
    due_date_timestamp: Optional[int] = None,
    conversation_id: Optional[str] = None,
    is_subtask: bool = False
) -> str:
    """Create a new task in Missive.
    
    Args:
        title: Task title (required, max 1000 characters)
        description: Task description (optional, max 10000 characters)
        organization_id: Organization ID (required when using team_id or assignee_ids)
        team_id: Team ID (either team_id or assignee_ids required for standalone tasks)
        assignee_ids: List of user IDs to assign (either team_id or assignee_ids required for standalone tasks)
        due_date_timestamp: Unix timestamp for due date (optional)
        conversation_id: Conversation ID for subtasks (required when is_subtask=True)
        is_subtask: Whether this is a subtask of a conversation
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Build task payload
    task_data = {
        "title": title[:1000],  # Limit to 1000 characters
        "description": description[:10000] if description else "",  # Limit to 10000 characters
    }
    
    # Add optional fields
    if organization_id:
        task_data["organization"] = organization_id
    
    if team_id:
        task_data["team"] = team_id
    
    if assignee_ids:
        task_data["assignees"] = assignee_ids
    
    if due_date_timestamp:
        task_data["due_at"] = due_date_timestamp
    
    if is_subtask:
        if not conversation_id:
            return "Error: conversation_id is required when creating a subtask"
        task_data["conversation"] = conversation_id
        task_data["subtask"] = True
    else:
        # For standalone tasks, either team or assignees is required
        if not team_id and not assignee_ids:
            return "Error: Either team_id or assignee_ids is required for standalone tasks"
    
    payload = {"tasks": task_data}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://public.missiveapp.com/v1/tasks",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            task = data.get("tasks", {})
            
            result = f"✅ Task Created Successfully!\n\n"
            result += f"Title: {task.get('title', 'Unknown')}\n"
            result += f"Description: {task.get('description', 'No description')}\n"
            result += f"State: {task.get('state', 'unknown')}\n"
            result += f"Task ID: {task.get('id')}\n"
            
            # Due date
            due_at = task.get("due_at")
            if due_at:
                result += f"Due: {format_timestamp(due_at)}\n"
            
            # Assignees
            assignees = task.get("assignees", [])
            if assignees:
                result += f"Assignees: {', '.join(assignees)}\n"
            
            # Team
            team = task.get("team")
            if team:
                result += f"Team: {team}\n"
            
            # Conversation (for subtasks)
            conversation = task.get("conversation")
            if conversation:
                result += f"Conversation: {conversation}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 400:
                return f"Error: Invalid task data. Please check your parameters."
            else:
                return f"Error creating task: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error creating task: {str(e)}"

@mcp.tool
async def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    state: Optional[str] = None,
    assignee_ids: Optional[List[str]] = None,
    team_id: Optional[str] = None,
    due_date_timestamp: Optional[int] = None
) -> str:
    """Update an existing task.
    
    Args:
        task_id: ID of the task to update (required)
        title: New task title (optional, max 1000 characters)
        description: New task description (optional, max 10000 characters)
        state: New task state (optional: todo, in_progress, closed)
        assignee_ids: New list of user IDs to assign (optional)
        team_id: New team ID (optional)
        due_date_timestamp: New Unix timestamp for due date (optional)
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Build update payload with only provided fields
    task_data = {}
    
    if title is not None:
        task_data["title"] = title[:1000]
    
    if description is not None:
        task_data["description"] = description[:10000]
    
    if state is not None:
        if state not in ["todo", "in_progress", "closed"]:
            return "Error: state must be one of: todo, in_progress, closed"
        task_data["state"] = state
    
    if assignee_ids is not None:
        task_data["assignees"] = assignee_ids
    
    if team_id is not None:
        task_data["team"] = team_id
    
    if due_date_timestamp is not None:
        task_data["due_at"] = due_date_timestamp
    
    if not task_data:
        return "Error: At least one field must be provided to update"
    
    payload = {"tasks": task_data}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"https://public.missiveapp.com/v1/tasks/{task_id}",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            task = data.get("tasks", {})
            
            result = f"✅ Task Updated Successfully!\n\n"
            result += f"Title: {task.get('title', 'Unknown')}\n"
            result += f"Description: {task.get('description', 'No description')}\n"
            result += f"State: {task.get('state', 'unknown')}\n"
            result += f"Task ID: {task.get('id')}\n"
            
            # Due date
            due_at = task.get("due_at")
            if due_at:
                result += f"Due: {format_timestamp(due_at)}\n"
            
            # Assignees
            assignees = task.get("assignees", [])
            if assignees:
                result += f"Assignees: {', '.join(assignees)}\n"
            
            # Team
            team = task.get("team")
            if team:
                result += f"Team: {team}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Task {task_id} not found"
            elif e.response.status_code == 400:
                return f"Error: Invalid task data. Please check your parameters."
            else:
                return f"Error updating task: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error updating task: {str(e)}"

# ============================================================================
# MESSAGE ENDPOINTS
# ============================================================================

@mcp.tool
async def get_message_details(message_id: str) -> str:
    """Get full details of a specific message including body and attachments.
    
    Args:
        message_id: The ID of the message to retrieve
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/messages/{message_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()
            
            message = data.get("messages", {})
            if not message:
                return f"Message {message_id} not found"
            
            result = f"📨 Message Details:\n\n"
            result += f"Subject: {message.get('subject', 'No subject')}\n"
            result += f"Type: {message.get('type', 'unknown')}\n"
            result += f"Message ID: {message.get('id')}\n"
            
            # From field
            from_field = message.get("from_field", {})
            if from_field:
                result += f"From: {from_field.get('name', 'Unknown')} <{from_field.get('address', 'unknown')}>\n"
            
            # To fields
            to_fields = message.get("to_fields", [])
            if to_fields:
                to_names = [f"{t.get('name', 'Unknown')} <{t.get('address', 'unknown')}>" for t in to_fields]
                result += f"To: {', '.join(to_names)}\n"
            
            # CC fields
            cc_fields = message.get("cc_fields", [])
            if cc_fields:
                cc_names = [f"{c.get('name', 'Unknown')} <{c.get('address', 'unknown')}>" for c in cc_fields]
                result += f"CC: {', '.join(cc_names)}\n"
            
            # Timestamps
            delivered_at = message.get("delivered_at")
            if delivered_at:
                result += f"Delivered: {format_timestamp(delivered_at)}\n"
            
            created_at = message.get("created_at")
            if created_at:
                result += f"Created: {format_timestamp(created_at)}\n"
            
            # Preview
            preview = message.get("preview", "")
            if preview:
                result += f"Preview: {preview}\n"
            
            # Body (truncated for display)
            body = message.get("body", "")
            if body:
                # Remove HTML tags for cleaner display
                import re
                clean_body = re.sub('<[^<]+?>', '', body)
                result += f"Body: {clean_body[:500]}{'...' if len(clean_body) > 500 else ''}\n"
            
            # Attachments
            attachments = message.get("attachments", [])
            if attachments:
                result += f"\nAttachments ({len(attachments)}):\n"
                for att in attachments:
                    result += f"  • {att.get('filename', 'Unknown')} ({att.get('size', 0)} bytes)\n"
                    result += f"    Type: {att.get('media_type', 'unknown')}/{att.get('sub_type', 'unknown')}\n"
                    if att.get('width') and att.get('height'):
                        result += f"    Dimensions: {att.get('width')}x{att.get('height')}\n"
            
            # Conversation info
            conversation = message.get("conversation", {})
            if conversation:
                result += f"\nConversation: {conversation.get('latest_message_subject', 'No subject')}\n"
                result += f"Conversation ID: {conversation.get('id')}\n"
                
                # Team
                team = conversation.get("team", {})
                if team:
                    result += f"Team: {team.get('name')}\n"
                
                # Organization
                org = conversation.get("organization", {})
                if org:
                    result += f"Organization: {org.get('name')}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Message {message_id} not found"
            else:
                return f"Error fetching message: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching message: {str(e)}"

@mcp.tool
async def search_messages_by_email_id(email_message_id: str) -> str:
    """Find messages by email Message-ID header.
    
    Args:
        email_message_id: The Message-ID found in an email's header
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/messages",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"email_message_id": email_message_id}
            )
            response.raise_for_status()
            data = response.json()
            
            messages = data.get("messages", [])
            if not messages:
                return f"No messages found with email Message-ID: {email_message_id}"
            
            result = f"📧 Messages found for Message-ID '{email_message_id}' ({len(messages)} found):\n\n"
            
            for i, message in enumerate(messages, 1):
                result += f"{i}. {message.get('subject', 'No subject')}\n"
                
                # From field
                from_field = message.get("from_field", {})
                if from_field:
                    result += f"   From: {from_field.get('name', 'Unknown')} <{from_field.get('address', 'unknown')}>\n"
                
                # To fields
                to_fields = message.get("to_fields", [])
                if to_fields:
                    to_names = [f"{t.get('name', 'Unknown')} <{t.get('address', 'unknown')}>" for t in to_fields]
                    result += f"   To: {', '.join(to_names)}\n"
                
                # Preview
                preview = message.get("preview", "")
                if preview:
                    result += f"   Preview: {preview[:100]}{'...' if len(preview) > 100 else ''}\n"
                
                # Delivered time
                delivered_at = message.get("delivered_at")
                if delivered_at:
                    result += f"   Delivered: {format_timestamp(delivered_at)}\n"
                
                # Message type
                msg_type = message.get("type", "unknown")
                result += f"   Type: {msg_type}\n"
                
                result += f"   Message ID: {message.get('id')}\n\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: No messages found with Message-ID: {email_message_id}"
            else:
                return f"Error searching messages: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error searching messages: {str(e)}"

@mcp.tool
async def create_custom_message(
    account_id: str,
    body: str,
    from_field_data: str,
    to_fields_data: str,
    subject: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> str:
    """Create a message in a custom channel.
    
    Args:
        account_id: Account ID from custom channel settings
        body: HTML or text message body
        from_field_data: JSON string with sender info (e.g., '{"name": "John", "address": "john@example.com"}')
        to_fields_data: JSON string with recipients info (e.g., '[{"name": "Jane", "address": "jane@example.com"}]')
        subject: Email subject (for email channels only)
        conversation_id: Optional conversation ID to append to existing conversation
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Parse JSON strings
    try:
        from_field = json.loads(from_field_data)
        to_fields = json.loads(to_fields_data)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format in from_field_data or to_fields_data: {str(e)}"
    
    # Build message payload
    message_data = {
        "account": account_id,
        "body": body,
        "from_field": from_field,
        "to_fields": to_fields
    }
    
    if subject:
        message_data["subject"] = subject
    
    if conversation_id:
        message_data["conversation"] = conversation_id
    
    payload = {"messages": message_data}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://public.missiveapp.com/v1/messages",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            message = data.get("messages", {})
            
            result = f"📨 Message Created Successfully!\n\n"
            result += f"Subject: {message.get('subject', 'No subject')}\n"
            result += f"Type: {message.get('type', 'unknown')}\n"
            result += f"Message ID: {message.get('id')}\n"
            
            # From field
            from_field = message.get("from_field", {})
            if from_field:
                result += f"From: {from_field.get('name', 'Unknown')} <{from_field.get('address', 'unknown')}>\n"
            
            # To fields
            to_fields = message.get("to_fields", [])
            if to_fields:
                to_names = [f"{t.get('name', 'Unknown')} <{t.get('address', 'unknown')}>" for t in to_fields]
                result += f"To: {', '.join(to_names)}\n"
            
            # Delivered time
            delivered_at = message.get("delivered_at")
            if delivered_at:
                result += f"Delivered: {format_timestamp(delivered_at)}\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 400:
                return f"Error: Invalid message data. Please check your parameters."
            else:
                return f"Error creating message: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error creating message: {str(e)}"

# ============================================================================
# USER ENDPOINTS
# ============================================================================

@mcp.tool
async def get_users(
    organization_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> str:
    """List users in organizations the authenticated user is part of.
    
    Args:
        organization_id: Optional organization ID to filter users
        limit: Number of users to return (max 200, default 50)
        offset: Offset for pagination (default 0)
    """
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Build parameters
    params = {
        "limit": min(limit, 200),
        "offset": max(offset, 0)
    }
    
    if organization_id:
        params["organization"] = organization_id
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/users",
                headers={"Authorization": f"Bearer {api_token}"},
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            users = data.get("users", [])
            if not users:
                org_filter = f" in organization {organization_id}" if organization_id else ""
                return f"No users found{org_filter}"
            
            # Find the authenticated user
            current_user = next((u for u in users if u.get("me")), None)
            
            result = f"👥 Users ({len(users)} found"
            if organization_id:
                result += f" in organization {organization_id}"
            result += "):\n\n"
            
            # Show current user first if found
            if current_user:
                result += f"🔹 {current_user.get('name', 'Unknown')} (You)\n"
                result += f"   Email: {current_user.get('email', 'No email')}\n"
                result += f"   ID: {current_user.get('id')}\n"
                if current_user.get('avatar_url'):
                    result += f"   Avatar: {current_user.get('avatar_url')}\n"
                result += "\n"
            
            # Show other users
            other_users = [u for u in users if not u.get("me")]
            for i, user in enumerate(other_users, 1):
                result += f"{i}. {user.get('name', 'Unknown')}\n"
                result += f"   Email: {user.get('email', 'No email')}\n"
                result += f"   ID: {user.get('id')}\n"
                if user.get('avatar_url'):
                    result += f"   Avatar: {user.get('avatar_url')}\n"
                result += "\n"
            
            # Add pagination info if applicable
            if len(users) == limit:
                result += f"📄 Showing {len(users)} users (offset: {offset})\n"
                result += f"Use offset={offset + limit} to see more users.\n"
            
            return result
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Organization {organization_id} not found" if organization_id else "Error: Users endpoint not found"
            else:
                return f"Error fetching users: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching users: {str(e)}"

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@mcp.tool
async def create_analytics_report(
    organization_id: str,
    start_date: str,
    end_date: str,
    time_zone: str = "Pacific/Auckland",
    team_ids: Optional[List[str]] = None,
    user_ids: Optional[List[str]] = None,
    account_ids: Optional[List[str]] = None,
    label_ids: Optional[List[str]] = None
) -> str:
    """Create an analytics report request in Missive.

    This creates an async report request. Use get_analytics_report with the
    returned report ID to fetch the results once processing is complete.

    Args:
        organization_id: Organization ID to generate report for (required)
        start_date: Start date in YYYY-MM-DD format (required)
        end_date: End date in YYYY-MM-DD format (required)
        time_zone: Time zone identifier (default: Pacific/Auckland)
        team_ids: Optional list of team IDs to filter by
        user_ids: Optional list of user IDs to filter by
        account_ids: Optional list of account IDs to filter by
        label_ids: Optional list of shared label IDs to filter by
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    # Convert date strings to Unix timestamps
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())
    except ValueError:
        return "Error: Dates must be in YYYY-MM-DD format"

    # Build report payload per Missive API spec
    report_data = {
        "organization": organization_id,
        "start": start_ts,
        "end": end_ts,
        "time_zone": time_zone
    }

    # Add optional filters
    if team_ids:
        report_data["teams"] = team_ids

    if user_ids:
        report_data["users"] = user_ids

    if account_ids:
        report_data["accounts"] = account_ids

    if label_ids:
        report_data["shared_labels"] = label_ids

    payload = {"reports": report_data}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://public.missiveapp.com/v1/analytics/reports",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            report = data.get("reports", {})

            report_id = report.get('id')
            
            result = f"📊 Analytics Report Created!\n\n"
            result += f"Report ID: {report_id}\n"
            result += f"Organization: {organization_id}\n"
            result += f"Date Range: {start_date} to {end_date}\n"
            result += f"Time Zone: {time_zone}\n"

            # Show applied filters
            if team_ids:
                result += f"Teams: {', '.join(team_ids)}\n"
            if user_ids:
                result += f"Users: {', '.join(user_ids)}\n"
            if account_ids:
                result += f"Accounts: {', '.join(account_ids)}\n"
            if label_ids:
                result += f"Labels: {', '.join(label_ids)}\n"

            result += f"\n💡 Report is processing. Use get_analytics_report with ID '{report_id}' in ~5 seconds to fetch results."

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 400:
                error_detail = ""
                try:
                    error_data = e.response.json()
                    error_detail = f" - {json.dumps(error_data)}"
                except:
                    error_detail = f" - {e.response.text}"
                return f"Error: Invalid report parameters{error_detail}\n\nPayload sent: {json.dumps(payload, indent=2)}"
            elif e.response.status_code == 404:
                return f"Error: Organization {organization_id} not found or analytics not available."
            else:
                return f"Error creating analytics report: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error creating analytics report: {str(e)}"


@mcp.tool
async def get_analytics_report(report_id: str) -> str:
    """Get the results of an analytics report by ID.

    Use this after creating a report with create_analytics_report to fetch
    the actual analytics data once processing is complete.

    Args:
        report_id: The ID of the analytics report to retrieve
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/analytics/reports/{report_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()

            report = data.get("reports", {})
            if not report:
                return f"Analytics report {report_id} not found or still processing. Try again in a few seconds."

            result = f"📊 Analytics Report Results\n\n"

            # Date range
            start_ts = report.get("start")
            end_ts = report.get("end")
            if start_ts and end_ts:
                start_date = datetime.fromtimestamp(start_ts).strftime("%d %b %Y")
                end_date = datetime.fromtimestamp(end_ts).strftime("%d %b %Y")
                result += f"📅 Period: {start_date} to {end_date}\n"
                result += f"🌏 Timezone: {report.get('time_zone', 'UTC')}\n\n"

            # Helper function to format seconds to human readable
            def format_duration(seconds):
                if not seconds:
                    return "N/A"
                seconds = int(seconds)
                if seconds < 60:
                    return f"{seconds}s"
                elif seconds < 3600:
                    mins = seconds // 60
                    secs = seconds % 60
                    return f"{mins}m {secs}s" if secs else f"{mins}m"
                else:
                    hours = seconds // 3600
                    mins = (seconds % 3600) // 60
                    return f"{hours}h {mins}m" if mins else f"{hours}h"

            # Get selected period metrics
            selected = report.get("selected_period", {})
            previous = report.get("previous_period", {})
            
            if selected:
                global_data = selected.get("global", {})
                totals = global_data.get("totals", {})
                metrics = totals.get("metrics", {})
                
                if metrics:
                    # Messages section
                    result += "═" * 40 + "\n"
                    result += "📧 MESSAGES\n"
                    result += "═" * 40 + "\n"
                    
                    inbound = metrics.get("inbound_count", {}).get("v", 0)
                    outbound = metrics.get("outbound_count", {}).get("v", 0)
                    first_inbound = metrics.get("first_inbound_count", {}).get("v", 0)
                    reply_count = metrics.get("reply_count", {}).get("v", 0)
                    first_reply = metrics.get("first_reply_count", {}).get("v", 0)
                    
                    result += f"  Messages received:     {inbound:,}\n"
                    result += f"  Messages sent:         {outbound:,}\n"
                    result += f"  New conversations:     {first_inbound:,}\n"
                    result += f"  Conversations replied: {first_reply:,}\n"
                    result += f"  Total replies:         {reply_count:,}\n\n"
                    
                    # Response times section
                    result += "═" * 40 + "\n"
                    result += "⏱️  RESPONSE TIMES\n"
                    result += "═" * 40 + "\n"
                    
                    first_reply_avg = metrics.get("first_reply_time_avg", {}).get("v", 0)
                    reply_avg = metrics.get("reply_time_avg", {}).get("v", 0)
                    handle_avg = metrics.get("handle_time_avg", {}).get("v", 0)
                    
                    result += f"  First reply time (avg): {format_duration(first_reply_avg)}\n"
                    result += f"  Reply time (avg):       {format_duration(reply_avg)}\n"
                    result += f"  Handle time (avg):      {format_duration(handle_avg)}\n\n"
                    
                    # First reply time distribution
                    tallies = totals.get("tallies", {})
                    first_reply_dist = tallies.get("first_reply_time_counts", [])
                    
                    if first_reply_dist:
                        result += "═" * 40 + "\n"
                        result += "📊 FIRST REPLY TIME DISTRIBUTION\n"
                        result += "═" * 40 + "\n"
                        
                        # Group into meaningful buckets
                        under_15m = sum(item.get("v", 0) for item in first_reply_dist if item.get("d") in ["1m", "2m", "3m", "4m", "5m", "10m", "15m"])
                        under_1h = sum(item.get("v", 0) for item in first_reply_dist if item.get("d") in ["30m", "45m", "1h"])
                        under_4h = sum(item.get("v", 0) for item in first_reply_dist if item.get("d") in ["2h", "3h", "4h"])
                        under_12h = sum(item.get("v", 0) for item in first_reply_dist if item.get("d") in ["6h", "8h", "10h", "12h"])
                        under_48h = sum(item.get("v", 0) for item in first_reply_dist if item.get("d") in ["24h", "48h"])
                        over_48h = sum(item.get("v", 0) for item in first_reply_dist if item.get("d") in ["72h", "72h_plus"])
                        
                        total_replies = under_15m + under_1h + under_4h + under_12h + under_48h + over_48h
                        
                        if total_replies > 0:
                            result += f"  Under 15 min:  {under_15m:>5} ({under_15m*100//total_replies}%)\n"
                            result += f"  15min - 1hr:   {under_1h:>5} ({under_1h*100//total_replies}%)\n"
                            result += f"  1hr - 4hr:     {under_4h:>5} ({under_4h*100//total_replies}%)\n"
                            result += f"  4hr - 12hr:    {under_12h:>5} ({under_12h*100//total_replies}%)\n"
                            result += f"  12hr - 48hr:   {under_48h:>5} ({under_48h*100//total_replies}%)\n"
                            result += f"  Over 48hr:     {over_48h:>5} ({over_48h*100//total_replies}%)\n"
                        result += "\n"

            # Compare with previous period if available
            if previous:
                prev_global = previous.get("global", {})
                prev_totals = prev_global.get("totals", {})
                prev_metrics = prev_totals.get("metrics", {})
                
                if prev_metrics and metrics:
                    result += "═" * 40 + "\n"
                    result += "📈 VS PREVIOUS PERIOD\n"
                    result += "═" * 40 + "\n"
                    
                    curr_inbound = metrics.get("inbound_count", {}).get("v", 0)
                    prev_inbound = prev_metrics.get("inbound_count", {}).get("v", 0)
                    
                    curr_outbound = metrics.get("outbound_count", {}).get("v", 0)
                    prev_outbound = prev_metrics.get("outbound_count", {}).get("v", 0)
                    
                    curr_first_reply = metrics.get("first_reply_time_avg", {}).get("v", 0)
                    prev_first_reply = prev_metrics.get("first_reply_time_avg", {}).get("v", 0)
                    
                    def format_change(curr, prev, reverse=False):
                        if prev == 0:
                            return "N/A"
                        change = ((curr - prev) / prev) * 100
                        arrow = "↓" if change < 0 else "↑"
                        # For times, down is good
                        if reverse:
                            colour = "better" if change < 0 else "worse"
                        else:
                            colour = "worse" if change < 0 else "better"
                        return f"{arrow} {abs(change):.1f}%"
                    
                    result += f"  Messages received: {format_change(curr_inbound, prev_inbound)} ({prev_inbound:,} → {curr_inbound:,})\n"
                    result += f"  Messages sent:     {format_change(curr_outbound, prev_outbound)} ({prev_outbound:,} → {curr_outbound:,})\n"
                    result += f"  First reply time:  {format_change(curr_first_reply, prev_first_reply, True)} ({format_duration(prev_first_reply)} → {format_duration(curr_first_reply)})\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token. Please check your token in Claude Desktop config."
            elif e.response.status_code == 404:
                return f"Error: Analytics report {report_id} not found"
            else:
                return f"Error fetching analytics report: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching analytics report: {str(e)}"


# ============================================================================
# DRAFTS ENDPOINTS
# ============================================================================

@mcp.tool
async def create_draft(
    account_id: str,
    to_fields_data: str,
    subject: Optional[str] = None,
    body: Optional[str] = None,
    send: bool = False,
    send_at: Optional[int] = None,
    conversation_id: Optional[str] = None,
    team_id: Optional[str] = None,
    add_shared_labels: Optional[List[str]] = None,
    add_assignees: Optional[List[str]] = None,
    close: bool = False
) -> str:
    """Create a draft or send a message (email/SMS) immediately.

    Args:
        account_id: The account ID to send from (required)
        to_fields_data: JSON string with recipients (e.g., '[{"address": "email@example.com", "name": "John"}]')
        subject: Email subject (required for email, optional for SMS)
        body: HTML or text message body
        send: Set to true to send immediately instead of creating a draft
        send_at: Unix timestamp to schedule sending (cannot use with send=true)
        conversation_id: Add draft to existing conversation instead of creating new one
        team_id: Link draft's conversation to a team
        add_shared_labels: List of shared label IDs to add to conversation
        add_assignees: List of user IDs to assign to conversation
        close: Set to true to close the conversation after sending
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    # Parse recipients JSON
    try:
        to_fields = json.loads(to_fields_data)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON in to_fields_data: {str(e)}"

    # Build draft payload
    draft_data = {
        "drafts": {
            "account": account_id,
            "to_fields": to_fields
        }
    }

    if subject:
        draft_data["drafts"]["subject"] = subject

    if body:
        draft_data["drafts"]["body"] = body

    if send:
        draft_data["drafts"]["send"] = True

    if send_at and not send:
        draft_data["drafts"]["send_at"] = send_at

    if conversation_id:
        draft_data["drafts"]["conversation"] = conversation_id

    if team_id:
        draft_data["drafts"]["team"] = team_id

    if add_shared_labels:
        draft_data["drafts"]["add_shared_labels"] = add_shared_labels

    if add_assignees:
        draft_data["drafts"]["add_assignees"] = add_assignees

    if close:
        draft_data["drafts"]["close"] = True

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://public.missiveapp.com/v1/drafts",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=draft_data
            )
            response.raise_for_status()
            data = response.json()

            draft = data.get("drafts", {})

            if send:
                result = f"📤 Message Sent Successfully!\n\n"
            else:
                result = f"📝 Draft Created Successfully!\n\n"

            result += f"ID: {draft.get('id')}\n"

            if subject:
                result += f"Subject: {subject}\n"

            # Show recipients
            result += f"To: {to_fields_data}\n"

            if send_at and not send:
                result += f"Scheduled for: {format_timestamp(send_at)}\n"

            if conversation_id:
                result += f"Conversation: {conversation_id}\n"

            if team_id:
                result += f"Team: {team_id}\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 400:
                error_detail = ""
                try:
                    error_data = e.response.json()
                    error_detail = f" - {error_data}"
                except:
                    pass
                return f"Error: Invalid draft data{error_detail}"
            else:
                return f"Error creating draft: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error creating draft: {str(e)}"


@mcp.tool
async def get_conversation_drafts(conversation_id: str, limit: int = 10) -> str:
    """Get drafts from a specific conversation.

    Args:
        conversation_id: The ID of the conversation
        limit: Number of drafts to return (max 25)
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/conversations/{conversation_id}/drafts",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"limit": min(limit, 25)}
            )
            response.raise_for_status()
            data = response.json()

            drafts = data.get("drafts", [])
            if not drafts:
                return f"No drafts found in conversation {conversation_id}"

            result = f"📝 Drafts in Conversation ({len(drafts)} found):\n\n"

            for i, draft in enumerate(drafts, 1):
                result += f"{i}. {draft.get('subject', 'No subject')}\n"

                # To fields
                to_fields = draft.get("to_fields", [])
                if to_fields:
                    to_names = [f"{t.get('name', '')} <{t.get('address', '')}>".strip() for t in to_fields]
                    result += f"   To: {', '.join(to_names)}\n"

                # Scheduled time
                send_at = draft.get("send_at")
                if send_at:
                    result += f"   Scheduled: {format_timestamp(send_at)}\n"

                # Created time
                created_at = draft.get("created_at")
                if created_at:
                    result += f"   Created: {format_timestamp(created_at)}\n"

                result += f"   Draft ID: {draft.get('id')}\n\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 404:
                return f"Error: Conversation {conversation_id} not found"
            else:
                return f"Error fetching drafts: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching drafts: {str(e)}"


@mcp.tool
async def delete_draft(draft_id: str) -> str:
    """Delete a scheduled draft.

    Args:
        draft_id: The ID of the draft to delete
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"https://public.missiveapp.com/v1/drafts/{draft_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()

            return f"✅ Draft {draft_id} deleted successfully."

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 404:
                return f"Error: Draft {draft_id} not found"
            else:
                return f"Error deleting draft: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error deleting draft: {str(e)}"


# ============================================================================
# POSTS ENDPOINTS
# ============================================================================

@mcp.tool
async def create_post(
    conversation_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    notification_title: Optional[str] = None,
    notification_body: Optional[str] = None,
    username: Optional[str] = None,
    username_icon: Optional[str] = None,
    text: Optional[str] = None,
    markdown: Optional[str] = None,
    team_id: Optional[str] = None,
    add_shared_labels: Optional[List[str]] = None,
    remove_shared_labels: Optional[List[str]] = None,
    add_assignees: Optional[List[str]] = None,
    remove_assignees: Optional[List[str]] = None,
    close: bool = False,
    reopen: bool = False,
    add_to_inbox: bool = False
) -> str:
    """Create a post in a conversation with optional conversation management.

    Posts are the recommended way to manage conversations from integrations
    as they leave a visible audit trail.

    Args:
        conversation_id: ID of existing conversation (or create new if not provided)
        organization_id: Organization ID (required when creating new conversation)
        notification_title: Push notification title
        notification_body: Push notification body
        username: Display name for the post author
        username_icon: URL for author icon
        text: Plain text content
        markdown: Markdown formatted content
        team_id: Link conversation to a team
        add_shared_labels: Label IDs to add to conversation
        remove_shared_labels: Label IDs to remove from conversation
        add_assignees: User IDs to assign to conversation
        remove_assignees: User IDs to unassign from conversation
        close: Close the conversation
        reopen: Reopen a closed conversation
        add_to_inbox: Move conversation to inbox
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    # Build post payload
    post_data = {}

    if conversation_id:
        post_data["conversation"] = conversation_id

    if organization_id:
        post_data["organization"] = organization_id

    if notification_title:
        post_data["notification"] = post_data.get("notification", {})
        post_data["notification"]["title"] = notification_title

    if notification_body:
        post_data["notification"] = post_data.get("notification", {})
        post_data["notification"]["body"] = notification_body

    if username:
        post_data["username"] = username

    if username_icon:
        post_data["username_icon"] = username_icon

    if text:
        post_data["text"] = text

    if markdown:
        post_data["markdown"] = markdown

    if team_id:
        post_data["team"] = team_id

    if add_shared_labels:
        post_data["add_shared_labels"] = add_shared_labels

    if remove_shared_labels:
        post_data["remove_shared_labels"] = remove_shared_labels

    if add_assignees:
        post_data["add_assignees"] = add_assignees

    if remove_assignees:
        post_data["remove_assignees"] = remove_assignees

    if close:
        post_data["close"] = True

    if reopen:
        post_data["reopen"] = True

    if add_to_inbox:
        post_data["add_to_inbox"] = True

    payload = {"posts": post_data}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://public.missiveapp.com/v1/posts",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            post = data.get("posts", {})

            result = f"📌 Post Created Successfully!\n\n"
            result += f"Post ID: {post.get('id')}\n"

            if username:
                result += f"Author: {username}\n"

            if text:
                result += f"Text: {text[:100]}{'...' if len(text) > 100 else ''}\n"
            elif markdown:
                result += f"Markdown: {markdown[:100]}{'...' if len(markdown) > 100 else ''}\n"

            # Show actions taken
            actions = []
            if close:
                actions.append("closed conversation")
            if reopen:
                actions.append("reopened conversation")
            if add_to_inbox:
                actions.append("moved to inbox")
            if add_shared_labels:
                actions.append(f"added {len(add_shared_labels)} label(s)")
            if remove_shared_labels:
                actions.append(f"removed {len(remove_shared_labels)} label(s)")
            if add_assignees:
                actions.append(f"assigned {len(add_assignees)} user(s)")
            if remove_assignees:
                actions.append(f"unassigned {len(remove_assignees)} user(s)")

            if actions:
                result += f"Actions: {', '.join(actions)}\n"

            # Conversation info
            conversation = post.get("conversation", {})
            if conversation:
                result += f"Conversation ID: {conversation.get('id')}\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 400:
                error_detail = ""
                try:
                    error_data = e.response.json()
                    error_detail = f" - {error_data}"
                except:
                    pass
                return f"Error: Invalid post data{error_detail}"
            else:
                return f"Error creating post: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error creating post: {str(e)}"


@mcp.tool
async def get_conversation_posts(conversation_id: str, limit: int = 10) -> str:
    """Get posts from a specific conversation.

    Args:
        conversation_id: The ID of the conversation
        limit: Number of posts to return (max 25)
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/conversations/{conversation_id}/posts",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"limit": min(limit, 25)}
            )
            response.raise_for_status()
            data = response.json()

            posts = data.get("posts", [])
            if not posts:
                return f"No posts found in conversation {conversation_id}"

            result = f"📌 Posts in Conversation ({len(posts)} found):\n\n"

            for i, post in enumerate(posts, 1):
                result += f"{i}. "

                username = post.get("username", "Unknown")
                result += f"By: {username}\n"

                text = post.get("text", "")
                if text:
                    result += f"   Text: {text[:150]}{'...' if len(text) > 150 else ''}\n"

                markdown = post.get("markdown", "")
                if markdown and not text:
                    result += f"   Content: {markdown[:150]}{'...' if len(markdown) > 150 else ''}\n"

                created_at = post.get("created_at")
                if created_at:
                    result += f"   Created: {format_timestamp(created_at)}\n"

                result += f"   Post ID: {post.get('id')}\n\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 404:
                return f"Error: Conversation {conversation_id} not found"
            else:
                return f"Error fetching posts: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching posts: {str(e)}"


# ============================================================================
# CONTACTS ENDPOINTS
# ============================================================================

@mcp.tool
async def list_contacts(
    contact_book_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> str:
    """List contacts from Missive.

    Args:
        contact_book_id: Filter by contact book ID
        search: Search term to filter contacts
        limit: Number of contacts to return (max 200)
        offset: Offset for pagination
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    params = {
        "limit": min(limit, 200),
        "offset": max(offset, 0)
    }

    if contact_book_id:
        params["contact_book"] = contact_book_id

    if search:
        params["search"] = search

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/contacts",
                headers={"Authorization": f"Bearer {api_token}"},
                params=params
            )
            response.raise_for_status()
            data = response.json()

            contacts = data.get("contacts", [])
            if not contacts:
                return "No contacts found"

            result = f"👤 Contacts ({len(contacts)} found):\n\n"

            for i, contact in enumerate(contacts, 1):
                name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                if not name:
                    name = "Unknown"

                result += f"{i}. {name}\n"

                # Email addresses
                infos = contact.get("infos", [])
                emails = [info.get("value") for info in infos if info.get("kind") == "email"]
                if emails:
                    result += f"   Email: {', '.join(emails[:2])}\n"

                # Phone numbers
                phones = [info.get("value") for info in infos if info.get("kind") == "phone"]
                if phones:
                    result += f"   Phone: {', '.join(phones[:2])}\n"

                # Organization memberships
                memberships = contact.get("memberships", [])
                orgs = [m.get("group", {}).get("name") for m in memberships
                        if m.get("group", {}).get("kind") == "organization"]
                if orgs:
                    result += f"   Organization: {', '.join(orgs[:2])}\n"

                # Groups
                groups = [m.get("group", {}).get("name") for m in memberships
                         if m.get("group", {}).get("kind") == "group"]
                if groups:
                    result += f"   Groups: {', '.join(groups[:3])}\n"

                result += f"   ID: {contact.get('id')}\n\n"

            if len(contacts) == limit:
                result += f"📄 Use offset={offset + limit} to see more contacts.\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            else:
                return f"Error fetching contacts: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching contacts: {str(e)}"


@mcp.tool
async def get_contact(contact_id: str) -> str:
    """Get details of a specific contact.

    Args:
        contact_id: The ID of the contact to retrieve
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://public.missiveapp.com/v1/contacts/{contact_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()

            # Handle both object and array responses from the API
            contacts_data = data.get("contacts", {})
            if isinstance(contacts_data, list):
                contact = contacts_data[0] if contacts_data else {}
            else:
                contact = contacts_data

            if not contact:
                return f"Contact {contact_id} not found"

            name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
            if not name:
                name = "Unknown"

            result = f"👤 Contact Details:\n\n"
            result += f"Name: {name}\n"
            result += f"ID: {contact.get('id')}\n"

            # Contact book
            contact_book = contact.get("contact_book")
            if contact_book:
                result += f"Contact Book: {contact_book}\n"

            # All info fields
            infos = contact.get("infos", [])
            if infos:
                result += "\nContact Info:\n"
                for info in infos:
                    kind = info.get("kind", "unknown")
                    value = info.get("value", "")
                    label = info.get("label", "")
                    if label:
                        result += f"  {kind.title()} ({label}): {value}\n"
                    else:
                        result += f"  {kind.title()}: {value}\n"

            # Memberships (organizations and groups)
            memberships = contact.get("memberships", [])
            if memberships:
                result += "\nMemberships:\n"
                for membership in memberships:
                    group = membership.get("group", {})
                    group_name = group.get("name", "Unknown")
                    group_kind = group.get("kind", "unknown")
                    title = membership.get("title", "")
                    location = membership.get("location", "")

                    if group_kind == "organization":
                        result += f"  🏢 {group_name}"
                        if title:
                            result += f" - {title}"
                        if location:
                            result += f" ({location})"
                        result += "\n"
                    else:
                        result += f"  🏷️ Group: {group_name}\n"

            # Notes
            notes = contact.get("notes", "")
            if notes:
                result += f"\nNotes: {notes}\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 404:
                return f"Error: Contact {contact_id} not found"
            else:
                return f"Error fetching contact: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching contact: {str(e)}"


@mcp.tool
async def create_contact(
    contact_book_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    notes: Optional[str] = None,
    memberships_data: Optional[str] = None
) -> str:
    """Create a new contact.

    Args:
        contact_book_id: The contact book ID to create contact in (required)
        first_name: Contact's first name
        last_name: Contact's last name
        email: Contact's email address
        phone: Contact's phone number
        notes: Notes about the contact
        memberships_data: JSON string for group/org memberships (e.g., '[{"group": {"kind": "group", "name": "VIPs"}}]')
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    # Build contact payload
    contact_data = {
        "contact_book": contact_book_id
    }

    if first_name:
        contact_data["first_name"] = first_name

    if last_name:
        contact_data["last_name"] = last_name

    # Build infos array
    infos = []
    if email:
        infos.append({"kind": "email", "value": email})
    if phone:
        infos.append({"kind": "phone", "value": phone})
    if infos:
        contact_data["infos"] = infos

    if notes:
        contact_data["notes"] = notes

    # Parse memberships if provided
    if memberships_data:
        try:
            memberships = json.loads(memberships_data)
            contact_data["memberships"] = memberships
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in memberships_data: {str(e)}"

    payload = {"contacts": contact_data}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://public.missiveapp.com/v1/contacts",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            # Handle both object and array responses from the API
            contacts_data = data.get("contacts", {})
            if isinstance(contacts_data, list):
                contact = contacts_data[0] if contacts_data else {}
            else:
                contact = contacts_data

            name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
            if not name:
                name = "New Contact"

            result = f"✅ Contact Created Successfully!\n\n"
            result += f"Name: {name}\n"
            result += f"ID: {contact.get('id')}\n"

            if email:
                result += f"Email: {email}\n"
            if phone:
                result += f"Phone: {phone}\n"

            memberships = contact.get("memberships", [])
            if memberships:
                groups = [m.get("group", {}).get("name") for m in memberships]
                result += f"Groups: {', '.join(groups)}\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 400:
                error_detail = ""
                try:
                    error_data = e.response.json()
                    error_detail = f" - {error_data}"
                except:
                    pass
                return f"Error: Invalid contact data{error_detail}"
            else:
                return f"Error creating contact: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error creating contact: {str(e)}"


@mcp.tool
async def update_contact(
    contact_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    notes: Optional[str] = None,
    memberships_data: Optional[str] = None
) -> str:
    """Update an existing contact.

    Note: When updating memberships, you must include ALL memberships.
    Missing memberships will be removed from the contact.

    Args:
        contact_id: The ID of the contact to update (required)
        first_name: New first name
        last_name: New last name
        email: New email address (replaces existing emails)
        phone: New phone number (replaces existing phones)
        notes: New notes
        memberships_data: JSON string for ALL group/org memberships
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    # Build update payload
    contact_data = {}

    if first_name is not None:
        contact_data["first_name"] = first_name

    if last_name is not None:
        contact_data["last_name"] = last_name

    # Build infos array if email or phone provided
    if email is not None or phone is not None:
        infos = []
        if email:
            infos.append({"kind": "email", "value": email})
        if phone:
            infos.append({"kind": "phone", "value": phone})
        contact_data["infos"] = infos

    if notes is not None:
        contact_data["notes"] = notes

    # Parse memberships if provided
    if memberships_data is not None:
        try:
            memberships = json.loads(memberships_data)
            contact_data["memberships"] = memberships
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in memberships_data: {str(e)}"

    if not contact_data:
        return "Error: At least one field must be provided to update"

    # API expects contacts as an array with id included
    contact_data["id"] = contact_id
    payload = {"contacts": [contact_data]}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"https://public.missiveapp.com/v1/contacts/{contact_id}",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            # Handle both object and array responses from the API
            contacts_data = data.get("contacts", {})
            if isinstance(contacts_data, list):
                contact = contacts_data[0] if contacts_data else {}
            else:
                contact = contacts_data

            name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
            if not name:
                name = "Contact"

            result = f"✅ Contact Updated Successfully!\n\n"
            result += f"Name: {name}\n"
            result += f"ID: {contact.get('id')}\n"

            infos = contact.get("infos", [])
            emails = [info.get("value") for info in infos if info.get("kind") == "email"]
            phones = [info.get("value") for info in infos if info.get("kind") == "phone"]

            if emails:
                result += f"Email: {', '.join(emails)}\n"
            if phones:
                result += f"Phone: {', '.join(phones)}\n"

            memberships = contact.get("memberships", [])
            if memberships:
                groups = [m.get("group", {}).get("name") for m in memberships]
                result += f"Groups: {', '.join(groups)}\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 404:
                return f"Error: Contact {contact_id} not found"
            elif e.response.status_code == 400:
                return f"Error: Invalid contact data"
            else:
                return f"Error updating contact: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error updating contact: {str(e)}"


@mcp.tool
async def delete_contact(contact_id: str) -> str:
    """Delete a contact.

    Args:
        contact_id: The ID of the contact to delete
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"https://public.missiveapp.com/v1/contacts/{contact_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()

            return f"✅ Contact {contact_id} deleted successfully."

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 404:
                return f"Error: Contact {contact_id} not found"
            else:
                return f"Error deleting contact: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error deleting contact: {str(e)}"


@mcp.tool
async def list_contact_books() -> str:
    """List all contact books the authenticated user has access to."""

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/contact_books",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()

            contact_books = data.get("contact_books", [])
            if not contact_books:
                return "No contact books found"

            result = f"📚 Contact Books ({len(contact_books)} found):\n\n"

            for i, book in enumerate(contact_books, 1):
                result += f"{i}. {book.get('name', 'Unnamed')}\n"
                result += f"   ID: {book.get('id')}\n"

                # Show if shared
                shared = book.get("shared", False)
                if shared:
                    result += f"   Shared: Yes\n"

                result += "\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            else:
                return f"Error fetching contact books: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching contact books: {str(e)}"


@mcp.tool
async def list_contact_groups(
    contact_book_id: str,
    kind: str = "group"
) -> str:
    """List contact groups or organizations linked to a contact book.

    Args:
        contact_book_id: The contact book ID
        kind: Type of groups to list ('group' or 'organization')
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    if kind not in ["group", "organization"]:
        return "Error: kind must be 'group' or 'organization'"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/contact_groups",
                headers={"Authorization": f"Bearer {api_token}"},
                params={"contact_book": contact_book_id, "kind": kind}
            )
            response.raise_for_status()
            data = response.json()

            contact_groups = data.get("contact_groups", [])
            if not contact_groups:
                return f"No {kind}s found in contact book {contact_book_id}"

            emoji = "🏢" if kind == "organization" else "🏷️"
            result = f"{emoji} {kind.title()}s ({len(contact_groups)} found):\n\n"

            for i, group in enumerate(contact_groups, 1):
                result += f"{i}. {group.get('name', 'Unnamed')}\n"
                result += f"   ID: {group.get('id')}\n\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 404:
                return f"Error: Contact book {contact_book_id} not found"
            else:
                return f"Error fetching groups: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching groups: {str(e)}"


@mcp.tool
async def get_contacts_by_group(
    contact_book_id: str,
    group_name: str,
    limit: int = 200
) -> str:
    """Get contacts that belong to a specific group.

    Note: The Missive API doesn't support filtering by group directly,
    so this fetches contacts from the book and filters by group membership.

    Args:
        contact_book_id: The contact book ID (required)
        group_name: The name of the group to filter by (required)
        limit: Maximum contacts to scan (max 200)
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    params = {
        "contact_book": contact_book_id,
        "limit": min(limit, 200)
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/contacts",
                headers={"Authorization": f"Bearer {api_token}"},
                params=params
            )
            response.raise_for_status()
            data = response.json()

            contacts = data.get("contacts", [])
            if not contacts:
                return f"No contacts found in contact book {contact_book_id}"

            # Filter contacts by group membership
            matching_contacts = []
            for contact in contacts:
                memberships = contact.get("memberships", [])
                for m in memberships:
                    group = m.get("group", {})
                    if group.get("name", "").lower() == group_name.lower():
                        matching_contacts.append(contact)
                        break

            if not matching_contacts:
                return f"No contacts found in group '{group_name}'"

            result = f"👤 Contacts in group '{group_name}' ({len(matching_contacts)} found):\n\n"

            for i, contact in enumerate(matching_contacts, 1):
                name = f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
                if not name:
                    name = "Unknown"

                result += f"{i}. {name}\n"

                # Email addresses
                infos = contact.get("infos", [])
                emails = [info.get("value") for info in infos if info.get("kind") == "email"]
                if emails:
                    result += f"   Email: {', '.join(emails[:2])}\n"

                # Phone numbers
                phones = [info.get("value") for info in infos if info.get("kind") == "phone"]
                if phones:
                    result += f"   Phone: {', '.join(phones[:2])}\n"

                result += f"   ID: {contact.get('id')}\n\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            else:
                return f"Error fetching contacts: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching contacts: {str(e)}"


@mcp.tool
async def add_contact_to_group(
    contact_id: str,
    group_name: str,
    group_kind: str = "group"
) -> str:
    """Add a contact to a group (preserving existing memberships).

    Args:
        contact_id: The ID of the contact to update (required)
        group_name: The name of the group to add (required)
        group_kind: Type of group - 'group' or 'organization' (default: 'group')
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    if group_kind not in ["group", "organization"]:
        return "Error: group_kind must be 'group' or 'organization'"

    async with httpx.AsyncClient() as client:
        try:
            # First, fetch the current contact to get existing memberships
            response = await client.get(
                f"https://public.missiveapp.com/v1/contacts/{contact_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()

            # Handle both object and array responses from the API
            contacts_data = data.get("contacts", {})
            if isinstance(contacts_data, list):
                contact = contacts_data[0] if contacts_data else {}
            else:
                contact = contacts_data

            if not contact:
                return f"Error: Contact {contact_id} not found"

            # Get existing memberships and contact book
            existing_memberships = contact.get("memberships", [])
            contact_book_id = contact.get("contact_book")

            # Check if already in this group
            for m in existing_memberships:
                group = m.get("group", {})
                if group.get("name", "").lower() == group_name.lower() and group.get("kind") == group_kind:
                    return f"Contact is already in {group_kind} '{group_name}'"

            # Look up the target group ID from the contact_groups endpoint
            target_group_id = None
            if contact_book_id:
                groups_response = await client.get(
                    "https://public.missiveapp.com/v1/contact_groups",
                    headers={"Authorization": f"Bearer {api_token}"},
                    params={"contact_book": contact_book_id, "kind": group_kind}
                )
                if groups_response.status_code == 200:
                    groups_data = groups_response.json()
                    for g in groups_data.get("contact_groups", []):
                        if g.get("name", "").lower() == group_name.lower():
                            target_group_id = g.get("id")
                            break

            if not target_group_id:
                return f"Error: Group '{group_name}' not found in the contact book. Please create the group in Missive first."

            # Build new memberships list (preserve existing + add new)
            # Use documented format: kind + name
            new_memberships = []
            for m in existing_memberships:
                group = m.get("group", {})
                membership_entry = {
                    "group": {
                        "kind": group.get("kind", "group"),
                        "name": group.get("name", "")
                    }
                }
                # Preserve title/location for organizations
                if m.get("title"):
                    membership_entry["title"] = m.get("title")
                if m.get("location"):
                    membership_entry["location"] = m.get("location")
                new_memberships.append(membership_entry)

            # Add the new group using documented format (kind + name)
            new_memberships.append({
                "group": {
                    "kind": group_kind,
                    "name": group_name
                }
            })

            # Update the contact - API expects contacts as an array with id
            payload = {
                "contacts": [{
                    "id": contact_id,
                    "memberships": new_memberships
                }]
            }

            response = await client.patch(
                f"https://public.missiveapp.com/v1/contacts/{contact_id}",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            # Handle both object and array responses from the API
            contacts_data = data.get("contacts", {})
            if isinstance(contacts_data, list):
                updated_contact = contacts_data[0] if contacts_data else {}
            else:
                updated_contact = contacts_data

            name = f"{updated_contact.get('first_name', '')} {updated_contact.get('last_name', '')}".strip()
            if not name:
                name = "Contact"

            # List all current groups
            memberships = updated_contact.get("memberships", [])
            groups = [m.get("group", {}).get("name") for m in memberships if m.get("group", {}).get("kind") == "group"]
            orgs = [m.get("group", {}).get("name") for m in memberships if m.get("group", {}).get("kind") == "organization"]

            result = f"✅ Added {name} to {group_kind} '{group_name}'\n\n"
            result += f"Contact ID: {contact_id}\n"
            if groups:
                result += f"Groups: {', '.join(groups)}\n"
            if orgs:
                result += f"Organizations: {', '.join(orgs)}\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 404:
                return f"Error: Contact {contact_id} not found"
            else:
                return f"Error updating contact: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error updating contact: {str(e)}"


@mcp.tool
async def remove_contact_from_group(
    contact_id: str,
    group_name: str
) -> str:
    """Remove a contact from a group (preserving other memberships).

    Args:
        contact_id: The ID of the contact to update (required)
        group_name: The name of the group to remove (required)
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    async with httpx.AsyncClient() as client:
        try:
            # First, fetch the current contact to get existing memberships
            response = await client.get(
                f"https://public.missiveapp.com/v1/contacts/{contact_id}",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()

            # Handle both object and array responses from the API
            contacts_data = data.get("contacts", {})
            if isinstance(contacts_data, list):
                contact = contacts_data[0] if contacts_data else {}
            else:
                contact = contacts_data

            if not contact:
                return f"Error: Contact {contact_id} not found"

            # Get existing memberships
            existing_memberships = contact.get("memberships", [])

            # Check if in this group
            found = False
            for m in existing_memberships:
                group = m.get("group", {})
                if group.get("name", "").lower() == group_name.lower():
                    found = True
                    break

            if not found:
                return f"Contact is not in group '{group_name}'"

            # Build new memberships list (exclude the target group)
            new_memberships = []
            for m in existing_memberships:
                group = m.get("group", {})
                if group.get("name", "").lower() != group_name.lower():
                    membership_entry = {
                        "group": {
                            "kind": group.get("kind", "group"),
                            "name": group.get("name", "")
                        }
                    }
                    # Preserve title/location for organizations
                    if m.get("title"):
                        membership_entry["title"] = m.get("title")
                    if m.get("location"):
                        membership_entry["location"] = m.get("location")
                    new_memberships.append(membership_entry)

            # Update the contact - API expects contacts as an array with id
            payload = {
                "contacts": [{
                    "id": contact_id,
                    "memberships": new_memberships
                }]
            }

            response = await client.patch(
                f"https://public.missiveapp.com/v1/contacts/{contact_id}",
                headers={
                    "Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            # Handle both object and array responses from the API
            contacts_data = data.get("contacts", {})
            if isinstance(contacts_data, list):
                updated_contact = contacts_data[0] if contacts_data else {}
            else:
                updated_contact = contacts_data

            name = f"{updated_contact.get('first_name', '')} {updated_contact.get('last_name', '')}".strip()
            if not name:
                name = "Contact"

            # List remaining groups
            memberships = updated_contact.get("memberships", [])
            groups = [m.get("group", {}).get("name") for m in memberships if m.get("group", {}).get("kind") == "group"]
            orgs = [m.get("group", {}).get("name") for m in memberships if m.get("group", {}).get("kind") == "organization"]

            result = f"✅ Removed {name} from group '{group_name}'\n\n"
            result += f"Contact ID: {contact_id}\n"
            if groups:
                result += f"Remaining groups: {', '.join(groups)}\n"
            elif orgs:
                result += f"Organizations: {', '.join(orgs)}\n"
            else:
                result += "No remaining group memberships\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            elif e.response.status_code == 404:
                return f"Error: Contact {contact_id} not found"
            else:
                return f"Error updating contact: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error updating contact: {str(e)}"


# ============================================================================
# ORGANIZATIONS & TEAMS ENDPOINTS
# ============================================================================

@mcp.tool
async def list_organizations() -> str:
    """List organizations the authenticated user is part of."""

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/organizations",
                headers={"Authorization": f"Bearer {api_token}"}
            )
            response.raise_for_status()
            data = response.json()

            organizations = data.get("organizations", [])
            if not organizations:
                return "No organizations found"

            result = f"🏢 Organizations ({len(organizations)} found):\n\n"

            for i, org in enumerate(organizations, 1):
                result += f"{i}. {org.get('name', 'Unnamed')}\n"
                result += f"   ID: {org.get('id')}\n"

                # Show plan if available
                plan = org.get("plan", "")
                if plan:
                    result += f"   Plan: {plan}\n"

                result += "\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            else:
                return f"Error fetching organizations: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching organizations: {str(e)}"


@mcp.tool
async def list_teams(organization_id: Optional[str] = None) -> str:
    """List teams in organizations.

    Args:
        organization_id: Optional organization ID to filter teams
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    params = {}
    if organization_id:
        params["organization"] = organization_id

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/teams",
                headers={"Authorization": f"Bearer {api_token}"},
                params=params
            )
            response.raise_for_status()
            data = response.json()

            teams = data.get("teams", [])
            if not teams:
                filter_msg = f" in organization {organization_id}" if organization_id else ""
                return f"No teams found{filter_msg}"

            result = f"👥 Teams ({len(teams)} found):\n\n"

            for i, team in enumerate(teams, 1):
                result += f"{i}. {team.get('name', 'Unnamed')}\n"
                result += f"   ID: {team.get('id')}\n"

                # Organization
                org = team.get("organization")
                if org:
                    if isinstance(org, dict):
                        result += f"   Organization: {org.get('name', org.get('id', 'Unknown'))}\n"
                    else:
                        result += f"   Organization: {org}\n"

                result += "\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            else:
                return f"Error fetching teams: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching teams: {str(e)}"


# ============================================================================
# SHARED LABELS ENDPOINTS
# ============================================================================

@mcp.tool
async def list_shared_labels(organization_id: Optional[str] = None) -> str:
    """List shared labels in organizations.

    Args:
        organization_id: Optional organization ID to filter labels
    """

    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"

    params = {}
    if organization_id:
        params["organization"] = organization_id

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://public.missiveapp.com/v1/shared_labels",
                headers={"Authorization": f"Bearer {api_token}"},
                params=params
            )
            response.raise_for_status()
            data = response.json()

            labels = data.get("shared_labels", [])
            if not labels:
                filter_msg = f" in organization {organization_id}" if organization_id else ""
                return f"No shared labels found{filter_msg}"

            result = f"🏷️ Shared Labels ({len(labels)} found):\n\n"

            for i, label in enumerate(labels, 1):
                result += f"{i}. {label.get('name', 'Unnamed')}\n"
                result += f"   ID: {label.get('id')}\n"

                # Color
                color = label.get("color", "")
                if color:
                    result += f"   Color: {color}\n"

                # Parent label (for hierarchical labels)
                parent = label.get("parent")
                if parent:
                    if isinstance(parent, dict):
                        result += f"   Parent: {parent.get('name', parent.get('id', 'Unknown'))}\n"
                    else:
                        result += f"   Parent: {parent}\n"

                # Organization
                org = label.get("organization")
                if org:
                    if isinstance(org, dict):
                        result += f"   Organization: {org.get('name', org.get('id', 'Unknown'))}\n"
                    else:
                        result += f"   Organization: {org}\n"

                result += "\n"

            return result

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return "Error: Invalid Missive API token."
            else:
                return f"Error fetching shared labels: HTTP {e.response.status_code}"
        except Exception as e:
            return f"Error fetching shared labels: {str(e)}"


# ============================================================================
# TEAM METRICS (Custom Analytics)
# ============================================================================

@mcp.tool
async def calculate_team_metrics(
    team_id: str,
    start_date: str,
    end_date: str,
    internal_domains: Optional[str] = None,
    tracked_channels: Optional[str] = None,
    max_conversations: int = 200
) -> str:
    """Calculate custom metrics for a team inbox by analysing conversations and messages.
    
    Useful when native analytics filtering requires a higher plan tier.
    Fetches conversations from the team inbox and calculates:
    - Messages received/sent counts
    - First reply time calculations  
    - Breakdown by email channel
    
    Args:
        team_id: The team ID to analyse (required)
        start_date: Start date in YYYY-MM-DD format (required)
        end_date: End date in YYYY-MM-DD format (required)
        internal_domains: Comma-separated domains to identify outbound messages
                         (default: from INTERNAL_DOMAINS env var, or 'example.com')
        tracked_channels: Comma-separated email addresses to group by
                         (default: from TRACKED_CHANNELS env var, or auto-detect)
        max_conversations: Maximum conversations to analyse (default: 200, max: 2000)
    """
    import asyncio
    
    try:
        api_token = get_api_token()
    except ValueError as e:
        return f"Error: {str(e)}"
    
    # Parse dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        start_ts = start_dt.timestamp()
        end_ts = end_dt.timestamp()
    except ValueError:
        return "Error: Dates must be in YYYY-MM-DD format"
    
    # Get internal domains (for determining inbound vs outbound)
    if internal_domains:
        domains = [d.strip().lower() for d in internal_domains.split(",")]
    else:
        env_domains = os.getenv("INTERNAL_DOMAINS", "example.com")
        domains = [d.strip().lower() for d in env_domains.split(",")]
    
    # Get tracked channels if specified
    channels_to_track = None
    if tracked_channels:
        channels_to_track = [c.strip().lower() for c in tracked_channels.split(",")]
    elif os.getenv("TRACKED_CHANNELS"):
        channels_to_track = [c.strip().lower() for c in os.getenv("TRACKED_CHANNELS").split(",")]
    
    # Limit max conversations
    max_conversations = min(max_conversations, 2000)
    
    # Helper to check if email is internal
    def is_internal(email: str) -> bool:
        if not email:
            return False
        email_lower = email.lower()
        return any(domain in email_lower for domain in domains)
    
    # Helper to extract email address
    def get_email(field: dict) -> str:
        return (field.get("address") or "").lower() if field else ""
    
    # Metrics containers
    metrics = {
        "total_conversations": 0,
        "conversations_with_reply": 0,
        "total_inbound": 0,
        "total_outbound": 0,
        "first_reply_times": [],  # in seconds
        "channels_inbound": {},   # channel -> count
        "channels_outbound": {},  # channel -> count
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # Fetch conversations from team inbox
        conversations = []
        
        # We need to fetch from team_all to get all conversations including closed
        # and filter by date ourselves
        params = {"team_all": team_id, "limit": 50}
        
        while len(conversations) < max_conversations:
            try:
                response = await client.get(
                    "https://public.missiveapp.com/v1/conversations",
                    headers={"Authorization": f"Bearer {api_token}"},
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                batch = data.get("conversations", [])
                if not batch:
                    break
                
                # Filter by date - check last_activity_at
                for conv in batch:
                    last_activity = conv.get("last_activity_at", 0)
                    created_at = conv.get("created_at", 0)
                    
                    # Include if activity falls within our date range
                    if last_activity >= start_ts or created_at >= start_ts:
                        if created_at <= end_ts:
                            conversations.append(conv)
                
                # Check if we should continue (if oldest conv in batch is still in range)
                if batch:
                    oldest_activity = min(c.get("last_activity_at", 0) for c in batch)
                    if oldest_activity < start_ts:
                        # We've gone past our start date
                        break
                
                # Pagination - use the last conversation's ID for next batch
                # Missive uses cursor-based pagination
                if len(batch) < 50:
                    break
                    
                # Get next page using 'until' parameter (Missive pagination)
                last_conv = batch[-1]
                params["until"] = last_conv.get("last_activity_at")
                
                # Rate limit: 2 requests per second (within 5/sec burst limit)
                await asyncio.sleep(0.5)
                
            except httpx.HTTPStatusError as e:
                return f"Error fetching conversations: HTTP {e.response.status_code}"
            except Exception as e:
                return f"Error fetching conversations: {str(e)}"
        
        metrics["total_conversations"] = len(conversations)
        
        if not conversations:
            return f"No conversations found for team {team_id} in date range {start_date} to {end_date}"
        
        # Now fetch messages for each conversation and calculate metrics
        progress_total = len(conversations)
        
        for idx, conv in enumerate(conversations):
            conv_id = conv.get("id")
            
            try:
                # Fetch messages for this conversation
                msg_response = await client.get(
                    f"https://public.missiveapp.com/v1/conversations/{conv_id}/messages",
                    headers={"Authorization": f"Bearer {api_token}"},
                    params={"limit": 10}  # Missive API max is 10
                )
                msg_response.raise_for_status()
                msg_data = msg_response.json()
                
                messages = msg_data.get("messages", [])
                
                # Filter messages by date range and sort by delivered_at
                filtered_messages = []
                for msg in messages:
                    delivered_at = msg.get("delivered_at", 0)
                    if start_ts <= delivered_at <= end_ts:
                        filtered_messages.append(msg)
                
                # Sort by delivered time (oldest first)
                filtered_messages.sort(key=lambda m: m.get("delivered_at", 0))
                
                # Process messages
                first_inbound_time = None
                first_outbound_time = None
                
                for msg in filtered_messages:
                    from_field = msg.get("from_field", {})
                    to_fields = msg.get("to_fields", [])
                    delivered_at = msg.get("delivered_at", 0)
                    
                    from_email = get_email(from_field)
                    
                    # Determine if inbound or outbound
                    if is_internal(from_email):
                        # Outbound message (from internal)
                        metrics["total_outbound"] += 1
                        
                        # Track channel (the from address for outbound)
                        if from_email:
                            if channels_to_track is None or from_email in channels_to_track:
                                metrics["channels_outbound"][from_email] = \
                                    metrics["channels_outbound"].get(from_email, 0) + 1
                        
                        # Track first outbound time for reply time calc
                        if first_outbound_time is None and first_inbound_time is not None:
                            first_outbound_time = delivered_at
                    else:
                        # Inbound message (from external)
                        metrics["total_inbound"] += 1
                        
                        # Track channel (the to address for inbound - which of our addresses received it)
                        for to_field in to_fields:
                            to_email = get_email(to_field)
                            if is_internal(to_email):
                                if channels_to_track is None or to_email in channels_to_track:
                                    metrics["channels_inbound"][to_email] = \
                                        metrics["channels_inbound"].get(to_email, 0) + 1
                        
                        # Track first inbound time
                        if first_inbound_time is None:
                            first_inbound_time = delivered_at
                
                # Calculate first reply time for this conversation
                if first_inbound_time and first_outbound_time:
                    reply_time = first_outbound_time - first_inbound_time
                    if reply_time > 0:  # Sanity check
                        metrics["first_reply_times"].append(reply_time)
                        metrics["conversations_with_reply"] += 1
                
                # Rate limit: 2 requests per second (within 5/sec burst limit)
                await asyncio.sleep(0.5)
                    
            except httpx.HTTPStatusError:
                # Skip this conversation if we can't fetch messages
                continue
            except Exception:
                continue
    
    # Calculate averages
    avg_first_reply = 0
    if metrics["first_reply_times"]:
        avg_first_reply = sum(metrics["first_reply_times"]) / len(metrics["first_reply_times"])
    
    # Helper to format duration
    def format_duration(seconds):
        if not seconds:
            return "N/A"
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            mins = seconds // 60
            return f"{mins}m"
        else:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            return f"{hours}h {mins}m" if mins else f"{hours}h"
    
    # Build result
    result = f"📊 Team Metrics Report\n\n"
    result += f"📅 Period: {start_dt.strftime('%d %b %Y')} to {end_dt.strftime('%d %b %Y')}\n"
    result += f"🏷️  Team ID: {team_id}\n\n"
    
    result += "═" * 45 + "\n"
    result += "📧 OVERALL\n"
    result += "═" * 45 + "\n"
    result += f"  Conversations analysed:  {metrics['total_conversations']:,}\n"
    result += f"  Messages received:       {metrics['total_inbound']:,}\n"
    result += f"  Messages sent:           {metrics['total_outbound']:,}\n"
    result += f"  Conversations replied:   {metrics['conversations_with_reply']:,}\n"
    result += f"  First reply time (avg):  {format_duration(avg_first_reply)}\n\n"
    
    # First reply time distribution
    if metrics["first_reply_times"]:
        result += "═" * 45 + "\n"
        result += "⏱️  FIRST REPLY TIME DISTRIBUTION\n"
        result += "═" * 45 + "\n"
        
        times = metrics["first_reply_times"]
        under_15m = sum(1 for t in times if t < 900)
        under_1h = sum(1 for t in times if 900 <= t < 3600)
        under_4h = sum(1 for t in times if 3600 <= t < 14400)
        under_12h = sum(1 for t in times if 14400 <= t < 43200)
        under_48h = sum(1 for t in times if 43200 <= t < 172800)
        over_48h = sum(1 for t in times if t >= 172800)
        
        total = len(times)
        result += f"  Under 15 min:  {under_15m:>5} ({under_15m*100//total}%)\n"
        result += f"  15min - 1hr:   {under_1h:>5} ({under_1h*100//total}%)\n"
        result += f"  1hr - 4hr:     {under_4h:>5} ({under_4h*100//total}%)\n"
        result += f"  4hr - 12hr:    {under_12h:>5} ({under_12h*100//total}%)\n"
        result += f"  12hr - 48hr:   {under_48h:>5} ({under_48h*100//total}%)\n"
        result += f"  Over 48hr:     {over_48h:>5} ({over_48h*100//total}%)\n\n"
    
    # Inbound by channel
    if metrics["channels_inbound"]:
        result += "═" * 45 + "\n"
        result += "📬 INBOUND BY CHANNEL\n"
        result += "═" * 45 + "\n"
        
        # Sort by count descending
        sorted_channels = sorted(metrics["channels_inbound"].items(), 
                                  key=lambda x: x[1], reverse=True)
        total_inbound = metrics["total_inbound"]
        
        for channel, count in sorted_channels:
            pct = (count * 100 // total_inbound) if total_inbound > 0 else 0
            result += f"  {channel}: {count:,} ({pct}%)\n"
        result += "\n"
    
    # Outbound by channel
    if metrics["channels_outbound"]:
        result += "═" * 45 + "\n"
        result += "📤 OUTBOUND BY CHANNEL\n"
        result += "═" * 45 + "\n"
        
        sorted_channels = sorted(metrics["channels_outbound"].items(), 
                                  key=lambda x: x[1], reverse=True)
        total_outbound = metrics["total_outbound"]
        
        for channel, count in sorted_channels:
            pct = (count * 100 // total_outbound) if total_outbound > 0 else 0
            result += f"  {channel}: {count:,} ({pct}%)\n"
        result += "\n"
    
    # Note about limitations
    if len(conversations) >= max_conversations:
        result += f"\n⚠️  Note: Limited to {max_conversations} conversations. Use max_conversations parameter for more.\n"
    
    return result


# Run the server in stdio mode only (for Claude Desktop)
if __name__ == "__main__":
    mcp.run()
