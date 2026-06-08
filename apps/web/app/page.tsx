import Link from "next/link";
import {
  Activity,
  ArrowRight,
  Bot,
  ClipboardCheck,
  Database,
  FileSearch,
  GitBranch,
  TicketCheck
} from "lucide-react";

const features = [
  { title: "RAG Knowledge Base", icon: Database, copy: "Upload docs, chunk content, retrieve context, and cite sources." },
  { title: "LangGraph Workflows", icon: GitBranch, copy: "Model the support agent as a multi-step stateful workflow." },
  { title: "Human Approval", icon: ClipboardCheck, copy: "Route high-risk actions into a review queue before execution." },
  { title: "Ticket Automation", icon: TicketCheck, copy: "Create tickets and draft support replies from agent context." },
  { title: "Agent Tracing", icon: Activity, copy: "Capture runs, steps, tool calls, latency, cost, and errors." },
  { title: "RAG Evaluation", icon: FileSearch, copy: "Track faithfulness, relevancy, context precision, and recall." }
];

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-background">
      <section className="border-b border-border bg-card">
        <div className="mx-auto flex min-h-[78vh] max-w-7xl flex-col justify-between px-6 py-8 lg:px-8">
          <nav className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-primary-foreground">
                <Bot className="h-5 w-5" />
              </span>
              <span className="text-lg font-semibold">AgentDesk</span>
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex h-10 items-center gap-2 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground"
            >
              Enter Demo Dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
          </nav>

          <div className="grid gap-12 py-16 lg:grid-cols-[1fr_0.82fr] lg:items-end">
            <div className="max-w-3xl">
              <p className="mb-5 inline-flex rounded-md bg-amber-50 px-3 py-1 text-sm font-medium text-amber-800">
                Open-source AI Support Agent Platform
              </p>
              <h1 className="text-5xl font-semibold leading-tight text-foreground md:text-6xl">
                AgentDesk
              </h1>
              <p className="mt-6 max-w-2xl text-lg leading-8 text-muted-foreground">
                A production-style AI support and operations workspace with RAG, tool calling,
                human-in-the-loop approvals, observability, and evaluations.
              </p>
            </div>

            <div className="rounded-md border border-border bg-background p-4 shadow-soft">
              <div className="mb-4 flex items-center justify-between border-b border-border pb-3">
                <span className="text-sm font-semibold">Live workflow preview</span>
                <span className="rounded-md bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">
                  Phase 1 shell
                </span>
              </div>
              <div className="space-y-3 text-sm">
                {["Intent classified", "Knowledge retrieval queued", "Draft answer generated", "Approval rule checked"].map(
                  (step, index) => (
                    <div key={step} className="flex items-center gap-3 rounded-md border border-border bg-card p-3">
                      <span className="flex h-7 w-7 items-center justify-center rounded-md bg-muted text-xs font-semibold">
                        {index + 1}
                      </span>
                      <span>{step}</span>
                    </div>
                  )
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-6 py-12 lg:px-8">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <article key={feature.title} className="rounded-md border border-border bg-card p-5 shadow-sm">
                <Icon className="mb-4 h-5 w-5 text-primary" />
                <h2 className="text-base font-semibold">{feature.title}</h2>
                <p className="mt-2 text-sm leading-6 text-muted-foreground">{feature.copy}</p>
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}

