"use client";

import { useEffect, useState } from "react";
import { fetchInsights, type DemoPayload, type PlanResult } from "@/lib/api";

export default function InsightPanel({ demo, plan }: { demo: DemoPayload; plan: PlanResult | null }) {
  const [data, setData] = useState<{ insights: string[]; next_actions: string[]; highlights: string[] } | null>(null);

  useEffect(() => {
    if (!plan) return;
    void fetchInsights("assumptions", plan.summary).then(setData).catch(() => setData(null));
  }, [plan]);

  return <section />;
}
