export type Scenario = "baseline" | "cautious" | "aggressive";

export async function fetchItems() {
  const [plan, insights] = await Promise.all([
    fetch("/api/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: "seed", preferences: { scenario: "baseline" } })
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
    body: JSON.stringify({ query, preferences })
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
