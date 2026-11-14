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
                    if category == "平行四边形" and mode == 14:
                        expected = sum(triangulated([p[n] for n in name]) for name in ("ABO","CDO"))
                    else:
                        expected = triangulated([p[n] for n in q["target"]])
                elif category == "长方形与正方形" and mode in (13,14):
                    cutout = triangulated([p[n] for n in "AEFG"])
                    polygon = [p[n] for n in "EBCDGF"]
                    expected = (sum(abs(x-u)+abs(y-v) for (x,y),(u,v) in zip(polygon,polygon[1:]+polygon[:1]))
                                if mode == 13 else cutout / triangulated([p[n] for n in "ABCD"]))
                elif category == "鸟头模型" and mode % 5 == 3:
                    expected = triangulated([p[n] for n in "CMN"])/triangulated([p[n] for n in "ABC"])
                elif category == "三角形边角关系":
                    from math import acos
                    def distance(m,n):
                        return hypot(float(m[0]-n[0]),float(m[1]-n[1]))
                    ab,ac,bc = distance(a,b),distance(a,c),distance(b,c)
                    angle_a = degrees(acos((ab*ab+ac*ac-bc*bc)/(2*ab*ac)))
                    angle_b = degrees(acos((ab*ab+bc*bc-ac*ac)/(2*ab*bc)))
                    if mode == 1:
                        expected = 180-angle_b
                    elif mode == 2:
                        expected = angle_a
                    elif mode in (6,7,8):
                        lo,hi = abs(round(ab)-round(ac))+1,round(ab)+round(ac)-1
                        expected = {6:hi,7:lo,8:hi-lo+1}[mode]
                    else:
                        expected = 180-angle_a-angle_b
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

    def test_built_svg_matches_construction(self):
        from fractions import Fraction
        ns = "{http://www.w3.org/2000/svg}"
        checked = 0
        for q in self.bank:
            if "construction" not in q:
                continue
            points = {n:tuple(map(Fraction, pair)) for n,pair in q["construction"].items()}
            xs,ys = zip(*points.values())
            scale = min(Fraction(290,max(xs)-min(xs)), Fraction(140,max(ys)-min(ys)))
            for field in ("questionSvg","answerSvg"):
                root = ET.fromstring(q[field])
                shape = root.findall(ns + "polygon")[-1]
                coordinates = [tuple(map(float,pair.split(","))) for pair in shape.attrib["points"].split()]
                self.assertEqual(len(coordinates),len(q["outline"]),q["id"])
                for vertex,(x,y) in zip(q["outline"],coordinates):
                    u,v = points[vertex]
                    self.assertAlmostEqual(x,float(65+(u-min(xs))*scale),delta=.001,msg=str(q["id"]))
                    self.assertAlmostEqual(y,float(185-(v-min(ys))*scale),delta=.001,msg=str(q["id"]))
                svg_labels = {label.text for label in root.findall(ns + "text")}
                self.assertTrue(set(q["outline"]) <= svg_labels,q["id"])
                checked += 1
        self.assertEqual(checked,9990)
