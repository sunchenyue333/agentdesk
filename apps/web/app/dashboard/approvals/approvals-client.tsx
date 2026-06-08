"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { CheckCircle2, ClipboardCheck, RefreshCw, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { approveApproval, getApprovals, getDemoWorkspace, rejectApproval } from "@/lib/api";
import type { ApprovalStatus, HumanApproval, Workspace } from "@/lib/types";

const statusOptions: Array<ApprovalStatus | "all"> = ["pending", "approved", "edited", "rejected", "all"];

const statusTone = {
  pending: "amber",
  approved: "green",
  edited: "blue",
  rejected: "red",
} as const;

function prettyJson(value: unknown) {
  return JSON.stringify(value, null, 2);
}

function textFromAction(approval: HumanApproval, key: string) {
  const value = approval.proposed_action_json[key];
  return typeof value === "string" ? value : "";
}

export function ApprovalsClient() {
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [approvals, setApprovals] = useState<HumanApproval[]>([]);
  const [status, setStatus] = useState<ApprovalStatus | "all">("pending");
  const [feedbackById, setFeedbackById] = useState<Record<string, string>>({});
  const [draftById, setDraftById] = useState<Record<string, string>>({});
  const [busyId, setBusyId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const pendingCount = useMemo(
    () => approvals.filter((approval) => approval.status === "pending").length,
    [approvals]
  );

  async function loadApprovals(nextWorkspace = workspace, nextStatus = status) {
    setIsLoading(true);
    setError(null);
    try {
      const activeWorkspace = nextWorkspace ?? (await getDemoWorkspace());
      setWorkspace(activeWorkspace);
      const response = await getApprovals(activeWorkspace.id, nextStatus);
      setApprovals(response.approvals);
      setDraftById((current) => {
        const next = { ...current };
        for (const approval of response.approvals) {
          if (!next[approval.id]) {
            next[approval.id] = prettyJson(approval.proposed_action_json);
          }
        }
        return next;
      });
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Failed to load approvals");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadApprovals();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function applyStatus(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await loadApprovals(workspace, status);
  }

  async function handleApprove(approval: HumanApproval) {
    setBusyId(approval.id);
    setError(null);
    try {
      const editedActionJson = JSON.parse(draftById[approval.id] ?? "{}") as Record<string, unknown>;
      const changed = prettyJson(editedActionJson) !== prettyJson(approval.proposed_action_json);
      await approveApproval(approval.id, {
        human_feedback: feedbackById[approval.id],
        edited_action_json: changed ? editedActionJson : undefined,
      });
      await loadApprovals();
    } catch (approveError) {
      setError(approveError instanceof Error ? approveError.message : "Approval failed");
    } finally {
      setBusyId(null);
    }
  }

  async function handleReject(approval: HumanApproval) {
    setBusyId(approval.id);
    setError(null);
    try {
      await rejectApproval(approval.id, { human_feedback: feedbackById[approval.id] });
      await loadApprovals();
    } catch (rejectError) {
      setError(rejectError instanceof Error ? rejectError.message : "Reject failed");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-6">
      <section className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold">Approvals</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Review high-risk answers and proposed tool actions before they affect customers.
          </p>
        </div>
        <button
          onClick={() => void loadApprovals()}
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
          <p className="text-sm text-muted-foreground">Visible approvals</p>
          <p className="mt-2 text-3xl font-semibold">{approvals.length}</p>
        </article>
        <article className="rounded-md border border-border bg-card p-4 shadow-sm">
          <p className="text-sm text-muted-foreground">Pending in view</p>
          <p className="mt-2 text-3xl font-semibold">{pendingCount}</p>
        </article>
      </section>

      <form onSubmit={applyStatus} className="flex flex-wrap items-end gap-3 rounded-md border border-border bg-card p-4 shadow-sm">
        <label className="block">
          <span className="text-sm font-medium">Status</span>
          <select
            value={status}
            onChange={(event) => setStatus(event.target.value as ApprovalStatus | "all")}
            className="mt-2 h-10 rounded-md border border-border bg-background px-3 text-sm outline-none focus:border-primary"
          >
            {statusOptions.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </label>
        <button className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-background px-4 text-sm font-semibold">
          <ClipboardCheck className="h-4 w-4" />
          Apply
        </button>
      </form>

      <section className="space-y-4">
        {isLoading ? (
          <p className="rounded-md border border-border bg-card px-5 py-6 text-sm text-muted-foreground shadow-sm">
            Loading approvals
          </p>
        ) : approvals.length ? approvals.map((approval) => (
          <article key={approval.id} className="rounded-md border border-border bg-card shadow-sm">
            <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border px-5 py-4">
              <div className="min-w-0">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <Badge tone={statusTone[approval.status]}>{approval.status}</Badge>
                  <Badge tone="blue">{approval.action_type}</Badge>
                  <Badge tone={textFromAction(approval, "risk_level") === "medium" ? "amber" : "neutral"}>
                    risk: {textFromAction(approval, "risk_level") || "low"}
                  </Badge>
                </div>
                <p className="truncate text-sm font-semibold">{approval.agent_run.input}</p>
                <p className="mt-1 text-xs text-muted-foreground">
                  Run {approval.agent_run_id} · {approval.agent_run.latency_ms ?? 0}ms
                </p>
              </div>
            </div>

            <div className="grid gap-5 p-5 xl:grid-cols-[1fr_0.82fr]">
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-semibold">Agent answer</h3>
                  <p className="mt-2 max-h-56 overflow-auto whitespace-pre-wrap rounded-md border border-border bg-background p-3 text-sm leading-6 text-muted-foreground">
                    {approval.agent_run.final_output ?? "No final output recorded."}
                  </p>
                </div>
                <label className="block">
                  <span className="text-sm font-semibold">Proposed action JSON</span>
                  <textarea
                    value={draftById[approval.id] ?? prettyJson(approval.proposed_action_json)}
                    onChange={(event) => setDraftById((items) => ({ ...items, [approval.id]: event.target.value }))}
                    disabled={approval.status !== "pending"}
                    className="mt-2 min-h-72 w-full rounded-md border border-border bg-background px-3 py-2 font-mono text-xs leading-5 outline-none focus:border-primary disabled:opacity-70"
                  />
                </label>
              </div>

              <div className="space-y-4">
                <label className="block">
                  <span className="text-sm font-semibold">Human feedback</span>
                  <textarea
                    value={feedbackById[approval.id] ?? approval.human_feedback ?? ""}
                    onChange={(event) => setFeedbackById((items) => ({ ...items, [approval.id]: event.target.value }))}
                    disabled={approval.status !== "pending"}
                    placeholder="Reason, edits, or customer-facing review notes"
                    className="mt-2 min-h-36 w-full rounded-md border border-border bg-background px-3 py-2 text-sm leading-6 outline-none focus:border-primary disabled:opacity-70"
                  />
                </label>

                <div className="rounded-md border border-border bg-background p-4">
                  <h3 className="text-sm font-semibold">Action summary</h3>
                  <dl className="mt-3 space-y-2 text-sm">
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted-foreground">Tool</dt>
                      <dd className="font-medium">{textFromAction(approval, "selected_tool") || "send answer"}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-muted-foreground">Confidence</dt>
                      <dd className="font-medium">{textFromAction(approval, "confidence") || "unknown"}</dd>
                    </div>
                  </dl>
                </div>

                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => void handleApprove(approval)}
                    disabled={approval.status !== "pending" || busyId === approval.id}
                    className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground disabled:opacity-50"
                  >
                    <CheckCircle2 className="h-4 w-4" />
                    {busyId === approval.id ? "Working" : "Approve"}
                  </button>
                  <button
                    onClick={() => void handleReject(approval)}
                    disabled={approval.status !== "pending" || busyId === approval.id}
                    className="inline-flex h-10 items-center gap-2 rounded-md border border-border bg-background px-4 text-sm font-semibold disabled:opacity-50"
                  >
                    <XCircle className="h-4 w-4" />
                    Reject
                  </button>
                </div>
              </div>
            </div>
          </article>
        )) : (
          <p className="rounded-md border border-border bg-card px-5 py-6 text-sm text-muted-foreground shadow-sm">
            No approvals match this status. Create a chat request that needs human review to populate the queue.
          </p>
        )}
      </section>
    </div>
  );
}
