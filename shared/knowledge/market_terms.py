"""交易术语库 — 市场概念与术语解释。

内置 ~50 条中文 A 股交易术语，覆盖基础交易、圈层黑话、策略术语、技术分析。
支持术语名 + 别名 + 定义全文搜索，关键词计分匹配。
"""

from shared.types import KnowledgeDomain, KnowledgeEntry, KnowledgeResult


_TERMS: list[dict] = [
    # ═══════════════════════════════════════════════════════════
    # 基础交易 (15 terms)
    # ═══════════════════════════════════════════════════════════
    {
        "id": "term_001",
        "term": "涨停板",
        "definition": "当日涨幅达到交易所规定上限。A股主板±10%，科创/创业板±20%，北交所±30%。",
        "category": "基础交易",
        "aliases": ["涨停", "封板", "打板", "板"],
        "related": ["跌停板", "炸板", "连板", "天地板"],
    },
    {
        "id": "term_002",
        "term": "跌停板",
        "definition": "当日跌幅达到交易所规定下限。个股跌停时卖单远大于买单，难以卖出。",
        "category": "基础交易",
        "aliases": ["跌停", "地板", "核按钮"],
        "related": ["涨停板", "天地板", "闷杀"],
    },
    {
        "id": "term_003",
        "term": "成交量",
        "definition": "一定时间内成交的股票数量或金额。放量上涨视为多头信号，缩量下跌视为空头衰竭。",
        "category": "基础交易",
        "aliases": ["量", "成交额", "量能", "放量", "缩量"],
        "related": ["换手率", "量比", "成交额"],
    },
    {
        "id": "term_004",
        "term": "换手率",
        "definition": "一定时间内股票转手买卖的频率（成交量÷流通股本）。高换手率意味着交易活跃，也可能意味着筹码松动。",
        "category": "基础交易",
        "aliases": ["换手", "周转率"],
        "related": ["成交量", "流通市值", "活跃度"],
    },
    {
        "id": "term_005",
        "term": "市盈率",
        "definition": "股价÷每股收益（PE）。衡量市场对公司未来盈利的预期。高PE=市场预期高增长，低PE=市场预期悲观或被低估。",
        "category": "基础交易",
        "aliases": ["PE", "本益比", "市盈"],
        "related": ["市净率", "估值", "ROE"],
    },
    {
        "id": "term_006",
        "term": "市净率",
        "definition": "股价÷每股净资产（PB）。小于1时股价低于净资产（破净）。银行、钢铁等重资产行业PB通常较低。",
        "category": "基础交易",
        "aliases": ["PB", "市净"],
        "related": ["市盈率", "破净", "净资产"],
    },
    {
        "id": "term_007",
        "term": "流通市值",
        "definition": "可在二级市场自由交易的股份总市值。A股有流通股和限售股之分，流通市值才是市场真金白银的估值。",
        "category": "基础交易",
        "aliases": ["流通值", "盘子", "市值"],
        "related": ["总市值", "换手率", "大小非解禁"],
    },
    {
        "id": "term_008",
        "term": "开盘价",
        "definition": "每个交易日首笔成交价格。A股开盘前有集合竞价（9:15-9:25），最终撮合出开盘价。",
        "category": "基础交易",
        "aliases": ["开盘"],
        "related": ["收盘价", "集合竞价", "高开", "低开"],
    },
    {
        "id": "term_009",
        "term": "收盘价",
        "definition": "每个交易日最后一笔成交价格（A股为15:00）。收盘价是计算涨跌幅和各类指标的基准价格。",
        "category": "基础交易",
        "aliases": ["收盘"],
        "related": ["开盘价", "尾盘", "次日涨跌幅"],
    },
    {
        "id": "term_010",
        "term": "K线",
        "definition": "记录一段时间内开盘价、收盘价、最高价、最低价的图形。阳线（红/白）=收盘高于开盘，阴线（绿/黑）=收盘低于开盘。",
        "category": "基础交易",
        "aliases": ["蜡烛图", "阴阳线", "技术图形"],
        "related": ["均线", "MACD", "KDJ", "RSI"],
    },
    {
        "id": "term_011",
        "term": "均线",
        "definition": "一定时间内的平均收盘价连线（MA）。5日/10日/20日/60日/120日/250日均线是常用参考。均线多头排列=上涨趋势，空头排列=下跌趋势。",
        "category": "基础交易",
        "aliases": ["MA", "移动平均线"],
        "related": ["金叉", "死叉", "K线", "支撑位"],
    },
    {
        "id": "term_012",
        "term": "内盘/外盘",
        "definition": "内盘=主动性卖盘（卖方主动降价成交），外盘=主动性买盘（买方主动加价成交）。外盘>内盘看多，内盘>外盘看空。",
        "category": "基础交易",
        "aliases": ["内外盘"],
        "related": ["委比", "量比", "买卖力道"],
    },
    {
        "id": "term_013",
        "term": "量比",
        "definition": "当前成交量与过去5日均量之比。量比>1=放量，量比<1=缩量。量比>5可能意味着大资金进出。",
        "category": "基础交易",
        "aliases": [],
        "related": ["成交量", "换手率", "放量"],
    },
    {
        "id": "term_014",
        "term": "振幅",
        "definition": "当日最高价与最低价之差÷前收盘价×100%。高振幅个股波动大、风险高，但也意味着短线机会。",
        "category": "基础交易",
        "aliases": [],
        "related": ["波动率", "最高价", "最低价"],
    },
    {
        "id": "term_015",
        "term": "除权/除息",
        "definition": "上市公司分红或送股后，股价相应下调整市值保持不变。除息=分红后股价减分红金额，除权=送股后股价按比例下调。",
        "category": "基础交易",
        "aliases": ["除权除息", "XD", "XR", "DR"],
        "related": ["分红", "送转", "填权", "贴权"],
    },

    # ═══════════════════════════════════════════════════════════
    # 圈层黑话 (15 terms)
    # ═══════════════════════════════════════════════════════════
    {
        "id": "term_016",
        "term": "核按钮",
        "definition": "在跌停板价格挂巨量卖单，企图制造恐慌引发踩踏。比喻为按下核按钮引发连锁反应。",
        "category": "圈层黑话",
        "aliases": ["核"],
        "related": ["跌停板", "闷杀", "踩踏", "天地板"],
    },
    {
        "id": "term_017",
        "term": "天地板",
        "definition": "当天从涨停板直接跌至跌停板（20%波动），或从跌停板拉升至涨停板。是极端暴涨暴跌的圈层形容。",
        "category": "圈层黑话",
        "aliases": ["天地"],
        "related": ["涨停板", "跌停板", "地天板", "核按钮"],
    },
    {
        "id": "term_018",
        "term": "地天板",
        "definition": "当天从跌停板被资金拉到涨停板，是极度戏剧性的逆转行情。",
        "category": "圈层黑话",
        "aliases": ["地天"],
        "related": ["涨停板", "跌停板", "天地板"],
    },
    {
        "id": "term_019",
        "term": "打板",
        "definition": "在涨停价挂单买入，赌次日继续涨停。是一种高风险的短线交易策略，赚的是溢价。",
        "category": "圈层黑话",
        "aliases": ["打涨停", "追板", "板上买"],
        "related": ["涨停板", "炸板", "连板", "龙头"],
    },
    {
        "id": "term_020",
        "term": "炸板",
        "definition": "涨停板被打开，卖盘涌出导致价格回落。打板客最怕的情况，意味着当日可能大幅亏损。",
        "category": "圈层黑话",
        "aliases": ["开板", "放量炸板"],
        "related": ["涨停板", "打板", "核按钮"],
    },
    {
        "id": "term_021",
        "term": "龙头",
        "definition": "板块中涨幅最大、资金量最大、人气最高的领涨股。龙头的走势往往决定整个板块的方向。",
        "category": "圈层黑话",
        "aliases": ["龙头股", "领头羊", "妖股"],
        "related": ["打板", "连板", "板块联动"],
    },
    {
        "id": "term_022",
        "term": "妖股",
        "definition": "脱离基本面，依靠资金博弈连续暴涨的个股。市值小、筹码集中、故事多（如重组/壳资源等）。",
        "category": "圈层黑话",
        "aliases": ["妖", "妖票"],
        "related": ["龙头", "打板", "小盘股"],
    },
    {
        "id": "term_023",
        "term": "韭菜",
        "definition": "散户的自嘲称呼，意指定期被收割（亏损）的投资者。源自韭菜割了一茬又长一茬的特性。",
        "category": "圈层黑话",
        "aliases": ["散韭", "绿油油"],
        "related": ["割韭菜", "散户", "主力"],
    },
    {
        "id": "term_024",
        "term": "割韭菜",
        "definition": "形容大资金/主力利用信息优势和资金优势，在散户追涨杀跌中获利的收割行为。",
        "category": "圈层黑话",
        "aliases": ["收割"],
        "related": ["韭菜", "主力", "散户"],
    },
    {
        "id": "term_025",
        "term": "梭哈",
        "definition": "将全部资金买入一只股票。源自扑克术语'show hand'，是极高风险的操作方式。",
        "category": "圈层黑话",
        "aliases": ["全仓", "all in", "满仓干"],
        "related": ["满仓", "仓位管理", "韭菜"],
    },
    {
        "id": "term_026",
        "term": "关灯吃面",
        'definition': 'A股经典段子：2011年重庆啤酒9个跌停后，一篇《关灯吃面》的帖子走红。比喻亏损后沮丧落魄的心情，关着灯吃一碗面。',
        "category": "圈层黑话",
        "aliases": ["吃面"],
        "related": ["亏损", "跌停", "韭菜"],
    },
    {
        "id": "term_027",
        "term": "踩踏",
        "definition": "市场恐慌蔓延导致大量投资者同时抛售，价格加速下跌，形成'卖得越狠跌得越快→更想卖'的恶性循环。",
        "category": "圈层黑话",
        "aliases": ["多杀多", "踩踏式下跌", "恐慌性抛盘"],
        "related": ["跌停", "核按钮", "流动性危机"],
    },
    {
        "id": "term_028",
        "term": "闷杀",
        "definition": "开盘即大幅下跌甚至跌停，不给任何离场机会。投资者像被闷住一样无法止损。",
        "category": "圈层黑话",
        "aliases": ["闷", "直接闷死"],
        "related": ["核按钮", "跌停", "踩踏"],
    },
    {
        "id": "term_029",
        "term": "抬轿子",
        "definition": "在高位接盘、给先入场的人当接盘侠。形容自己花钱买股票，结果是为别人赚钱、把股价'抬'上去。",
        "category": "圈层黑话",
        "aliases": ["抬轿", "接盘"],
        "related": ["追涨", "高位接盘", "韭菜"],
    },
    {
        "id": "term_030",
        "term": "主力",
        "definition": "有能力影响个股或板块走势的大资金（公募/私募/游资/产业资本等）。散户常在分析时假设'主力要拉'或'主力在出货'。",
        "category": "圈层黑话",
        "aliases": ["大资金", "机构", "庄", "游资"],
        "related": ["割韭菜", "散户", "龙虎榜"],
    },

    # ═══════════════════════════════════════════════════════════
    # 策略术语 (10 terms)
    # ═══════════════════════════════════════════════════════════
    {
        "id": "term_031",
        "term": "价值投资",
        "definition": "以低于内在价值的价格买入优质公司，长期持有等待价值回归。核心指标：ROE、PE、PB、自由现金流。巴菲特为代表性实践者。",
        "category": "策略术语",
        "aliases": ["价值"],
        "related": ["市盈率", "市净率", "ROE", "长期持有"],
    },
    {
        "id": "term_032",
        "term": "趋势跟踪",
        "definition": "追随市场趋势而非预测市场。上涨趋势做多、下跌趋势做空或空仓。不试图抄底逃顶，只获取趋势中段利润。",
        "category": "策略术语",
        "aliases": ["趋势交易", "顺势而为"],
        "related": ["均线", "支撑位/压力位", "动量策略"],
    },
    {
        "id": "term_033",
        "term": "均值回归",
        "definition": "假设价格会回归到历史均值水平。超跌买入、超涨卖出。是逆向投资的核心逻辑。",
        "category": "策略术语",
        "aliases": ["回归均值", "逆向投资"],
        "related": ["价值投资", "技术分析", "波动率"],
    },
    {
        "id": "term_034",
        "term": "动量策略",
        "definition": "买入近期涨幅大的股票、卖出近期跌幅大的股票，押注趋势延续。与均值回归策略方向相反。",
        "category": "策略术语",
        "aliases": ["动量", "强者恒强"],
        "related": ["趋势跟踪", "均值回归", "换手率"],
    },
    {
        "id": "term_035",
        "term": "网格交易",
        "definition": "在设定的价格区间内分档买卖。每下跌一格买入，每上涨一格卖出，赚取波动差价。适合震荡市。",
        "category": "策略术语",
        "aliases": ["网格"],
        "related": ["量化交易", "定投", "波段操作"],
    },
    {
        "id": "term_036",
        "term": "定投",
        "definition": "定期定额买入同一标的。通过分批买入摊平成本、降低择时风险。长期执行可有效降低波动影响。",
        "category": "策略术语",
        "aliases": ["定期定额", "DCA", "微笑曲线"],
        "related": ["网格交易", "长期持有", "均值回归"],
    },
    {
        "id": "term_037",
        "term": "对冲",
        "definition": "通过建立相反方向的头寸来降低风险。如持有股票的同时买入看跌期权，或做多一只同时做空另一只。",
        "category": "策略术语",
        "aliases": ["对冲交易", "hedge"],
        "related": ["套利", "风险管理", "期权"],
    },
    {
        "id": "term_038",
        "term": "套利",
        "definition": "利用相同（或相关）资产在不同市场的价差进行无风险或低风险获利。如A/H股差价套利、期现套利。",
        "category": "策略术语",
        "aliases": ["arbitrage", "价差交易"],
        "related": ["对冲", "量化交易", "A/H溢价"],
    },
    {
        "id": "term_039",
        "term": "波段操作",
        "definition": "在股价的波浪运动中，低买高卖赚取差价。不同于超短线的频繁操作，持股周期通常为几天到几周。",
        "category": "策略术语",
        "aliases": ["波段", "做波段"],
        "related": ["短线", "中长线", "趋势跟踪"],
    },
    {
        "id": "term_040",
        "term": "超短线",
        "definition": "持股几秒到几分钟的高频交易模式。利用微小价差反复获利，对心理素质和交易系统要求极高。A股T+1制度下受限较大。",
        "category": "策略术语",
        "aliases": ["超短", "短线", "T+0"],
        "related": ["打板", "高频交易", "流动性"],
    },

    # ═══════════════════════════════════════════════════════════
    # 技术分析 (10 terms)
    # ═══════════════════════════════════════════════════════════
    {
        "id": "term_041",
        "term": "MACD",
        "definition": "指数平滑异同移动平均线。通过快慢均线的离差分析趋势强弱。金叉（快线上穿慢线）=看多，死叉（快线下穿慢线）=看空。",
        "category": "技术分析",
        "aliases": ["MACD指标"],
        "related": ["均线", "金叉/死叉", "RSI", "KDJ"],
    },
    {
        "id": "term_042",
        "term": "KDJ",
        "definition": "随机指标，分析超买超卖状态。K值>80=超买（可能回调），K值<20=超卖（可能反弹）。短线交易者常用。",
        "category": "技术分析",
        "aliases": ["KD", "随机指标"],
        "related": ["MACD", "RSI", "超买超卖"],
    },
    {
        "id": "term_043",
        "term": "RSI",
        "definition": "相对强弱指标，衡量价格变动速度和幅度。RSI>70=超买，RSI<30=超卖。背离（价格新高但RSI下降）是趋势反转信号。",
        "category": "技术分析",
        "aliases": ["相对强弱指标"],
        "related": ["MACD", "KDJ", "顶背离/底背离"],
    },
    {
        "id": "term_044",
        "term": "布林带",
        "definition": "由中轨（MA20）和上/下轨（±2标准差）组成的通道。价格触及上轨=短期压力，触及下轨=短期支撑。收窄=即将变盘。",
        "category": "技术分析",
        "aliases": ["BOLL", "布林线"],
        "related": ["均线", "支撑位/压力位", "突破"],
    },
    {
        "id": "term_045",
        "term": "支撑位/压力位",
        "definition": "支撑位=下跌时可能止跌回升的价位（前低/密集成交区/均线）；压力位=上涨时可能遇阻回落的价位（前高/套牢盘区域/均线）。",
        "category": "技术分析",
        "aliases": ["支撑", "压力", "阻力位"],
        "related": ["均线", "突破", "回踩", "布林带"],
    },
    {
        "id": "term_046",
        "term": "金叉/死叉",
        "definition": "金叉=短期均线上穿长期均线（看多信号）；死叉=短期均线下穿长期均线（看空信号）。可发生在MA、MACD等多类指标中。",
        "category": "技术分析",
        "aliases": ["黄金交叉", "死亡交叉"],
        "related": ["MACD", "均线", "RSI"],
    },
    {
        "id": "term_047",
        "term": "顶背离/底背离",
        "definition": "价格与指标走势相反。顶背离=价格新高但指标走弱（即将下跌），底背离=价格新低但指标走强（即将反弹）。",
        "category": "技术分析",
        "aliases": ["背离"],
        "related": ["RSI", "MACD", "KDJ"],
    },
    {
        "id": "term_048",
        "term": "放量",
        "definition": "成交量显著放大（通常量比>1.5或直接直观对比前几日）。放量上涨=资金主动进场，放量下跌=资金争相出逃。",
        "category": "技术分析",
        "aliases": ["放量上涨", "放量下跌", "爆量"],
        "related": ["成交量", "量比", "突破", "筹码松动"],
    },
    {
        "id": "term_049",
        "term": "突破",
        "definition": "价格向上突破重要压力位（前高/均线/下降趋势线等），通常伴随放量。有效突破=突破后连续3天站稳或涨幅超3%。",
        "category": "技术分析",
        "aliases": ["突破压力位", "突破平台"],
        "related": ["支撑位/压力位", "放量", "回踩"],
    },
    {
        "id": "term_050",
        "term": "回踩",
        "definition": "价格突破重要阻力位后，先回落到该位置附近确认支撑的有效性，再继续上涨。回踩成功=原阻力位变成了新支撑位。",
        "category": "技术分析",
        "aliases": ["回抽确认", "二次探底"],
        "related": ["突破", "支撑位/压力位", "均线"],
    },
]


class MarketTermsKnowledge:
    """交易术语知识库"""

    def search(self, keywords: list[str]) -> KnowledgeResult:
        """按关键词搜索术语。

        Args:
            keywords: 搜索关键词列表

        Returns:
            KnowledgeResult，按匹配得分排序
        """
        if not keywords:
            return KnowledgeResult()

        scored = []
        for term in _TERMS:
            score = self._match_score(keywords, term)
            if score > 0:
                entry = KnowledgeEntry(
                    id=term["id"],
                    content=f"{term['term']}：{term['definition']}",
                    domain=KnowledgeDomain.MARKET_TERMS,
                    score=score,
                    metadata={
                        "term": term["term"],
                        "category": term["category"],
                        "aliases": term["aliases"],
                        "related": term["related"],
                    },
                )
                scored.append(entry)

        scored.sort(key=lambda e: e.score, reverse=True)
        top = scored[:5]

        avg_score = sum(e.score for e in top) / len(top) if top else 0.0
        return KnowledgeResult(
            entries=top,
            confidence=avg_score,
            source_domain=KnowledgeDomain.MARKET_TERMS,
        )

    @staticmethod
    def _match_score(keywords: list[str], term: dict) -> float:
        """关键词匹配评分。

        - 精确匹配术语名: 1.0
        - 匹配别名: 0.9
        - 关键词在定义中出现: 0.5
        """
        best = 0.0
        for kw in keywords:
            kw_lower = kw.lower()

            # 精确匹配
            if kw_lower == term["term"].lower():
                best = max(best, 1.0)
                continue

            # 别名匹配
            for alias in term.get("aliases", []):
                if kw_lower == alias.lower():
                    best = max(best, 0.9)
                    break

            # 定义全文匹配
            definition = term.get("definition", "").lower()
            if kw_lower in definition:
                best = max(best, 0.5)

            # 相关术语匹配
            for related in term.get("related", []):
                if kw_lower == related.lower():
                    best = max(best, 0.6)
                    break

        return best

    def get_all_entries(self) -> "list[KnowledgeEntry]":
        """导出全部术语为 KnowledgeEntry 列表（供 KnowledgeManager 索引 GrepRetriever）。"""
        entries = []
        for term in _TERMS:
            entries.append(KnowledgeEntry(
                id=term["id"],
                content=f"{term['term']}：{term['definition']}",
                domain=KnowledgeDomain.MARKET_TERMS,
                score=1.0,
                metadata={
                    "term": term["term"],
                    "category": term["category"],
                    "aliases": term["aliases"],
                    "related": term["related"],
                },
            ))
        return entries
