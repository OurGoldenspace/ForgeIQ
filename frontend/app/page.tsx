import { ScenarioNav } from "@/components/scenario-nav"
import { TelemetryReplay } from "@/components/telemetry-replay"

import {
  fetchIncidents,
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
  let incidents
  let error: string | null = null

  try {
    const loaded = await Promise.all([
      fetchTelemetry(scenarioId),
      fetchMaintenance(scenarioId),
      fetchIncidents(scenarioId),
    ])
    points = loaded[0]
    maintenance = loaded[1]
    incidents = loaded[2]
  } catch (cause) {
    error = cause instanceof Error ? cause.message : "Failed to load telemetry"
    points = []
    maintenance = []
    incidents = []
  }

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
        <TelemetryReplay
          key={scenarioId}
          points={points}
          maintenance={maintenance}
          incidents={incidents}
          scenarioLabel={scenario?.label ?? scenarioId}
        />
      )}
    </main>
  )
}
