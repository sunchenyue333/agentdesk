export type NavItem = {
  label: string;
  href: string;
};

export type Workspace = {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type DocumentStatus = "uploaded" | "processing" | "ready" | "failed";

export type KnowledgeDocument = {
  id: string;
  workspace_id: string;
  title: string;
  filename: string;
  file_type: string;
  status: DocumentStatus;
  created_at: string;
  updated_at: string;
};

export type KnowledgeDocumentDetail = KnowledgeDocument & {
  raw_text: string | null;
  chunk_count: number;
};

export type DocumentChunk = {
  id: string;
  document_id: string;
  workspace_id: string;
  chunk_index: number;
  content: string;
  token_count: number | null;
  metadata_: Record<string, unknown> | null;
  created_at: string;
};

export type KnowledgeSearchChunk = {
  chunk_id: string;
  document_id: string;
  document_title: string;
  heading: string | null;
  heading_path: string[];
  content: string;
  score: number;
};

export type KnowledgeSearchResponse = {
  query: string;
  chunks: KnowledgeSearchChunk[];
};

export type TicketStatus = "open" | "pending" | "resolved" | "closed";
export type TicketPriority = "low" | "medium" | "high" | "urgent";
export type TicketMessageRole = "customer" | "agent" | "human";

export type SupportTicket = {
  id: string;
  workspace_id: string;
  customer_name: string;
  customer_email: string;
  title: string;
  description: string;
  status: TicketStatus;
  priority: TicketPriority;
  created_at: string;
  updated_at: string;
};

export type TicketMessage = {
  id: string;
  ticket_id: string;
  role: TicketMessageRole;
  content: string;
  created_at: string;
};

export type TicketDetail = SupportTicket & {
  messages: TicketMessage[];
};

export type ChatCitation = {
  document_id: string;
  document_title: string;
  chunk_id: string;
  heading: string;
  quote: string;
};

export type ChatStep = {
  title: string;
  detail: string;
};

export type ChatToolCall = {
  tool_name: string;
  tool_args_json: Record<string, unknown> | null;
  tool_result_json: Record<string, unknown> | null;
  status: string;
};

export type ChatRetrievedChunk = {
  chunk_id: string;
  document_id: string;
  document_title: string;
  heading: string | null;
  heading_path: string[];
  content: string;
  score: number;
};

export type ChatResponse = {
  answer: string;
  citations: ChatCitation[];
  confidence: "high" | "medium" | "low" | string;
  needs_human_review: boolean;
  answer_mode: "mock" | "llm" | string;
  agent_run_id: string;
  structured_steps: string[];
  retrieved_chunks: ChatRetrievedChunk[];
  tool_calls: ChatToolCall[];
  latency_ms: number | null;
};

export type ApprovalStatus = "pending" | "approved" | "rejected" | "edited";

export type ApprovalAgentRun = {
  id: string;
  input: string;
  final_output: string | null;
  status: string;
  model: string | null;
  latency_ms: number | null;
  created_at: string;
  updated_at: string;
};

export type HumanApproval = {
  id: string;
  workspace_id: string;
  agent_run_id: string;
  action_type: string;
  proposed_action_json: Record<string, unknown>;
  status: ApprovalStatus;
  human_feedback: string | null;
  created_at: string;
  updated_at: string;
  agent_run: ApprovalAgentRun;
};

export type ApprovalListResponse = {
  approvals: HumanApproval[];
};

export type ApprovalActionResponse = {
  approval_id: string;
  status: ApprovalStatus;
  executed_result_json: Record<string, unknown> | null;
};
