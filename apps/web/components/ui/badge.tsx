import { cn } from "@/lib/utils";

type BadgeProps = {
  children: React.ReactNode;
  tone?: "neutral" | "green" | "amber" | "red" | "blue";
};

const tones = {
  neutral: "bg-muted text-muted-foreground",
  green: "bg-emerald-50 text-emerald-700",
  amber: "bg-amber-50 text-amber-800",
  red: "bg-rose-50 text-rose-700",
  blue: "bg-sky-50 text-sky-700"
};

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return (
    <span className={cn("inline-flex rounded-md px-2 py-1 text-xs font-medium", tones[tone])}>
      {children}
    </span>
  );
}

