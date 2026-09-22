export interface TelemetryPoint {
  timestamp: string
  machine_id: string
  production_run_id: string | null
  pressure_x: number | null
  pressure_y: number | null
  vibration: number | null
  velocity: number | null
  temperature: number | null
  motor_current: number | null
  line_speed: number | null
  operating_mode: string | null
  scenario_id: string | null
}

export interface MaintenanceEvent {
  maintenance_code: string
  machine_id: string
  component_id: string | null
  started_at: string
  completed_at: string | null
  maintenance_type: string
  parameter_name: string | null
  old_value: number | null
  new_value: number | null
  notes: string | null
  scenario_id: string | null
}

export const API_URL =
  process.env.API_URL ?? "http://127.0.0.1:8000"

export const SCENARIOS = [
  {
    id: "guide_rail_misalignment",
    label: "Guide rail misalignment",
  },
  {
    id: "sensor_calibration_drift",
    label: "Sensor calibration drift",
  },
  {
    id: "normal_operation",
    label: "Normal operation",
  },
] as const

export function isScenarioId(value: string | undefined): boolean {
  if (!value)
    return false
  return SCENARIOS.some((scenario) => scenario.id === value)
}

export async function fetchTelemetry(scenarioId: string): Promise<TelemetryPoint[]> {
  const url = new URL("/telemetry", API_URL)
  url.searchParams.set("scenario_id", scenarioId)
  const response = await fetch(url, { cache: "no-store" })
  if (!response.ok)
    throw new Error(`Telemetry request failed (${response.status})`)
  return response.json()
}

export async function fetchMaintenance(scenarioId: string): Promise<MaintenanceEvent[]> {
  const url = new URL("/maintenance", API_URL)
  url.searchParams.set("scenario_id", scenarioId)
  const response = await fetch(url, { cache: "no-store" })
  if (!response.ok)
    throw new Error(`Maintenance request failed (${response.status})`)
  return response.json()
}
