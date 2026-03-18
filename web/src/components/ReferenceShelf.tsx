"use client";

export default function ReferenceShelf({ seeds, onPick }: { seeds: string[]; onPick: (v: string) => void }) {
  return (
    <section className="rounded-lg border border-border bg-card p-4 shadow-card">
      <h3 className="text-lg font-[--font-display]">Seeded Profiles</h3>
      <p className="mt-1 text-sm text-muted-foreground">Tap one to populate the intake panel.</p>
      <div className="mt-4 grid gap-2">
        {seeds.map((s, i) => (
          <button
            key={i}
            onClick={() => onPick(s)}
            className="rounded-md border border-border bg-muted px-3 py-2 text-left text-sm transition hover:border-accent"
          >
            {s}
          </button>
        ))}
      </div>
    </section>
  );
}
