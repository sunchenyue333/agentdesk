# AgentDesk API Spec

## Implemented

### `GET /health`

Returns service health and environment metadata.

```json
{
  "status": "ok",
  "service": "agentdesk-api",
  "environment": "development"
}
```

### `GET /workspaces`

Returns available workspaces. The demo workspace is created automatically if none exists.

### `GET /workspaces/demo`

Returns the `Acme SaaS Support` demo workspace.

### `GET /workspaces/{workspace_id}/documents`

Lists knowledge base documents for a workspace.

### `POST /workspaces/{workspace_id}/documents/upload`

Uploads and immediately processes a PDF, TXT, or Markdown file.

Multipart form fields:

- `file`: required
- `title`: optional

### `GET /documents/{document_id}`

Returns document metadata, raw text, and chunk count.

### `DELETE /documents/{document_id}`

Deletes a document and its chunks.

### `GET /documents/{document_id}/chunks`

Returns chunk previews for a document.

### `POST /workspaces/{workspace_id}/knowledge/search`

Searches document chunks with pgvector.

Request:

```json
{
  "query": "How long is the refund window?",
  "top_k": 5
}
```

Response:

```json
{
  "query": "How long is the refund window?",
  "chunks": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "document_title": "Refund Policy",
      "content": "Relevant chunk text",
      "score": 0.87
    }
  ]
}
```

### `GET /workspaces/{workspace_id}/tickets`

Lists support tickets for a workspace.

Optional query parameters:

- `status`: `open`, `pending`, `resolved`, or `closed`
- `priority`: `low`, `medium`, `high`, or `urgent`

### `POST /workspaces/{workspace_id}/tickets`

Creates a ticket and stores the initial customer message.

Request:

```json
{
  "customer_name": "Jane Customer",
  "customer_email": "jane@example.com",
  "title": "Customer cannot log in",
  "description": "I cannot log in after resetting my password.",
  "priority": "high"
}
```

### `GET /tickets/{ticket_id}`

Returns ticket details and message history.

### `PATCH /tickets/{ticket_id}`

Updates ticket fields such as `status`, `priority`, `title`, or `description`.

### `POST /tickets/{ticket_id}/messages`

Adds a ticket message.

Request:

```json
{
  "role": "human",
  "content": "Thanks, we are checking your account status."
}
```

### `POST /tickets/{ticket_id}/draft-reply`

Returns a deterministic reply draft placeholder.

Request:

```json
{
  "tone": "professional",
  "context": "Password reset emails expire after 30 minutes."
}
```

### `POST /workspaces/{workspace_id}/chat`

Runs the LangGraph support agent for a workspace. The agent classifies intent, retrieves knowledge-base context, drafts an answer, prepares tool calls when needed, marks risky responses for human review, and persists an agent run trace.

If `OPENAI_API_KEY` is not configured, the response is explicitly marked as `answer_mode: "mock"` and uses deterministic demo answer generation. Mock mode does not concatenate raw chunks; it filters retrieved evidence to sentences directly related to the user question.

Request:

```json
{
  "message": "What is the refund window?"
}
```

Response:

```json
{
  "answer": "Based on the available support knowledge...",
  "citations": [
    {
      "document_id": "uuid",
      "document_title": "Refund Policy",
      "chunk_id": "uuid",
      "heading": "Billing SOP > Refund Policy",
      "quote": "Relevant source excerpt"
    }
  ],
  "confidence": "medium",
  "needs_human_review": true,
  "answer_mode": "mock",
  "agent_run_id": "uuid",
  "structured_steps": [
    "判断意图：密码重置问题",
    "检索知识库：找到账户设置相关资料",
    "生成回答：基于密码重置 SOP",
    "风险等级：低",
    "不需要人工审批"
  ],
  "retrieved_chunks": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "document_title": "Login SOP",
      "heading": "登录与密码问题处理 SOP > 用户忘记密码",
      "heading_path": ["登录与密码问题处理 SOP", "用户忘记密码"],
      "content": "Relevant chunk text",
      "score": 12.7
    }
  ],
  "tool_calls": [
    {
      "tool_name": "create_ticket",
      "tool_args_json": {
        "title": "Customer issue",
        "priority": "medium"
      },
      "tool_result_json": {
        "status": "pending_approval"
      },
      "status": "completed"
    }
  ],
  "latency_ms": 20
}
```

Tool calls are prepared and traced by the agent. Actions that affect customer data, such as creating a ticket from chat, are held for human approval before execution.

### `GET /workspaces/{workspace_id}/approvals`

Lists human approval tasks for a workspace.

Optional query parameters:

- `status`: `pending`, `approved`, `edited`, or `rejected`

Response:

```json
{
  "approvals": [
    {
      "id": "uuid",
      "workspace_id": "uuid",
      "agent_run_id": "uuid",
      "action_type": "create_ticket",
      "proposed_action_json": {
        "selected_tool": "create_ticket",
        "tool_args": {
          "title": "Customer billing issue",
          "priority": "medium"
        }
      },
      "status": "pending",
      "human_feedback": null,
      "agent_run": {
        "id": "uuid",
        "input": "Please create a ticket...",
        "final_output": "Based on the available support knowledge...",
        "status": "waiting_for_approval",
        "model": "local-deterministic-agent",
        "latency_ms": 20
      }
    }
  ]
}
```

### `GET /approvals/{approval_id}`

Returns one approval task with the associated agent run summary.

### `POST /approvals/{approval_id}/approve`

Approves a pending action. If the approval is for `create_ticket`, the backend executes the proposed ticket creation and updates the traced tool call result.

Request:

```json
{
  "human_feedback": "Looks good.",
  "edited_action_json": {
    "selected_tool": "create_ticket",
    "tool_args": {
      "customer_name": "Demo Customer",
      "customer_email": "customer@example.com",
      "title": "Customer billing issue",
      "description": "Customer cannot access billing.",
      "priority": "high"
    }
  }
}
```

`edited_action_json` is optional. If present, the approval status becomes `edited`; otherwise it becomes `approved`.

Response:

```json
{
  "approval_id": "uuid",
  "status": "approved",
  "executed_result_json": {
    "status": "executed",
    "ticket_id": "uuid"
  }
}
```

### `POST /approvals/{approval_id}/reject`

Rejects a pending action without executing side effects.

Request:

```json
{
  "human_feedback": "Refund request needs a senior support review."
}
```

Response:

```json
{
  "approval_id": "uuid",
  "status": "rejected",
  "executed_result_json": null
}
```

## Persisted Trace Tables

Phase 5 and Phase 6 write LangGraph execution and approval data to:

- `agent_runs`: one row per chat request, including status, final output, latency, model label, and token estimates
- `agent_steps`: structured step timeline for classification, retrieval, action choice, risk checks, drafting, approval checks, and final response
- `tool_calls`: prepared tool invocations and their result metadata
- `human_approvals`: pending and reviewed human approval tasks, proposed action JSON, and reviewer feedback

Example trace rows:

```json
{
  "agent_run": {
    "status": "waiting_for_approval",
    "final_output": {
      "answer": "Based on the available support knowledge..."
    }
  },
  "tool_call": {
    "tool_name": "create_ticket",
    "tool_result_json": {
      "status": "pending_approval"
    }
  }
}
```

## Planned Endpoints

The rest of the API will be implemented by phase: auth, agent run explorer endpoints, evals, and settings.
