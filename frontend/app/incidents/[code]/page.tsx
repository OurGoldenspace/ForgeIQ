import Link from "next/link"

import { ReviewActions } from "@/components/review-actions"
import { TelemetryChart } from "@/components/telemetry-chart"
import { fetchIncidentTelemetry, fetchInvestigation } from "@/lib/api"

interface IncidentPageProps {
  params: {
    code: string
  }
}

export default async function IncidentPage({ params }: IncidentPageProps) {
  let investigation
  try {
    investigation = await fetchInvestigation(params.code)
  } catch {
    return (
      <main className="mx-auto max-w-5xl px-4 py-8">
        <p>Incident {params.code} was not found.</p>
        <Link href="/" className="text-sm text-blue-700">
          Back to telemetry
        </Link>
      </main>
    )
  }

  const points = await fetchIncidentTelemetry(investigation)
  const { incident, changes, similar, documents, hypotheses, expert } = investigation

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6">
      <header>
        <Link href={`/?scenario=${incident.scenario_id ?? ""}`} className="text-sm text-zinc-500">
          ← Telemetry
        </Link>
        <p className="mt-3 text-xs font-medium uppercase tracking-wide text-zinc-500">
          {incident.incident_code} · {incident.status}
        </p>
        <h1 className="text-2xl font-semibold text-zinc-900">
          Abnormal pressure investigation
        </h1>
        <p className="mt-1 text-sm text-zinc-600">
          Detected {new Date(incident.detected_at).toISOString().replace(".000Z", "Z")}.
          Ranked hypotheses are evidence-backed, not ground truth.
        </p>
      </header>

      <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
        <h2 className="mb-3 text-sm font-medium text-zinc-800">Observed pressure</h2>
        <TelemetryChart points={points} maintenance={changes} />
      </section>

      <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
        <h2 className="mb-3 text-sm font-medium text-zinc-800">What changed?</h2>
        {changes.length === 0 ? (
          <p className="text-sm text-zinc-500">No recent maintenance or configuration change.</p>
        ) : (
          <ul className="space-y-2 text-sm text-zinc-700">
            {changes.map((event) => (
              <li key={event.maintenance_code}>
                {event.parameter_name}: {event.old_value} → {event.new_value}
                {event.notes ? ` — ${event.notes}` : ""}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
        <h2 className="mb-3 text-sm font-medium text-zinc-800">Has this happened before?</h2>
        {similar.length === 0 ? (
          <p className="text-sm text-zinc-500">No resolved similar incidents.</p>
        ) : (
          <ul className="space-y-3 text-sm text-zinc-700">
            {similar.map((item) => (
              <li key={item.incident_code}>
                <span className="font-medium">{item.incident_code}</span>
                {" "}
                {(item.score * 100).toFixed(0)}%
                <ul className="mt-1 list-disc pl-5 text-zinc-600">
                  {item.reasons.map((reason) => (
                    <li key={reason}>{reason}</li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
        <h2 className="mb-3 text-sm font-medium text-zinc-800">Likely causes</h2>
        <ol className="space-y-4">
          {hypotheses.map((item, index) => (
            <li key={item.name} className="text-sm text-zinc-700">
              <p className="font-medium">
                {index + 1}. {item.name} · {item.score.toFixed(2)}
              </p>
              <p className="mt-1 text-zinc-500">Supporting</p>
              <ul className="list-disc pl-5">
                {item.supporting.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
              {item.contradictory.length ? (
                <>
                  <p className="mt-1 text-zinc-500">Contradictory</p>
                  <ul className="list-disc pl-5">
                    {item.contradictory.map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                </>
              ) : null}
              <p className="mt-1 text-zinc-500">Checks</p>
              <ul className="list-disc pl-5">
                {item.recommended_checks.map((line) => (
                  <li key={line}>{line}</li>
                ))}
              </ul>
            </li>
          ))}
        </ol>
      </section>

      <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
        <h2 className="mb-3 text-sm font-medium text-zinc-800">Evidence documents</h2>
        <ul className="space-y-3 text-sm text-zinc-700">
          {documents.map((doc) => (
            <li key={doc.document_code}>
              <p className="font-medium">{doc.document_code} · {doc.title}</p>
              <p className="text-zinc-500">{doc.why}</p>
              <p className="mt-1 text-zinc-600">{doc.excerpt}</p>
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
        <h2 className="mb-3 text-sm font-medium text-zinc-800">Who should investigate?</h2>
        {expert ? (
          <div className="text-sm text-zinc-700">
            <p className="font-medium">{expert.name}</p>
            <p className="text-zinc-500">{expert.role}</p>
            <ul className="mt-2 list-disc pl-5">
              {expert.reasons.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="text-sm text-zinc-500">No ranked expert yet.</p>
        )}
      </section>

      <ReviewActions incident={incident} />
    </main>
  )
}
