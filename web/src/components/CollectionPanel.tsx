"use client";

import { useEffect, useState } from "react";
import { fetchArtifacts, type PlanResult } from "@/lib/api";

export default function CollectionPanel({ onOpenPlan }: { onOpenPlan: (plan: PlanResult) => void }) {
  const [items, setItems] = useState<{ id: string; name: string; updated_at: string; scenario: string }[]>([]);

  useEffect(() => {
    void fetchArtifacts().then(setItems).catch(() => setItems([]));
  }, []);

  return <section />;
}
