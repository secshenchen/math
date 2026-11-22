"""Independent checks for the twelve teaching examples."""
import unittest
from xml.etree import ElementTree as ET

from geometry.bank import QUOTAS
from geometry.lessons import build_lessons


def polygon_area(points, names):
    vertices = [points[n] for n in names]
    return abs(sum(x * vertices[(i + 1) % len(vertices)][1] - y * vertices[(i + 1) % len(vertices)][0]
                   for i, (x, y) in enumerate(vertices))) / 2


def parallel(points, ab, cd):
    a, b, c, d = (points[n] for n in ab + cd)
    return (b[0]-a[0])*(d[1]-c[1]) == (b[1]-a[1])*(d[0]-c[0])


class LessonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lessons = build_lessons()

    def test_twelve_standalone_accessible_cards(self):
        self.assertEqual(set(self.lessons), set(QUOTAS))
        namespace = {'s': 'http://www.w3.org/2000/svg'}
        for category, card in self.lessons.items():
            with self.subTest(category=category):
                for field in ('title', 'condition', 'rule', 'caution'):
                    self.assertTrue(card[field].strip())
                self.assertGreaterEqual(len(card['steps']), 2)
                svg = ET.fromstring(card['svg'])
                self.assertIn('viewBox', svg.attrib)
                self.assertEqual(svg.get('role'), 'img')
                self.assertIn(category, svg.find('s:title', namespace).text)
                self.assertIn('教学示例', svg.find('s:desc', namespace).text)
                self.assertTrue(svg.findall('s:polygon', namespace))
                self.assertNotIn('http://', card['svg'].replace('http://www.w3.org/2000/svg', ''))
                self.assertNotIn('id', card)  # Lessons are not numbered bank questions.

    def test_fixed_example_areas(self):
        cases = {
            '长方形与正方形': ('ABCD', 84),
            '平行四边形': ('ABCD', 72),
            '梯形': ('ABCD', 54),
            '三角形基础': ('ABC', 48),
            '等积模型': ('ABC', 36),
            '一半模型': ('ABC', 96),
        }
        for category, (names, expected) in cases.items():
            with self.subTest(category=category):
                self.assertEqual(polygon_area(self.lessons[category]['construction']['points'], names), expected)

    def test_midpoints_and_parallel_bases(self):
        p = self.lessons['一半模型']['construction']['points']
        for mid, start, end in [('D', 'A', 'B'), ('E', 'A', 'C')]:
            self.assertEqual(tuple(p[mid]), tuple((p[start][i]+p[end][i])/2 for i in (0, 1)))
        self.assertTrue(parallel(p, 'DE', 'BC'))
        self.assertEqual(polygon_area(p, 'ADE'), 24)
        for category in ('平行四边形', '梯形', '蝴蝶模型', '综合几何模型'):
            self.assertTrue(parallel(self.lessons[category]['construction']['points'], 'AB', 'DC'))

    def test_equal_area_kite_butterfly_and_bird(self):
        p = self.lessons['等积模型']['construction']['points']
        self.assertEqual(polygon_area(p, 'ABD'), 36)
        self.assertTrue(parallel(p, 'AB', 'CD'))
        p = self.lessons['风筝模型']['construction']['points']
        self.assertEqual([polygon_area(p, n) for n in ('AOB', 'BOC', 'COD', 'DOA')], [12, 24, 12, 6])
        p = self.lessons['蝴蝶模型']['construction']['points']
        self.assertEqual([polygon_area(p, n) for n in ('ABO', 'CDO', 'ADO', 'BCO')], [24, 6, 12, 12])
        for a, b in [('A', 'C'), ('B', 'D')]:
            self.assertEqual((p['O'][0]-p[a][0])*(p[b][1]-p[a][1]),
                             (p['O'][1]-p[a][1])*(p[b][0]-p[a][0]))
        p = self.lessons['鸟头模型']['construction']['points']
        self.assertEqual(polygon_area(p, 'OAB'), 6)
        self.assertEqual(polygon_area(p, 'OCD'), 36)
        self.assertEqual(p['A'][0]/p['C'][0], 1/2)
        self.assertEqual(p['B'][1]/p['D'][1], 1/3)

    def test_altitude_angles_swallow_and_combined(self):
        p = self.lessons['三角形基础']['construction']['points']
        self.assertEqual(p['C'][0], p['D'][0])
        self.assertEqual(p['D'][1], p['A'][1])
        p = self.lessons['三角形边角关系']['construction']['points']
        self.assertEqual(sum((p['B'][i]-p['A'][i])*(p['C'][i]-p['A'][i]) for i in (0, 1)), 0)
        self.assertEqual(sum((p['B'][i]-p['A'][i])**2 for i in (0, 1)),
                         sum((p['C'][i]-p['A'][i])**2 for i in (0, 1)))
        p = self.lessons['燕尾模型']['construction']['points']
        self.assertEqual(polygon_area(p, 'ABC'), 48)
        self.assertEqual(polygon_area(p, 'BPC'), 24)
        self.assertEqual(polygon_area(p, 'ABP'), 8)
        self.assertEqual(polygon_area(p, 'ACP'), 16)
        self.assertEqual(tuple(p['P']), tuple((p['A'][i]+p['D'][i])/2 for i in (0, 1)))
        p = self.lessons['综合几何模型']['construction']['points']
        self.assertEqual(tuple(p['M']), tuple((p['A'][i]+p['B'][i])/2 for i in (0, 1)))
        self.assertEqual(polygon_area(p, 'CDO'), 6)
        self.assertEqual(polygon_area(p, 'AMO'), 12)


if __name__ == '__main__':
    unittest.main()
