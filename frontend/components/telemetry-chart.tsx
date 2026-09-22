"use client"

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceArea,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

import type { MaintenanceEvent, TelemetryPoint } from "@/lib/api"

interface TelemetryChartProps {
  points: TelemetryPoint[]
  maintenance: MaintenanceEvent[]
}

function toIso(value: string) {
  return new Date(value).toISOString()
}

function clockLabel(value: string) {
  return new Date(value).toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
  })
}

export function TelemetryChart({
  points,
  maintenance,
}: TelemetryChartProps) {
  const data = points.map((point) => ({
    timestamp: toIso(point.timestamp),
    pressure_x: point.pressure_x,
    pressure_y: point.pressure_y,
  }))

  const values = data.flatMap((point) => [
    point.pressure_x,
    point.pressure_y,
  ]).filter((value): value is number => typeof value === "number" && Number.isFinite(value))

  const min = values.length ? Math.min(...values) - 0.5 : 0
  const max = values.length ? Math.max(...values) + 0.5 : 1

  return (
    <div className="h-[360px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 8, right: 16, left: 8, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={clockLabel}
            minTickGap={48}
            tick={{ fontSize: 12, fill: "#71717a" }}
          />
          <YAxis
            width={48}
            tick={{ fontSize: 12, fill: "#71717a" }}
            domain={[min, max]}
            tickFormatter={(value: number) => value.toFixed(0)}
          />
          <Tooltip
            labelFormatter={clockLabel}
            formatter={(value, name) => [
              Number(value).toFixed(2),
              name === "pressure_x" ? "Pressure X" : "Pressure Y",
            ]}
          />
          <Legend />
          {maintenance.map((event) => (
            <ReferenceArea
              key={event.maintenance_code}
              x1={toIso(event.started_at)}
              x2={toIso(event.completed_at ?? event.started_at)}
              fill="#f59e0b"
              fillOpacity={0.12}
            />
          ))}
          <Line
            type="monotone"
            dataKey="pressure_x"
            name="Pressure X"
            stroke="#2563eb"
            dot={false}
            strokeWidth={1.75}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="pressure_y"
            name="Pressure Y"
            stroke="#059669"
            dot={false}
            strokeWidth={1.75}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
