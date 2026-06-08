"use client";

import Link from "next/link";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { Filter, Plus, RefreshCw, Ticket } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { createTicket, getDemoWorkspace, getTickets } from "@/lib/api";
import type { SupportTicket, TicketPriority, TicketStatus, Workspace } from "@/lib/types";

const statuses: Array<"" | TicketStatus> = ["", "open", "pending", "resolved", "closed"];
const priorities: Array<"" | TicketPriority> = ["", "low", "medium", "high", "urgent"];

const statusTone = {
  open: "blue",
  pending: "amber",
  resolved: "green",
  closed: "neutral",
} as const;

const priorityTone = {
  low: "neutral",
  medium: "blue",
  high: "amber",
  urgent: "red",
} as const;

export function TicketsClient() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [status, setStatus] = useState("");
  const [priority, setPriority] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  const openCount = useMemo(() => tickets.filter((ticket) => ticket.status === "open").length, [tickets]);
  const urgentCount = useMemo(
    () => tickets.filter((ticket) => ticket.priority === "urgent").length,
    [tickets]
  );

  async function loadTickets(nextWorkspace = workspace) {
    setError(null);
    setIsLoading(true);
    try {
      const activeWorkspace = nextWorkspace ?? (await getDemoWorkspace());
      setWorkspace(activeWorkspace);
      setTickets(await getTickets(activeWorkspace.id, { status, priority }));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load tickets");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadTickets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function applyFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadTickets();
  }

  async function handleCreate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    if (!workspace) {
      return;
    }

    const formData = new FormData(form);
    setIsCreating(true);
    setError(null);
    try {
      await createTicket(workspace.id, {
        customer_name: String(formData.get("customer_name") ?? ""),
        customer_email: String(formData.get("customer_email") ?? ""),
        title: String(formData.get("title") ?? ""),
        description: String(formData.get("description") ?? ""),
        priority: String(formData.get("priority") ?? "medium"),
      });
      form.reset();
      await loadTickets();
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Failed to create ticket");
    } finally {
      setIsCreating(false);
    }
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold">Tickets</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Create, filter, and manage customer support requests.
          </p>
        </div>
        <button
          onClick={() => void loadTickets()}
          className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-card px-3 text-sm font-medium"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </section>

      {error ? (
        <div className="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
          {error}
        </div>
      ) : null}

      <section className="grid gap-4 md:grid-cols-3">
        <article className="rounded-md border border-border bg-card p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">Workspace</p>
          <p className="mt-2 text-lg font-semibold">{workspace?.name ?? "Loading"}</p>
        </article>
        <article className="rounded-md border border-border bg-card p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">Open tickets</p>
          <p className="mt-2 text-3xl font-semibold">{openCount}</p>
        </article>
        <article className="rounded-md border border-border bg-card p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">Urgent</p>
          <p className="mt-2 text-3xl font-semibold">{urgentCount}</p>
        </article>
      </section>

      <section className="grid gap-6 xl:grid-cols-[0.78fr_1fr]">
        <form onSubmit={handleCreate} className="rounded-md border border-border bg-card p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <Plus className="h-5 w-5 text-primary" />
            <h3 className="text-base font-semibold">Create ticket</h3>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <input name="customer_name" required placeholder="Customer name" className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary" />
            <input name="customer_email" required type="email" placeholder="customer@example.com" className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary" />
            <input name="title" required placeholder="Login issue" className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary md:col-span-2" />
            <select name="priority" defaultValue="medium" className="h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary md:col-span-2">
              {priorities.filter(Boolean).map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
            <textarea name="description" required placeholder="Describe the customer issue" className="min-h-28 rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary md:col-span-2" />
          </div>
          <button disabled={isCreating} className="mt-4 inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50">
            <Ticket className="h-4 w-4" />
            {isCreating ? "Creating" : "Create ticket"}
          </button>
        </form>

        <form onSubmit={applyFilters} className="rounded-md border border-border bg-card p-5 shadow-sm">
          <div className="mb-5 flex items-center gap-3">
            <Filter className="h-5 w-5 text-primary" />
            <h3 className="text-base font-semibold">Filters</h3>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <label className="block">
              <span className="text-sm font-medium">Status</span>
              <select value={status} onChange={(event) => setStatus(event.target.value)} className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary">
                {statuses.map((item) => (
                  <option key={item || "all"} value={item}>{item || "all"}</option>
                ))}
              </select>
            </label>
            <label className="block">
              <span className="text-sm font-medium">Priority</span>
              <select value={priority} onChange={(event) => setPriority(event.target.value)} className="mt-2 h-10 w-full rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary">
                {priorities.map((item) => (
                  <option key={item || "all"} value={item}>{item || "all"}</option>
                ))}
              </select>
            </label>
          </div>
          <button className="mt-4 inline-flex h-10 items-center gap-2 rounded-md border border-border bg-background px-4 text-sm font-semibold">
            Apply filters
          </button>
        </form>
      </section>

      <section className="rounded-md border border-border bg-card shadow-sm">
        <div className="border-b border-border px-5 py-4">
          <h3 className="text-base font-semibold">Ticket queue</h3>
        </div>
        {isLoading ? (
          <p className="px-5 py-6 text-sm text-muted-foreground">Loading tickets</p>
        ) : tickets.length ? (
          <div className="divide-y divide-border">
            {tickets.map((ticket) => (
              <Link key={ticket.id} href={`/dashboard/tickets/${ticket.id}`} className="block px-5 py-4 hover:bg-muted/60">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold">{ticket.title}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {ticket.customer_name} · {ticket.customer_email}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge tone={priorityTone[ticket.priority]}>{ticket.priority}</Badge>
                    <Badge tone={statusTone[ticket.status]}>{ticket.status}</Badge>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="px-5 py-6 text-sm text-muted-foreground">
            No tickets match the current filters.
          </p>
        )}
      </section>
    </div>
  );
}
