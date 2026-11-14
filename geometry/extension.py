"""Additional constructions for the areas with few existing exercise types."""
from fractions import Fraction
from math import cos, sin, tau
from .coordinates import area, midpoint, intersection


def construct(group, mode, a, b, c):
    width, height = a+b, 2*c
    p = {"A": (0,0), "B": (width,0), "C": (width,height), "D": (0,height)}
    outline, segments, unit = "ABCD", [], "cm²"
    if mode >= 22:
        if group == "一半模型":
            p.update(C=(width+a,height),D=(a,height))
            p["M"] = midpoint(p["A"],p["B"])
            p["N"] = midpoint(p["D"],p["C"])
            p["P"] = intersection(p["A"],p["C"],p["M"],p["N"])
            segments = [("A","C"),("M","N"),("B","P")]
            known = f"平行四边形ABCD面积为{width*height}平方厘米，M、N分别是AB、CD的中点，AC与MN交于P"
            target, answer = ("ABP",Fraction(width*height,4)) if mode==22 else ("MBP",Fraction(width*height,8))
            prompt = f"求△{target}面积"
            method = "MN平行于AD，且M是AB中点，故P为AC中点。P到AB的高是原高的一半；再按所求三角形的底边计算。"
        elif group == "三角形基础":
            outline = "ABC"
            if mode == 22:
                p.update(B=(2*a,0),C=(a,height))
                known = f"等腰三角形ABC以AB为底，AB为{2*a}厘米，高CD为{height}厘米"
                p["D"] = (a,0)
                segments = [("C","D")]
                target, answer, prompt = "ACD",a*c,"D是高的垂足，求△ACD面积"
                method = "等腰三角形的顶角平分线、底边高和底边中线重合，所以AD等于AB的一半。"
            else:
                p.update(C=(-a,height),D=(-a,0))
                segments = [("C","D"),("D","A")]
                known = f"△ABC中，高CD的垂足D在BA的延长线上，DA为{a}厘米、AB为{width}厘米、CD为{height}厘米"
                target, answer, prompt = "ABC",width*c,"用△BCD与△ACD的面积差求△ABC面积"
                method = f"两块三角形共用高{height}，底分别是{width+a}和{a}，两面积相减得到△ABC的面积。"
        elif group == "鸟头模型":
            p.update(A=(-a,0), B=(2*a,0), C=(0,height), D=(0,-3*c), O=(0,0))
            outline = "ACBD"
            segments = [("A","B"),("C","D")]
            known = f"AB与CD交于O，AO:OB＝1:2，CO:OD＝2:3，△AOC面积为{a*c}平方厘米"
            target,answer = ("BOD",3*a*c) if mode == 22 else ("AOD",Fraction(3*a*c,2))
            prompt = f"求△{target}面积"
            method = ("先按AO:OB把△AOC面积扩大为△BOC的面积，再按CO:OD换算△BOD。"
                      if mode == 22 else "△AOC与△AOD共用底AO，C与D到AB的高之比等于CO:OD。")
        elif group == "等积模型":
            p.update(C=(width+a,height),D=(a,height))
            p["E"] = midpoint(p["A"],p["D"])
            p["F"] = midpoint(p["B"],p["C"])
            segments = [("E","F"),("A","F"),("D","F")]
            known = f"平行四边形ABCD面积为{width*height}平方厘米，E、F分别是AD、BC的中点"
            target, answer = ("ADF",Fraction(width*height,2)) if mode==22 else ("AEF",Fraction(width*height,4))
            prompt = f"求△{target}面积"
            method = "以AD为底，F和B到AD的高相同，所以△ADF与△ADB等积。若用AE为底，其底边又减半。"
        else:
            return None
        return p, outline, segments, unit, known, target, answer, f"{known}。{prompt}。", method
    if mode >= 20 and group == "长方形与正方形":
        # A rectangle split into a square and a smaller rectangle.
        p.update(B=(width,0), C=(width,a), D=(0,a), E=(a,0), F=(a,a))
        segments = [("E","F")]
        if mode == 20:
            known = f"长方形ABCD的长为{width}厘米，宽为{a}厘米，切去正方形AEFD"
            target, answer, prompt = "EBCF", a*b, "求剩下长方形的面积"
            method = f"切去的正方形边长等于原宽。剩下的长为{width}－{a}＝{b}厘米，面积为{a}×{b}"
        else:
            known = f"长方形ABCD的长为{width}厘米，宽为{a}厘米，分为正方形AEFD与长方形EBCF"
            target, answer, prompt = "AEFD", a*a, "求正方形的面积"
            method = f"正方形边长等于AD，即{a}厘米，面积为{a}×{a}"
    elif mode >= 20 and group == "风筝模型":
        p.update(C=(width+a,height),D=(1,3*c))
        p["O"] = intersection(p["A"],p["C"],p["B"],p["D"])
        segments = [("A","C"),("B","D")]
        left = area([p[n] for n in "ABO"])
        right = area([p[n] for n in ("BCO" if mode == 20 else "DAO")])
        fraction = left/right
        known = f"凸四边形ABCD的对角线交于O，△ABO与△{'BCO' if mode == 20 else 'DAO'}的面积之比为{fraction.numerator}:{fraction.denominator}"
        target, unit, answer = "", "", f"{fraction.numerator}:{fraction.denominator}"
        prompt = "求AO:OC" if mode == 20 else "求BO:OD"
        method = "两个三角形有共同的高，面积比等于相应的对角线分段之比"
    elif mode >= 20 and group == "等积模型":
        p.update(C=(a,height),D=(a,3*c),E=(a,0))
        outline = "ABD"
        segments = [("A","C"),("B","C"),("D","E")]
        known = f"C、D在AB同侧且在同一条垂线DE上，CE:DE＝2:3，△ABD面积为{Fraction(width*3*c,2)}平方厘米"
        target, answer, prompt = "ABC", width*c, "求△ABC的面积"
        method = "两个三角形共用AB，面积之比等于垂线上的高之比2:3"
    elif group == "三角形边角关系" and mode >= 18:
        n = a + 2
        outline = "".join(chr(65+i) for i in range(n))
        p = {name: (cos(i*tau/n),sin(i*tau/n)) for i,name in enumerate(outline)}
        segments = [(outline[0],name) for name in outline[2:-1]]
        unit, target = "°", ""
        if mode == 18:
            known = f"凸{n}边形的各顶点如图，从A向不相邻的顶点作对角线"
            answer, prompt = (n-2)*180, "求所有内角的和"
            method = f"从A把凸{n}边形分成{n-2}个三角形，内角和为{n-2}×180°"
        else:
            known = f"正{n}边形各边相等、各角相等"
            answer, prompt = Fraction(360,n), "沿边走一周时，每个顶点的外角是多少度"
            segments = []
            method = f"沿边走一圈共转360°，{n}个顶点等分一整圈"
    elif group == "一半模型":
        p.update(M=midpoint(p["A"],p["B"]), N=midpoint(p["B"],p["C"]),
                 P=midpoint(p["C"],p["D"]), Q=midpoint(p["D"],p["A"]))
        segments = list(zip("MNPQ","NPQM"))
        known = f"长方形ABCD长{width}厘米，宽{height}厘米，M、N、P、Q依次是四边中点"
        target = "MNPQ" if mode%2 == 0 else "AMQ"
        answer = Fraction(width*height, 2 if mode%2 == 0 else 8)
        prompt = f"求四边形{target}的面积" if target == "MNPQ" else "求△AMQ面积"
        method = "每个角上的三角形面积都是长方形面积的八分之一"
    elif group == "平行四边形":
        p.update(C=(width+a,height), D=(a,height))
        p["M"] = midpoint(p["A"],p["B"])
        p["N"] = midpoint(p["C"],p["D"])
        segments = [("M","N"),("D","M")]
        known = f"平行四边形ABCD底AB长{width}厘米，高{height}厘米，M、N分别为AB、CD中点"
        target = "AMND" if mode%2 == 0 else "DMN"
        answer = Fraction(width*height,2 if target == "AMND" else 4)
        prompt = f"求四边形{target}的面积" if target == "AMND" else "求△DMN面积"
        method = "中点连线把平行四边形分成面积相等的两部分，DM再平分左半部分"
    elif group == "蝴蝶模型":
        side = height if mode == 16 else width
        p.update(B=(side,0), C=(side,height), D=(0,height))
        if mode == 17:
            p.update(C=(width+a,height),D=(a,height))
        p["O"] = intersection(p["A"],p["C"],p["B"],p["D"])
        segments = [("A","C"),("B","D")]
        shape = {15:"长方形",16:"正方形",17:"平行四边形"}[mode]
        known = f"{shape}ABCD面积为{side*height}平方厘米，两条对角线交于O"
        target = {15:"ABO",16:"BCO",17:"CDO"}[mode]
        answer, prompt = Fraction(side*height,4), f"求△{target}面积"
        method = "一条对角线平分整图，另一条对角线经过其中点，各小三角形占整图四分之一"
    elif group == "梯形":
        p.update(C=(width,height),D=(b,height),B=(width+b,0))
        p["H"] = (b,0)
        segments = [("D","H")]
        known = f"等腰梯形ABCD下底AB长{width+b}厘米，上底CD长{width-b}厘米，高DH为{height}厘米"
        target, answer, prompt = "ADH", Fraction(b*height,2), "H为D到AB的垂足，求△ADH面积"
        method = f"两腰等长，两端的水平距离相等，各为({width+b}－{width-b})÷2＝{b}厘米"
    elif group == "燕尾模型":
        outline = "ABC"
        p["C"] = (a,height)
        p["D"] = (a,0)
        p["P"] = (a,Fraction(height,3 if mode%2==0 else 4))
        p["Q"] = midpoint(p["P"],p["C"])
        segments = [("C","D"),("A","P"),("B","P"),("A","Q"),("B","Q")]
        divisor = 3 if mode%2==0 else 4
        known = f"△ABC中D在AB上，P在CD上，DP:DC＝1:{divisor}，Q是PC中点，△ABC面积为{width*c}平方厘米"
        target = "AQB" if mode < 17 else "ADQ"
        base_area = width*c if target == "AQB" else a*c
        if target == "ADQ":
            known += f"，AD:AB＝{a}:{width}"
        answer = Fraction(base_area*(divisor+1),2*divisor)
        prompt = f"求△{target}面积"
        method = "从底边到Q的高等于原高的(1＋1/分母)÷2，再按底边比例折算"
    else:
        return None
    return p, outline, segments, unit, known, target, answer, f"{known}。{prompt}。", method
