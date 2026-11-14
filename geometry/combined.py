"""Constructions that require combining area relationships."""
from fractions import Fraction as F

from .coordinates import intersection, midpoint

TOPICS = {
    "一半模型": {
        27: "顶天立地", 28: "锯齿", 29: "交头接耳", 30: "离家出走",
    },
    "鸟头模型": {27: "互补夹角", 28: "沙漏", 29: "金字塔"},
    "综合几何模型": {
        27: "燕尾与中点", 28: "风筝与中点", 29: "平行四边形与燕尾",
        30: "中点与梯形蝴蝶", 31: "鸟头与相似",
    },
}


def construct_combined(group, mode, a, b, c):
    w, h = a+b, 2*c
    s = w*h
    outline = "ABCD"
    p = {"A": (0,0), "B": (w,0), "C": (w+a,h), "D": (a,h)}
    if group == "一半模型":
        if mode == 27:
            p.update(M=(a,0), P=(a+F(w,3),h))
            lines = [("A","P"),("B","P"),("M","P")]
            given = f"平行四边形ABCD面积为{s}平方厘米，P在CD上，M在AB上且AM:MB＝{a}:{b}"
            target, answer = "AMP", F(a*h,2)
            reason = "△ABP与平行四边形同底等高，面积是整图的一半。△AMP与△ABP同高，再按AM:AB分配。"
        elif mode == 28:
            p.update(M=(a,0), P=(a+F(w,3),h), Q=(a+F(2*w,3),h))
            lines = [("A","P"),("P","M"),("M","Q"),("Q","B")]
            given = f"平行四边形ABCD面积为{s}平方厘米，M在AB上，P、Q从D到C三等分CD，沿A、P、M、Q、B连成折线"
            target, answer = "PMQ", F(s,6)
            reason = "三块锯齿三角形的高都是平行四边形的高。△PMQ的底PQ是CD的三分之一，因此面积为整图的六分之一。"
        elif mode == 29:
            p["M"], p["N"] = (a,0), (a+F(w,2),h)
            p["P"] = intersection(p["B"], p["N"], p["C"], p["M"])
            lines = [("B","N"),("M","C")]
            given = f"平行四边形ABCD面积为{s}平方厘米，M在AB上且AM:MB＝{a}:{b}，N是CD中点，BN与CM交于P"
            target, answer = "MBP", F(h*b*b,w+2*b)
            reason = "交叉线与两条平行边组成相似三角形MBP与CNP。其高之比等于MB:CN；先从原图高分出△MBP的高，再乘MB除以二。"
        else:
            p["P"] = (w+a+b,h)
            lines = [("C","P"),("A","P"),("B","P"),("B","C")]
            given = f"平行四边形ABCD面积为{s}平方厘米，AB长{w}厘米，将DC延长到P，使CP长{b}厘米"
            target, answer = "BCP", F(h*b,2)
            reason = "P虽在图外，但P、C仍在平行于AB的直线上。△ABP占整图一半，再用△BCP与△ABP的底长比CP:AB换算。"
    elif group == "鸟头模型":
        if mode == 27:
            p = {"O":(0,0),"A":(-a,0),"B":(b,0),"C":(a,h),"D":(F(3*a,2),F(3*h,2))}
            outline = "ACDB"
            lines = [("O","C"),("O","D")]
            given = f"A、O、B依次共线，C、D在从O出发的同一射线上，OA:OB＝{a}:{b}、OC:OD＝2:3，△AOC面积为{a*c}平方厘米"
            target, answer = "BOD", F(3*b*c,2)
            reason = "两个夹角互补。先用OA:OB换算△AOC与△BOC，再用OC:OD换算△BOC与△BOD。"
        else:
            outline = "ABC"
            p = {"A":(0,0),"B":(w,0),"C":(a,h)}
            if mode == 28:
                p.update(E=(F(a,2),F(h,2)), F=(F(w+a,2),F(h,2)))
                lines = [("B","E"),("A","F"),("E","F")]
                p["O"] = intersection(p["B"],p["E"],p["A"],p["F"])
                given = f"△ABC面积为{w*c}平方厘米，E、F分别是AC、BC中点，BE与AF交于O"
                target, answer = "EFO", F(w*c,12)
                reason = "EF平行AB且为其一半，沙漏的△EFO和△BAO相似；两块的高分去EF与AB间距离的三分之一和三分之二。"
            else:
                p.update(E=(F(a,2),F(h,2)),F=(F(w+a,2),F(h,2)),M=(a,0))
                lines = [("E","F"),("C","M")]
                p["N"] = midpoint(p["C"],p["M"])
                given = f"△ABC面积为{w*c}平方厘米，E、F分别为CA、CB中点，M在AB上，AM:MB＝{a}:{b}，CM交EF于N"
                target, answer = "CEN", F(a*c,4)
                reason = "EF平行AB，金字塔上层△CEF是整图的四分之一。CN把上层按EN:NF＝AM:MB分成两块。"
    else:
        if mode in (27,31):
            outline = "ABC"
            p["C"] = (a,h)
            p["M"] = (a,0)
            p["P"] = midpoint(p["C"],p["M"])
            p["E"],p["F"] = midpoint(p["C"],p["A"]),midpoint(p["C"],p["B"])
            lines = [("C","M"),("E","F"),("B","P"),("A","P")]
            given = f"△ABC面积为{w*c}平方厘米，M在AB上且AM:MB＝{a}:{b}，P是CM中点，E、F分别是CA、CB中点"
            target,answer = ("ABP",F(w*c,2)) if mode==27 else ("CPF",F(b*c,4))
            if mode == 27:
                given = f"△APC面积为{F(a*c,2)}平方厘米，M在AB上且AM:MB＝{a}:{b}，P是CM中点，E、F分别是CA、CB中点"
                reason = "先由CP:CM求△ACM，再用AM:AB求整图，用P的半高求△ABP。"
            else:
                reason = "用中位线EF得到上层相似三角形的面积是整图四分之一，再用PF:EF＝MB:AB分配。"
        elif mode in (28,30):
            p["C"],p["D"] = (w,h),(b,h)
            p["O"] = intersection(p["A"],p["C"],p["B"],p["D"])
            p["M"] = midpoint(p["A"],p["O"])
            lines = [("A","C"),("B","D"),("B","M"),("D","M")]
            wing, upper, lower = F(a*w*c,a+w), F(w*w*c,a+w), F(a*a*c,a+w)
            if mode == 28:
                target, answer = "DMO", wing/2
                # The requested region requires the wing to be derived first.
                given = f"凸四边形ABCD的对角线交于O，M是AO中点，△ABO、△BCO、△CDO面积分别为{upper}、{wing}、{lower}平方厘米"
                reason = "对角面积乘积相等，先用△ABO、△BCO和△CDO求△ADO。DMO和ADO从D到AC同高，MO是AO一半。"
            else:
                given = f"梯形ABCD的对角线交于O，AB:CD＝{w}:{a}，△CDO面积为{lower}平方厘米，M是AO中点"
                target, answer = "ABM",upper/2
                reason = "先由蝴蝶模型的相似关系把△CDO面积乘以底边比的平方，求△ABO。再按AM:AO取一半。"
        else:
            p["O"] = intersection(p["A"],p["C"],p["B"],p["D"])
            p["P"] = midpoint(p["A"],p["O"])
            lines = [("A","C"),("B","D"),("B","P"),("D","P")]
            given = f"平行四边形ABCD的对角线交于O，P是AO中点，△ABP面积为{F(s,8)}平方厘米"
            target,answer = "BCO",F(s,4)
            reason = "先用AP:AO从△ABP求△ABO。两条对角线互相平分，△ABO与△BCO等积。"
    return p, outline, lines, "cm²", given, target, answer, f"{given}。求△{target}面积。", reason
