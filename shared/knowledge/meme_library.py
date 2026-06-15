"""热梗语料库 — 股市亚文化情绪缓冲垫。

内置 ~30 条中文股民自嘲热梗，按亏损等级组织。
每条梗含 GENTLE（温柔化）和 MEME（原味）两种变体。
RATIONAL 人设禁用热梗（返回空结果）。
"""

from shared.types import KnowledgeDomain, KnowledgeEntry, KnowledgeResult, PersonaType


_MEME_CORPUS: list[dict] = [
    # ═══════════════════════════════════════════════════════════
    # mild (0-3%) 轻度亏损 — 轻自嘲
    # ═══════════════════════════════════════════════════════════
    {
        "id": "meme_001",
        "text": "今天小亏，问题不大，明天又是一条好汉 💪",
        "loss_level": "mild",
        "gentle_variant": "今天只是小波动呢宝，调整一下心态，明天又是阳光灿烂的一天 ✨",
        "tags": ["自嘲", "乐观", "短线"],
        "source": "淘股吧",
        "freshness": 0.90,
    },
    {
        "id": "meme_002",
        "text": "大盘跌了一个点，我跌了两个点，问题是我还跑赢了大盘的下跌速度",
        "loss_level": "mild",
        "gentle_variant": "今天大盘有点小调整，你的持仓也跟着波动了一点点，这在交易中很正常的～",
        "tags": ["自嘲", "跑输大盘", "幽默"],
        "source": "雪球",
        "freshness": 0.85,
    },
    {
        "id": "meme_003",
        "text": "今天唯一的好消息：跌得没昨天多",
        "loss_level": "mild",
        "gentle_variant": "虽然今天还是跌了，但比昨天好一些呢。市场总是在波动中前行的～",
        "tags": ["自嘲", "连续下跌", "比烂"],
        "source": "淘股吧",
        "freshness": 0.80,
    },
    {
        "id": "meme_004",
        "text": "早上追进去的票，现在已经绿得发光了。追涨技术一流 👍",
        "loss_level": "mild",
        "gentle_variant": "早上追高了吧？下次咱们可以多看看再动手，不着急的 ✨",
        "tags": ["追涨", "自嘲", "短线"],
        "source": "雪球",
        "freshness": 0.88,
    },
    {
        "id": "meme_005",
        "text": "我的持仓：三只绿的，一只红的。红的那只…买少了",
        "loss_level": "mild",
        "gentle_variant": "组合里总有些涨有些跌，那只涨的不错呀，下次可以多配一点呢～",
        "tags": ["仓位管理", "自嘲", "遗憾"],
        "source": "东方财富",
        "freshness": 0.75,
    },
    {
        "id": "meme_006",
        "text": "今天赚了200，感觉自己就是巴菲特；明天亏了2000，巴菲特也不过如此",
        "loss_level": "mild",
        "gentle_variant": "盈亏之间的情绪波动很正常。重要的是长期来看，咱们的策略能不能持续跑赢市场 ✨",
        "tags": ["情绪波动", "过度自信", "自嘲"],
        "source": "雪球",
        "freshness": 0.90,
    },
    {
        "id": "meme_007",
        "text": "每次我一满仓，大盘就见顶。这个技能比任何指标都准",
        "loss_level": "mild",
        "gentle_variant": "很多交易者都有这种感觉呢。其实这是确认偏误在起作用——我们会无意识地寻找支持自己决策的证据",
        "tags": ["满仓", "情绪指标", "反向指标"],
        "source": "淘股吧",
        "freshness": 0.82,
    },
    {
        "id": "meme_008",
        "text": "开盘笑嘻嘻，收盘MMP。A股股民的一天",
        "loss_level": "mild",
        "gentle_variant": "高开低走确实让人难受。不过一天的波动不代表什么，关掉软件休息一下吧 ✨",
        "tags": ["日常", "情绪", "行情"],
        "source": "微博股市",
        "freshness": 0.78,
    },

    # ═══════════════════════════════════════════════════════════
    # moderate (3-8%) 中度亏损 — 黑色幽默
    # ═══════════════════════════════════════════════════════════
    {
        "id": "meme_009",
        "text": "我的账户就像过山车，可惜只有下坡没有上坡 🎢",
        "loss_level": "moderate",
        "gentle_variant": "回撤是交易的一部分呢。职业交易员也会经历30%以上的回撤，关键是控制好底线 ✨",
        "tags": ["回撤", "黑色幽默", "心态"],
        "source": "雪球",
        "freshness": 0.90,
    },
    {
        "id": "meme_010",
        "text": "别人是价值投资，我是价值蒸发",
        "loss_level": "moderate",
        "gentle_variant": "短期波动不代表价值消失。好的公司基本面不会因为几天下跌就改变。咱们关注长期价值 ✨",
        "tags": ["价值投资", "亏损", "自嘲"],
        "source": "淘股吧",
        "freshness": 0.85,
    },
    {
        "id": "meme_011",
        "text": "每天都在见证历史：今天又跌出新低",
        "loss_level": "moderate",
        "gentle_variant": "市场有时候确实会超出所有人的预期。但历史告诉我们，最恐慌的时候往往是转机的前夜",
        "tags": ["连续下跌", "历史", "黑色幽默"],
        "source": "雪球",
        "freshness": 0.88,
    },
    {
        "id": "meme_012",
        "text": "不看不卖就不亏。只要我不打开APP，我的钱就还在",
        "loss_level": "moderate",
        "gentle_variant": "鸵鸟心态其实是大脑的自我保护机制呢。不过宝，设定好止损线，就不需要逃避了。咱们勇敢面对 ✨",
        "tags": ["逃避", "亏损", "自欺"],
        "source": "淘股吧",
        "freshness": 0.92,
    },
    {
        "id": "meme_013",
        "text": "上周刚割肉，这周就涨停。主力就差我这点筹码是吧？",
        "loss_level": "moderate",
        "gentle_variant": "割在地板上确实是交易中最让人沮丧的事。但这不代表你的判断能力有问题——市场短期波动本就有随机性",
        "tags": ["割肉", "踏空", "主力"],
        "source": "东方财富",
        "freshness": 0.86,
    },
    {
        "id": "meme_014",
        "text": "补仓补成了重仓，重仓补成了满仓，满仓变成了请补充保证金",
        "loss_level": "moderate",
        "gentle_variant": "越跌越补是很多交易者的习惯，但这会放大风险。有时候停止补仓、接受亏损，比加倍投入更明智",
        "tags": ["补仓", "满仓", "杠杆"],
        "source": "雪球",
        "freshness": 0.84,
    },
    {
        "id": "meme_015",
        "text": "我的交易计划：赚钱→消费→亏钱→吃面→继续亏→关灯吃面 🍜",
        "loss_level": "moderate",
        "gentle_variant": "关灯吃面是股民最经典的梗了。其实每一个职业交易者都经历过这样的时刻。面吃完了，明天太阳照常升起",
        "tags": ["关灯吃面", "经典梗", "无奈"],
        "source": "淘股吧",
        "freshness": 0.95,
    },
    {
        "id": "meme_016",
        "text": "韭菜的自我修养：被割了一茬又一茬，依然茁壮成长 🌱",
        "loss_level": "moderate",
        "gentle_variant": "没有人是天生的交易高手。每一次亏损都是一课，重要的是同样错误不犯两次。你已经在成长了 ✨",
        "tags": ["韭菜", "成长", "自嘲"],
        "source": "雪球",
        "freshness": 0.91,
    },

    # ═══════════════════════════════════════════════════════════
    # severe (>8%) 严重亏损 — 治疗性共鸣
    # ═══════════════════════════════════════════════════════════
    {
        "id": "meme_017",
        "text": "别人炒股是为了赚钱，我炒股是为了见证历史 📖",
        "loss_level": "severe",
        "gentle_variant": "经历了这种级别的亏损，你一定很难受。但宝，你不是一个人。历史上每一个伟大的交易员都经历过至暗时刻。先停下来，深呼吸",
        "tags": ["见证历史", "重度亏损", "豁达"],
        "source": "雪球",
        "freshness": 0.90,
    },
    {
        "id": "meme_018",
        "text": "今年的目标：争取亏得比去年少",
        "loss_level": "severe",
        "gentle_variant": "今年的市场确实很难做。降低预期不是认输，是在艰难时期保护自己的智慧。先活下来，才有翻盘的机会",
        "tags": ["年度亏损", "小目标", "黑色幽默"],
        "source": "淘股吧",
        "freshness": 0.82,
    },
    {
        "id": "meme_019",
        "text": "如果时间能倒流，我会对一年前的自己说：别炒股了",
        "loss_level": "severe",
        "gentle_variant": "后悔是最消耗心力的情绪。如果现在退出，那之前的亏损就成了永远的亏损。如果坚持总结改进，亏损就只是学费",
        "tags": ["后悔", "入市", "自省"],
        "source": "东方财富",
        "freshness": 0.88,
    },
    {
        "id": "meme_020",
        "text": "我怀疑我的账户被诅咒了：每次我一卖它就涨，一买它就跌",
        "loss_level": "severe",
        "gentle_variant": "这种反向指标的感觉几乎每个交易者都有过。其实是因为我们在情绪最极端的时候做出了决定。下次试试在买卖之前等24小时 ✨",
        "tags": ["反向指标", "情绪交易", "诅咒"],
        "source": "雪球",
        "freshness": 0.85,
    },
    {
        "id": "meme_021",
        "text": "杠杆一时爽，爆仓火葬场。含泪写下这行字",
        "loss_level": "severe",
        "gentle_variant": "杠杆是把双刃剑。你现在能认识到它的危险，说明你已经比大多数人成长了。以后有机会，只用自己能承受亏损的钱去交易",
        "tags": ["杠杆", "爆仓", "惨痛教训"],
        "source": "淘股吧",
        "freshness": 0.87,
    },
    {
        "id": "meme_022",
        "text": "假如生活欺骗了你，不要悲伤——因为它还会继续欺骗你。A股同理",
        "loss_level": "severe",
        "gentle_variant": "改编普希金的诗来调侃自己，说明你骨子里是个乐观的人。市场有周期，寒冬之后必有春天。保重身体，等风来",
        "tags": ["诗歌改编", "持续亏损", "深沉自嘲"],
        "source": "微博股市",
        "freshness": 0.80,
    },
    {
        "id": "meme_023",
        "text": "今年最大的收获：认清了自己不是股神，只是一个普通的韭菜",
        "loss_level": "severe",
        "gentle_variant": "从'我可以战胜市场'到'我只是普通人'——这个认知转变本身就是巨大的成长。真正的投资从接受自己的局限开始",
        "tags": ["认知升级", "韭菜", "成长"],
        "source": "雪球",
        "freshness": 0.92,
    },
    {
        "id": "meme_024",
        "text": "感觉自己不是在炒股，是在交学费。这学费也太贵了",
        "loss_level": "severe",
        "gentle_variant": "你不是在交学费，你是在积累经验。经历过这些的投资者，对风险的理解比任何人都深刻。这份认知未来会保护你",
        "tags": ["学费", "严重亏损", "成长"],
        "source": "淘股吧",
        "freshness": 0.83,
    },

    # ═══════════════════════════════════════════════════════════
    # any — 共同体共鸣（不限亏损等级）
    # ═══════════════════════════════════════════════════════════
    {
        "id": "meme_025",
        "text": "A股虐我千百遍，我待A股如初恋 ❤️",
        "loss_level": "any",
        "gentle_variant": "这句话是A股股民的精神图腾。因为相信，所以坚持。因为坚持，才有希望 ✨",
        "tags": ["经典", "坚持", "信仰"],
        "source": "雪球",
        "freshness": 0.95,
    },
    {
        "id": "meme_026",
        "text": "炒股三年，钱没了，朋友多了——都是难兄难弟",
        "loss_level": "any",
        "gentle_variant": "这些年一起熬过熊市的股友，感情比一般的朋友深得多。一起亏过钱的交情是最铁的 ✨",
        "tags": ["社交", "兄弟", "共同体"],
        "source": "淘股吧",
        "freshness": 0.80,
    },
    {
        "id": "meme_027",
        "text": "牛市的时候我是巴菲特，熊市的时候我是巴韭特",
        "loss_level": "any",
        "gentle_variant": "在牛熊之间切换自我认知，是每个交易者的必修课。重要的是在不同的市场环境中保持同一种交易纪律",
        "tags": ["牛熊", "自我认知", "幽默"],
        "source": "雪球",
        "freshness": 0.89,
    },
    {
        "id": "meme_028",
        "text": "炒股最大的成本不是本金，是头发",
        "loss_level": "any",
        "gentle_variant": "交易确实消耗心力，所以更要照顾好自己。身体是革命的本钱，头发也是 ✨",
        "tags": ["健康", "压力", "幽默"],
        "source": "微博股市",
        "freshness": 0.78,
    },
    {
        "id": "meme_029",
        "text": "今天又是为A股流泪的一天 😢",
        "loss_level": "any",
        "gentle_variant": "想哭就哭出来吧。交易日不长，但情绪需要出口。我一直在听",
        "tags": ["情绪宣泄", "日常", "陪伴"],
        "source": "雪球",
        "freshness": 0.77,
    },
    {
        "id": "meme_030",
        "text": "大家好，我是A股的长期股东——被迫的那种",
        "loss_level": "any",
        "gentle_variant": "被动长期投资也是一种策略呢（笑）。不过既然持有了这么久，研究清楚它的基本面，说不定会发现被低估的价值",
        "tags": ["长期持有", "被动投资", "自嘲"],
        "source": "东方财富",
        "freshness": 0.86,
    },
]


class MemeLibrary:
    """热梗语料库"""

    def pick(self, loss_level: str, persona: PersonaType) -> KnowledgeResult:
        """按亏损程度 + 人设匹配热梗。

        Args:
            loss_level: 亏损等级 — mild / moderate / severe / any
            persona: 当前人设类型。RATIONAL 返回空结果。

        Returns:
            KnowledgeResult with up to 5 matching entries
        """
        # RATIONAL 禁用热梗
        if persona == PersonaType.RATIONAL:
            return KnowledgeResult(
                entries=[],
                confidence=0.0,
                source_domain=KnowledgeDomain.MEME,
            )

        # 筛选
        if loss_level == "any":
            candidates = list(_MEME_CORPUS)
        else:
            candidates = [
                m for m in _MEME_CORPUS
                if m["loss_level"] == loss_level or m["loss_level"] == "any"
            ]

        if not candidates:
            return KnowledgeResult(
                entries=[],
                confidence=0.0,
                source_domain=KnowledgeDomain.MEME,
            )

        # 按 freshness 排序，取 top 5
        candidates.sort(key=lambda m: m["freshness"], reverse=True)
        top = candidates[:5]

        entries = []
        for m in top:
            # 按人设选择文本变体
            if persona == PersonaType.GENTLE:
                text = m.get("gentle_variant", m["text"])
            else:
                text = m["text"]

            entries.append(KnowledgeEntry(
                id=m["id"],
                content=text,
                domain=KnowledgeDomain.MEME,
                score=m["freshness"],
                metadata={
                    "loss_level": m["loss_level"],
                    "tags": m["tags"],
                    "source": m["source"],
                },
            ))

        avg_score = sum(e.score for e in entries) / len(entries) if entries else 0.0
        return KnowledgeResult(
            entries=entries,
            confidence=avg_score,
            source_domain=KnowledgeDomain.MEME,
        )

    def get_all_entries(self) -> "list[KnowledgeEntry]":
        """导出全部热梗为 KnowledgeEntry 列表（供 KnowledgeManager 索引）。"""
        entries = []
        for m in _MEME_CORPUS:
            entries.append(KnowledgeEntry(
                id=m["id"],
                content=m["text"],
                domain=KnowledgeDomain.MEME,
                score=m["freshness"],
                metadata={
                    "loss_level": m["loss_level"],
                    "tags": m["tags"],
                    "source": m["source"],
                    "gentle_variant": m.get("gentle_variant", ""),
                },
            ))
        return entries
