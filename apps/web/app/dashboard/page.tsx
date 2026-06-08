import { Badge } from "@/components/ui/badge";

const metrics = [
  { label: "Documents", value: "Live", detail: "Upload, chunk, embed, and search" },
  { label: "Tickets", value: "Live", detail: "Create, filter, update, and message" },
  { label: "Approvals", value: "Live", detail: "Review, approve, edit, or reject" },
  { label: "Agent runs", value: "Live", detail: "LangGraph chat with persisted traces" },
  { label: "Latest eval score", value: "-", detail: "Evaluation arrives in Phase 8" }
];

const roadmap = [
  ["Phase 3", "Knowledge base upload, chunking, embeddings, pgvector search", "Done"],
  ["Phase 4", "Support ticket system", "Done"],
  ["Phase 5", "LangGraph support agent and chat endpoint", "Done"],
  ["Phase 6", "Human approval queue and action execution", "Done"],
  ["Phase 7", "Agent run explorer", "Next"]
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <section>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-semibold">Dashboard</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Production-style AI support operations workspace through Phase 6.
            </p>
          </div>
          <Badge tone="green">Phase 6 ready</Badge>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          {metrics.map((metric) => (
            <article key={metric.label} className="rounded-md border border-border bg-card p-4 shadow-sm">
              <p className="text-sm text-muted-foreground">{metric.label}</p>
              <p className="mt-3 text-3xl font-semibold">{metric.value}</p>
              <p className="mt-2 text-xs leading-5 text-muted-foreground">{metric.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.72fr]">
        <div className="rounded-md border border-border bg-card p-5 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-base font-semibold">Implementation Roadmap</h3>
            <Badge tone="amber">Strict phased build</Badge>
          </div>
          <div className="overflow-hidden rounded-md border border-border">
            <table className="w-full text-left text-sm">
              <thead className="bg-muted text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">Phase</th>
                  <th className="px-4 py-3 font-medium">Scope</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {roadmap.map(([phase, scope, status]) => (
                  <tr key={phase}>
                    <td className="px-4 py-3 font-medium">{phase}</td>
                    <td className="px-4 py-3 text-muted-foreground">{scope}</td>
                    <td className="px-4 py-3">
                      <Badge tone={status === "Next" ? "blue" : "green"}>{status}</Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-md border border-border bg-card p-5 shadow-sm">
          <h3 className="text-base font-semibold">Demo Workspace</h3>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Acme SaaS Support will become the default seed workspace with refund policy, pricing FAQ,
            account setup, troubleshooting, security docs, tickets, and eval cases.
          </p>
          <div className="mt-5 space-y-2">
            {["PostgreSQL + pgvector", "Redis", "FastAPI", "Next.js App Router"].map((item) => (
              <div key={item} className="flex items-center justify-between rounded-md bg-muted px-3 py-2 text-sm">
                <span>{item}</span>
                <Badge tone="green">Configured</Badge>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
