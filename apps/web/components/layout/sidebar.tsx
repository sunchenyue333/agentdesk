import Link from "next/link";
import {
  Activity,
  Bot,
  ClipboardCheck,
  Gauge,
  MessageSquare,
  Settings,
  ShieldCheck,
  Ticket,
  UploadCloud
} from "lucide-react";

const navItems = [
  { label: "Dashboard", href: "/dashboard", icon: Gauge },
  { label: "Knowledge Base", href: "/dashboard/knowledge-base", icon: UploadCloud },
  { label: "Chat", href: "/dashboard/chat", icon: MessageSquare },
  { label: "Tickets", href: "/dashboard/tickets", icon: Ticket },
  { label: "Approvals", href: "/dashboard/approvals", icon: ClipboardCheck },
  { label: "Agent Runs", href: "/dashboard/agent-runs", icon: Activity },
  { label: "Evals", href: "/dashboard/evals", icon: ShieldCheck },
  { label: "Settings", href: "/dashboard/settings", icon: Settings }
];

export function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-72 border-r border-border bg-card px-4 py-5 lg:block">
      <Link href="/" className="flex items-center gap-3 px-2">
        <span className="flex h-10 w-10 items-center justify-center rounded-md bg-primary text-primary-foreground">
          <Bot className="h-5 w-5" />
        </span>
        <span>
          <span className="block text-lg font-semibold">AgentDesk</span>
          <span className="block text-xs text-muted-foreground">AI support workspace</span>
        </span>
      </Link>

      <nav className="mt-8 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className="flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium text-muted-foreground transition hover:bg-muted hover:text-foreground"
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

