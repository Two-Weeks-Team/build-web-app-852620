export type Scenario = "baseline" | "cautious" | "aggressive";

export type PlanResult = {
  summary: string;
  items: string[];
  score: number;
  assumptions?: string[];
  note?: string;
};

export type DemoPayload = {
  seed_profiles: string[];
};

export async function fetchItems() {
  const [plan, insights] = await Promise.all([
    fetch("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: "seed", preferences: "baseline" })
    }),
    fetch("/api/insights", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ selection: "seed", context: "initial" })
    })
  ]);

  if (!plan.ok || !insights.ok) throw new Error("Unable to load planning workspace.");
  return { plan: await plan.json(), insights: await insights.json() };
}

export async function createPlan(query: string, preferences: { scenario: Scenario }) {
  const res = await fetch("/api/plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, preferences: preferences.scenario })
  });
  if (!res.ok) throw new Error("Could not build your plan. Please retry.");
  return res.json();
}

export async function fetchInsights(selection: string, context: string) {
  const res = await fetch("/api/insights", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ selection, context })
  });
  if (!res.ok) throw new Error("Could not load explanation notes.");
  return res.json();
}

export async function fetchArtifacts(): Promise<{ id: string; name: string; updated_at: string; scenario: string }[]> {
  const res = await fetch("/api/artifacts", { method: "GET" });
  if (!res.ok) return [];
  const data = await res.json();
  const items = Array.isArray(data?.items) ? data.items : [];
  return items.map((a: any) => ({
    id: String(a?.artifact_id ?? a?.id ?? ""),
    name: String(a?.name ?? ""),
    updated_at: String(a?.updated_at ?? ""),
    scenario: String(a?.active_scenario ?? a?.scenario ?? "baseline")
  }));
}

export async function buildPlan(query: string, opts: { scenario: Scenario }): Promise<PlanResult> {
  return createPlan(query, opts);
}

export async function saveArtifact(name: string, scenario: Scenario, plan: PlanResult): Promise<any> {
  const res = await fetch("/api/artifacts/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, query: plan.summary || "", preferences: scenario })
  });
  if (!res.ok) throw new Error("Could not save.");
  return res.json();
}
