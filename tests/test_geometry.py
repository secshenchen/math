import re
import unittest
import xml.etree.ElementTree as ET
from fractions import Fraction

from geometry.samples import build_samples
from geometry.coordinates import area, intersection, midpoint


class GeometryTests(unittest.TestCase):
    def test_known_midline_condition_is_visible_in_standalone_svg(self):
        from geometry.bank import build_problem
        q = build_problem("梯形",8,7,5,4)
        self.assertIn("中点","".join(ET.fromstring(q["questionSvg"]).itertext()))

    def test_wrapping_never_splits_numeric_values_and_units(self):
        from geometry.samples import wrap_notes
        for token in ("2457/11平方厘米","180°","2925/34","2:3","12.25cm²"):
            rows = wrap_notes("已知条件"*5+token+"。继续推理。")
            self.assertTrue(any(token in row for row in rows),rows)
            self.assertEqual("".join(rows),"已知条件"*5+token+"。继续推理。")

    def test_answer_diagram_contains_the_reasoning_not_just_result(self):
        from geometry.bank import build_problem
        q = build_problem("三角形边角关系",2,7,5,4)
        self.assertIn(q["solution"][0],"".join(ET.fromstring(q["answerSvg"]).itertext()))

    def test_determined_triangle_and_rectangle_labels(self):
        from geometry.bank import build_problem
        for group,modes in (("长方形与正方形",range(15)),("三角形基础",(2,5,8,9,10,11,12,13,14,32,33))):
            for mode in modes:
                q = build_problem(group,mode,7,5,4)
                self.assertEqual(q["geometryStatus"],"determined",(group,mode))
                self.assertNotIn("形状不唯一",q["questionSvg"],(group,mode))
        q = build_problem("三角形基础",2,7,5,4)
        self.assertIn("D在边AB上",q["question"])

    def test_midpoint_constructions_state_and_mark_the_known_halves(self):
        from geometry.bank import build_problem
        for mode, pairs in ((10,1),(11,2),(12,1),(13,1),(14,2)):
            q = build_problem("一半模型",mode,7,5,4)
            for key in ("questionSvg","answerSvg"):
                root = ET.fromstring(q[key])
                self.assertIn("中点","".join(root.itertext()),mode)
                ticks = root.findall("{http://www.w3.org/2000/svg}line[@class='equal-length']")
                self.assertEqual(len(ticks),sum(2*n for n in range(1,pairs+1)),mode)

    def test_exact_coordinates(self):
        self.assertEqual(midpoint((0, 0), (5, 3)), (Fraction(5, 2), Fraction(3, 2)))
        self.assertEqual(intersection((0, 0), (5, 5), (0, 5), (5, 0)), (Fraction(5, 2),) * 2)
        self.assertEqual(area([(0, 0), (12, 0), (12, 7), (0, 7)]), 84)
        with self.assertRaises(ValueError):
            intersection((0, 0), (1, 1), (0, 1), (1, 2))

    def test_sample_answers_and_artifacts(self):
        samples = build_samples()
        self.assertEqual([q["id"] for q in samples], [1, 2, 3, 4, 5])
        self.assertEqual([q["answer"] for q in samples], [str(12 * 7), str(96 // 4), f"{2**2}:{5**2}", str(56 // 2), str(24 * 6 // 12)])
        documents = set()
        for q in samples:
            for key in ("questionSvg", "answerSvg"):
                svg = q[key]
                root = ET.fromstring(svg)
                self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertIn("viewBox", root.attrib)
                self.assertIsNone(re.search(r"NaN|Infinity|href=|url\(", svg))
                documents.add(svg)
            self.assertNotIn("答案 " + q["answer"], q["questionSvg"])
            self.assertIn("答案 " + q["answer"], q["answerSvg"])
        self.assertEqual(len(documents), 10)


    def test_rendered_geometry_relationships(self):
        _, triangle, trapezoid, _, _ = build_samples()
        ns = {"svg": "http://www.w3.org/2000/svg"}

        def endpoints(element):
            a = tuple(float(element.attrib[k]) for k in ("x1", "y1"))
            b = tuple(float(element.attrib[k]) for k in ("x2", "y2"))
            return a, b

        for key in ("questionSvg", "answerSvg"):
            root = ET.fromstring(triangle[key])
            outer = root.findall("svg:polygon", ns)[-1]
            a, b, c = [tuple(map(float, p.split(","))) for p in outer.attrib["points"].split()]
            midline, *ticks = root.findall("svg:line", ns)
            for actual, expected in zip(endpoints(midline), (midpoint(a, b), midpoint(a, c))):
                for observed, wanted in zip(actual, expected):
                    self.assertAlmostEqual(observed, wanted, delta=0.001)
            self.assertEqual(len(ticks), 6)
            self.assertTrue(all(t.attrib.get("class") == "equal-length" for t in ticks))

            root = ET.fromstring(trapezoid[key])
            diagonals = [endpoints(line) for line in root.findall("svg:line", ns)]
            a, c = diagonals[0]
            b, d = diagonals[1]
            # Convert the serialized decimal coordinates before exact calculation.
            a, b, c, d = [tuple(Fraction(str(x)) for x in p) for p in (a, b, c, d)]
            o = intersection(a, c, b, d)
            self.assertAlmostEqual(float(area([a, b, o]) / area([c, d, o])), 4 / 25, delta=0.00001)


if __name__ == "__main__":
    unittest.main()
