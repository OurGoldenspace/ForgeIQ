# ForgeIQ

Local manufacturing investigation prototype. Milestone 0 is the simulator and data foundation only.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run scenarios

```powershell
python -m simulator.run --scenario normal
python -m simulator.run --scenario guide_rail
python -m simulator.run --scenario sensor_drift
```

Plot:

```powershell
python scripts/plot_run.py --file data/generated/guide_rail_misalignment.parquet
```

Validate:

```powershell
python scripts/validate_dataset.py --file data/generated/guide_rail_misalignment.parquet
```

Tests:

```powershell
python -m unittest tests.simulator.test_scenarios
```

Postgres (container is on **5433** because local Postgres already uses 5432):

```powershell
docker compose up -d
python -m simulator.ingest
```

Application queries should use `telemetry_observed`, not the base `telemetry` table. Ground truth lives in `telemetry.metadata` and the `fault_*` columns.

API:

```powershell
uvicorn backend.main:app --reload --port 8000
```

```text
GET http://localhost:8000/machines
GET http://localhost:8000/telemetry?scenario_id=guide_rail_misalignment
GET http://localhost:8000/maintenance?scenario_id=guide_rail_misalignment
GET http://localhost:8000/incidents?scenario_id=guide_rail_misalignment
GET http://localhost:8000/incidents/INC-0001/investigation
```

Dashboard:

```powershell
cd frontend
npm run dev
```

Open http://localhost:3000. The API on port 8000 must already be running.
