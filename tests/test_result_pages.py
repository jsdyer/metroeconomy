import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from result_pages import publish


class ResultPageTests(unittest.TestCase):
    def test_only_written_pages_are_indexed_and_labels_are_escaped(self):
        with TemporaryDirectory() as temporary:
            stage = Path(temporary)
            tool = {"url": "/example/", "title": "Example"}
            records = [("new-item", "A & B", "A & B results", "Observed value < 1", "<p>Details</p>")]
            publish(stage, tool, "records", "All records", "Browse observations.", records)
            url = "https://coolcode.ca/example/records/"
            self.assertEqual([node.text for node in ElementTree.parse(stage / "sitemap.xml").iter()
                              if node.tag.endswith("}loc")], [url, url + "new-item/"])
            page = (stage / "records/new-item/index.html").read_text()
            self.assertIn("A &amp; B results", page)
            self.assertIn("Observed value &lt; 1", page)
            self.assertIn(f'rel="canonical" href="{url}new-item/"', page)
