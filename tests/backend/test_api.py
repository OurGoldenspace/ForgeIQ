import unittest

from fastapi.testclient import TestClient

from backend.main import app
from backend.models import Machine, MaintenanceEvent, TelemetryPoint


FORBIDDEN = {
    "metadata",
    "fault_active",
    "fault_type",
    "fault_severity",
    "actual_root_cause",
    "true_pressure_x",
    "_true_pressure_x",
}


class ApiContractTests(unittest.TestCase):

    def test_response_models_omit_ground_truth(self):
        for model in (Machine, TelemetryPoint, MaintenanceEvent):
            fields = set(model.model_fields)
            overlap = fields & FORBIDDEN
            self.assertEqual(overlap, set(), model.__name__)


class ApiLiveTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        try:
            response = cls.client.get("/machines")
            cls.db_available = response.status_code == 200
        except Exception:
            cls.db_available = False

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_machines(self):
        if not self.db_available:
            self.skipTest("Postgres is not available")
        response = self.client.get("/machines")
        self.assertEqual(response.status_code, 200)
        codes = [row["machine_code"] for row in response.json()]
        self.assertIn("M-003", codes)

    def test_guide_rail_telemetry_has_no_ground_truth(self):
        if not self.db_available:
            self.skipTest("Postgres is not available")
        response = self.client.get(
            "/telemetry",
            params={"scenario_id": "guide_rail_misalignment"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()
        self.assertEqual(len(rows), 1200)
        self.assertTrue(
            set(rows[0]).isdisjoint(FORBIDDEN)
        )
        late = rows[900]["pressure_x"]
        early = rows[100]["pressure_x"]
        self.assertGreater(late, early + 3)

    def test_maintenance_for_guide_rail(self):
        if not self.db_available:
            self.skipTest("Postgres is not available")
        response = self.client.get(
            "/maintenance",
            params={"scenario_id": "guide_rail_misalignment"},
        )
        self.assertEqual(response.status_code, 200)
        rows = response.json()
        self.assertEqual(len(rows), 1)
        event = rows[0]
        self.assertEqual(event["parameter_name"], "guide_clearance_mm")
        self.assertEqual(event["old_value"], 4.8)
        self.assertEqual(event["new_value"], 4.1)
        self.assertTrue(set(event).isdisjoint(FORBIDDEN))


if __name__ == "__main__":
    unittest.main()
