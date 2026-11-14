"""Build a deterministic offline bank from coordinate constructions."""
from fractions import Fraction
from itertools import product
from random import Random
from .coordinates import area, intersection, midpoint
from .samples import build_samples, diagram
from .extension import construct

QUOTAS = {
    "长方形与正方形": 400, "平行四边形": 350, "梯形": 400, "三角形基础": 500,
    "三角形边角关系": 450, "等积模型": 450, "一半模型": 600, "风筝模型": 400,
    "蝴蝶模型": 450, "鸟头模型": 400, "燕尾模型": 400, "综合几何模型": 200,
}


def number(value):
    return str(Fraction(value))


def build_problem(group, mode, a, b, c):
    h = 2 * c
    u = a + b
    points = {"A": (0, 0), "B": (u, 0)}
    lines = []
    outline = "ABCD"
    unit = "cm²"
    target = ""
    known = ""
    metadata = {}
    additional = construct(group, mode, a, b, c) if mode >= 15 else None
    if additional:
        points, outline, lines, unit, known, target, answer, question, explanation = additional
    elif group == "燕尾模型" and mode >= 8:
        points.update(C=(u+2,h), D=(2,h))
        points["P"] = midpoint(points["A"],points["C"]) if mode % 2 else (Fraction(u+2,3),Fraction(h,3))
        lines = [("A","C"),("B","P"),("D","P")]
        numerator, denominator = (1,2) if mode % 2 else (1,3)
        outer = u*c
        known = f"平行四边形ABCD中，P在AC上，AP:AC＝{numerator}:{denominator}，△ABC面积为{outer}平方厘米"
        if mode % 3 == 0:
            target, answer = "APD", Fraction(outer*numerator,denominator)
            explanation = "△ADC与△ABC等积。△APD与△ACD从D到AC的高相同，再按底边比换算"
        elif mode % 3 == 1:
            target, answer = "BCP", Fraction(outer*(denominator-numerator),denominator)
            explanation = "先由AP:AC求PC:AC，再用从B到AC的公共高换算"
        else:
            target, answer = "CDP", Fraction(outer*(denominator-numerator),denominator)
            explanation = "△ACD与△ABC等积。△CDP与△CDA从D到AC的高相同，再按PC:AC换算"
        question = f"{known}。求△{target}面积。"
    elif group == "一半模型" and 12 <= mode <= 14:
        top = a
        points.update(C=(2+top,h), D=(2,h))
        points["M"] = midpoint(points["A"],points["B"])
        points["N"] = midpoint(points["A"],points["D"])
        points["P"] = midpoint(points["B"],points["C"])
        known = f"梯形ABCD中AB∥CD，AB＝{u}厘米，CD＝{top}厘米，高为{h}厘米"
        if mode == 12:
            lines = [("D","M")]
            question = f"{known}，M为AB中点。求△ADM面积。"
            target, answer = "ADM", Fraction(u*h,4)
            explanation = "以AM为底，高与梯形相同，AM是AB的一半"
        elif mode == 13:
            lines = [("B","N")]
            question = f"{known}，N为AD中点。求△ABN面积。"
            target, answer = "ABN", Fraction(u*h,4)
            explanation = "N到AB的距离是梯形高的一半"
        else:
            lines = [("N","P")]
            question = f"{known}，N、P分别是两腰中点。求梯形ABPN面积。"
            target, answer = "ABPN", Fraction((3*u+top)*h,8)
            explanation = "中位线NP等于两底和的一半，下半梯形的高等于原高的一半"
    elif group == "长方形与正方形" and 12 <= mode <= 14:
        points.update(C=(u,h),D=(0,h),E=(a,0),F=(a,c),G=(0,c))
        known = f"长方形ABCD中AB＝{u}厘米、BC＝{h}厘米。角A处剪去小长方形AEFG，AE＝{a}厘米、AG＝{c}厘米"
        lines = [("E","F"),("F","G")]
        if mode == 12:
            question = f"{known}。求剩余图形面积。"
            target, answer = "EBCDGF", u*h-a*c
            explanation = f"原面积{u}×{h}，剪去面积{a}×{c}，相减得到剩余面积"
        elif mode == 13:
            question = f"{known}。求剩余图形周长，答案须带单位。"
            target, answer, unit = "EBCDGF", 2*(u+h), "cm"
            explanation = "剪掉的一横一竖分别由凹口的一横一竖补回，周长等于原矩形周长"
        else:
            question = f"{known}。剪去面积占原图面积的几分之几？"
            target, answer, unit = "AEFG", Fraction(a*c,u*h), ""
            explanation = f"用剪去面积{a}×{c}除以原面积{u}×{h}，再约分"
    elif group == "平行四边形" and 12 <= mode <= 14:
        points.update(C=(u+2,h),D=(2,h))
        points["O"] = intersection(points["A"],points["C"],points["B"],points["D"])
        lines = [("A","C"),("B","D")]
        known = f"平行四边形ABCD的对角线交于O，AB＝{u}厘米，AB边对应高为{h}厘米"
        if mode == 12:
            question = f"{known}。求△ABO面积。"
            target, answer = "ABO", Fraction(u*h,4)
            explanation = "对角线互相平分，O到AB的距离为原高的一半"
        elif mode == 13:
            question = f"{known}。求△BCO面积。"
            target, answer = "BCO", Fraction(u*h,4)
            explanation = "AC平分整图面积，BO又平分△ABC的面积"
        else:
            question = f"{known}。求△ABO与△CDO的面积和。"
            answer = Fraction(u*h,2)
            explanation = "两块相对的区域各占总面积的四分之一"
    elif group == "等积模型" and mode >= 10:
        points.update(C=(a,h), D=(b+2,h), E=(a+1,0))
        lines = [("A","C"),("B","D")]
        outline = "ABC"
        if mode == 10:
            known = f"CD∥AB，△ABC面积为{u*c}平方厘米"
            question = f"C、D是直线AB同侧的两个不同点，{known}。求△ABD面积。"
            answer, target = u*c, "ABD"
            explanation = "△ABC与△ABD共用底AB，且C、D到AB等距"
            lines = [("A","D"),("B","D"),("C","D")]
            if points["C"] == points["D"]:
                points["D"] = (b+3,h)
        else:
            known = f"AE＝{a+1}厘米，AB＝{u}厘米，△ABC面积为{u*c}平方厘米"
            question = f"E在△ABC的边AB上，{known}。求△AEC面积。"
            answer, target = (a+1)*c, "AEC"
            lines = [("C","E")]
            explanation = "两三角形从C到直线AB的高相同，面积按底边之比换算"
    elif group == "一半模型" and mode >= 10:
        points.update(C=(u+2,h),D=(2,h))
        points["M"] = midpoint(points["A"], points["B"])
        points["N"] = midpoint(points["B"], points["C"])
        known = f"平行四边形ABCD面积为{u*h}平方厘米"
        if mode == 10:
            question = f"{known}，M为AB中点。求△ADM面积。"
            target, answer = "ADM", Fraction(u*h,4)
            lines = [("D","M")]
            explanation = "AM是AB的一半，△ADM的高与平行四边形的高相同"
        else:
            question = f"{known}，M为AB中点，N为BC中点。求△BMN面积。"
            target, answer = "BMN", Fraction(u*h,8)
            lines = [("M","N")]
            explanation = "△ABC占整图一半，△BMN与△BAC相似，面积是它的四分之一"
    elif group == "综合几何模型" and mode >= 10:
        points.update(C=(b+a,h),D=(b,h))
        points["O"] = intersection(points["A"],points["C"],points["B"],points["D"])
        lines = [("A","C"),("B","D")]
        points["M"] = midpoint(points["A"],points["O"])
        lines.append(("B","M"))
        known = f"梯形ABCD中AB∥CD，AB:CD＝{u}:{a}，△CDO面积为{number(area([points[n] for n in 'CDO']))}平方厘米"
        question = f"{known}。对角线交于O，M是AO中点。求△BMO面积。"
        target = "BMO"
        answer = area([points[n] for n in "CDO"])*Fraction(u*u,2*a*a)
        explanation = "先用蝴蝶模型将△CDO面积按底边平方比换成△ABO，再利用中点与共同高取一半"
    elif group in ("长方形与正方形", "平行四边形", "梯形"):
        offset = 0 if group == "长方形与正方形" else 2
        top = a if group == "梯形" else u
        if group == "长方形与正方形" and 4 <= mode < 8:
            u, h, top = a, a, a
            points["B"] = (u, 0)
        points.update(C=(offset + top, h), D=(offset, h), H=(offset, 0))
        total = Fraction((u + top) * h, 2)
        base = f"{group.split('与')[0]}ABCD" if group != "长方形与正方形" else ("正方形ABCD" if 4 <= mode < 8 else "长方形ABCD")
        if group == "梯形":
            dimensions = f"下底AB＝{u}厘米，上底CD＝{top}厘米"
        else:
            dimensions = f"底AB＝{u}厘米"
        if mode == 8 and group == "长方形与正方形":
            known, prompt = f"长AB＝{u}厘米，宽BC＝{h}厘米", "求周长"
            answer, explanation, unit = 2*(u+h), f"({u}＋{h})×2", "cm"
        elif mode == 8 and group == "梯形":
            points["M"] = midpoint(points["A"],points["D"])
            points["N"] = midpoint(points["B"],points["C"])
            lines.append(("M","N"))
            known, prompt = dimensions, "M、N分别是两腰中点，求中位线MN的长"
            answer, explanation, unit = Fraction(u+top,2), f"({u}＋{top})÷2", "cm"
        elif mode == 8:
            known, prompt = f"底AB＝{u}厘米，面积为{number(total)}平方厘米", "求底AB与其对应高的长度和"
            answer, explanation, unit = u+h, f"先求高：{number(total)}÷{u}＝{h}。再计算{u}＋{h}", "cm"
        elif mode == 9 and group != "梯形":
            # Use a 3–4–5 side displacement to obtain an exact sloping side.
            if group == "平行四边形":
                h, offset = 4*c, 3*c
                points.update(C=(u+offset,h),D=(offset,h),H=(offset,0))
                side = 5*c
            else:
                side = h
            known, prompt = f"周长为{2*(u+side)}厘米，边AB长{u}厘米", "求邻边BC长"
            answer, explanation, unit = side, f"{2*(u+side)}÷2－{u}", "cm"
        elif mode == 9:
            known, prompt = f"下底AB＝{u}厘米，高为{h}厘米，面积为{number(total)}平方厘米", "求上底CD长"
            answer, explanation, unit = top, f"{number(total)}×2÷{h}－{u}", "cm"
        elif mode % 4 == 0:
            known, prompt = f"{dimensions}，高为{h}厘米", "求面积"
            answer, explanation, target = total, f"({u}＋{top})×{h}÷2", outline
        elif mode % 4 == 1:
            known, prompt = f"{dimensions}，面积为{number(total)}平方厘米", "求高"
            answer, explanation, unit = h, f"{number(total)}×2÷({u}＋{top})", "cm"
        elif mode % 4 == 2:
            lines.append(("A", "C"))
            known, prompt = f"{dimensions}，高为{h}厘米", "连接AC，求△ABC的面积"
            answer, explanation, target = Fraction(u * h, 2), f"{u}×{h}÷2", "ABC"
        else:
            lines.append(("A", "C"))
            partial = Fraction(u*h, 2)
            known, prompt = f"{dimensions}，△ABC面积为{number(partial)}平方厘米", "连接AC，求△ACD的面积"
            answer, explanation, target = Fraction(top*h,2), f"{number(partial)}×{top}÷{u}", "ACD"
        if offset and (mode in (0, 2, 4, 6) or mode == 9 and group == "梯形"):
            lines.append(("D", "H"))
        question = f"{base}中，{known}。{prompt}。"
    elif group in ("风筝模型", "蝴蝶模型"):
        if group == "蝴蝶模型":
            points.update(C=(a+b-1,h), D=(b-1,h))
        else:
            points.update(C=(u+2,h), D=(1,h+c))
        points["O"] = intersection(points["A"],points["C"],points["B"],points["D"])
        lines = [("A","C"),("B","D")]
        regions = ("ABO","BCO","CDO","DAO")
        sizes = [area([points[n] for n in name]) for name in regions]
        k = mode % 4
        target = regions[k]
        known = "，".join(f"△{name}＝{number(value)}" for i,(name,value) in enumerate(zip(regions,sizes)) if i != k)
        if group == "蝴蝶模型" and mode >= 8:
            target = "ABO"
            known = f"AB:CD＝{u}:{a}，△CDO面积＝{number(sizes[2])}平方厘米"
            if mode % 3 == 0:
                target = "CDO"
                known = f"AB:CD＝{u}:{a}，△ABO面积＝{number(sizes[0])}平方厘米"
                answer = sizes[0]*Fraction(a*a,u*u)
                explanation = "对应底边的比给出相似比，用其平方由△ABO面积换算△CDO"
            else:
                answer = sizes[2]*Fraction(u*u,a*a)
                explanation = "先根据平行底边得到相似三角形，再把底边比平方以换算面积"
            question = f"梯形ABCD的对角线交于O，{known}。求△{target}面积。"
        elif group == "蝴蝶模型" and mode >= 4:
            target = "ABO"
            known = f"AB:CD＝{u}:{a}"
            answer = f"{Fraction(u*u,a*a).numerator}:{Fraction(u*u,a*a).denominator}"
            question = f"梯形ABCD的对角线交于O，{known}。求△ABO与△CDO的面积比。"
            unit, explanation = "", "上下三角形相似，面积比等于对应底边比的平方"
        elif group == "蝴蝶模型" and k in (1,3):
            question = f"梯形ABCD的对角线交于O。{known}（单位为平方厘米）。求△{target}面积。"
            answer, explanation = sizes[k], "△ABC与△ABD等底等高，减去公共部分后两翼等积"
        else:
            question = f"凸四边形ABCD的对角线交于O。{known}（单位为平方厘米）。求△{target}面积。"
            answer = sizes[(k+1)%4]*sizes[(k-1)%4]/sizes[(k+2)%4]
            explanation = "对角面积乘积相等，源于同底直线上的两组底边比"
    else:
        outline = "ABC"
        points["C"] = (a, h)
        points["D"] = (a, 0)
        points["M"] = midpoint(points["B"], points["C"])
        points["N"] = midpoint(points["A"], points["C"])
        total = Fraction(u*h,2)
        if group == "三角形边角关系":
            from math import radians, sin, cos
            if mode < 3:
                x, y = 25+a, 20+b
                angle = radians(x)
                length = u*sin(radians(y))/sin(radians(180-x-y))
                points["C"] = (length*cos(angle),length*sin(angle))
                if mode == 0:
                    known = f"∠A＝{x}°，∠B＝{y}°"
                    question = f"在△ABC中，{known}。求∠C。"
                    answer, explanation = 180-x-y, f"内角和减去两个已知角：180°－{x}°－{y}°"
                elif mode == 1:
                    points["E"] = (u+5,0)
                    lines = [("B","E")]
                    known = f"∠A＝{x}°，∠ACB＝{180-x-y}°"
                    question = f"在△ABC中，延长AB到E，{known}。求外角∠CBE。"
                    answer, explanation = 180-y, "三角形外角等于与它不相邻的两个内角之和"
                else:
                    known = f"∠A比∠B大{x-y}°，∠C＝{180-x-y}°" if x>=y else f"∠B比∠A大{y-x}°，∠C＝{180-x-y}°"
                    question = f"在△ABC中，{known}。求∠A。"
                    answer, explanation = x, "先用内角和求∠A和∠B的和，再结合角度之差求出∠A"
                unit = "°"
            elif mode < 6:
                points["C"] = (Fraction(u,2),u*sin(radians(25+a))/2/cos(radians(25+a)))
                known = f"AC＝BC，∠A＝{25+a}°"
                question = f"在△ABC中，{known}。求顶角∠C。"
                answer, unit, explanation = 180-2*(25+a),"°","等腰三角形两底角相等，180°减去两倍底角"
            elif mode < 9:
                x,y = a+2,b+2
                k = abs(x-y)+1
                points["B"] = (x,0)
                horizontal = Fraction(x*x+y*y-k*k,2*x)
                points["C"] = (horizontal,(y*y-horizontal*horizontal)**0.5)
                known = f"AB＝{x}厘米，AC＝{y}厘米"
                if mode == 6:
                    question = f"在△ABC中，{known}。若BC为整数厘米，BC最大是多少厘米？"
                    answer, explanation = x+y-1,"第三边严格小于另两边之和，所以最大整数为两边和减一"
                elif mode == 7:
                    question = f"在△ABC中，{known}。若BC为整数厘米，BC最小是多少厘米？"
                    answer, explanation = k,"第三边严格大于另两边之差，所以最小整数为两边差加一"
                else:
                    question = f"在△ABC中，{known}。若BC为整数厘米，BC有多少种可能？"
                    answer, explanation = 2*min(x,y)-1,"整数第三边介于两边差和两边和之间，两个端点都不计入"
                unit = "cm" if mode != 8 else ""
            else:
                points["C"] = (0,h)
                x = 15+a
                points["B"] = (h*sin(radians(90-x))/sin(radians(x)),0)
                known = f"∠A＝90°，∠B＝{x}°"
                answer, unit = 90-x,"°"
                question = f"在△ABC中，{known}。求∠C。"
                explanation = f"两个锐角互余，90°－{x}°"
        elif group == "三角形基础":
            lines = [("C","D")]
            if mode in (10,11,12):
                kind = mode-10
                x = a if kind == 0 else 0 if kind == 1 else -a
                points = {"A":(0,0), "B":(u,0), "C":(x,2*u)}
                known = f"AB＝{u}厘米。从C向直线AB作高，垂足D{'在AB内部' if kind == 0 else '与A重合' if kind == 1 else f'在AB的延长线上，且A在D、B之间，AD＝{a}厘米'}"
                if kind == 0:
                    known += f"，AD＝{a}厘米，CD＝{2*u}厘米"
                else:
                    known += f"，CD＝{2*u}厘米"
                lines = [("C","D")] if kind != 1 else []
                points["D"] = (x,0)
                if kind == 2:
                    lines.append(("D","A"))
                answer = ("锐角三角形","直角三角形","钝角三角形")[kind]
                explanation = ("垂足在AB内部，两底角为锐角；按给定长度，C处两条边的夹角也是锐角",
                               "CD垂直AB，且D就是A，因此∠A为直角",
                               "CD垂直AB，且A在D、B之间，∠CAB大于90°")[kind]
                question = f"△ABC中，{known}。按角分类，△ABC是哪一类三角形？"
                if kind == 0:
                    explanation = "A、B处均为锐角。C到AB的距离为AB的两倍，所以C处夹角也小于90°"
                metadata = {"answerType":"text", "alternatives":[answer[:2]]}
                unit = ""
            elif mode >= 8:
                points = {"A": (0,0), "B": (3*c,0), "C": (0,4*c)}
                lines = []
                known = f"AB＝{3*c}厘米，AC＝{4*c}厘米，BC＝{5*c}厘米"
                if mode == 8:
                    answer, unit, explanation = 12*c, "cm", f"{3*c}＋{4*c}＋{5*c}"
                    question = f"△ABC中，{known}。求周长。"
                else:
                    answer, unit, explanation = 3, "", "三边长度各不相等"
                    question = f"△ABC中，{known}。三条边中，有几个不同的长度？"
            elif mode % 3 == 0:
                known, answer, target = f"AB＝{u}厘米，高CD＝{h}厘米", total, "ABC"
                question, explanation = f"△ABC中，{known}。求面积。", f"{u}×{h}÷2"
            elif mode % 3 == 1:
                known, answer, unit = f"AB＝{u}厘米，面积＝{number(total)}平方厘米", h, "cm"
                question, explanation = f"△ABC中，{known}。求AB边上的高CD。", f"{number(total)}×2÷{u}"
            else:
                known, answer, target = f"AD＝{a}厘米，DB＝{b}厘米，CD＝{h}厘米，CD⊥AB", Fraction(b*h,2), "BDC"
                question, explanation = f"△ABC中，{known}。求△BDC面积。", f"{b}×{h}÷2"
        elif group in ("等积模型","燕尾模型"):
            lines = [("C","D")]
            known = f"AD:DB＝{a}:{b}，△ADC面积＝{number(Fraction(a*h,2))} cm²"
            target = "BDC" if mode % 2 else "ABC"
            answer = Fraction((b if mode%2 else u)*h,2)
            explanation = "各三角形共用从C到直线AB的高，面积与底边成正比"
            question = f"在△ABC中，D在AB上，{known}。求△{target}面积。"
            if group == "燕尾模型":
                points["P"] = midpoint(points["C"],points["D"])
                lines.extend([("A","P"),("B","P")])
                target = "PDB" if mode%2 else "APB"
                answer /= 2
                explanation = "先按公共高换算面积，再由P是CD中点将高减半"
                question = f"在△ABC中，D在AB上，P是CD中点，{known}。求△{target}面积。"
        else:
            lines = [("M","N")]
            known = f"M、N为BC、AC中点，△ABC面积＝{number(total)} cm²"
            if group == "一半模型" and mode % 2:
                lines = [("A","M")]
                target, answer = "ABM", total/2
                explanation = "BM是BC的一半，从A作出的高相同"
                known = f"M为BC中点，△ABC面积＝{number(total)} cm²"
                question = f"在△ABC中，{known}。求△ABM面积。"
            elif group == "综合几何模型":
                points["P"] = midpoint(points["M"],points["N"])
                lines.append(("C","P"))
                target, answer = ("CMP" if mode%2 else "CNP"), total/8
                explanation = "先用中位线相似得到面积的四分之一，再按中点等底分成两半"
                question = f"在△ABC中，{known}。P是MN中点，求△{target}面积。"
            elif group == "鸟头模型":
                r,s = mode%3+2,mode//3+2
                points["M"] = (Fraction(u,r)+Fraction(r-1,r)*a,Fraction(r-1,r)*h)
                points["N"] = (Fraction(s-1,s)*a,Fraction(s-1,s)*h)
                small = total/(r*s)
                target, answer = "CMN", small
                known = f"CM:CB＝1:{r}，CN:CA＝1:{s}，△ABC面积＝{number(total)} cm²"
                explanation = "两三角形共用夹角。先固定CN换算CM与CB，再固定CB换算CN与CA"
                question = f"在△ABC中，M在CB上，N在CA上。{known}。求△CMN面积。"
                if mode % 5 == 1:
                    target, answer = "ABC", total
                    known = f"CM:CB＝1:{r}，CN:CA＝1:{s}，△CMN面积＝{number(small)} cm²"
                    question = f"在△ABC中，M在CB上，N在CA上。{known}。求△ABC面积。"
                    explanation = f"沿两条射线把两边分别放大{r}倍和{s}倍，面积依次乘{r}和{s}"
                elif mode % 5 == 2:
                    lines.append(("B","N"))
                    target, answer = "CBN", total/s
                    known = f"CM:CB＝1:{r}，△CMN面积＝{number(small)} cm²"
                    question = f"在△ABC中，M在CB上，N在CA上。{known}。连BN，求△CBN面积。"
                    explanation = "△CMN与△CBN的底边同在CB上，从N到CB的高相同"
                elif mode % 5 == 3:
                    unit, answer = "", Fraction(1,r*s)
                    known = f"CM:CB＝1:{r}，CN:CA＝1:{s}"
                    question = f"在△ABC中，M在CB上，N在CA上。{known}。△CMN面积占△ABC面积的几分之几？"
                    explanation = "两边分两次用同高面积比换算，将两个边长比相乘"
                elif mode % 5 == 4:
                    lines.append(("A","M"))
                    target, answer = "AMN", total*(s-1)/(r*s)
                    known = f"CN:CA＝1:{s}，△CMN面积＝{number(small)} cm²"
                    question = f"在△ABC中，M在CB上，N在CA上。{known}。连AM，求△AMN面积。"
                    explanation = "从M到CA的高相同，△AMN与△CMN的面积之比等于AN:CN"
            else:
                target, answer = "CMN", total/4
                explanation = "中位线平行于底边，相似边长比1:2，面积比1:4"
                question = f"在△ABC中，{known}。求△CMN面积。"

    used = set(outline + target)
    for start, end in lines:
        used.update((start,end))
    if "O" in points:
        used.add("O")
    drawn = {n:p for n,p in points.items() if n in used}
    xs, ys = zip(*drawn.values())
    scale = min(290/(max(xs)-min(xs)),140/(max(ys)-min(ys)))
    labels = []
    cx, cy = sum(xs)/len(xs), sum(ys)/len(ys)
    for n,(x,y) in drawn.items():
        px,py = 65+(x-min(xs))*scale,185-(y-min(ys))*scale
        preferred = (-12 if x<cx else 12, 16 if y<cy else -7)
        options = [preferred, (-12,-8), (12,-8), (-12,17), (12,17),
                   (-24,5), (24,5), (0,-19), (0,26), (-33,-10), (33,-10)]
        def usable(dx,dy):
            tx,ty = px+dx,py+dy
            return 8 <= tx <= 412 and 16 <= ty <= 214 and all(
                abs(tx-lx)>=14 or abs(ty-ly)>=18 for lx,ly,_ in labels)
        dx,dy = next((d for d in options if usable(*d)), preferred)
        labels.append((px+dx,py+dy,n))
    if target and unit == "cm²" and Fraction(answer) != area([points[n] for n in target]):
        raise ValueError(f"Inconsistent shaded area for {question}")
    answer = answer if isinstance(answer,str) else number(answer)
    # Wrap known conditions into multiple lines under the drawing.
    import re
    clauses = re.split(r"(?<=[，、。])", known)
    rows = []
    row = ""
    for clause in clauses:
        if row and len(row+clause) > 22:
            rows.append(row)
            row = ""
        while len(clause) > 22:
            rows.append(clause[:22])
            clause = clause[22:]
        row += clause
    if row:
        rows.append(row)
    notes = tuple(rows)
    args = dict(segments=lines,labels=labels)
    regions = [(target,"#bfdbfe")] if target else ()
    if group == "平行四边形" and mode == 14:
        regions = [("ABO","#bfdbfe"),("CDO","#fde68a")]
    if ":" in answer and group == "蝴蝶模型":
        regions.append(("CDO","#fde68a"))
    return dict(category=group, modelMode=mode,
                construction={n:[str(value) for value in pair] for n,pair in drawn.items()},
                outline=outline, target=target, subcategory=explanation if len(explanation)<25 else question.split("求")[-1].strip("。"),
                question=question, answer=answer, unit=unit, answerType=metadata.get("answerType", "ratio" if ":" in answer else "number"),
                alternatives=metadata.get("alternatives", []), requiresUnit="答案须带单位" in question,
                geometryStatus="representative", givens={"description":known},
                solution=[explanation,f"答案为 {answer} {unit}".strip()],
                questionSvg=diagram(drawn,outline,notes=("示意图，形状不唯一",*notes),**args),
                answerSvg=diagram(drawn,outline,regions=regions,notes=("示意图，形状不唯一",*notes,f"答案 {answer} {unit}".strip()),**args))


def build_bank():
    result = build_samples()
    seen = {q["question"] for q in result}
    inputs = list(product(range(3,22),range(2,23),range(2,25),range(18)))
    Random(5000).shuffle(inputs)
    for group, quota in QUOTAS.items():
        remaining = quota - sum(q["category"] == group for q in result)
        count = 0
        for a,b,c,mode in inputs:
            question = build_problem(group,mode,a,b,c)
            if question["question"] in seen:
                continue
            seen.add(question["question"])
            identifier = len(result)+1
            if group == "综合几何模型" or (mode >= 15 and group in ("燕尾模型","梯形","一半模型")):
                difficulty = "挑战"
            elif group in ("风筝模型", "蝴蝶模型", "鸟头模型", "燕尾模型", "等积模型", "一半模型") or mode in (2,3):
                difficulty = "提高"
            else:
                difficulty = "基础"
            result.append(dict(question,id=identifier,difficulty=difficulty))
            count += 1
            if count == remaining:
                break
        if count != remaining:
            raise ValueError(f"{group}: {count}/{remaining}")
    return result
