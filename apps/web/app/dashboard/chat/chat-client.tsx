"use client";

import { FormEvent, useEffect, useState } from "react";
import { Bot, Clock, Send, UserRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { getDemoWorkspace, sendChatMessage } from "@/lib/api";
import type { ChatResponse, Workspace } from "@/lib/types";

type ChatTurn = {
  id: string;
  message: string;
  response: ChatResponse;
};

export function ChatClient() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [message, setMessage] = useState("What is the refund window?");
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    async function loadWorkspace() {
      try {
        setWorkspace(await getDemoWorkspace());
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : "Failed to load workspace");
      }
    }
    void loadWorkspace();
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!workspace || !message.trim()) {
      return;
    }
    const userMessage = message.trim();
    setIsSending(true);
    setError(null);
    try {
      const response = await sendChatMessage(workspace.id, userMessage);
      setTurns((items) => [
        {
          id: response.agent_run_id,
          message: userMessage,
          response,
        },
        ...items,
      ]);
      setMessage("");
    } catch (chatError) {
      setError(chatError instanceof Error ? chatError.message : "Chat request failed");
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold">Agent Chat</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Ask the support agent and inspect citations, workflow steps, and tool activity.
          </p>
        </div>
        <Badge tone="blue">{workspace?.name ?? "Loading workspace"}</Badge>
      </section>

      {error ? (
        <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <form onSubmit={handleSubmit} className="rounded-md border border-border bg-card p-5 shadow-sm">
        <label className="block">
          <span className="text-sm font-medium">Message</span>
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            className="mt-2 min-h-28 w-full rounded-md border border-border bg-background px-3 py-2 text-sm leading-6 outline-none focus:border-primary"
            placeholder="Ask about refund policy, password reset, pricing, or a customer issue"
          />
        </label>
        <button
          disabled={!workspace || !message.trim() || isSending}
          className="mt-4 inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
          {isSending ? "Running agent" : "Send"}
        </button>
      </form>

      <section className="space-y-4">
        {turns.map((turn) => (
          <article key={turn.id} className="rounded-md border border-border bg-card shadow-sm">
            <div className="border-b border-border p-5">
              <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                <UserRound className="h-4 w-4 text-primary" />
                User
              </div>
              <p className="whitespace-pre-wrap text-sm leading-6 text-muted-foreground">{turn.message}</p>
            </div>
            <div className="p-5">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <Bot className="h-4 w-4 text-primary" />
                  Agent
                </div>
                <div className="flex items-center gap-2">
                  <Badge tone={turn.response.needs_human_review ? "amber" : "green"}>
                    {turn.response.needs_human_review ? "human review" : "auto-ready"}
                  </Badge>
                  <Badge tone="blue">{turn.response.confidence}</Badge>
                  <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {turn.response.latency_ms ?? 0}ms
                  </span>
                </div>
              </div>
              <p className="whitespace-pre-wrap text-sm leading-6 text-foreground">{turn.response.answer}</p>

              <div className="mt-5 grid gap-4 xl:grid-cols-3">
                <div className="rounded-md border border-border bg-background p-4">
                  <h3 className="text-sm font-semibold">Citations</h3>
                  <div className="mt-3 space-y-3">
                    {turn.response.citations.length ? turn.response.citations.map((citation) => (
                      <div key={citation.chunk_id} className="text-sm">
                        <p className="font-medium text-primary">{citation.document_title}</p>
                        <p className="mt-1 line-clamp-4 text-xs leading-5 text-muted-foreground">{citation.quote}</p>
                      </div>
                    )) : (
                      <p className="text-xs text-muted-foreground">No citations returned.</p>
                    )}
                  </div>
                </div>

                <div className="rounded-md border border-border bg-background p-4">
                  <h3 className="text-sm font-semibold">Structured Steps</h3>
                  <ol className="mt-3 space-y-2">
                    {turn.response.steps.map((step, index) => (
                      <li key={`${step.title}-${index}`} className="text-sm">
                        <span className="font-medium">{index + 1}. {step.title}</span>
                        <p className="mt-1 text-xs text-muted-foreground">{step.detail}</p>
                      </li>
                    ))}
                  </ol>
                </div>

                <div className="rounded-md border border-border bg-background p-4">
                  <h3 className="text-sm font-semibold">Tool Calls</h3>
                  <div className="mt-3 space-y-3">
                    {turn.response.tool_calls.length ? turn.response.tool_calls.map((toolCall, index) => (
                      <div key={`${toolCall.tool_name}-${index}`} className="text-xs text-muted-foreground">
                        <div className="mb-1 flex items-center justify-between gap-2">
                          <span className="font-medium text-foreground">{toolCall.tool_name}</span>
                          <Badge tone="green">{toolCall.status}</Badge>
                        </div>
                        <pre className="max-h-32 overflow-auto rounded-md bg-muted p-2">
                          {JSON.stringify(toolCall.tool_result_json, null, 2)}
                        </pre>
                      </div>
                    )) : (
                      <p className="text-xs text-muted-foreground">No tool calls for this run.</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </article>
        ))}
        {!turns.length ? (
          <p className="rounded-md border border-border bg-card px-5 py-6 text-sm text-muted-foreground shadow-sm">
            Agent responses will appear here. Upload knowledge base documents first for better citations.
          </p>
        ) : null}
      </section>
    </div>
  );
}
