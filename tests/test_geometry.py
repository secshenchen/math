import re
import unittest
import xml.etree.ElementTree as ET
from fractions import Fraction

from geometry.samples import build_samples
from geometry.coordinates import area, intersection, midpoint


class GeometryTests(unittest.TestCase):
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
