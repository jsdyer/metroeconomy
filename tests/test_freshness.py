import json
from pathlib import Path
import sys, tempfile, unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collect import save

class FreshnessTests(unittest.TestCase):
    def test_unchanged_source_advances_check_without_changing_capture_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            meta={"start":"2026-01", "through":"2026-10", "count":1, "metros":[{"id":"001"}]}
            records={"001":{"2026-10":[1]}}
            save(dict(meta), records, root, "2026-11-20T00:00:00+00:00")
            first=json.loads((root/"summary.json").read_text())
            save(dict(meta), records, root, "2026-11-24T00:00:00+00:00")
            second=json.loads((root/"summary.json").read_text())
            self.assertEqual(first["retrieved"], second["retrieved"])
            self.assertNotEqual(first["checked_at"], second["checked_at"])
            before=(root/"summary.json").read_bytes()
            with self.assertRaises(ValueError):
                save({**meta,"through":"2026-09"}, records, root, "2026-11-25T00:00:00+00:00")
            self.assertEqual(before,(root/"summary.json").read_bytes())
            save(dict(meta), records, root)
            self.assertEqual(json.loads((root/"summary.json").read_text())["checked_at"],second["checked_at"])
