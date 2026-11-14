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

    def test_coordinate_and_answer_agreement(self):
        from fractions import Fraction
        from math import atan2, degrees, hypot, isclose

        def triangulated(points):
            origin, *rest = points
            x, y = origin
            return abs(sum((a-x)*(d-y)-(b-y)*(c-x)
                           for (a,b),(c,d) in zip(rest, rest[1:]))) / 2

        checked = 0
        for q in self.bank:
            if "construction" not in q:
                continue
            p = {key: tuple(map(Fraction, pair)) for key, pair in q["construction"].items()}
            mode, category = q["modelMode"], q["category"]
            answer = Fraction(q["answer"].replace(":", "/"))
            a, b, c = (p[n] for n in "ABC")
            height = c[1]-a[1]
            base = b[0]-a[0]
            with self.subTest(id=q["id"]):
                self.assertGreater(triangulated([p[n] for n in q["outline"]]), 0)
                if q["answerType"] == "ratio":
                    upper = triangulated([p[n] for n in "ABO"])
                    lower = triangulated([p[n] for n in "CDO"])
                    expected = upper/lower
                elif q["unit"] == "cm²":
                    expected = triangulated([p[n] for n in q["target"]])
                elif category == "三角形边角关系":
                    angle_b = degrees(atan2(float(height), float(base)))
                    expected = 90 if mode<8 and mode%2==0 else 90-angle_b if mode>=8 or mode>=4 else angle_b
                elif category == "三角形基础" and mode >= 8:
                    legs = [hypot(float(m[0]-n[0]),float(m[1]-n[1])) for m,n in [(a,b),(b,c),(c,a)]]
                    expected = sum(legs) if mode == 8 else len(set(legs))
                elif mode == 8 and category == "长方形与正方形":
                    expected = 2*(base+height)
                elif mode == 8 and category == "平行四边形":
                    expected = base+height
                elif category == "梯形" and mode in (8,9):
                    expected = p["N"][0]-p["M"][0] if mode == 8 else c[0]-p["D"][0]
                elif mode == 9 and category in ("平行四边形","长方形与正方形"):
                    expected = hypot(float(c[0]-b[0]),float(height))
                else:
                    expected = height
                self.assertTrue(isclose(float(answer), float(expected), abs_tol=1e-8))
                checked += 1
        self.assertEqual(checked, 4995)
