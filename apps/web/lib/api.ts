export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/health`, { cache: "no-store" });

  if (!response.ok) {
    throw new Error("Unable to reach AgentDesk API");
  }

  return response.json() as Promise<{
    status: string;
    service: string;
    environment: string;
  }>;
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function getDemoWorkspace() {
  return apiFetch<import("@/lib/types").Workspace>("/workspaces/demo");
}

export async function getDocuments(workspaceId: string) {
  return apiFetch<import("@/lib/types").KnowledgeDocument[]>(`/workspaces/${workspaceId}/documents`);
}

export async function uploadDocument(workspaceId: string, formData: FormData) {
  return apiFetch<import("@/lib/types").KnowledgeDocument>(
    `/workspaces/${workspaceId}/documents/upload`,
    {
      method: "POST",
      body: formData,
    }
  );
}

export async function deleteDocument(documentId: string) {
  return apiFetch<void>(`/documents/${documentId}`, { method: "DELETE" });
}

export async function getDocumentDetail(documentId: string) {
  return apiFetch<import("@/lib/types").KnowledgeDocumentDetail>(`/documents/${documentId}`);
}

export async function getDocumentChunks(documentId: string) {
  return apiFetch<import("@/lib/types").DocumentChunk[]>(`/documents/${documentId}/chunks`);
}

export async function searchKnowledge(workspaceId: string, query: string, topK = 5) {
  return apiFetch<import("@/lib/types").KnowledgeSearchResponse>(
    `/workspaces/${workspaceId}/knowledge/search`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, top_k: topK }),
    }
  );
}

export async function getTickets(workspaceId: string, filters?: { status?: string; priority?: string }) {
  const params = new URLSearchParams();
  if (filters?.status) {
    params.set("status", filters.status);
  }
  if (filters?.priority) {
    params.set("priority", filters.priority);
  }
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return apiFetch<import("@/lib/types").SupportTicket[]>(`/workspaces/${workspaceId}/tickets${suffix}`);
}

export async function createTicket(
  workspaceId: string,
  payload: {
    customer_name: string;
    customer_email: string;
    title: string;
    description: string;
    priority: string;
  }
) {
  return apiFetch<import("@/lib/types").SupportTicket>(`/workspaces/${workspaceId}/tickets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function getTicketDetail(ticketId: string) {
  return apiFetch<import("@/lib/types").TicketDetail>(`/tickets/${ticketId}`);
}

export async function updateTicket(
  ticketId: string,
  payload: Partial<Pick<import("@/lib/types").SupportTicket, "status" | "priority" | "title" | "description">>
) {
  return apiFetch<import("@/lib/types").SupportTicket>(`/tickets/${ticketId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function addTicketMessage(
  ticketId: string,
  payload: { role: import("@/lib/types").TicketMessageRole; content: string }
) {
  return apiFetch<import("@/lib/types").TicketMessage>(`/tickets/${ticketId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function draftTicketReply(ticketId: string, payload: { tone: string; context?: string }) {
  return apiFetch<{ draft_reply: string }>(`/tickets/${ticketId}/draft-reply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function sendChatMessage(workspaceId: string, message: string) {
  return apiFetch<import("@/lib/types").ChatResponse>(`/workspaces/${workspaceId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
}

export async function getApprovals(workspaceId: string, status?: import("@/lib/types").ApprovalStatus | "all") {
  const suffix = status && status !== "all" ? `?status=${status}` : "";
  return apiFetch<import("@/lib/types").ApprovalListResponse>(`/workspaces/${workspaceId}/approvals${suffix}`);
}

export async function approveApproval(
  approvalId: string,
  payload: { human_feedback?: string; edited_action_json?: Record<string, unknown> }
) {
  return apiFetch<import("@/lib/types").ApprovalActionResponse>(`/approvals/${approvalId}/approve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function rejectApproval(approvalId: string, payload: { human_feedback?: string }) {
  return apiFetch<import("@/lib/types").ApprovalActionResponse>(`/approvals/${approvalId}/reject`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
