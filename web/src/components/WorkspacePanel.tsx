"use client";

import { FormEvent, useMemo, useState } from "react";
import { buildPlan, saveArtifact, type DemoPayload, type PlanResult, type Scenario } from "@/lib/api";

export default function WorkspacePanel({ demo, onBuiltPlan }: { demo: DemoPayload; onBuiltPlan: (plan: PlanResult) => void }) {
  const [scenario, setScenario] = useState<Scenario>("baseline");
  const [query, setQuery] = useState(demo.seed_profiles[1]);
  const [name, setName] = useState("Andre — Stability Sprint v1");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [plan, setPlan] = useState<PlanResult | null>(null);

  const chips: Scenario[] = ["baseline", "cautious", "aggressive"];
  const canSave = useMemo(() => !!plan && name.trim().length > 2, [plan, name]);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);
    try {
      const res = await buildPlan(query, { scenario });
      setPlan(res);
      onBuiltPlan(res);
      setMsg("Plan built. Financial Brief and timeline recomposed for selected scenario.");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Could not build plan.");
    } finally {
      setLoading(false);
    }
  };

  const onSave = async () => {
    if (!plan) return;
    setSaving(true);
    setMsg(null);
    try {
      await saveArtifact(name, scenario, plan);
      setMsg("Saved to your plan library.");
    } catch (err) {
      setMsg(err instanceof Error ? err.message : "Could not save.");
    } finally {
      setSaving(false);
    }
  };

  return <section />;
}
