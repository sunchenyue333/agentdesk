import { Badge } from "@/components/ui/badge";

type PlaceholderPageProps = {
  title: string;
  phase: string;
  summary: string;
};

export function PlaceholderPage({ title, phase, summary }: PlaceholderPageProps) {
  return (
    <section className="rounded-md border border-border bg-card p-6 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold">{title}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted-foreground">{summary}</p>
        </div>
        <Badge tone="blue">{phase}</Badge>
      </div>
    </section>
  );
}

