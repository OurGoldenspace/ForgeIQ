"use client"

import Link from "next/link"
import { useEffect, useState } from "react"

import { TelemetryChart } from "@/components/telemetry-chart"
import type { Incident, MaintenanceEvent, TelemetryPoint } from "@/lib/api"

const SPEEDS = [1, 10, 60] as const

interface TelemetryReplayProps {
  points: TelemetryPoint[]
  maintenance: MaintenanceEvent[]
  incidents: Incident[]
  scenarioLabel: string
}

export function visibleSlice(points: TelemetryPoint[], cursor: number) {
  return points.slice(0, Math.max(0, Math.min(cursor, points.length)))
}

export function reachedTimestamp(cursorTime: string | undefined, target: string) {
  if (!cursorTime)
    return false
  return new Date(cursorTime).getTime() >= new Date(target).getTime()
}

export function visibleMaintenance(
  events: MaintenanceEvent[],
  cursorTime: string | undefined,
) {
  if (!cursorTime)
    return []
  return events
    .filter((event) => reachedTimestamp(cursorTime, event.started_at))
    .map((event) => {
      if (event.completed_at && !reachedTimestamp(cursorTime, event.completed_at))
        return { ...event, completed_at: cursorTime }
      return event
    })
}

export function TelemetryReplay({
  points,
  maintenance,
  incidents,
  scenarioLabel,
}: TelemetryReplayProps) {
  const [cursor, setCursor] = useState(0)
  const [isPlaying, setIsPlaying] = useState(true)
  const [speed, setSpeed] = useState<(typeof SPEEDS)[number]>(10)

  useEffect(() => {
    if (!isPlaying || points.length === 0)
      return undefined

    const id = window.setInterval(() => {
      setCursor((current) => {
        if (current >= points.length)
          return current
        return current + 1
      })
    }, Math.max(16, 1000 / speed))

    return () => window.clearInterval(id)
  }, [isPlaying, points.length, speed])

  useEffect(() => {
    if (cursor >= points.length && isPlaying)
      setIsPlaying(false)
  }, [cursor, isPlaying, points.length])

  const visible = visibleSlice(points, cursor)
  const last = visible[visible.length - 1]
  const first = visible[0]
  const cursorTime = last?.timestamp
  const shownMaintenance = visibleMaintenance(maintenance, cursorTime)
  const shownIncident = incidents.find((incident) =>
    reachedTimestamp(cursorTime, incident.detected_at),
  )
  const isLiveAnomaly = Boolean(last?.anomaly_detected)

  function restart() {
    setCursor(0)
    setIsPlaying(true)
  }

  return (
    <>
      {shownIncident ? (
        <section className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950">
          Persistent pressure anomaly detected.
          {" "}
          <Link
            className="font-medium underline"
            href={`/incidents/${shownIncident.incident_code}`}
          >
            Open {shownIncident.incident_code}
          </Link>
        </section>
      ) : (
        <section className="rounded-xl border border-zinc-200 bg-white p-4 text-sm text-zinc-600">
          {isLiveAnomaly
            ? "Pressure looks abnormal. Waiting for persistence before opening an incident."
            : incidents.length
              ? "Watching the line. No persistent pressure incident yet."
              : "No pressure incident created for this scenario."}
        </section>
      )}

      <section className="grid gap-3 sm:grid-cols-3">
        <Stat label="Scenario" value={scenarioLabel} />
        <Stat
          label="Samples"
          value={`${visible.length} / ${points.length}`}
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
        <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-medium text-zinc-800">
              Lateral and longitudinal pressure (N)
            </h2>
            <p className="mt-1 text-xs text-zinc-500">
              {cursorTime
                ? `Line clock ${new Date(cursorTime).toISOString().replace(".000Z", "Z")}`
                : "Replay starts at the first sample."}
              {` · ${speed}×`}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              className="rounded-md bg-zinc-900 px-3 py-1.5 text-sm text-white"
              onClick={() => setIsPlaying((current) => !current)}
              disabled={cursor >= points.length && !isPlaying}
            >
              {isPlaying ? "Pause" : "Play"}
            </button>
            <button
              type="button"
              className="rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-sm text-zinc-700"
              onClick={restart}
            >
              Restart
            </button>
            {SPEEDS.map((option) => (
              <button
                key={option}
                type="button"
                className={
                  option === speed
                    ? "rounded-md bg-zinc-900 px-3 py-1.5 text-sm text-white"
                    : "rounded-md border border-zinc-200 bg-white px-3 py-1.5 text-sm text-zinc-700"
                }
                onClick={() => setSpeed(option)}
              >
                {option}×
              </button>
            ))}
          </div>
        </div>
        <TelemetryChart points={visible} maintenance={shownMaintenance} />
      </section>

      <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
        <h2 className="mb-3 text-sm font-medium text-zinc-800">
          Maintenance in this run
        </h2>
        {shownMaintenance.length === 0 ? (
          <p className="text-sm text-zinc-500">
            {maintenance.length
              ? "No maintenance has occurred yet in this replay."
              : "No maintenance events for this scenario."}
          </p>
        ) : (
          <ul className="space-y-2 text-sm text-zinc-700">
            {shownMaintenance.map((event) => (
              <li key={event.maintenance_code}>
                {event.parameter_name}: {event.old_value} → {event.new_value}
                {event.notes ? ` — ${event.notes}` : ""}
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
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
