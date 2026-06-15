"""
social-tactician 工具实现 — 股市圈层社交辅助。

工具返回纯数据（不含 Persona 色彩）。
Persona 转换由 Host LLM 在 Phase 2 完成。

核心定位: 情境感知型关系策动器、同频共鸣发生器。
MVP: 基于场景模板的静态话术生成，不依赖实时行情数据。
"""

from shared.knowledge.manager import KnowledgeManager
from shared.types import ToolContext


# ═══════════════════════════════════════════════════════════
# 破冰场景模板
# ═══════════════════════════════════════════════════════════

_ICE_BREAK_SCENARIOS: dict[str, dict] = {
    "market_down_broad": {
        "condition": "通用市场下行",
        "topics": [
            {"subject": "最近行情真磨人", "angle": "共情式",
             "market_connection": "大盘连续调整，市场情绪低迷"},
            {"subject": "你还有仓位吗", "angle": "关心式",
             "market_connection": "仓位管理是熊市最重要的话题"},
            {"subject": "有什么抗跌的票推荐吗", "angle": "请教式",
             "market_connection": "防御性板块/高股息标的"},
        ],
        "ice_breakers": [
            "最近这行情，我都不敢看账户了，你呢？",
            "今天又绿了，有没有什么好票抗跌的？交流下避风港方向",
            "这波调整你仓位控制得怎么样？想学学你的防守策略",
        ],
        "market_hooks": ["大盘下跌", "恐慌情绪", "防御板块", "仓位管理"],
    },
    "market_up_broad": {
        "condition": "通用市场上行",
        "topics": [
            {"subject": "这波赚到了吗", "angle": "轻松式",
             "market_connection": "行情回暖，赚钱效应扩散"},
            {"subject": "有什么好方向推荐", "angle": "请教式",
             "market_connection": "领涨板块/龙头个股"},
            {"subject": "这波能走多远", "angle": "讨论式",
             "market_connection": "技术分析/宏观判断"},
        ],
        "ice_breakers": [
            "最近行情不错啊，你抓住了吗？",
            "今天你手里哪个票涨得最好？让我眼红一下",
            "你觉得这波是反弹还是反转？想听听你的看法",
        ],
        "market_hooks": ["大盘上涨", "赚钱效应", "领涨板块", "趋势判断"],
    },
    "specific_holding_down": {
        "condition": "对方持仓可能下跌",
        "topics": [
            {"subject": "一起聊聊这只票", "angle": "共情式",
             "market_connection": "个股波动/板块联动"},
            {"subject": "你的逻辑是什么", "angle": "请教式",
             "market_connection": "投资理念/选股逻辑"},
        ],
        "ice_breakers": [
            "诶，你那个票最近走得不太顺啊，你还在拿着吗？",
            "你当初为什么选这只票的？想学习下你的选股思路",
            "我也遇到过这种情况，聊聊你是怎么应对的？",
        ],
        "market_hooks": ["个股下跌", "持仓波动", "投资逻辑", "持有心态"],
    },
    "generic": {
        "condition": "无特定行情信息",
        "topics": [
            {"subject": "炒股心得交流", "angle": "开放式",
             "market_connection": "投资理念/交易经验"},
            {"subject": "最近在学什么", "angle": "成长式",
             "market_connection": "交易学习/策略研究"},
            {"subject": "你是怎么复盘的", "angle": "请教式",
             "market_connection": "复盘方法/交易系统"},
            {"subject": "你觉得做短线好还是做波段好", "angle": "讨论式",
             "market_connection": "交易风格/策略选择"},
        ],
        "ice_breakers": [
            "你一般怎么做复盘？我最近想改进下方法，想听听你的",
            "你觉得做短线好还是做波段好？想听听你的经验和判断",
            "最近在学什么新的交易策略吗？交流一下",
            "除了炒股，你还有什么爱好？感觉盘后得找点事做",
        ],
        "market_hooks": ["交易理念", "复盘方法", "策略选择", "生活平衡"],
    },
}

# ═══════════════════════════════════════════════════════════
# 深度话题框架
# ═══════════════════════════════════════════════════════════

_DEEP_TALK_FRAMEWORKS: dict[str, dict] = {
    "投资哲学": {
        "framework": {
            "opener": "你是什么时候开始意识到，投资其实是在投自己对这个世界的认知？",
            "bridge": "所以你的投资决策框架大概是什么样的？是从基本面出发，还是更看技术面？",
            "core_theme": "投资理念的背后是一个人的世界观——你怎么看风险、怎么看时间、怎么看自己在这个市场中的位置。",
            "closer": "今天聊得很深，回头我把你刚才说的那个方法论实践一下，有结果了告诉你。这样下次聊更有话题。",
        },
        "discussion_points": [
            "你是更相信基本面还是技术面？为什么？",
            "有没有一本书改变了你的投资观念？",
            "你觉得散户最大的优势是什么？最大的劣势呢？",
            "如果你的孩子想学炒股，你第一句话会告诉他什么？",
        ],
        "pitfalls": [
            "不要争论'长线好还是短线好'——这是价值观，不是技术问题",
            "不要炫耀自己的收益率——这会立刻破坏深度交流的氛围",
            "不要批评别人的持仓——每个人都有自己看不到的约束条件",
            "不要强行输出建议——先理解对方的逻辑，再给看法",
            "不要在对方分享亏损时评价'你怎么不早止损'——这是最伤人的马后炮",
        ],
    },
    "风险认知": {
        "framework": {
            "opener": "你觉得自己能承受的最大回撤是多少？不是理性上的，是心理上的——那个让你睡不着觉的数字。",
            "bridge": "你有没有经历过那种'睡不着觉'的回撤？后来怎么走出来的？",
            "core_theme": "风险承受能力不是问卷上的一个选项，而是在凌晨3点看着账户时，心跳还能不能稳。",
            "closer": "风险这件事，每个人都有自己的答案。关键是找到让自己睡得着觉的那个仓位。",
        },
        "discussion_points": [
            "你觉得散户最大的风险是什么？不是市场风险，是行为风险",
            "如果明天大盘跌停，你的第一反应会是什么？",
            "你有没有给自己设过'最大亏损线'？实际执行过吗？",
            "仓位管理和选股能力，你觉得哪个更重要？",
        ],
        "pitfalls": [
            "不要把别人对风险的描述当成'胆小'去评判",
            "不要比较'谁亏得更多'——这不是勇气比赛，是创伤比较",
            "不要在对方分享脆弱时给建议——先听，再问，最后才说",
            "不要说'才亏这点算什么'——每个人的心理承受力不同",
            "不要炫耀自己在暴跌中抄底成功——这在对方亏损时最刺耳",
        ],
    },
    "市场周期": {
        "framework": {
            "opener": "你有没有发现，每次你忍不住想满仓的时候，往往是阶段高点；每次想清仓的时候，往往是阶段低点？",
            "bridge": "你觉得现在是牛市、熊市还是震荡市？为什么这么判断？",
            "core_theme": "识别市场周期不是为了精准抄底逃顶，而是为了知道自己现在站在什么位置，该用多大的仓位去参与。",
            "closer": "周期的话题永远聊不完。下次出了什么大新闻，咱们再一起分析分析。",
        },
        "discussion_points": [
            "你觉得现在的市场像历史上哪个阶段？为什么？",
            "牛市的顶部和熊市的底部，你觉得各有什么特征？",
            "如果大盘再跌20%，你会怎么做？如果涨20%呢？",
            "政策、资金、情绪——你觉得现在市场主要受哪个因素驱动？",
        ],
        "pitfalls": [
            "不要预测具体点位和时间——'下周一定会涨到3500'这种话打脸概率99%",
            "不要用'牛市'或'熊市'来判断别人的持仓——标签化是思考的捷径",
            "不要用宏大的经济分析压制对方的经验感受——宏观是宏观，操作是操作",
            "不要在对方分享判断时打断'不对，我觉得是...'——先听完",
            "不要居高临下纠正别人的周期判断——没有人能100%看对市场",
        ],
    },
    "交易心理": {
        "framework": {
            "opener": "你觉得交易中最难控制的情绪是什么？贪婪还是恐惧？还是别的什么？",
            "bridge": "你最近一次因为情绪做了错误的交易决定是什么时候？",
            "core_theme": "交易的本质不是图形分析，是自我管理。每一笔交易中最难战胜的对手，永远是自己。",
            "closer": "跟你聊完感觉心态都稳了。交易心理这东西，光看书不够，得跟人交流。以后多聊聊。",
        },
        "discussion_points": [
            "你有过'明知不该买但还是买了'的经历吗？当时在想什么？",
            "盈利后你会飘吗？怎么控制盈利后的过度自信？",
            "亏钱的时候，有没有什么帮自己冷静下来的方法？",
            "你觉得交易纪律是可以训练出来的吗？还是天生的？",
        ],
        "pitfalls": [
            "不要把对方的交易失误当成笑话——那是信任的终结",
            "不要说自己'从不情绪化交易'——这在老股民听来是典型的过度自信",
            "不要拿巴菲特索罗斯来对比对方的错误——凡人不跟神比",
            "不要在对方聊心理脆弱时说'那你别炒股了'——这不是建议，是否定",
            "不要分享'我朋友一天赚了XX万'的故事——这只会增加焦虑",
        ],
    },
    "生活平衡": {
        "framework": {
            "opener": "除了看盘，你最近一次完全忘记股票是什么时候？在做什么？",
            "bridge": "很多全职交易者的生活被屏幕绑架了。你有刻意留出'不看盘'的时间吗？",
            "core_theme": "生活不是为了交易，交易是为了更好的生活。当账户的涨跌决定了每天的喜怒哀乐，就需要重新审视这个关系了。",
            "closer": "下次周末约着出去走走（至少精神上），不看盘不聊票，就聊吃喝玩乐。交易不是生活的全部。",
        },
        "discussion_points": [
            "你有规律的锻炼习惯吗？交易对身体消耗真的很夸张",
            "家里人支持你全职炒股吗？你是怎么处理这个压力的？",
            "如果有一天你不炒股了，你会去做什么？",
            "盘后你一般怎么切换状态？直接复盘还是先放松？",
        ],
        "pitfalls": [
            "不要说'一天赚X万还累什么'——心理疲劳和盈亏无关",
            "不要嘲笑对方'看盘看到没朋友'——这是职业交易者的共性困境",
            "不要强行拉对方'出来玩'——先理解，再建议",
            "不要在对方说一个人很孤独时说'那找个对象啊'——这是最无效的建议",
            "不要暗示'全职炒股不务正业'——这是对职业选择的否定",
        ],
    },
}


class SocialTacticianTools:
    """社交辅助工具集"""

    def __init__(self, knowledge: KnowledgeManager = None):
        self._knowledge = knowledge

    # ── 破冰建议 ──────────────────────────────────

    def ice_break_suggest(
        self,
        target_holdings: list[str] = None,
        context: ToolContext = None,
    ) -> dict:
        """根据场景生成社交破冰建议。

        Args:
            target_holdings: 社交对象的持仓标的（可选）
            context: 用户上下文

        Returns:
            { topics: [dict], ice_breakers: [str], market_hooks: [str], scenario: str }
        """
        scenario = self._detect_scenario(target_holdings, context)
        template = _ICE_BREAK_SCENARIOS.get(scenario, _ICE_BREAK_SCENARIOS["generic"])

        return {
            "topics": template["topics"][:3],
            "ice_breakers": template["ice_breakers"],
            "market_hooks": template["market_hooks"],
            "scenario": scenario,
            "scenario_description": template["condition"],
        }

    @staticmethod
    def _detect_scenario(
        target_holdings: list[str] = None,
        context: ToolContext = None,
    ) -> str:
        """从输入推断当前社交场景。"""
        # 有持仓信息 → 特定标的场景
        if target_holdings:
            return "specific_holding_down"

        # 从 user_input 推断市场方向
        user_input = ""
        if context:
            user_input = context.user_input.lower()

        down_keywords = ["跌", "绿", "跳水", "崩", "亏", "调整", "下跌", "熊", "惨"]
        up_keywords = ["涨", "红", "牛", "赚", "起飞", "反弹", "突破", "新高"]

        has_down = any(kw in user_input for kw in down_keywords)
        has_up = any(kw in user_input for kw in up_keywords)

        if has_down:
            return "market_down_broad"
        elif has_up:
            return "market_up_broad"
        else:
            return "generic"

    # ── 深度话题 ──────────────────────────────────

    def deep_talk_suggest(
        self,
        topic: str = "",
        context: ToolContext = None,
    ) -> dict:
        """生成深度交流话题框架。

        Args:
            topic: 话题名称 — 投资哲学 / 风险认知 / 市场周期 / 交易心理 / 生活平衡 / ""
            context: 用户上下文

        Returns:
            { framework: dict, discussion_points: [str], pitfalls: [str], topic: str }
        """
        topic = topic.strip()
        if not topic:
            topic = self._infer_topic(context)

        framework = _DEEP_TALK_FRAMEWORKS.get(topic)
        if not framework:
            # 回退到最通用的话题
            topic = "交易心理"
            framework = _DEEP_TALK_FRAMEWORKS[topic]

        return {
            "framework": framework["framework"],
            "discussion_points": framework["discussion_points"],
            "pitfalls": framework["pitfalls"],
            "topic": topic,
        }

    @staticmethod
    def _infer_topic(context: ToolContext = None) -> str:
        """从上下文推断适合的深度话题。"""
        if not context:
            return "交易心理"

        user_input = context.user_input.lower()

        # 关键词 → 话题映射
        topic_hints = {
            "投资哲学": ["为什么买", "逻辑", "投资理念", "选股逻辑", "认知"],
            "风险认知": ["回撤", "止损", "风险", "仓位", "睡不着", "担心"],
            "市场周期": ["牛市", "熊市", "周期", "见顶", "见底", "反弹", "反转"],
            "交易心理": ["心态", "情绪", "贪婪", "恐惧", "后悔", "扛单", "纪律"],
            "生活平衡": ["累", "孤独", "无聊", "一个人", "朋友", "家人", "生活"],
        }

        for topic_name, hints in topic_hints.items():
            if any(hint in user_input for hint in hints):
                return topic_name

        return "交易心理"

    def list_topics(self) -> list[str]:
        """返回所有可用的深度话题列表。"""
        return list(_DEEP_TALK_FRAMEWORKS.keys())
