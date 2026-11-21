"""Missing curriculum constructions; integration is owned by the bank builder."""
from fractions import Fraction as F
from math import cos, radians, sin, sqrt, tau

from .coordinates import intersection


MODELS = {
    "平行四边形": {40: "邻角互补", 41: "对角相等"},
    "三角形基础": {40: "按边分类·等边", 41: "按边分类·等腰", 42: "按边分类·不等边"},
    "三角形边角关系": {40: "等边三角形的角", 41: "多边形总外角和"},
    "长方形与正方形": {40: "两矩形拼成L形面积", 41: "两矩形拼成L形周长"},
    "综合几何模型": {40: "中线与分点连线交点面积"},
}


def construct_curriculum(group, mode, a, b, c):
    """Return the same nine fields as construct_varied(), or None if unsupported."""
    if mode not in MODELS.get(group, {}):
        return None
    lines, unit, target = [], "", ""
    if group == "平行四边形":
        theta, base, side = 30+(7*a+3*b+c) % 100, a+b, c+3
        dx, dy = side*cos(radians(theta)), side*sin(radians(theta))
        p = {"A": (0, 0), "B": (base, 0), "C": (base+dx, dy), "D": (dx, dy)}
        outline, unit = "ABCD", "°"
        known = f"平行四边形ABCD中，∠A＝{theta}°"
        if mode == 40:
            answer, ask = 180-theta, "∠B是多少度"
            explanation = f"AD∥BC，AB是截线，同旁内角互补。因此∠B＝180°－{theta}°＝{answer}°。"
        else:
            answer, ask = theta, "∠C是多少度"
            explanation = f"平行四边形相邻两角互补，∠B＝180°－{theta}°；∠C与∠B也互补，所以∠C＝{theta}°，即对角相等。"
    elif group == "三角形基础":
        outline = "ABC"
        if mode == 40:
            side = a+b+c
            p = {"A": (0, 0), "B": (side, 0), "C": (side/2, side*sqrt(3)/2)}
            known = f"△ABC中，AB＝BC＝CA＝{side}厘米"
            answer, explanation = "等边三角形", "三条边都相等，所以按边分类是等边三角形。等边三角形也是特殊的等腰三角形；本题填写更具体的类别。"
        elif mode == 41:
            side, base = 2*a+b, 2*a
            p = {"A": (0, sqrt(side*side-a*a)), "B": (-a, 0), "C": (a, 0)}
            known = f"△ABC中，AB＝AC＝{side}厘米，BC＝{base}厘米"
            answer, explanation = "等腰三角形", f"两边AB、AC相等，而底边BC长{base}厘米，与腰长{side}厘米不同，所以是等腰但不是等边三角形。"
        else:
            p = {"A": (0, 0), "B": (3*c, 0), "C": (0, 4*c)}
            known = f"△ABC中，AB＝{3*c}厘米，AC＝{4*c}厘米，BC＝{5*c}厘米"
            answer, explanation = "不等边三角形", "三条边的长度各不相同，所以按边分类是不等边三角形。它同时是直角三角形，这是按角分类，不能代替按边分类的答案。"
        ask = "按边分类，△ABC属于哪一类？若有更具体的类别，填写更具体的类别"
    elif group == "三角形边角关系":
        unit = "°"
        if mode == 40:
            side = a+b
            p = {"A": (0, 0), "B": (side, 0), "C": (side/2, side*sqrt(3)/2)}
            outline = "ABC"
            known = f"等边三角形ABC的每条边长{side}厘米"
            answer, ask = 60, "∠B是多少度"
            explanation = "三边相等，所以三个内角相等；三角形内角和180°，每个角为180°÷3＝60°。"
        else:
            n = 3+a % 20
            outline = "".join(chr(65+i) for i in range(n))
            p = {name: (10*cos(i*tau/n), 10*sin(i*tau/n)) for i, name in enumerate(outline)}
            p["W"] = tuple(p["B"][i]+(p["B"][i]-p["A"][i])/3 for i in (0, 1))
            lines = [("B", "W")]
            known = f"正{n}边形如图，在每个顶点各取一个沿边行进方向的外角，图中BW是AB的延长线"
            answer, ask = 360, "这些外角的总和是多少度"
            explanation = f"沿正{n}边形边界同向走一周，方向总共转过一整圈，即360°。每个顶点的外角是一次转向角，全部相加为360°，与边数无关。"
    elif group == "长方形与正方形":
        w, h = a+b, b+c
        p = {"A": (0, 0), "B": (w, 0), "C": (w, c), "D": (a, c),
             "E": (a, h), "F": (0, h), "G": (0, c)}
        outline, lines = "ABCDEF", [("G", "D")]
        known = f"长方形ABCG长AB＝{w}厘米、宽BC＝{c}厘米；长方形GDEF的GD＝{a}厘米、GF＝{b}厘米。两块沿GD拼接，内部不重叠，组成凹六边形ABCDEF"
        if mode == 40:
            target, answer, unit, ask = outline, w*c+a*b, "cm²", "凹六边形的总面积是多少平方厘米"
            explanation = f"两块内部不重叠，面积相加：{w}×{c}＋{a}×{b}＝{answer}平方厘米。公共边GD只有长度，没有面积，不需要扣面积。"
        else:
            answer, unit, ask = 2*(w+h), "cm", "凹六边形外边界的周长是多少厘米"
            explanation = f"先加两块周长，再去掉各自计入的一条公共边GD：2×({w}＋{c})＋2×({a}＋{b})－2×{a}＝{answer}厘米。公共边在图形内部，不属于外边界。"
    else:
        w, h = 2*(a+b)*c, 2*(2*a+b)
        p = {"A": (0, h), "B": (0, 0), "C": (w, 0), "D": (F(w, 2), 0),
             "E": (0, F(h*b, a+b))}
        p["P"] = intersection(p["A"], p["D"], p["C"], p["E"])
        outline, lines, unit, target = "ABC", [("A", "D"), ("C", "E")], "cm²", "BDP"
        parts = a+b
        total, partial, portion, answer = 2*parts*(2*a+b)*c, 2*a*(2*a+b)*c, 2*a*c, parts*b*c
        known = f"△ABC面积为{total}平方厘米，D是BC中点，E在AB上且AE:EB＝{a}:{b}，AD与CE交于P"
        ask = "△BDP的面积是多少平方厘米"
        explanation = (f"先按AB上的底边比分配，S(AEC)＝{total}×{a}÷{parts}＝{partial}。"
                       f"以△AEP为{a}份，则△BEP为{b}份，△ABP为{parts}份。"
                       f"D是BC中点，B、C到直线AD的高相等，故△ACP与△ABP等积，也是{parts}份。"
                       f"△AEC由△AEP与△ACP组成，共{2*a+b}份，每份面积＝{partial}÷{2*a+b}＝{portion}。"
                       f"因此S(BPC)＝{total}－2×{parts}×{portion}＝{2*parts*b*c}。"
                       f"BD＝DC，两块共用P到BC的高，S(BDP)＝{2*parts*b*c}÷2＝{answer}平方厘米。")
    question = f"{known}。{ask}。"
    return p, outline, lines, unit, known, target, answer, question, explanation
