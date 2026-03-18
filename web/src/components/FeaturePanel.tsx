"use client";

export default function FeaturePanel({ assumptions }: { assumptions: string[] }) {
  return (
    <aside className="rounded-lg border border-border bg-card p-4 shadow-card">
      <h3 className="text-lg font-[--font-display]">Evidence Rail</h3>
      <p className="mt-1 text-sm text-muted-foreground">Assumptions and ambiguity handling</p>
      <div className="mt-4 space-y-3">
        {assumptions.map((a, idx) => (
          <div key={idx} className="rounded-md border border-border bg-muted p-3 text-sm">
            <span className="text-warning">Assumption {idx + 1}:</span> {a}
          </div>
        ))}
      </div>
    </aside>
  );
}
