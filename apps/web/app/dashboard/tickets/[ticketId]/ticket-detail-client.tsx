"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";
import { ArrowLeft, Bot, MessageSquare, Save } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { addTicketMessage, draftTicketReply, getTicketDetail, updateTicket } from "@/lib/api";
import type { TicketDetail, TicketMessageRole, TicketPriority, TicketStatus } from "@/lib/types";

const statuses: TicketStatus[] = ["open", "pending", "resolved", "closed"];
const priorities: TicketPriority[] = ["low", "medium", "high", "urgent"];
const roles: TicketMessageRole[] = ["customer", "human", "agent"];

const roleTone = {
  customer: "blue",
  human: "green",
  agent: "amber",
} as const;

export function TicketDetailClient({ ticketId }: { ticketId: string }) {
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [status, setStatus] = useState<TicketStatus>("open");
  const [priority, setPriority] = useState<TicketPriority>("medium");
  const [messageRole, setMessageRole] = useState<TicketMessageRole>("human");
  const [message, setMessage] = useState("");
  const [draft, setDraft] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [isDrafting, setIsDrafting] = useState(false);

  async function loadTicket() {
    setError(null);
    try {
      const detail = await getTicketDetail(ticketId);
      setTicket(detail);
      setStatus(detail.status);
      setPriority(detail.priority);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load ticket");
    }
  }

  useEffect(() => {
    void loadTicket();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticketId]);

  async function handleUpdate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);
    try {
      await updateTicket(ticketId, { status, priority });
      await loadTicket();
    } catch (updateError) {
      setError(updateError instanceof Error ? updateError.message : "Failed to update ticket");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleAddMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!message.trim()) {
      return;
    }
    setError(null);
    try {
      await addTicketMessage(ticketId, { role: messageRole, content: message.trim() });
      setMessage("");
      await loadTicket();
    } catch (messageError) {
      setError(messageError instanceof Error ? messageError.message : "Failed to add message");
    }
  }

  async function handleDraftReply() {
    setIsDrafting(true);
    setError(null);
    try {
      const response = await draftTicketReply(ticketId, { tone: "professional" });
      setDraft(response.draft_reply);
    } catch (draftError) {
      setError(draftError instanceof Error ? draftError.message : "Failed to draft reply");
    } finally {
      setIsDrafting(false);
    }
  }

  if (error && !ticket) {
    return (
      <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
        {error}
      </div>
    );
  }

  if (!ticket) {
    return <p className="text-sm text-muted-foreground">Loading ticket</p>;
  }

  return (
    <div className="space-y-6">
      <Link href="/dashboard/tickets" className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" />
        Back to tickets
      </Link>

      {error ? (
        <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <section className="rounded-md border border-border bg-card p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-semibold">{ticket.title}</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              {ticket.customer_name} · {ticket.customer_email}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Badge tone={ticket.priority === "urgent" ? "red" : ticket.priority === "high" ? "amber" : "blue"}>{ticket.priority}</Badge>
            <Badge tone={ticket.status === "resolved" ? "green" : ticket.status === "pending" ? "amber" : "blue"}>{ticket.status}</Badge>
          </div>
        </div>
        <p className="mt-5 whitespace-pre-wrap rounded-md bg-muted p-4 text-sm leading-6 text-muted-foreground">
          {ticket.description}
        </p>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.72fr_1fr]">
        <div className="space-y-6">
          <form onSubmit={handleUpdate} className="rounded-md border border-border bg-card p-5 shadow-sm">
            <h3 className="text-base font-semibold">Ticket state</h3>
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="text-sm font-medium">Status</span>
                <select value={status} onChange={(event) => setStatus(event.target.value as TicketStatus)} className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary">
                  {statuses.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
              <label className="block">
                <span className="text-sm font-medium">Priority</span>
                <select value={priority} onChange={(event) => setPriority(event.target.value as TicketPriority)} className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary">
                  {priorities.map((item) => <option key={item} value={item}>{item}</option>)}
                </select>
              </label>
            </div>
            <button disabled={isSaving} className="mt-4 inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50">
              <Save className="h-4 w-4" />
              {isSaving ? "Saving" : "Save"}
            </button>
          </form>

          <div className="rounded-md border border-border bg-card p-5 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <h3 className="text-base font-semibold">AI draft</h3>
              <button onClick={() => void handleDraftReply()} disabled={isDrafting} className="inline-flex h-9 items-center gap-2 rounded-md border border-border bg-background px-3 text-sm font-medium disabled:opacity-50">
                <Bot className="h-4 w-4" />
                {isDrafting ? "Drafting" : "Draft reply"}
              </button>
            </div>
            <textarea value={draft} onChange={(event) => setDraft(event.target.value)} className="mt-4 min-h-56 w-full rounded-md border border-border bg-background px-3 py-2 text-sm leading-6 outline-none focus:border-primary" placeholder="AI draft will appear here" />
          </div>
        </div>

        <div className="rounded-md border border-border bg-card shadow-sm">
          <div className="border-b border-border px-5 py-4">
            <h3 className="text-base font-semibold">Messages</h3>
          </div>
          <div className="divide-y divide-border">
            {ticket.messages.map((item) => (
              <article key={item.id} className="px-5 py-4">
                <div className="mb-2 flex items-center justify-between gap-3">
                  <Badge tone={roleTone[item.role]}>{item.role}</Badge>
                  <span className="text-xs text-muted-foreground">
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="whitespace-pre-wrap text-sm leading-6 text-muted-foreground">{item.content}</p>
              </article>
            ))}
          </div>
          <form onSubmit={handleAddMessage} className="border-t border-border p-5">
            <div className="mb-3 flex items-center gap-3">
              <MessageSquare className="h-4 w-4 text-primary" />
              <span className="text-sm font-semibold">Add message</span>
            </div>
            <select value={messageRole} onChange={(event) => setMessageRole(event.target.value as TicketMessageRole)} className="mb-3 h-10 w-full rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary">
              {roles.map((role) => <option key={role} value={role}>{role}</option>)}
            </select>
            <textarea value={message} onChange={(event) => setMessage(event.target.value)} className="min-h-28 w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary" placeholder="Write a message" />
            <button className="mt-3 inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground">
              Add message
            </button>
          </form>
        </div>
      </section>
    </div>
  );
}
