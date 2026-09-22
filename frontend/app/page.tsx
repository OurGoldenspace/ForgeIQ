import { ScenarioNav } from "@/components/scenario-nav"
import { TelemetryChart } from "@/components/telemetry-chart"
import {
  fetchMaintenance,
  fetchTelemetry,
  isScenarioId,
  SCENARIOS,
} from "@/lib/api"

interface HomeProps {
  searchParams: {
    scenario?: string
  }
}

export default async function Home({ searchParams }: HomeProps) {
  const scenarioId = isScenarioId(searchParams.scenario)
    ? searchParams.scenario!
    : SCENARIOS[0].id

  let points
  let maintenance
  let error: string | null = null

  try {
    const loaded = await Promise.all([
      fetchTelemetry(scenarioId),
      fetchMaintenance(scenarioId),
    ])
    points = loaded[0]
    maintenance = loaded[1]
  } catch (cause) {
    error = cause instanceof Error ? cause.message : "Failed to load telemetry"
    points = []
    maintenance = []
  }

  const first = points[0]
  const last = points[points.length - 1]
  const scenario = SCENARIOS.find((item) => item.id === scenarioId)

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6">
      <header className="flex flex-col gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
            ForgeIQ
          </p>
          <h1 className="text-2xl font-semibold text-zinc-900">
            Transfer Wheel telemetry
          </h1>
          <p className="mt-1 text-sm text-zinc-600">
            Observed signals from M-003. Ground-truth fault labels are not shown.
          </p>
        </div>
        <ScenarioNav selected={scenarioId} />
      </header>

      {error ? (
        <section className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          {error}. Is the API running on port 8000?
        </section>
      ) : (
        <>
          <section className="grid gap-3 sm:grid-cols-3">
            <Stat label="Scenario" value={scenario?.label ?? scenarioId} />
            <Stat
              label="Samples"
              value={String(points.length)}
            />
            <Stat
              label="Pressure X"
              value={
                first && last
                  ? `${first.pressure_x?.toFixed(1)} → ${last.pressure_x?.toFixed(1)} N`
                  : "—"
              }
            />
          </section>

          <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
            <h2 className="mb-3 text-sm font-medium text-zinc-800">
              Lateral and longitudinal pressure (N)
            </h2>
            <TelemetryChart points={points} maintenance={maintenance} />
          </section>

          <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
            <h2 className="mb-3 text-sm font-medium text-zinc-800">
              Maintenance in this run
            </h2>
            {maintenance.length === 0 ? (
              <p className="text-sm text-zinc-500">
                No maintenance events for this scenario.
              </p>
            ) : (
              <ul className="space-y-2 text-sm text-zinc-700">
                {maintenance.map((event) => (
                  <li key={event.maintenance_code}>
                    {event.parameter_name}: {event.old_value} → {event.new_value}
                    {event.notes ? ` — ${event.notes}` : ""}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </>
      )}
    </main>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
      <p className="text-xs uppercase tracking-wide text-zinc-500">{label}</p>
      <p className="mt-1 text-sm font-medium text-zinc-900">{value}</p>
    </div>
  )
}
