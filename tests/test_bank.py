import json
import re
import unittest
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from geometry.bank import QUOTAS


class BuiltBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = Path("candidate/index.html").read_text(encoding="utf-8")
        payload = html.split('<script type="application/json" id="bank">', 1)[1].split("</script>", 1)[0]
        cls.bank = json.loads(payload)

    def test_counts_and_prompt_uniqueness(self):
        self.assertEqual([q["id"] for q in self.bank], list(range(1, 5001)))
        self.assertEqual(Counter(q["category"] for q in self.bank), QUOTAS)
        self.assertEqual(len({q["question"] for q in self.bank}), 5000)
        for q in self.bank:
            self.assertTrue(all(q[key] for key in ("subcategory", "difficulty", "answer", "answerType", "solution")))

    def test_all_svg_documents(self):
        ns = "{http://www.w3.org/2000/svg}"
        for q in self.bank:
            with self.subTest(id=q["id"]):
                self.assertNotEqual(q["questionSvg"], q["answerSvg"])
                for field in ("questionSvg", "answerSvg"):
                    svg = q[field]
                    root = ET.fromstring(svg)
                    self.assertEqual(root.tag, ns + "svg")
                    _, _, width, height = map(float, root.attrib["viewBox"].split())
                    self.assertGreater(width * height, 0)
                    self.assertIsNotNone(root.find(ns + "polygon"))
                    self.assertIsNone(re.search(r"NaN|Infinity|href=|url\(", svg))
                    for label in root.findall(ns + "text"):
                        self.assertTrue(0 <= float(label.attrib["x"]) <= width)
                        self.assertTrue(0 <= float(label.attrib["y"]) <= height)
                        if field == "questionSvg":
                            self.assertFalse((label.text or "").startswith("答案 "))
