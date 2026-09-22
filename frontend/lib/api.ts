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
  anomaly_detected: boolean
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

export interface Incident {
  incident_code: string
  machine_id: string
  production_run_id: string | null
  detected_at: string
  resolved_at: string | null
  incident_type: string
  severity: string
  status: string
  resolution: string | null
  review_decision: string | null
  human_root_cause: string | null
  review_notes: string | null
  scenario_id: string | null
}

export interface Hypothesis {
  name: string
  score: number
  supporting: string[]
  contradictory: string[]
  recommended_checks: string[]
}

export interface SimilarIncident {
  incident_code: string
  score: number
  reasons: string[]
  resolution: string | null
}

export interface DocumentHit {
  document_code: string
  title: string
  document_type: string
  excerpt: string
  why: string
}

export interface ExpertRecommendation {
  name: string
  role: string
  reasons: string[]
}

export interface Investigation {
  incident: Incident
  changes: MaintenanceEvent[]
  similar: SimilarIncident[]
  documents: DocumentHit[]
  hypotheses: Hypothesis[]
  expert: ExpertRecommendation | null
}

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  process.env.API_URL ??
  "http://127.0.0.1:8000"

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

async function readJson<T>(response: Response, label: string): Promise<T> {
  if (!response.ok)
    throw new Error(`${label} failed (${response.status})`)
  return response.json()
}

export async function fetchTelemetry(scenarioId: string): Promise<TelemetryPoint[]> {
  const url = new URL("/telemetry", API_URL)
  url.searchParams.set("scenario_id", scenarioId)
  return readJson(await fetch(url, { cache: "no-store" }), "Telemetry")
}

export async function fetchMaintenance(scenarioId: string): Promise<MaintenanceEvent[]> {
  const url = new URL("/maintenance", API_URL)
  url.searchParams.set("scenario_id", scenarioId)
  return readJson(await fetch(url, { cache: "no-store" }), "Maintenance")
}

export async function fetchIncidents(scenarioId: string): Promise<Incident[]> {
  const url = new URL("/incidents", API_URL)
  url.searchParams.set("scenario_id", scenarioId)
  return readJson(await fetch(url, { cache: "no-store" }), "Incidents")
}

export async function fetchInvestigation(code: string): Promise<Investigation> {
  const url = new URL(`/incidents/${code}/investigation`, API_URL)
  return readJson(await fetch(url, { cache: "no-store" }), "Investigation")
}

export async function fetchIncidentTelemetry(investigation: Investigation): Promise<TelemetryPoint[]> {
  if (!investigation.incident.scenario_id)
    return []
  return fetchTelemetry(investigation.incident.scenario_id)
}
