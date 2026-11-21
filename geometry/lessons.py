"""Twelve offline teaching cards, separate from the numbered exercise bank."""
from html import escape
from math import hypot

from .samples import diagram


def _card(category, title, condition, rule, steps, caution, points, outline,
          *, segments=(), regions=(), notes=(), equal_pairs=()):
    # Match diagram()'s projection so every vertex label follows its own point.
    xs, ys = zip(*points.values())
    scale = min(290 / (max(xs)-min(xs)), 140 / (max(ys)-min(ys)))
    center = (sum(xs)/len(xs), sum(ys)/len(ys))
    labels = []
    for name, (x, y) in points.items():
        dx, dy = x-center[0], center[1]-y
        length = hypot(dx, dy) or 1
        labels.append((65+(x-min(xs))*scale+13*dx/length,
                       185-(y-min(ys))*scale+13*dy/length+5, name))
    svg = diagram(points, outline, segments=segments, regions=regions,
                  labels=labels, notes=("教学示例 · 不计入练习题库", *notes),
                  equal_pairs=equal_pairs)
    svg = svg.replace("<title>几何关系图</title>",
                      "<title>"+escape(category+"教学示例："+title)+"</title>", 1)
    description = "教学示例；"+condition+"；"+"；".join(steps)
    start, end = svg.index("<desc>"), svg.index("</desc>")+len("</desc>")
    svg = svg[:start]+"<desc>"+escape(description)+"</desc>"+svg[end:]
    return dict(title=title, condition=condition, rule=rule, steps=steps,
                caution=caution, svg=svg, construction={"points": points})


def build_lessons():
    """Return one illustrated card per curriculum category; all data is local."""
    cards = {}

    def add(category, *args, **kwargs):
        cards[category] = _card(category, *args, **kwargs)

    add("长方形与正方形", "用长和宽求面积",
        "长方形四个角都是直角；面积用相邻两边的长度相乘。",
        "长方形面积＝长×宽；正方形四边相等，面积＝边长×边长。",
        ["例题：长方形ABCD，AB＝12厘米，BC＝7厘米，求面积。",
         "每排12个单位小正方形，共7排，面积为12×7＝84平方厘米。"],
        "周长计算边界长度，面积计算覆盖大小；厘米与平方厘米不能混用。",
        {"A": (0, 0), "B": (12, 0), "C": (12, 7), "D": (0, 7)}, "ABCD",
        regions=(("ABCD", "#dbeafe"),), notes=("AB＝12 cm，BC＝7 cm", "面积＝12×7＝84 cm²"))
    add("平行四边形", "对角线把面积分成两半",
        "AB与CD平行且相等，AD与BC平行；AC是平行四边形的对角线。",
        "面积＝底×对应高；一条对角线分出的两个三角形面积相等。",
        ["例题：平行四边形ABCD，AB＝12厘米，对应高6厘米，连接AC。",
         "整图面积＝12×6＝72平方厘米。", "△ABC面积＝72÷2＝36平方厘米。"],
        "斜边不是高；只有与所选底垂直的距离才是对应高。",
        {"A": (0, 0), "B": (12, 0), "C": (15, 6), "D": (3, 6)}, "ABCD",
        segments=(("A", "C"),), regions=(("ABC", "#dbeafe"),),
        notes=("AB＝12 cm，对应高＝6 cm", "整图72 cm²，△ABC＝36 cm²"))
    trapezoid = {"A": (0, 0), "B": (12, 0), "C": (9, 6), "D": (3, 6)}
    add("梯形", "认清两底和高",
        "梯形ABCD中AB∥CD，高是两条平行底边间的垂直距离。",
        "梯形面积＝(上底＋下底)×高÷2。",
        ["例题：AB＝12厘米，CD＝6厘米，高6厘米，求梯形面积。",
         "两底和为12＋6＝18厘米。", "面积＝18×6÷2＝54平方厘米。"],
        "两腰通常不是高；不能把两底差代入面积公式。",
        trapezoid.copy(), "ABCD", regions=(("ABCD", "#dbeafe"),),
        notes=("AB∥CD，AB＝12 cm，CD＝6 cm", "高6 cm，面积54 cm²"))
    add("三角形基础", "底和高要对应",
        "CD垂直AB，D在AB上；CD是以AB为底时的高。",
        "三角形面积＝底×对应高÷2。垂足也可能在底边延长线上。",
        ["例题：△ABC中AB＝12厘米，CD＝8厘米，CD⊥AB。",
         "面积＝12×8÷2＝48平方厘米。"],
        "高是垂直距离；换底后必须换成该底对应的高。",
        {"A": (0, 0), "B": (12, 0), "C": (3, 8), "D": (3, 0)}, "ABC",
        segments=(("C", "D"),), regions=(("ABC", "#dbeafe"),),
        notes=("AB＝12 cm，CD＝8 cm，CD⊥AB", "△ABC面积＝48 cm²"))
    add("三角形边角关系", "内角和与等腰底角",
        "△ABC中∠A＝90°，AB＝AC，两个底角相等。",
        "三角形内角和180°；等腰三角形的两个底角相等。",
        ["例题：AB＝AC，∠A＝90°，求∠B和∠C。",
         "两个底角之和＝180°－90°＝90°。", "∠B＝∠C＝90°÷2＝45°。"],
        "只有已知两边相等或已证明等腰，才可以把两个底角设为相等。",
        {"A": (0, 0), "B": (8, 0), "C": (0, 8)}, "ABC",
        equal_pairs=((("A", "B"), ("A", "C")),),
        notes=("AB＝AC，∠A＝90°", "∠B＝∠C＝45°"))
    add("等积模型", "平行线间的公共高",
        "C、D在AB同侧，CD∥AB；△ABC与△ABD共用底AB。",
        "同底等高的三角形面积相等；同高时面积比等于底边比。",
        ["例题：AB＝12厘米，C、D到AB的距离都是6厘米。",
         "△ABC面积＝12×6÷2＝36平方厘米。", "△ABD同底等高，面积也为36平方厘米。"],
        "只知道底边相等不能推出等积；还需要对应高相等。",
        {"A": (0, 0), "B": (12, 0), "C": (3, 6), "D": (9, 6)}, "ABC",
        segments=(("A", "D"), ("B", "D"), ("C", "D")),
        notes=("AB＝12 cm，CD∥AB，距离＝6 cm", "△ABC与△ABD面积都是36 cm²"))
    add("一半模型", "两边中点带来四分之一",
        "D、E分别是△ABC的AB、AC中点，连接DE。",
        "DE∥BC且DE＝BC的一半；△ADE面积是△ABC的四分之一。",
        ["例题：△ABC面积96平方厘米，D、E分别为AB、AC中点。",
         "两条对应边都缩小到一半，可将大三角形分成四个等积小三角形。",
         "△ADE面积＝96÷4＝24平方厘米。"],
        "一个中点配合一条中线平分面积；两个对应边中点形成的小三角形占四分之一。",
        {"A": (4, 12), "B": (0, 0), "C": (16, 0), "D": (2, 6), "E": (10, 6)}, "ABC",
        segments=(("D", "E"),), regions=(("ADE", "#dbeafe"),),
        equal_pairs=((("A", "D"), ("D", "B")), (("A", "E"), ("E", "C"))),
        notes=("D、E是中点，DE∥BC", "整图96 cm²，△ADE＝24 cm²"))
    kite = {"A": (-4, 0), "B": (0, 6), "C": (8, 0), "D": (0, -3), "O": (0, 0)}
    add("风筝模型", "用公共高传递面积比",
        "凸四边形ABCD的对角线AC、BD相交于内部点O。",
        "S(AOB):S(BOC)＝AO:OC＝S(AOD):S(COD)，所以相对面积乘积相等。",
        ["例题：S(AOB)＝12、S(BOC)＝24、S(AOD)＝6，单位均为平方厘米。",
         "前两块共用B到AC的高，AO:OC＝12:24＝1:2。",
         "后两块共用D到AC的高，S(COD)＝6×2＝12平方厘米。"],
        "此处风筝指四块面积关系，不要求四边形有两组邻边相等；必须确认对角线交于内部。",
        kite, "ABCD", segments=(("A", "C"), ("B", "D")), regions=(("COD", "#dbeafe"),),
        notes=("S(AOB)＝12，S(BOC)＝24，S(AOD)＝6", "AO:OC＝1:2，S(COD)＝12 cm²"))
    butterfly = dict(trapezoid, O=(6, 4))
    add("蝴蝶模型", "两底比与面积平方比",
        "梯形ABCD中AB∥CD，两条对角线AC、BD交于O。",
        "上下三角形对应底边比等于高之比；面积比等于两底比的平方，两翼等积。",
        ["例题：AB:CD＝2:1，S(CDO)＝6平方厘米，求S(ABO)。",
         "平行底边和交叉对角线给出对应高比2:1。",
         "面积比＝(2×2):(1×1)＝4:1，S(ABO)＝6×4＝24平方厘米。"],
        "两底必须平行；上下两块的面积比不能直接写成两底比。",
        butterfly.copy(), "ABCD", segments=(("A", "C"), ("B", "D")),
        regions=(("ABO", "#dbeafe"), ("CDO", "#fde68a")),
        notes=("AB∥CD，AB:CD＝2:1", "S(CDO)＝6，S(ABO)＝24 cm²"))
    add("鸟头模型", "同夹角，逐条边换算",
        "O、A、C在同一射线上，O、B、D在另一射线上；两三角形共用夹角O。",
        "固定一条边时，另一边按比例变化，对应高和面积也按相同比例变化。",
        ["例题：OA＝4、OC＝8、OB＝3、OD＝9厘米，夹角O为90°。",
         "△OAB面积＝4×3÷2＝6平方厘米；把OA扩大到OC，面积先乘2。",
         "再把OB扩大到OD，面积乘3，△OCD面积＝6×2×3＝36平方厘米。"],
        "共用或相等夹角是适用条件；两条边不能随意配对。本例直角只为便于核对面积。",
        {"O": (0, 0), "A": (4, 0), "B": (0, 3), "C": (8, 0), "D": (0, 9)}, "OCD",
        segments=(("A", "B"),), regions=(("OAB", "#dbeafe"),),
        notes=("OA:OC＝1:2，OB:OD＝1:3，∠O＝90°", "小三角形6 cm²，大三角形36 cm²"))
    add("燕尾模型", "先分总面积，再用共同高",
        "D在BC上，BD:DC＝1:2；P是AD中点，连接BP、CP。",
        "先利用P到BC的高，再利用B、C到直线AD的高比传递面积。",
        ["例题：△ABC面积48平方厘米，P是AD中点，BD:DC＝1:2。",
         "P到BC的高是A的一半，S(BPC)＝48÷2＝24平方厘米。",
         "其余两块总面积＝48－24＝24，且S(ABP):S(ACP)＝BD:DC＝1:2。",
         "S(ABP)＝24÷3＝8平方厘米，S(ACP)＝16平方厘米。"],
        "面积分配要先找到对应的公共底或高；不能因为图形看起来对称就认定等积。",
        {"A": (4, 8), "B": (0, 0), "C": (12, 0), "D": (4, 0), "P": (4, 4)}, "ABC",
        segments=(("A", "D"), ("B", "P"), ("C", "P")), regions=(("ABP", "#dbeafe"),),
        equal_pairs=((("A", "P"), ("P", "D")),),
        notes=("P是AD中点，BD:DC＝1:2，整图48 cm²", "S(BPC)＝24，S(ABP)＝8 cm²"))
    add("综合几何模型", "蝴蝶关系接上中点等积",
        "梯形ABCD中AB∥CD，AC与BD交于O，M是AB中点。",
        "先用梯形上下三角形的面积平方比，再用中线平分三角形面积。",
        ["例题：AB:CD＝2:1，S(CDO)＝6平方厘米，M是AB中点，求S(AMO)。",
         "蝴蝶关系给出S(ABO):S(CDO)＝4:1，故S(ABO)＝24平方厘米。",
         "△AMO与△BMO同高且AM＝MB，S(AMO)＝24÷2＝12平方厘米。"],
        "两种模型必须作用在同一图形上，并把第一步的结果作为下一步的条件。",
        dict(butterfly, M=(6, 0)), "ABCD",
        segments=(("A", "C"), ("B", "D"), ("O", "M")), regions=(("AMO", "#dbeafe"),),
        equal_pairs=((("A", "M"), ("M", "B")),),
        notes=("AB∥CD，AB:CD＝2:1，M是AB中点", "S(CDO)＝6，S(AMO)＝12 cm²"))
    return cards
