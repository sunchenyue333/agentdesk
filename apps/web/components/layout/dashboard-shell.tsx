import { Bell, Search } from "lucide-react";
import { Sidebar } from "@/components/layout/sidebar";

export function DashboardShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        <Sidebar />
        <main className="min-w-0 flex-1">
          <header className="sticky top-0 z-10 border-b border-border bg-background/95 px-4 py-3 backdrop-blur md:px-8">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
                  Acme SaaS Support
                </p>
                <h1 className="text-xl font-semibold">Agent Operations</h1>
              </div>
              <div className="flex items-center gap-2">
                <button className="hidden h-9 items-center gap-2 rounded-md border border-border bg-card px-3 text-sm text-muted-foreground md:flex">
                  <Search className="h-4 w-4" />
                  Search
                </button>
                <button className="flex h-9 w-9 items-center justify-center rounded-md border border-border bg-card">
                  <Bell className="h-4 w-4" />
                </button>
              </div>
            </div>
          </header>
          <div className="px-4 py-6 md:px-8">{children}</div>
        </main>
      </div>
    </div>
  );
}

