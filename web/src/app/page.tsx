"use client";

import { useEffect, useState } from "react";
import FeaturePanel from "@/components/FeaturePanel";
import ReferenceShelf from "@/components/ReferenceShelf";
import StatsStrip from "@/components/StatsStrip";
import { createPlan, fetchItems, fetchInsights, type Scenario } from "@/lib/api";

const seedData = [
  "Maya Chen — salaried designer, $4,800 monthly take-home, $9,200 credit card debt, goal: build a 6-month emergency fund",
  "Andre Ruiz — freelance videographer with uneven income, rent-heavy budget, goal: stabilize cash flow and set quarterly tax reserves",
  "Keisha Thompson — early-career nurse, student loan balance $24,000, goal: debt payoff while saving for a used car"
];

export default function Page() {
  const [query, setQuery] = useState(seedData[0]);
  const [scenario, setScenario] = useState<Scenario>("baseline");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [plan, setPlan] = useState<any>(null);
  const [insights, setInsights] = useState<any>(null);

  useEffect(() => {
    (async () => {
      try {
        setLoading(true);
        const data = await fetchItems();
        setPlan(data.plan);
        setInsights(data.insights);
      } catch (e: any) {
        setError(e.message || "Failed to load.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const handleBuild = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSuccess("");
    try {
      const nextPlan = await createPlan(query, { scenario });
      const nextInsights = await fetchInsights("financial_brief", query);
      setPlan(nextPlan);
      setInsights(nextInsights);
      setSuccess("Plan built and recomposed successfully.");
    } catch (e: any) {
      setError(e.message || "Build failed.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="mx-auto min-h-screen max-w-7xl p-4 md:p-8">
      <header className="mb-6 rounded-xl border border-border bg-card p-6 shadow-card">
        <h1 className="text-3xl font-[--font-display]">Financial Field Journal</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground">Turn scraps into a living money plan with assumptions, confidence bands, and scenario-aware actions.</p>
      </header>

      <StatsStrip summary={{ surplus: plan?.summary ?? "$620", priority: "Credit card payoff", milestone: "Emergency fund month 2", confidence: `${plan?.score ?? 74}%` }} />

      <div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_1.4fr_1fr]">
        <section className="space-y-4">
          <form onSubmit={handleBuild} className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h2 className="text-xl font-[--font-display]">Messy Money Intake</h2>
            <textarea value={query} onChange={(e) => setQuery(e.target.value)} className="mt-3 h-48 w-full rounded-md border border-border bg-muted p-3 text-sm outline-none" />
            <div className="mt-3 flex flex-wrap gap-2">
              {(["baseline", "cautious", "aggressive"] as Scenario[]).map((s) => (
                <button key={s} type="button" onClick={() => setScenario(s)} className={`rounded-full border px-3 py-1 text-xs ${scenario === s ? "border-accent bg-accent text-accent-foreground" : "border-border bg-muted"}`}>
                  {s}
                </button>
              ))}
            </div>
            <button disabled={saving} type="submit" className="mt-4 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground disabled:opacity-60">
              {saving ? "Building..." : "Build My Plan"}
            </button>
          </form>
          <ReferenceShelf seeds={seedData} onPick={setQuery} />
        </section>

        <section className="rounded-lg border border-border bg-card p-4 shadow-card">
          <h2 className="text-xl font-[--font-display]">Financial Brief Canvas</h2>
          {loading ? <p className="mt-4 text-muted-foreground">Loading your saved planning artifact...</p> : null}
          {error ? <p className="mt-4 text-destructive">{error}</p> : null}
          {success ? <p className="mt-4 text-success">{success}</p> : null}
          {!loading && !error && (
            <div className="mt-4 space-y-4 animate-[fadeIn_.35s_ease]">
              <div className="rounded-md border border-border bg-muted p-3 text-sm">{plan?.summary ?? "No plan yet."}</div>
              <div>
                <h3 className="text-sm text-muted-foreground">Cash-Flow Timeline</h3>
                <ul className="mt-2 list-disc space-y-1 pl-4 text-sm">{(plan?.items || []).map((i: string, idx: number) => <li key={idx}>{i}</li>)}</ul>
              </div>
              <div>
                <h3 className="text-sm text-muted-foreground">Action Checklist</h3>
                <ul className="mt-2 list-disc space-y-1 pl-4 text-sm">{(insights?.next_actions || []).map((i: string, idx: number) => <li key={idx}>{i}</li>)}</ul>
              </div>
            </div>
          )}
        </section>

        <div className="space-y-4">
          <FeaturePanel assumptions={insights?.highlights || ["Irregular freelance income assumed at 3-month average."]} />
          <section className="rounded-lg border border-border bg-card p-4 shadow-card">
            <h3 className="text-lg font-[--font-display]">Saved Plan Snapshots</h3>
            <button onClick={() => fetchInsights("history", query).then(setInsights).catch((e) => setError(e.message))} className="mt-3 rounded-md border border-border bg-muted px-3 py-2 text-sm">Refresh Library</button>
            <p className="mt-2 text-sm text-muted-foreground">Named artifacts stay visible for reopen-and-compare demos.</p>
          </section>
        </div>
      </div>
    </main>
  );
}
