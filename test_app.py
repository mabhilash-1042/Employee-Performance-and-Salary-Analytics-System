import unittest
import app as project


class EmployeeAnalyticsTests(unittest.TestCase):
    def setUp(self):
        project.app.config["TESTING"] = True
        self.client = project.app.test_client()

    def test_dashboard_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Employee analytics", response.data)

    def test_csv_export(self):
        response = self.client.get("/export.csv")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Employee Code", response.data)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")


if __name__ == "__main__":
    unittest.main()
