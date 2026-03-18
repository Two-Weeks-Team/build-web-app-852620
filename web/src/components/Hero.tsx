"use client";

export default function Hero() {
  return (
    <section className="mb-5 rounded-lg border border-border bg-card/80 p-5 shadow-card backdrop-blur">
      <p className="text-sm text-muted-foreground">Financial Field Journal</p>
      <h1 className="mt-1 font-[--font-display] text-3xl leading-tight text-foreground md:text-4xl">
        Turn messy money details into a clear plan you can act on today.
      </h1>
      <p className="mt-2 max-w-3xl text-muted-foreground">
        Paste rough notes about income, debt, spending, and goals. We convert it into a Financial Brief, Cash-Flow Timeline, Debt Payoff Ladder, Savings Goal Plan, and an action checklist with visible assumption notes.
      </p>
    </section>
  );
}
