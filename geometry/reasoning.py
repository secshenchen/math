"""Conservative reviewed reasoning chains; labels alone are not evidence."""

# A formula substitution, a fixed fraction, and a deliberately long solution to
# an equal-area shortcut do not qualify. These families need chained relations.
MULTISTEP = {
    "一半模型": {16,22,23,24,25,26,27,29,30,32},
    "三角形基础": {32,33,34},
    "三角形边角关系": {32,33},
    "梯形": {15,16,17,32,33},
    "燕尾模型": {15,16,17,24,25,26,32},
    "等积模型": {34},
    "综合几何模型": {10,11,12,13,14,27,28,29,30,31,40},
    "蝴蝶模型": {24,25,26,33},
    "风筝模型": {32,33,34},
    "鸟头模型": {27,28,29},
}


def reviewed_multistep(question):
    return question.get("modelMode") in MULTISTEP.get(question["category"],set())
