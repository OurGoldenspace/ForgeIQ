"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"

import { API_URL, type Incident } from "@/lib/api"

interface ReviewActionsProps {
  incident: Incident
}

export function ReviewActions({ incident }: ReviewActionsProps) {
  const router = useRouter()
  const [notes, setNotes] = useState(incident.review_notes ?? "")
  const [rootCause, setRootCause] = useState(incident.human_root_cause ?? "")
  const [resolution, setResolution] = useState(incident.resolution ?? "")
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)
  const isResolved = incident.status === "resolved"

  async function review(decision: "confirm" | "reject" | "modify") {
    setPending(true)
    setError(null)
    const response = await fetch(
      `${API_URL}/incidents/${incident.incident_code}/review`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          decision,
          root_cause: rootCause || null,
          notes: notes || null,
        }),
      },
    )
    setPending(false)
    if (!response.ok) {
      setError(await response.text())
      return
    }
    router.refresh()
  }

  async function resolve() {
    setPending(true)
    setError(null)
    const response = await fetch(
      `${API_URL}/incidents/${incident.incident_code}/resolve`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resolution: resolution || "Closed after human review.",
        }),
      },
    )
    setPending(false)
    if (!response.ok) {
      setError(await response.text())
      return
    }
    router.refresh()
  }

  return (
    <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-medium text-zinc-800">
        Human review
      </h2>
      <p className="mb-3 text-sm text-zinc-600">
        The model cannot mark a root cause as actual. Confirm, reject, or modify it.
      </p>
      <label className="mb-2 block text-xs uppercase tracking-wide text-zinc-500">
        Human root cause
      </label>
      <input
        className="mb-3 w-full rounded-md border border-zinc-200 px-3 py-2 text-sm"
        disabled={isResolved}
        value={rootCause}
        onChange={(event) => setRootCause(event.target.value)}
        placeholder="guide_rail_misalignment"
      />
      <label className="mb-2 block text-xs uppercase tracking-wide text-zinc-500">
        Notes
      </label>
      <textarea
        className="mb-3 w-full rounded-md border border-zinc-200 px-3 py-2 text-sm"
        disabled={isResolved}
        rows={3}
        value={notes}
        onChange={(event) => setNotes(event.target.value)}
      />
      <div className="mb-4 flex flex-wrap gap-2">
        <button
          className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm text-white disabled:opacity-50"
          disabled={pending || isResolved}
          onClick={() => review("confirm")}
        >
          Confirm
        </button>
        <button
          className="rounded-md border border-zinc-200 px-3 py-1.5 text-sm disabled:opacity-50"
          disabled={pending || isResolved}
          onClick={() => review("reject")}
        >
          Reject
        </button>
        <button
          className="rounded-md border border-zinc-200 px-3 py-1.5 text-sm disabled:opacity-50"
          disabled={pending || isResolved}
          onClick={() => review("modify")}
        >
          Modify
        </button>
      </div>
      <label className="mb-2 block text-xs uppercase tracking-wide text-zinc-500">
        Resolution
      </label>
      <textarea
        className="mb-3 w-full rounded-md border border-zinc-200 px-3 py-2 text-sm"
        disabled={isResolved}
        rows={3}
        value={resolution}
        onChange={(event) => setResolution(event.target.value)}
        placeholder="Restore guide clearance to 4.8 mm and recapture pressure."
      />
      <button
        className="rounded-md bg-emerald-700 px-3 py-1.5 text-sm text-white disabled:opacity-50"
        disabled={pending || isResolved || !incident.review_decision}
        onClick={resolve}
      >
        Resolve and write lesson learned
      </button>
      {incident.review_decision ? (
        <p className="mt-3 text-sm text-zinc-600">
          Review: {incident.review_decision}
          {incident.human_root_cause ? ` · ${incident.human_root_cause}` : ""}
        </p>
      ) : null}
      {incident.status === "resolved" ? (
        <p className="mt-2 text-sm text-emerald-700">
          Incident resolved. Lesson learned stored as LL-{incident.incident_code}.
        </p>
      ) : null}
      {error ? (
        <p className="mt-2 text-sm text-red-700">{error}</p>
      ) : null}
    </section>
  )
}
