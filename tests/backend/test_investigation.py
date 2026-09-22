import unittest

from fastapi.testclient import TestClient

from backend.main import app


FORBIDDEN = {
    "actual_root_cause",
    "fault_type",
    "true_pressure_x",
}


class InvestigationLiveTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        try:
            response = cls.client.get("/incidents", params={"scenario_id": "guide_rail_misalignment"})
            cls.db_available = response.status_code == 200
            cls.rail = response.json()
        except Exception:
            cls.db_available = False
            cls.rail = []

    def test_normal_has_no_incident(self):
        if not self.db_available:
            self.skipTest("Postgres is not available")
        response = self.client.get("/incidents", params={"scenario_id": "normal_operation"})
        self.assertEqual(response.json(), [])

    def test_guide_rail_investigation(self):
        if not self.db_available or not self.rail:
            self.skipTest("Guide-rail incident is not ingested")
        code = self.rail[0]["incident_code"]
        response = self.client.get(f"/incidents/{code}/investigation")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(set(body["incident"]).isdisjoint(FORBIDDEN))
        self.assertEqual(body["hypotheses"][0]["name"], "guide_rail_misalignment")
        self.assertTrue(body["changes"])
        self.assertEqual(body["changes"][0]["parameter_name"], "guide_clearance_mm")
        similar_codes = [item["incident_code"] for item in body["similar"]]
        self.assertIn("INC-0017", similar_codes)
        doc_codes = [item["document_code"] for item in body["documents"]]
        self.assertIn("ENG-042", doc_codes)
        self.assertEqual(body["expert"]["name"], "Sarah Chen")

    def test_sensor_drift_investigation(self):
        if not self.db_available:
            self.skipTest("Postgres is not available")
        listing = self.client.get(
            "/incidents",
            params={"scenario_id": "sensor_calibration_drift"},
        ).json()
        if not listing:
            self.skipTest("Sensor-drift incident is not ingested")
        code = listing[0]["incident_code"]
        body = self.client.get(f"/incidents/{code}/investigation").json()
        self.assertEqual(body["hypotheses"][0]["name"], "sensor_calibration_drift")
        self.assertEqual(body["changes"], [])
        doc_codes = [item["document_code"] for item in body["documents"]]
        self.assertIn("MAINT-022", doc_codes)

    def test_review_and_resolve_roundtrip(self):
        if not self.db_available:
            self.skipTest("Postgres is not available")
        listing = self.client.get(
            "/incidents",
            params={"scenario_id": "sensor_calibration_drift"},
        ).json()
        if not listing:
            self.skipTest("Sensor-drift incident is not ingested")
        code = listing[0]["incident_code"]
        review = self.client.post(
            f"/incidents/{code}/review",
            json={"decision": "confirm", "notes": "Calibration overdue"},
        )
        self.assertEqual(review.status_code, 200)
        self.assertEqual(review.json()["review_decision"], "confirm")
        self.assertNotIn("actual_root_cause", review.json())
        resolved = self.client.post(
            f"/incidents/{code}/resolve",
            json={"resolution": "Recalibrate S-001 and restore the run."},
        )
        self.assertEqual(resolved.status_code, 200)
        self.assertEqual(resolved.json()["status"], "resolved")


if __name__ == "__main__":
    unittest.main()
