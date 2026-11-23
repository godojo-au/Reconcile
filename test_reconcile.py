import tempfile
import unittest
import io
import json
from pathlib import Path
from unittest.mock import patch

from reconcile import compare, explain_report


class ReconcileTests(unittest.TestCase):
    def test_report(self):
        folder = Path(__file__).parent / "examples"
        report = compare(folder / "before.csv", folder / "after.csv")
        self.assertEqual(report["added"], ["R-04"])
        self.assertEqual(report["removed"], ["R-03"])
        self.assertEqual(report["counts"]["changed"], 2)
        self.assertEqual(report["changed"][0]["fields"]["status"]["after"], "approved")

    def test_duplicate_flagged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.csv"
            path.write_text("id,status\n1,open\n1,closed\n")
            report = compare(path, path)
            self.assertEqual(report["duplicate_keys"]["before"], ["1"])
            self.assertEqual(report["skipped_duplicate_keys"], ["1"])
            self.assertEqual(report["changed"], [])

    def test_local_summary_is_separate_from_diff(self):
        response = {"message": {"content": "One record changed; review the values."}}
        with patch("reconcile.urllib.request.urlopen", return_value=io.BytesIO(json.dumps(response).encode())):
            summary = explain_report({"counts": {"changed": 1}}, "ollama", "local-model")
        self.assertIn("review", summary)


if __name__ == "__main__":
    unittest.main()
