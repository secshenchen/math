import base64
import gzip
import json
import re
import unittest
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from geometry.bank import QUOTAS


def released_html():
    packed = Path("index.html").read_bytes()
    payload = re.search(rb"atob\('([A-Za-z0-9+/=]+)'\)",packed)[1]
    return gzip.decompress(base64.b64decode(payload)).decode("utf-8")


def read_bank(html):
    payload = html.split('<script type="application/json" id="bank">', 1)[1].split("</script>", 1)[0]
    return json.loads(payload)


class BuiltBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = released_html()
        cls.bank = read_bank(cls.html)

    def test_counts_and_prompt_uniqueness(self):
        self.assertEqual([q["id"] for q in self.bank], list(range(1, 5001)))
        self.assertEqual(Counter(q["category"] for q in self.bank), QUOTAS)
        self.assertEqual(len({q["question"] for q in self.bank}), 5000)
        for q in self.bank:
            self.assertTrue(all(q[key] for key in ("subcategory", "difficulty", "answer", "answerType", "solution")))

    def test_frequent_prompts_are_replaced_with_varied_reasoning(self):
        forms = Counter((q["category"], re.sub(r"\d+(?:[./]\d+)?", "N", q["question"])) for q in self.bank)
        self.assertLessEqual(max(forms.values()), 65)
        self.assertGreaterEqual(len(forms), 145)
        added = [q for q in self.bank if 32 <= q.get("modelMode", 0) < 40]
        self.assertEqual(len({q["subcategory"] for q in added}), 18)
        self.assertEqual(len({q["category"] for q in added}), 8)

    def test_equal_area_height_ratio_specifies_the_foot(self):
        exercises = [q for q in self.bank if q["category"] == "等积模型" and q.get("modelMode") in (20,21)]
        self.assertEqual(len(exercises),65)
        for q in exercises:
            self.assertIn("E是DE在AB上的垂足",q["question"],q["id"])

    def test_checked_in_offline_file_contains_same_exercises_as_build(self):
        self.assertEqual(Path("index.html").read_bytes(), Path("candidate/offline.html").read_bytes())
        built = Path("candidate/index.html").read_text(encoding="utf-8")
        def app_without_bank(html):
            return re.sub(r'(id="bank">).*?(</script>)',r'\1\2',html,count=1,flags=re.S)
        self.assertEqual(app_without_bank(self.html),app_without_bank(built))
        for published, regenerated in zip(self.bank,read_bank(built),strict=True):
            # Browser tests check the actual shipped drawings. System math libraries can
            # place a numeric coordinate either side of a label layout threshold.
            exclude = {"construction","questionSvg","answerSvg"}
            self.assertEqual({k:v for k,v in published.items() if k not in exclude},
                             {k:v for k,v in regenerated.items() if k not in exclude},published["id"])

    def test_all_svg_documents(self):
        ns = "{http://www.w3.org/2000/svg}"
        for q in self.bank:
            with self.subTest(id=q["id"]):
                self.assertNotEqual(q["questionSvg"], q["answerSvg"])
                for field in ("questionSvg", "answerSvg"):
                    svg = q[field]
                    root = ET.fromstring(svg)
                    self.assertEqual(root.tag, ns + "svg")
                    self.assertIn(f"第{q['id']}题", root.findtext(ns + "title"))
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
            answer = q["answer"] if q["answerType"] == "text" else Fraction(q["answer"].replace(":", "/"))
            a, b, c = (p[n] for n in "ABC")
            height = c[1]-a[1]
            base = b[0]-a[0]
            with self.subTest(id=q["id"]):
                self.assertGreater(triangulated([p[n] for n in q["outline"]]), 0)
                if q["answerType"] == "text":
                    if mode >= 40:
                        sides = sorted(hypot(float(m[0]-n[0]),float(m[1]-n[1])) for m,n in ((a,b),(a,c),(b,c)))
                        expected = "等边三角形" if isclose(sides[0],sides[2]) else "等腰三角形" if isclose(sides[0],sides[1]) or isclose(sides[1],sides[2]) else "不等边三角形"
                        self.assertEqual(answer,expected)
                        checked += 1
                        continue
                    squares = sorted(sum((x-y)**2 for x,y in zip(m,n)) for m,n in ((a,b),(a,c),(b,c)))
                    compare = squares[0]+squares[1]-squares[2]
                    expected = "锐角三角形" if compare>0 else "钝角三角形" if compare<0 else "直角三角形"
                    self.assertEqual(answer, expected)
                    checked += 1
                    continue
                if category == "风筝模型" and mode in (20,21):
                    from math import dist
                    segment = "AC" if mode == 20 else "BD"
                    expected = dist(p[segment[0]],p["O"])/dist(p["O"],p[segment[1]])
                elif q["answerType"] == "ratio":
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
                elif mode >= 40 and category == "长方形与正方形":
                    poly = [p[n] for n in q["outline"]]
                    expected = sum(hypot(float(x-u),float(y-v)) for (x,y),(u,v) in zip(poly,poly[1:]+poly[:1]))
                elif mode >= 40 and category == "平行四边形":
                    from math import acos
                    first,vertex,last = ("A","B","C") if mode == 40 else ("B","C","D")
                    u = [p[first][i]-p[vertex][i] for i in (0,1)]
                    v = [p[last][i]-p[vertex][i] for i in (0,1)]
                    expected = degrees(acos(float(sum(x*y for x,y in zip(u,v)))/(hypot(*u)*hypot(*v))))
                elif category == "三角形边角关系" and mode == 41:
                    polygon = [p[n] for n in q["outline"]]
                    from math import atan2
                    turns = []
                    for i,(x,y) in enumerate(polygon):
                        before,after = polygon[i-1],polygon[(i+1)%len(polygon)]
                        u,v = (x-before[0],y-before[1]),(after[0]-x,after[1]-y)
                        turns.append(degrees(atan2(float(u[0]*v[1]-u[1]*v[0]),float(u[0]*v[0]+u[1]*v[1]))))
                    expected = abs(sum(turns))
                elif category == "三角形边角关系" and mode >= 32:
                    def angle_between(first, vertex, last):
                        x,y = p[vertex]
                        return degrees(abs(atan2(
                            float((p[first][0]-x)*(p[last][1]-y)-(p[first][1]-y)*(p[last][0]-x)),
                            float((p[first][0]-x)*(p[last][0]-x)+(p[first][1]-y)*(p[last][1]-y)))))
                    expected = angle_between("A","B","M") if mode == 32 else angle_between("A","C","B")
                elif category == "三角形基础" and mode == 32:
                    expected = p["D"][0]-a[0]
                elif category == "三角形边角关系" and mode >= 18:
                    from math import acos
                    polygon = [p[n] for n in q["outline"]]
                    angles = []
                    for i, origin in enumerate(polygon):
                        vectors = [tuple(float(x-y) for x,y in zip(other,origin))
                                   for other in (polygon[i-1], polygon[(i+1)%len(polygon)])]
                        (x,y),(u,v) = vectors
                        angles.append(degrees(acos((x*u+y*v)/(hypot(x,y)*hypot(u,v)))))
                    expected = sum(angles) if mode == 18 else 180-angles[0]
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
                projected = [(float(65+(x-min(xs))*scale),float(185-(y-min(ys))*scale)) for x,y in points.values()]
                for line in root.findall(ns + "line"):
                    if line.attrib.get("class") in ("equal-length","label-guide"):
                        continue
                    for end in ("1","2"):
                        x,y = float(line.attrib["x"+end]),float(line.attrib["y"+end])
                        self.assertTrue(any(abs(x-u)<=.002 and abs(y-v)<=.002 for u,v in projected),(q["id"],field,"auxiliary endpoint"))
                shape = root.findall(ns + "polygon")[-1]
                coordinates = [tuple(map(float,pair.split(","))) for pair in shape.attrib["points"].split()]
                self.assertEqual(len(coordinates),len(q["outline"]),q["id"])
                for vertex,(x,y) in zip(q["outline"],coordinates):
                    u,v = points[vertex]
                    self.assertAlmostEqual(x,float(65+(u-min(xs))*scale),delta=.001,msg=str(q["id"]))
                    self.assertAlmostEqual(y,float(185-(v-min(ys))*scale),delta=.001,msg=str(q["id"]))
                svg_labels = {label.text for label in root.findall(ns + "text")}
                names = set("".join(re.findall(r"[A-Z]+", q["question"])))
                self.assertTrue(set(points) == svg_labels.intersection(points),q["id"])
                self.assertTrue(names <= set(points), (q["id"],names-set(points)))
                if field == "answerSvg" and q["target"]:
                    expected = " ".join(f"{65+(points[n][0]-min(xs))*float(scale):.3f},{185-(points[n][1]-min(ys))*float(scale):.3f}" for n in q["target"])
                    matches = [poly.attrib["points"].split() for poly in root.findall(ns + "polygon")[:-1]]
                    self.assertIn(expected.split(),matches,q["id"])
                positions = [(float(t.attrib["x"]),float(t.attrib["y"]))
                             for t in root.findall(ns + "text") if t.text in points]
                for index,(x,y) in enumerate(positions):
                    self.assertFalse(any(abs(x-u)<13.99 and abs(y-v)<17.99
                                         for u,v in positions[:index]),q["id"])
                checked += 1
        self.assertEqual(checked,9990)

    def test_legacy_progress_mapping(self):
        from hashlib import sha256
        html = self.html
        previous = json.loads(Path("geometry/previous_bank.json").read_text())
        mapping = json.loads(html.split('id="migration">',1)[1].split("</script>",1)[0])
        self.assertEqual(len(mapping),5000)
        self.assertEqual(mapping[:5],[1,2,3,4,5])
        self.assertIn(0,mapping)
        self.assertGreaterEqual(sum(bool(new) for new in mapping), 2700)
        self.assertTrue(all(not new or old == new for old,new in enumerate(mapping,1)))
        for key,new in zip(previous,mapping):
            if new:
                self.assertEqual(key,sha256(self.bank[new-1]["question"].encode()).hexdigest()[:20])


    def test_challenge_model_coverage_and_distinct_diagrams(self):
        from geometry.combined import TOPICS
        difficulty = Counter(q["difficulty"] for q in self.bank)
        self.assertGreaterEqual(difficulty["挑战"], 1250)
        from geometry.reasoning import reviewed_multistep
        self.assertTrue(all(reviewed_multistep(q) for q in self.bank if q["difficulty"] == "挑战"))
        self.assertFalse(any(q["category"] == "鸟头模型" and q.get("modelMode") == 23
                             and q["difficulty"] == "挑战" for q in self.bank))
        for group, variants in TOPICS.items():
            for model in variants.values():
                self.assertTrue(any(q["category"] == group and q["subcategory"] == model for q in self.bank), model)
        bodies = [re.sub(r"<title>[^<]*</title>", "", q[key])
                  for q in self.bank for key in ("questionSvg", "answerSvg")]
        self.assertEqual(len(set(bodies)), 10000)


    def test_retired_ids_match_changed_exercises(self):
        html = self.html
        ids = json.loads(html.split('id="retired6">',1)[1].split("</script>",1)[0])
        retired8 = json.loads(Path("geometry/retired_v8.json").read_text())
        expected = sorted({q["id"] for q in self.bank if q.get("modelMode",0) >= 27} | set(retired8))
        self.assertEqual(ids, expected)
        self.assertGreaterEqual(len(ids),460)
        pi = json.loads(html.split('id="retired7">',1)[1].split("</script>",1)[0])
        self.assertEqual(pi, sorted({q["id"] for q in self.bank if q.get("modelMode",0) >= 32} | set(retired8)))
        self.assertEqual(json.loads(html.split('id="retired8">',1)[1].split("</script>",1)[0]),retired8)
