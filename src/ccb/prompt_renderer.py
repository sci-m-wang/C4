from __future__ import annotations

from typing import Any

SCENE_PLACEHOLDER = "{{SCENE_DESCRIPTION}}"
STYLE_CLAUSE = "风格为简洁手绘线稿，少量浅色填充，构图清楚，主体关系一眼能看懂。"
NEGATIVE_PROMPT = "避免长段说明、分栏拼贴、杂乱背景。"


CONCEPT_DESCRIPTIONS = {
    "椰": "一个椰子",
    "椰子": "一个椰子",
    "页": "一页纸",
    "一页": "一页纸",
    "第一页": "一页纸，页角清楚标着数字 1",
    "账目": "一本打开的账本",
    "会计账本": "一本打开的会计账本",
    "椅": "一把椅子",
    "医": "一名医生",
    "姨": "一位阿姨",
    "亿": "一个写着“亿”的巨大数字牌",
    "大劲": "一个正在用力举重的人",
    "大妗": "一位长辈女性，旁边有小标签写着“大妗”",
    "衣柜": "一个打开的衣柜",
    "平移": "一个几何图形被水平移动，旁边有虚线轨迹",
    "奥斯卡": "一座奥斯卡奖杯，旁边有小标签写着“奥斯卡”",
    "日本": "一幅日本地图和日式地标小场景",
    "上海": "一处上海城市地标小场景",
    "校聘": "一张校聘通知单",
    "街舞": "一个正在跳街舞的人",
    "结石": "一块小石头状结石",
    "挖掘金矿": "一个矿工挖掘金矿的小场景",
    "踢进球门": "一个足球飞进球门的小场景",
    "熊": "一只熊",
    "大爷": "一位大爷",
    "岳母": "一位岳母",
    "夜行衣": "一套黑色夜行衣",
    "孽障": "一个调皮的小怪物",
}

PROPER_PERSON_TERMS = {
    "岳飞",
    "曹操",
    "刘邦",
    "杜甫",
    "李白",
    "苏轼",
    "陶渊明",
    "茅盾",
    "牛顿",
    "爱因斯坦",
    "张三丰",
    "和珅",
    "王濛",
    "姚明",
    "张继科",
    "李娜",
    "达达利亚",
    "敖丙",
    "孙悟空",
    "哪吒",
    "福尔摩斯",
    "元春",
    "杨彪",
    "朱元璋",
    "袁隆平",
    "贝多芬",
}

TEXT_LABEL_TERMS = {
    "岳飞",
    "曹操",
    "刘邦",
    "杜甫",
    "李白",
    "苏轼",
    "陶渊明",
    "茅盾",
    "牛顿",
    "爱因斯坦",
    "张三丰",
    "和珅",
    "王濛",
    "姚明",
    "张继科",
    "李娜",
    "达达利亚",
    "敖丙",
    "孙悟空",
    "哪吒",
    "福尔摩斯",
    "奥斯卡",
    "王者荣耀",
    "支付宝",
    "微信",
    "无畏契约",
    "流星花园",
    "迪士尼",
    "富士山",
    "红富士苹果",
    "莆田假鞋",
    "元春",
    "杨彪",
    "朱元璋",
    "袁隆平",
    "贝多芬",
    "莫高窟",
    "兰亭序",
}

ANIMAL_KEYWORDS = (
    "羊",
    "牛",
    "马",
    "狗",
    "猫",
    "猪",
    "鸟",
    "雀",
    "蛙",
    "鱼",
    "龙",
    "虎",
    "狐",
    "鸡",
    "鸭",
    "鹅",
    "鹿",
    "猿",
    "猩猩",
    "猴",
    "鼠",
    "虫",
    "鲸",
    "蛛",
    "蛇",
    "驴",
    "熊猫",
    "企鹅",
    "喜鹊",
    "燕子",
    "知了",
    "蜻蜓",
)
PERSON_KEYWORDS = (
    "人",
    "者",
    "员",
    "夫",
    "母",
    "父",
    "爷",
    "叔",
    "姨",
    "男",
    "女",
    "孩",
    "童",
    "将",
    "官",
    "师",
    "家",
    "帝",
    "王",
    "公",
    "后",
    "神",
    "仙",
    "佛",
    "僧",
    "道士",
    "警察",
    "保镖",
    "医生",
    "护士",
    "老师",
    "演员",
    "作家",
    "画家",
    "导游",
    "裁判",
    "农夫",
    "岳母",
    "大爷",
    "歹徒",
    "骑士",
    "妻室",
    "新娘",
    "亲人",
)
CLOTHING_KEYWORDS = ("衣", "服", "裙", "鞋", "帽", "护甲", "夜行衣", "西装", "汉服", "婚纱", "校服", "冲锋衣", "护膝")
PAPER_KEYWORDS = ("纸", "页", "票", "牌", "证", "照片", "画", "图", "二维码", "收款码", "纸稿", "字帖", "合同")
BOOK_KEYWORDS = ("书", "账本", "字典", "本", "小说")
TOOL_KEYWORDS = ("伞", "刀", "剑", "扇", "弓", "笔", "枪", "尺", "箭", "针", "梳子", "吸管")
VEHICLE_KEYWORDS = ("车", "飞车", "游艇", "轿子")
DEVICE_KEYWORDS = ("手机", "电脑", "路由器", "充电器", "充电宝", "录音机", "混音器", "饮水机", "相机", "拍立得")
FOOD_KEYWORDS = (
    "饭",
    "饼",
    "鸡",
    "米",
    "奶",
    "水",
    "可乐",
    "芬达",
    "酸奶",
    "蜂蜜",
    "慕斯",
    "汉堡",
    "泡菜",
    "牛排",
    "火锅",
    "薯片",
    "红薯",
    "地瓜粥",
    "黄焖鸡米饭",
    "杏仁露",
    "旺仔牛奶",
    "小馒头",
    "曲奇",
    "桃",
)
PLACE_KEYWORDS = ("山", "海", "湖", "井", "馆", "店", "站", "场", "园", "宫", "院", "局", "森林", "沙漠", "海滩")

STOP_FRAGMENTS = {"一", "之", "于", "而", "为", "可"}

LITERAL_FRAGMENT_DESCRIPTIONS = {
    "障目": "遮挡一只睁大的人眼",
    "叶": "一片叶子",
    "易": "一本《易经》风格的书",
    "人": "一个人",
    "医": "一名医生",
    "姨": "一位阿姨",
    "椅": "一把椅子",
    "目": "一只睁大的人眼",
    "打尽": "把周围一排小物件全部打倒",
    "打": "击打旁边的小物件",
    "尽": "周围的小物件已经被全部清空",
    "网": "一张展开的大网",
    "亡羊": "一只羊从围栏旁消失，只留下空绳圈",
    "补牢": "修补破损的围栏",
    "牢": "一段破损围栏",
    "门": "一扇门",
    "罗雀": "一只小雀被轻轻网住",
    "井底": "井底的圆形空间",
    "蛙": "一只青蛙",
    "天罗": "天空中垂下的大网",
    "地网": "地面上铺开的大网",
    "地": "地面",
    "对": "面对面站着",
    "牛": "一头牛",
    "弹琴": "正在弹琴",
    "琴": "一架琴",
    "守株": "守在一个树桩旁",
    "株": "一个树桩",
    "待兔": "等待一只兔子出现",
    "兔": "一只兔子",
    "画饼": "在纸上画一张圆饼",
    "饼": "一张圆饼",
    "充饥": "旁边有一个饥饿的人等着吃东西",
    "饥": "一个饥饿的人",
    "掩耳": "一双手捂住耳朵",
    "耳": "一只耳朵",
    "盗铃": "有人偷拿一只铃铛",
    "铃": "一只铃铛",
    "惊弓": "一张让人受惊的弓",
    "弓": "一张弓",
    "鸟": "一只鸟",
    "自相": "一个人给自己拍照",
    "矛盾": "一支长矛和一面盾牌",
    "矛": "一支长矛",
    "盾": "一面盾牌",
    "分道": "一条道路分成两岔",
    "道": "一条路",
    "扬镳": "马具被高高扬起",
    "镳": "一件马具",
    "鱼目": "一只鱼眼",
    "鱼": "一条鱼",
    "珠": "一颗珠子",
    "舍本": "一本书被放在一边",
    "本": "一本书",
    "逐末": "追逐一小段末尾标记",
    "逐": "追逐动作",
    "末": "末尾的小标记",
    "指鹿": "手指着一只鹿",
    "指": "一只伸出的手指",
    "鹿": "一只鹿",
    "马": "一匹马",
    "南辕": "朝南的车辕",
    "北辙": "朝北的车辙",
    "辙": "车轮留下的痕迹",
    "狐假": "一只狐狸借来道具",
    "虎威": "老虎威风的姿态",
    "虎": "一只老虎",
    "滥竽": "一支坏掉的竽",
    "竽": "一支竽",
    "充数": "混在队伍里凑数",
    "数": "一串数字",
    "黑白": "黑白相间的图案",
    "混淆": "两种东西被混在一起",
    "混": "混合在一起的动作",
    "淆": "被混乱摆放的物件",
    "唇亡": "嘴唇消失的脸部轮廓",
    "唇": "嘴唇",
    "齿寒": "牙齿冷得发抖",
    "齿": "牙齿",
    "分庭": "庭院被分成两半",
    "庭": "一个小庭院",
    "抗礼": "两人互相行礼又互相较劲",
    "平易": "平移的几何图形",
    "平": "平坦的桌面",
    "近人": "靠近的人",
    "口蜜": "嘴边有蜂蜜",
    "口": "一张嘴",
    "蜜": "蜂蜜",
    "腹剑": "肚子旁放着一把剑",
    "腹": "肚子",
    "剑": "一把剑",
    "飞扬": "向上飞起的动作",
    "跋扈": "门牌和户口本被夸张摆放",
    "跋": "拔起东西的动作",
    "扈": "一扇写着户号的小门牌",
    "奴颜": "低眉顺眼的表情",
    "颜": "一张脸",
    "婢膝": "跪下的膝盖",
    "婢": "女仆形象",
    "膝": "膝盖",
    "推心": "把一个心形物轻轻推出去",
    "推": "推动动作",
    "心": "一个心形物",
    "置腹": "把物件放在肚子旁",
    "趾高": "脚趾高高抬起",
    "趾": "脚趾",
    "气扬": "气球向上飘起",
    "气": "一团白色气体",
    "扬": "向上扬起的动作",
    "得意": "得意的表情",
    "忘形": "轮廓线正在消失",
    "忘": "忘记事情的人",
    "形": "一个几何形状",
    "趋炎": "靠近火焰的动作",
    "趋": "快步走近",
    "炎": "火焰",
    "附势": "贴在斜坡上的物件",
    "欺世": "欺骗路人的小把戏",
    "盗名": "偷走姓名牌",
    "盗": "偷拿动作",
    "名": "姓名牌",
    "握手": "两只手握在一起",
    "言欢": "聊天时露出开心表情",
    "交浅": "浅浅交叉的两条线",
    "言深": "很深的对话气泡",
    "东施": "东方站着一位女子",
    "效颦": "模仿皱眉的表情",
    "东": "东方日出",
    "施": "施展动作",
    "叶公": "一位姓叶的人",
    "好龙": "喜欢龙的表情",
    "朝三": "早晨出现数字三",
    "朝": "早晨的太阳",
    "三": "数字三",
    "暮四": "傍晚出现数字四",
    "暮": "傍晚天空",
    "四": "数字四",
    "草木": "草和树木",
    "皆兵": "都戴上士兵头盔",
    "兵": "士兵",
    "闻鸡": "听见鸡叫",
    "起舞": "起身跳舞",
    "凿壁": "墙壁被凿开",
    "偷光": "从洞里偷来一束光",
    "卧薪": "躺在柴草上",
    "尝胆": "尝一只苦胆",
    "喜形": "开心表情画成形状",
    "色": "一片颜色",
    "杯弓": "杯子旁有弓形倒影",
    "蛇影": "蛇的影子",
    "毛遂": "一个毛笔形小人自我介绍",
    "自荐": "主动递出推荐信",
    "程门": "一扇门旁有姓名牌写着程",
    "立雪": "站在雪地里",
    "结草": "把草打结",
    "衔环": "嘴里衔着圆环",
    "罄竹": "一排竹简被用尽",
    "难书": "很难写下来的书页",
}


def contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def needs_text_label(concept: str) -> bool:
    if concept in TEXT_LABEL_TERMS:
        return True
    return any(term in concept for term in TEXT_LABEL_TERMS)


def concept_label_clause(concept: str) -> str:
    if needs_text_label(concept):
        return f"，小标签写着“{concept}”"
    return ""


def describe_concept(concept: str) -> str:
    if concept in CONCEPT_DESCRIPTIONS:
        return CONCEPT_DESCRIPTIONS[concept]
    label = concept_label_clause(concept)
    if needs_text_label(concept):
        if concept in PROPER_PERSON_TERMS:
            return f"一位人物{label}"
        return f"一个可识别对象{label}"
    if contains_any(concept, PERSON_KEYWORDS):
        return f"一位{concept}{label}"
    if contains_any(concept, ANIMAL_KEYWORDS):
        return f"一只{concept}{label}"
    if contains_any(concept, BOOK_KEYWORDS):
        return f"一本{concept}{label}"
    if contains_any(concept, PAPER_KEYWORDS):
        return f"一张{concept}{label}"
    if contains_any(concept, TOOL_KEYWORDS):
        return f"一把{concept}{label}"
    if contains_any(concept, VEHICLE_KEYWORDS):
        return f"一辆{concept}{label}"
    if contains_any(concept, DEVICE_KEYWORDS):
        return f"一台{concept}{label}"
    if contains_any(concept, FOOD_KEYWORDS):
        return f"一份{concept}{label}"
    if contains_any(concept, PLACE_KEYWORDS):
        return f"一处{concept}{label}"
    if contains_any(concept, CLOTHING_KEYWORDS):
        return f"一件或一套{concept}{label}"
    return f"一个{concept}{label}"


def selected_subject(selections: list[dict[str, Any]], default: str = "一个物体") -> str:
    if not selections:
        return default
    return describe_concept(selections[0]["substitution_text"])


def selected_descriptions(selections: list[dict[str, Any]]) -> list[str]:
    return [describe_concept(selection["substitution_text"]) for selection in selections]


def raw_fragments(idiom: str, selections: list[dict[str, Any]]) -> list[str]:
    spans = sorted([selection["span"] for selection in selections])
    fragments: list[str] = []
    cursor = 0
    for start, end in spans:
        if cursor < start:
            fragments.append(idiom[cursor:start])
        cursor = end
    if cursor < len(idiom):
        fragments.append(idiom[cursor:])
    return [fragment for fragment in fragments if fragment]


def split_literal_fragment(fragment: str) -> list[str]:
    if not fragment:
        return []
    descriptions: list[str] = []
    cursor = 0
    keys = sorted(LITERAL_FRAGMENT_DESCRIPTIONS, key=len, reverse=True)
    while cursor < len(fragment):
        matched = None
        for key in keys:
            if fragment.startswith(key, cursor):
                matched = key
                break
        if matched:
            descriptions.append(LITERAL_FRAGMENT_DESCRIPTIONS[matched])
            cursor += len(matched)
        else:
            char = fragment[cursor]
            if char not in STOP_FRAGMENTS:
                descriptions.append(LITERAL_FRAGMENT_DESCRIPTIONS.get(char, "一个抽象小符号"))
            cursor += 1
    return descriptions


def literal_descriptions(idiom: str, selections: list[dict[str, Any]]) -> list[str]:
    descriptions: list[str] = []
    for fragment in raw_fragments(idiom, selections):
        descriptions.extend(split_literal_fragment(fragment))
    return descriptions


def has_fragment(idiom: str, selections: list[dict[str, Any]], fragment: str) -> bool:
    return any(fragment in raw for raw in raw_fragments(idiom, selections))


def interaction_scene(idiom: str, selections: list[dict[str, Any]]) -> tuple[str, list[str]]:
    flags: list[str] = []
    concepts = selected_descriptions(selections)
    raw_desc = literal_descriptions(idiom, selections)
    subject = concepts[0] if concepts else "一个物体"

    if has_fragment(idiom, selections, "障目"):
        return f"{subject}遮挡在一只睁大的人眼前，眼睛被它挡住视线", flags
    if has_fragment(idiom, selections, "打尽"):
        return f"{subject}正在把周围一排小物件全部打倒，地上只剩被清空的空间", flags
    if has_fragment(idiom, selections, "弹琴"):
        return f"{subject}面对一架琴正在弹奏，琴声用几条简单线条表现出来", flags
    if has_fragment(idiom, selections, "补牢"):
        return f"{subject}正在修补一个破损的围栏，旁边有锤子和木板", flags
    if has_fragment(idiom, selections, "充饥"):
        return f"{subject}被放在一个饥饿的人面前，那个人正准备把它当食物", flags
    if has_fragment(idiom, selections, "盗铃"):
        return f"{subject}旁边有人正在偷拿一只铃铛，铃铛发出小小声波线", flags
    if has_fragment(idiom, selections, "弹") and any("琴" in desc for desc in raw_desc):
        return f"{subject}旁边有一架琴，人物伸手准备弹奏", flags
    if has_fragment(idiom, selections, "起舞"):
        return f"{subject}旁边有人起身跳舞，动作线表现舞步", flags
    if has_fragment(idiom, selections, "握手"):
        return f"{subject}旁边有两只手正在握手，场景像一次简短会面", flags
    if has_fragment(idiom, selections, "言欢"):
        return f"{subject}正在和一个笑脸人物聊天，旁边可以有短对话气泡", flags
    if has_fragment(idiom, selections, "难书"):
        return f"{subject}旁边有一本难以写满的书，纸面上可以有少量凌乱笔画", flags

    visible_parts = concepts + raw_desc
    if not visible_parts:
        flags.append("generic_empty_scene")
        return "画面中央放着一个被强调的物体，周围留白", flags
    if len(visible_parts) == 1:
        return f"画面中央清楚呈现{visible_parts[0]}，周围留白，重点突出", flags
    if len(visible_parts) == 2:
        return f"{visible_parts[0]}和{visible_parts[1]}被安排在同一张桌面或小场景里，二者有明确接触或视线关系", flags
    flags.append("generic_multi_element_scene")
    head = "、".join(visible_parts[:-1])
    return f"{head}和{visible_parts[-1]}被安排在同一个简洁场景里，主要元素彼此接触或指向，不做分栏拼贴", flags


def review_prompt(prompt: str, negative_prompt: str, idiom: str, phrase: str, scene_flags: list[str]) -> dict[str, Any]:
    flags = list(scene_flags)
    prompt_blob = prompt + negative_prompt
    if phrase and phrase in prompt_blob:
        flags.append("contains_final_substituted_phrase")
    if idiom and idiom in prompt_blob:
        flags.append("contains_source_idiom")
    if "只按照短语" in prompt_blob:
        flags.append("legacy_phrase_instruction")
    if any(term in prompt_blob for term in ["成语", "谜底", "答案", "替换短语"]):
        flags.append("contains_meta_task_terms")
    serious = {
        "contains_final_substituted_phrase",
        "contains_source_idiom",
        "legacy_phrase_instruction",
        "contains_meta_task_terms",
    }
    return {
        "status": "pass" if not (set(flags) & serious) else "review",
        "flags": sorted(set(flags)),
        "text_policy": "unconstrained",
    }


def build_full_prompt(scene_description: str) -> str:
    return f"白底单幅中文创意插画，画幅内容是：{scene_description}。{STYLE_CLAUSE}"


def render_generation_prompt(idiom: str, phrase: str, selections: list[dict[str, Any]]) -> dict[str, Any]:
    scene, scene_flags = interaction_scene(idiom, selections)
    prompt = build_full_prompt(scene)
    prompt_template = build_full_prompt(SCENE_PLACEHOLDER)
    return {
        "scene": scene,
        "scene_placeholder": SCENE_PLACEHOLDER,
        "prompt": prompt,
        "prompt_template": prompt_template,
        "negative_prompt": NEGATIVE_PROMPT,
        "review": review_prompt(prompt, NEGATIVE_PROMPT, idiom, phrase, scene_flags),
    }
