"use client";

export default function StatePanel({ mode, message, onRetry }: { mode: "loading" | "empty" | "error" | "success"; message: string; onRetry?: () => void }) {
  return (
    <section className="mb-5 rounded-lg border border-border bg-card p-4">
      <p className="text-muted-foreground">{message}</p>
      {mode === "error" && onRetry && (
        <button onClick={onRetry} className="mt-2 rounded-md bg-primary px-3 py-2 text-primary-foreground">
          Retry
        </button>
      )}
    </section>
  );
}
