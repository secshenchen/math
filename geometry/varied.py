"""Additional reasoning paths for the most repeated exercise families."""
from fractions import Fraction as F
from math import cos, radians, sin

from .coordinates import area, intersection, midpoint

MODELS = {
    "三角形基础": ("面积差反求分点", "由局部面积求高再求整体", "中点与面积差"),
    "等积模型": ("三段共高分配", "两处中点合并面积", "跨底边与中点"),
    "风筝模型": ("四边形总面积补翼", "对角线分段求半翼", "相邻面积反推全图"),
    "梯形": ("中位线还原上下底", "等腰梯形反求余部"),
    "蝴蝶模型": ("上下两块反推侧翼", "面积差与底边比"),
    "三角形边角关系": ("外角与角平分线", "两外角反求第三角"),
    "一半模型": ("中点与对角线分区", "边中点反推外部面积"),
    "燕尾模型": ("燕尾面积差与对角线",),
}
def construct_varied(group, mode, a, b, c):
    k = mode - 32
    w, h = a+b, 2*c
    ab, db = f"AB长{w}厘米", f"DB长{b}厘米"
    total, left, right = w*c, a*c, b*c
    p = {"A": (0,0), "B": (w,0), "C": (a,h), "D": (a,0)}
    outline, lines, unit = "ABC", [("C","D")], "cm²"
    if group == "三角形基础":
        if k == 0:
            known = f"△ABC面积为{total}平方厘米，CD是高且垂足D在边AB上，CD长{h}厘米，△BCD面积为{right}平方厘米"
            target, answer, ask, unit = "", a, "AD长多少厘米", "cm"
            reason = f"先减去△BCD求得△ACD面积为{left}平方厘米，再由AD＝2×△ACD的面积÷CD，得AD＝{a}厘米。"
        elif k == 1:
            known = f"△ACD面积为{left}平方厘米，CD是高且垂足D在边AB上，AD长{a}厘米，{db}"
            target, answer, ask = "ABC", total, "△ABC面积"
            reason = f"先由△ACD的面积求出高CD＝{left}×2÷{a}＝{h}厘米，再用(AD＋DB)×CD÷2求全图面积。"
        else:
            p["M"] = midpoint(p["C"],p["D"])
            lines.append(("B","M"))
            known = f"△ABC面积为{total}平方厘米，D在AB上，△ACD面积为{left}平方厘米，M为CD中点，连接BM"
            target, answer, ask = "BDM", F(right,2), "△BDM面积"
            reason = f"先从全图减去△ACD，得到△BCD面积{right}平方厘米。△BDM与△BCD共用BD；M在CD中点，高减半。"
    elif group == "等积模型":
        if k == 0:
            p["E"] = (a+b+c,0)
            p["B"] = (a+b+c+b,0)
            lines.append(("C","E"))
            known = f"D、E依次在AB上，AD:DE:EB＝{a}:{b+c}:{b}，△ABC面积为{(a+2*b+c)*c}平方厘米"
            target, answer, ask = "DCE", (b+c)*c, "中间的△DCE面积"
            reason = f"三块共用从C到AB的高。先算总份数{a+2*b+c}，再按DE的{b+c}份从整图分配中间面积。"
        elif k == 1:
            p.update(E=(F(a,2),0), F=(a+F(b,2),0))
            lines.extend([("C","E"),("C","F")])
            known = f"D在AB上，E、F分别为AD、DB的中点，△ACD、△DCB面积分别为{left}、{right}平方厘米"
            target, answer, ask = "ECF", F(total,2), "合并△ECD和△DCF后的面积"
            reason = f"对△ACD取一半得到△ECD面积{F(left,2)}；对△DCB取一半得到△DCF面积{F(right,2)}。把相邻两块相加。"
        else:
            p["P"] = midpoint(p["B"],p["C"])
            lines.extend([("A","P"),("D","P")])
            known = f"D在AB上，AD:DB＝{a}:{b}，P为BC中点，△ACD面积为{left}平方厘米，连接AP、DP"
            target, answer, ask = "BDP", F(right,2), "△BDP面积"
            reason = f"先用BD:AD和共高从△ACD算出△BCD面积{right}，再用BP:BC＝1:2取半，得到△BDP。"
    elif group in ("风筝模型","蝴蝶模型"):
        outline, lines = "ABCD", [("A","C"),("B","D")]
        p.update(C=(w,h), D=(b,h if group == "蝴蝶模型" else h+c))
        p["O"] = intersection(p["A"],p["C"],p["B"],p["D"])
        upper, wing, lower, other = (area([p[i] for i in shape]) for shape in ("ABO","BCO","CDO","DAO"))
        if group == "蝴蝶模型":
            if k == 0:
                known = f"梯形ABCD中AB∥CD，对角线交于O，△ABO面积为{upper}、△CDO面积为{lower}平方厘米"
                target, answer, ask = "BCO", wing, "△BCO面积"
                reason = "两侧翼面积相等。对角线相交给出△ABO与△CDO面积的乘积等于两侧翼面积的乘积，取正平方根得到一翼。"
            else:
                known = f"梯形ABCD中AB∥CD，对角线交于O，AB:CD＝{w}:{a}，△ABO面积比△CDO大{upper-lower}平方厘米"
                target, answer, ask = "CDO", lower, "△CDO面积"
                reason = f"上下三角形相似，面积比为{w*w}:{a*a}。差占{w*w-a*a}份；先求一份，再取{a*a}份。"
        elif k == 0:
            known = f"凸四边形ABCD的对角线交于O，ABCD面积为{upper+wing+lower+other}平方厘米，△ABO面积为{upper}、△BCO面积为{wing}平方厘米"
            target, answer, ask = "DAO", other, "△DAO面积"
            reason = f"从总面积扣除△ABO与△BCO，得另两块之和{lower+other}。两组共高三角形都按AO:OC＝{upper}:{wing}分配，取靠AO的一块。"
        elif k == 1:
            p["M"] = midpoint(p["O"],p["D"])
            lines.append(("C","M"))
            known = f"凸四边形ABCD的对角线交于O，M为OD中点，△ABO、△BCO、△DAO的面积分别为{upper}、{wing}、{other}平方厘米"
            target, answer, ask = "COM", lower/2, "△COM面积"
            reason = f"对角面积乘积相等，先求△CDO＝△BCO面积×△DAO面积÷△ABO面积＝{lower}平方厘米。再沿OD按OM:OD取一半。"
        else:
            p["M"] = midpoint(p["B"],p["O"])
            lines.extend([("A","M"),("C","M")])
            known = f"凸四边形ABCD的对角线交于O，M为BO中点，△AOM、△COM、△CDO的面积分别为{upper/2}、{wing/2}、{lower}平方厘米"
            target, answer, ask = "ABCD", upper+wing+lower+other, "四边形ABCD面积"
            reason = f"把中点两块分别翻倍，找回△ABO和△BCO；由对角面积乘积相等求△DAO面积{other}，再加四块。"
    elif group == "梯形":
        if k == 0:
            p.update(C=(w,h), D=(b,h))
            p.update(M=midpoint(p["A"],p["D"]), N=midpoint(p["B"],p["C"]))
            outline, lines = "ABCD", [("M","N"),("A","C")]
            known = f"梯形ABCD中AB∥CD，M、N是两腰中点，MN长{F(w+a,2)}厘米，{ab}，梯形面积为{(w+a)*c}平方厘米"
            target, answer, ask = "ACD", a*c, "△ACD面积"
            reason = f"先用CD＝2MN－AB求出CD长{a}厘米；再用梯形面积÷MN得到高{h}厘米，最后用CD与高求△ACD面积。"
        else:
            p.update(B=(a+2*b,0), C=(a+b,h), D=(b,h), H=(b,0))
            outline, lines = "ABCD", [("D","H")]
            known = f"等腰梯形ABCD中AB∥CD，梯形面积为{(2*a+2*b)*c}平方厘米，AB、CD分别长{a+2*b}、{a}厘米，H为D在边AB上的垂足"
            target, answer, ask = "BCDH", (2*a+b)*c, "去掉△ADH以后余下的面积"
            reason = f"两腰等长，AH＝(AB－CD)÷2＝{b}厘米。用梯形总面积÷中位线求高{h}厘米，再扣掉△ADH面积{b*c}平方厘米。"
    elif group == "三角形边角关系":
        x, y = 25+a, 20+b
        length = w*sin(radians(y))/sin(radians(180-x-y))
        p = {"A": (0,0), "B": (w,0), "C": (length*cos(radians(x)),length*sin(radians(x))),
             "E": (w+5,0)}
        lines, target, unit = [("B","E")], "", "°"
        if k == 0:
            # The internal angle bisector divides the opposite side in the ratio AB:BC.
            bc = w*sin(radians(x))/sin(radians(180-x-y))
            p["M"] = (p["C"][0]*w/(w+bc),p["C"][1]*w/(w+bc))
            lines.append(("B","M"))
            known = f"延长AB到E，外角∠CBE为{180-y}度，BM平分∠ABC，M在AC上"
            answer, ask = F(y,2), "∠ABM的度数"
            reason = f"先用邻补角得∠ABC＝180度－{180-y}度＝{y}度，再由角平分线取一半。"
        else:
            p["F"] = (-5,0)
            lines.append(("A","F"))
            known = f"A、B两端分别向外延长AB至F和E，外角∠FAC为{180-x}度，∠CBE为{180-y}度"
            answer, ask = 180-x-y, "∠ACB的度数"
            reason = f"由邻补角分别还原∠A＝{x}度、∠B＝{y}度，再从180度中减去这两个内角。"
    elif group == "一半模型":
        p.update(C=(w+a,h), D=(a,h), M=(a,0))
        outline = "ABCD"
        if k == 0:
            p["M"] = midpoint(p["A"],p["B"])
            p["O"] = midpoint(p["A"],p["C"])
            lines = [("A","C"),("B","D"),("M","O")]
            known = f"平行四边形ABCD的两条对角线交于O，M为AB中点，△AMO面积为{F(total,4)}平方厘米"
            target, answer, ask = "ABCD", 2*total, "平行四边形ABCD面积"
            reason = "M为AB中点，先把△AMO面积乘2得到△ABO；两条对角线把整图分成四块等积三角形，再乘4。"
        else:
            p["N"] = midpoint(p["C"],p["D"])
            lines = [("A","N"),("B","N")]
            known = f"平行四边形ABCD中N为CD中点，△ADN面积为{F(total,2)}平方厘米，连接AN、BN"
            target, answer, ask = "BCN", F(total,2), "从平行四边形减去△ADN、△ABN后余下的△BCN面积"
            reason = "△ADN与△CDA同高、底长减半，面积为全图的四分之一。△ABN占全图一半；扣除这两块后余下全图的四分之一。"
    else:
        p.update(C=(w+a,h), D=(a,h))
        p["O"] = midpoint(p["A"],p["C"])
        p["M"] = midpoint(p["A"],p["O"])
        outline, lines = "ABCD", [("A","C"),("B","D"),("B","M")]
        known = f"平行四边形ABCD的对角线交于O，M是AO的中点，△ABC的面积比△BMO多{F(3*total,4)}平方厘米"
        target, answer, ask = "CDO", F(total,2), "△CDO面积"
        reason = "对角线互相平分，△ABO占△ABC的一半；M再把AO平分，所以面积差占△ABC的四分之三。还原△ABC后取一半得到△CDO。"
    return p, outline, lines, unit, known, target, answer, f"{known}。求{ask}。", reason
