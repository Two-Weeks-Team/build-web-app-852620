"use client";

export default function StatsStrip({ summary }: { summary: { surplus: string; priority: string; milestone: string; confidence: string } }) {
  const items = [
    ["Monthly Surplus", summary.surplus],
    ["Top Priority", summary.priority],
    ["Next Milestone", summary.milestone],
    ["Confidence Band", summary.confidence]
  ];
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {items.map(([k, v]) => (
        <div key={k} className="rounded-lg border border-border bg-card p-3 shadow-pin">
          <p className="text-xs uppercase tracking-wide text-muted-foreground">{k}</p>
          <p className="mt-1 text-sm text-foreground">{v}</p>
        </div>
      ))}
    </div>
  );
}
