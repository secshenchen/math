"""Coordinate and reference-answer checks independent of the constructors."""
import math
import unittest

from geometry.curriculum import MODELS, construct_curriculum


def area(p, names):
    v = [p[n] for n in names]
    return abs(sum(x*v[(i+1) % len(v)][1] - y*v[(i+1) % len(v)][0]
                   for i, (x, y) in enumerate(v))) / 2


def length(p, a, b):
    return math.dist(p[a], p[b])


def angle(p, a, b, c):
    u = [p[a][i]-p[b][i] for i in (0, 1)]
    v = [p[c][i]-p[b][i] for i in (0, 1)]
    return math.degrees(math.acos(sum(x*y for x, y in zip(u, v)) / math.hypot(*u) / math.hypot(*v)))


class CurriculumTests(unittest.TestCase):
    def test_each_declared_model_has_complete_result(self):
        for group, modes in MODELS.items():
            for mode in modes:
                with self.subTest(group=group, mode=mode):
                    result = construct_curriculum(group, mode, 3, 5, 2)
                    self.assertEqual(len(result), 9)
                    p, outline, lines, unit, known, target, answer, question, explanation = result
                    self.assertTrue(p and outline and known and question and explanation)
                    self.assertTrue(all(n in p for n in outline))
                    self.assertTrue(all(a in p and b in p for a, b in lines))
                    self.assertIsNotNone(answer)
                    self.assertTrue(all(math.isfinite(float(x)) for point in p.values() for x in point))

    def test_parallelogram_angles_match_coordinates(self):
        for a, b, c in [(3, 5, 2), (22, 21, 8)]:
            for mode, vertex in [(40, ('A', 'B', 'C')), (41, ('B', 'C', 'D'))]:
                result = construct_curriculum('平行四边形', mode, a, b, c)
                p, answer = result[0], result[6]
                self.assertAlmostEqual(angle(p, *vertex), answer)
                self.assertAlmostEqual(angle(p, 'D', 'A', 'B')+angle(p, 'A', 'B', 'C'), 180)
                self.assertAlmostEqual(p['A'][0]+p['C'][0], p['B'][0]+p['D'][0])
                self.assertAlmostEqual(p['A'][1]+p['C'][1], p['B'][1]+p['D'][1])

    def test_side_classification_has_real_lengths(self):
        for mode, expected in [(40, '等边三角形'), (41, '等腰三角形'), (42, '不等边三角形')]:
            p, _, _, unit, _, _, answer, _, _ = construct_curriculum('三角形基础', mode, 3, 5, 2)
            sides = sorted(length(p, a, b) for a, b in [('A', 'B'), ('B', 'C'), ('C', 'A')])
            self.assertEqual(answer, expected)
            self.assertEqual(unit, '')
            self.assertGreater(sides[0]+sides[1], sides[2])
            if mode == 40:
                self.assertAlmostEqual(sides[0], sides[2])
            elif mode == 41:
                self.assertAlmostEqual(sides[1], sides[2])
                self.assertFalse(math.isclose(sides[0], sides[1]))
            else:
                self.assertFalse(math.isclose(sides[0], sides[1]))
                self.assertFalse(math.isclose(sides[1], sides[2]))

    def test_equilateral_and_every_regular_polygon(self):
        result = construct_curriculum('三角形边角关系', 40, 3, 5, 2)
        self.assertEqual(result[6], 60)
        self.assertAlmostEqual(angle(result[0], 'A', 'B', 'C'), 60)
        for n in range(3, 23):
            result = construct_curriculum('三角形边角关系', 41, n-3, 5, 2)
            p, outline, _, _, _, _, answer, _, _ = result
            self.assertEqual(len(outline), n)
            exterior_sum = sum(180-angle(p, outline[i-1], name, outline[(i+1) % n])
                               for i, name in enumerate(outline))
            self.assertAlmostEqual(exterior_sum, 360)
            self.assertEqual(answer, 360)

    def test_l_shape_area_and_exposed_perimeter(self):
        for mode, expected in [(40, 31), (41, 30)]:
            result = construct_curriculum('长方形与正方形', mode, 3, 5, 2)
            p, outline, answer = result[0], result[1], result[6]
            self.assertEqual(answer, expected)
            if mode == 40:
                self.assertEqual(area(p, outline), 31)
                self.assertEqual(area(p, 'ABCG')+area(p, 'GDEF'), 31)
            else:
                self.assertEqual(sum(length(p, name, outline[(i+1) % len(outline)])
                                     for i, name in enumerate(outline)), 30)
                self.assertEqual(2*(8+2)+2*(3+5)-2*3, 30)

    def test_median_intersection_reference_and_multiple_ratios(self):
        for a, b, c in [(3, 5, 2), (2, 7, 3), (8, 2, 1)]:
            result = construct_curriculum('综合几何模型', 40, a, b, c)
            p, answer = result[0], result[6]
            self.assertEqual(tuple(p['D']), tuple((p['B'][i]+p['C'][i])/2 for i in (0, 1)))
            self.assertAlmostEqual(length(p, 'A', 'E')/length(p, 'E', 'B'), a/b)
            for u, v in [('A', 'D'), ('C', 'E')]:
                self.assertAlmostEqual((p['P'][0]-p[u][0])*(p[v][1]-p[u][1]),
                                       (p['P'][1]-p[u][1])*(p[v][0]-p[u][0]))
            self.assertEqual(area(p, 'BDP'), answer)
            self.assertAlmostEqual(float(answer/area(p, 'ABC')), b/(2*(2*a+b)))
            self.assertEqual(answer, (a+b)*b*c)
        self.assertEqual(construct_curriculum('综合几何模型', 40, 3, 5, 2)[6], 80)


if __name__ == '__main__':
    unittest.main()
