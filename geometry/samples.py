"""Reference problems for the first geometry-to-SVG acceptance checks."""
from fractions import Fraction
from html import escape
from math import hypot
import re

from .coordinates import area, intersection, midpoint


def wrap_notes(text, width=22):
    rows, row = [], ""
    for token in re.findall(r"\d+(?:[./:]\d+)*(?:平方厘米|厘米|cm²|cm|°|度)?|cm²|[A-Za-z]+|.",text):
        if row and len(row+token)>width and token not in "，。；、：？！":
            rows.append(row)
            row = ""
        row += token
    if row:
        rows.append(row)
    return tuple(rows)


def diagram(points, outline, *, segments=(), regions=(), labels=(), notes=(), equal_pairs=(), label_guides=()):
    width, height = 420, max(312, 252 + 28 * len(notes))
    xs, ys = zip(*points.values())
    scale = min(290 / (max(xs) - min(xs)), 140 / (max(ys) - min(ys)))

    def project(point):
        x, y = point
        return 65 + (x - min(xs)) * scale, 185 - (y - min(ys)) * scale

    def polygon(names, fill, stroke):
        vertices = " ".join(f"{x:.3f},{y:.3f}" for x, y in (project(points[n]) for n in names))
        return f'<polygon points="{vertices}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'

    def label(x, y, text, anchor="start"):
        length = sum(16 if ord(char)>255 else 10 for char in text)
        fit = ' textLength="365" lengthAdjust="spacingAndGlyphs"' if anchor == "start" and length > 365 else ""
        halo = ' paint-order="stroke" stroke="white" stroke-width="2.5" stroke-linejoin="round"' if anchor == "middle" else ""
        return f'<text x="{x:.3f}" y="{y:.3f}" text-anchor="{anchor}"{fit}{halo}>{escape(text)}</text>'

    elements = ['<title>几何关系图</title>', '<desc>' + escape("；".join(text for _, _, text in labels) + "；" + "；".join(notes)) + '</desc>']
    elements += [polygon(names, fill, "none") for names, fill in regions]
    elements.append(polygon(outline, "none", "#26334a"))
    for a, b in segments:
        x1, y1 = project(points[a])
        x2, y2 = project(points[b])
        elements.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="#26334a" stroke-width="2"/>')
    for count, pair in enumerate(equal_pairs, 1):
        for a, b in pair:
            x1, y1 = project(points[a])
            x2, y2 = project(points[b])
            length = hypot(x2 - x1, y2 - y1)
            ux, uy = (x2 - x1) / length, (y2 - y1) / length
            for tick in range(count):
                offset = (tick - (count - 1) / 2) * 5
                x = (x1 + x2) / 2 + ux * offset
                y = (y1 + y2) / 2 + uy * offset
                elements.append(
                    f'<line x1="{x - uy * 5:.3f}" y1="{y + ux * 5:.3f}" '
                    f'x2="{x + uy * 5:.3f}" y2="{y - ux * 5:.3f}" '
                    'stroke="#26334a" stroke-width="2" class="equal-length"/>'
                )
    for name, x, y in label_guides:
        px, py = project(points[name])
        elements.append(f'<line class="label-guide" x1="{px:.3f}" y1="{py:.3f}" x2="{x:.3f}" y2="{y:.3f}" stroke="#64748b" stroke-width="1" stroke-dasharray="2 2"/>')
    elements.extend(label(x, y, text, "middle") for x, y, text in labels)
    elements.extend(label(18, 242 + 28 * i, text) for i, text in enumerate(notes))
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" font-family="sans-serif" font-size="16" fill="#172944">' + "".join(elements) + '</svg>'


def build_samples():
    rectangle = {"A": (0, 0), "B": (12, 0), "C": (12, 7), "D": (0, 7),
                 "P": (11, 0), "Q": (11, 1), "R": (12, 1)}
    triangle = {"A": (4, 12), "B": (0, 0), "C": (16, 0)}
    triangle["D"] = midpoint(triangle["A"], triangle["B"])
    triangle["E"] = midpoint(triangle["A"], triangle["C"])
    trapezoid = {"A": (3, 6), "B": (7, 6), "C": (10, 0), "D": (0, 0)}
    trapezoid["O"] = intersection(trapezoid["A"], trapezoid["C"], trapezoid["B"], trapezoid["D"])
    ratio = area([trapezoid[n] for n in "ABO"]) / area([trapezoid[n] for n in "CDO"])
    assert ratio == Fraction(4, 25)
    parallelogram = {"A": (0, 0), "B": (14, 0), "C": (20, 4), "D": (6, 4)}
    kite = {"A": (-4, 0), "B": (3, 6), "C": (8, 0), "D": (Fraction(-3, 2), -3)}
    kite["O"] = intersection(kite["A"], kite["C"], kite["B"], kite["D"])
    samples = [
        (
            "长方形与正方形", "长方形面积", "基础", "长方形ABCD中，AB长12厘米，BC长7厘米，求面积。",
            str(area([rectangle[n] for n in "ABCD"])), "number", "cm²",
            ["长方形面积＝长×宽", "12×7＝84（平方厘米）"],
            {"AB": 12, "BC": 7, "angleABC": 90}, "determined",
            rectangle, "ABCD", [("P", "Q"), ("Q", "R")],
            [(52, 202, "A"), (318, 202, "B"), (318, 44, "C"), (52, 44, "D"),
             (185, 205, "12 cm"), (333, 116, "7 cm")],
            (), [("ABCD", "#dbeafe")], "12 × 7",
        ),
        (
            "一半模型", "三角形两边中点", "提高", "三角形ABC面积为96平方厘米。D、E分别是AB、AC的中点，求三角形ADE的面积。",
            str(area([triangle[n] for n in "ADE"])), "number", "cm²",
            ["DE连接两边中点，故DE∥BC", "△ADE与△ABC的对应边之比为1:2，面积比为1:4", "96÷4＝24（平方厘米）"],
            {"areaABC": 96, "midpoints": {"D": "AB", "E": "AC"}}, "representative",
            triangle, "ABC", [("D", "E")],
            [(110, 37, "A"), (53, 202, "B"), (262, 202, "C"), (79, 109, "D"), (191, 111, "E")],
            ("S(△ABC)＝96 cm²", "示意图，形状不唯一"), [("ADE", "#bfdbfe")], "DE ∥ BC，边长比 1:2，面积比 1:4",
        ),
        (
            "蝴蝶模型", "梯形上下三角形", "提高", "梯形ABCD的上底AB与下底CD之比为2:5，对角线交于O，求△ABO与△CDO的面积比。",
            f"{ratio.numerator}:{ratio.denominator}", "ratio", "",
            ["AB∥CD且∠AOB＝∠COD，故△ABO∽△CDO", "对应边之比为2:5，面积比为4:25"],
            {"parallel": ["AB", "CD"], "ratioABCD": "2:5"}, "representative",
            trapezoid, "ABCD", [("A", "C"), ("B", "D")],
            [(125, 42, "A"), (235, 42, "B"), (312, 202, "C"), (50, 202, "D"), (198, 101, "O")],
            ("AB:CD＝2:5", "示意图，形状不唯一"), [("ABO", "#bfdbfe"), ("CDO", "#fde68a")], "△ABO ∽ △CDO",
        ),
        (
            "平行四边形", "对角线分割面积", "基础",
            "平行四边形ABCD的面积为56平方厘米。连接AC，求三角形ABC的面积。",
            str(area([parallelogram[n] for n in "ABC"])), "number", "cm²",
            ["△ABC与△CDA的三组对应边分别相等，因此两个三角形全等", "56÷2＝28（平方厘米）"],
            {"areaABCD": 56, "diagonal": "AC"}, "representative",
            parallelogram, "ABCD", [("A", "C")],
            [(54, 203, "A"), (270, 203, "B"), (368, 124, "C"), (148, 118, "D")],
            ("S(ABCD)＝56 cm²", "示意图，形状不唯一"), [("ABC", "#bfdbfe")], "△ABC与△CDA面积相等",
        ),
        (
            "风筝模型", "对角面积乘积", "提高",
            "凸四边形ABCD的对角线交于O。△AOB、△BOC、△DOA的面积分别为12、24、6平方厘米，求△COD的面积。",
            str(area([kite[n] for n in "COD"])), "number", "cm²",
            ["△AOB与△BOC对直线AC共用高，故AO:OC＝12:24＝1:2",
             "△DOA与△COD也对直线AC共用高，故面积比同为1:2", "6×2＝12（平方厘米）"],
            {"areaAOB": 12, "areaBOC": 24, "areaDOA": 6}, "representative",
            kite, "ABCD", [("A", "C"), ("B", "D")],
            [(54, 143, "A"), (179, 36, "B"), (265, 143, "C"), (102, 204, "D"), (124, 128, "O"),
             (122, 100, "12"), (175, 113, "24"), (98, 158, "6")],
            ("面积单位：cm²", "示意图，形状不唯一"), [("COD", "#bfdbfe")], "AO:OC＝1:2，所以 6×2＝12",
        ),
    ]
    questions = []
    for i, sample in enumerate(samples, 1):
        (category, subcategory, difficulty, question, answer, answer_type, unit, solution,
         givens, status, points, outline, segments, labels, notes, highlights, explanation) = sample
        # The student diagram marks the target without displaying its value.
        question_regions = highlights if i == 2 else ()
        answer_notes = (explanation, f"答案 {answer} {unit}".rstrip())
        if status == "representative":
            answer_notes = (notes[0], explanation, f"答案 {answer} {unit}".rstrip())
            labels = (*labels, (325, 25, notes[-1]))
        equal_pairs = ((("A", "D"), ("D", "B")), (("A", "E"), ("E", "C"))) if i == 2 else ()
        questions.append({
            "id": i, "category": category, "subcategory": subcategory, "difficulty": difficulty,
            "question": question, "answer": answer, "answerType": answer_type, "unit": unit,
            "solution": solution, "givens": givens, "geometryStatus": status,
            "questionSvg": diagram(points, outline, segments=segments, regions=question_regions, labels=labels, notes=notes[:1], equal_pairs=equal_pairs),
            "answerSvg": diagram(points, outline, segments=segments, regions=highlights, labels=labels, notes=answer_notes, equal_pairs=equal_pairs),
        })
    return questions
