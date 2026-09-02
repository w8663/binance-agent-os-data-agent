#!/usr/bin/env python3
"""
Binance Agent OS Data & Analysis Agent
基于币安 Agent OS 工具栈（Binance 公开市场数据 API + Agentic Wallet 技能 + 链上信号）
搭建的「数据&分析」Agent：拉取市场数据 → 技术分析 → 输出结构化分析报告。
无鉴权、不碰真实交易。赛道一作品。
"""
import json, sys, time, urllib.request, urllib.parse, os, sqlite3
from datetime import datetime

BINANCE = "https://api.binance.com/api/v3"
PROXY = os.environ.get("HTTPS_PROXY", "")
UA = "Mozilla/5.0 (Binance Agent OS Data Agent)"

def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    proxy_handler = urllib.request.ProxyHandler({"http": PROXY, "https": PROXY}) if PROXY else None
    opener = urllib.request.build_opener(proxy_handler) if proxy_handler else urllib.request.build_opener()
    return json.loads(opener.open(req, timeout=timeout).read().decode())

def kline(symbol, interval="1h", limit=48):
    url = f"{BINANCE}/klines?symbol={urllib.parse.quote(symbol)}&interval={interval}&limit={limit}"
    rows = http_get(url)
    return [[int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])] for r in rows]

def ticker_24h(symbol):
    url = f"{BINANCE}/ticker/24hr?symbol={urllib.parse.quote(symbol)}"
    return http_get(url)

def sma(vals, n):
    return sum(vals[-n:]) / n if len(vals) >= n else (sum(vals) / len(vals) if vals else 0)

def rsi(vals, n=14):
    if len(vals) < n + 1: return None
    gains, losses = [], []
    for i in range(1, len(vals)):
        d = vals[i] - vals[i-1]
        gains.append(max(d, 0)); losses.append(max(-d, 0))
    ag = sum(gains[-n:]) / n; al = sum(losses[-n:]) / n
    if al == 0: return 100
    rs = ag / al
    return 100 - (100 / (1 + rs))

def atr(rows, n=14):
    if len(rows) < n + 1: return None
    trs = []
    for i in range(1, len(rows)):
        h, l, pc = rows[i][2], rows[i][3], rows[i-1][4]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(trs[-n:]) / n

def analyze_symbol(sym):
    try:
        kl = kline(sym)
        t = ticker_24h(sym)
    except Exception as e:
        return {"symbol": sym, "error": str(e)[:120]}
    closes = [k[4] for k in kl]
    last = closes[-1]
    chg = float(t.get("priceChangePercent", 0))
    vol = float(t.get("quoteVolume", 0))
    s = {
        "symbol": sym,
        "price": round(last, 6),
        "change24h_pct": round(chg, 2),
        "quote_volume24h": round(vol, 0),
        "sma20": round(sma(closes, 20), 6),
        "rsi14": round(rsi(closes), 1) if rsi(closes) is not None else None,
        "atr14": round(atr(kl), 6) if atr(kl) is not None else None,
        "trend": None,
    }
    # 趋势判断
    if s["rsi14"] is not None:
        if s["rsi14"] > 70: s["trend"] = "超买"
        elif s["rsi14"] < 30: s["trend"] = "超卖"
        elif last > s["sma20"]: s["trend"] = "上行"
        elif last < s["sma20"]: s["trend"] = "下行"
        else: s["trend"] = "盘整"
    s["above_sma20"] = last > s["sma20"]
    return s

def onchain_signals(db_path):
    """读 ChainRadar 链上信号库(若存在)。"""
    out = []
    if db_path and os.path.exists(db_path):
        try:
            con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cur = con.execute("SELECT chain,source,name,change24,vol24 FROM signals ORDER BY CAST(change24 AS REAL) DESC LIMIT 20")
            for r in cur.fetchall():
                out.append({"chain": r[0], "source": r[1], "name": r[2], "change24": r[3], "vol24": r[4]})
            con.close()
        except Exception as e:
            out.append({"error": str(e)[:100]})
    return out

def build_report(analysis, onchain, ts=None):
    ts = ts or datetime.now().strftime("%Y-%m-%d %H:%M")
    ok = [a for a in analysis if not a.get("error")]
    err = [a for a in analysis if a.get("error")]
    lines = []
    lines.append(f"# 币安市场分析报告 — Binance Agent OS 数据分析 Agent")
    lines.append(f"**生成时间**：{ts}  |  数据源：Binance 公开行情 + 链上信号  |  分析：Binance Agent OS Data Agent")
    lines.append("")
    lines.append("## 一、大盘概览")
    lines.append("")
    for a in ok[:6]:
        lines.append(f"- **{a['symbol']}**  ${a['price']:,.4f}  24h **{a['change24h_pct']:+.2f}%**  成交 ${a['quote_volume24h']:,.0f}  RSI {a['rsi14']}  趋势**{a['trend']}**")
    lines.append("")
    lines.append("## 二、技术面（SMA20 / RSI14 / ATR14）")
    lines.append("")
    lines.append("| 币种 | 现价 | 24h% | SMA20 | RSI14 | ATR14 | 趋势 |")
    lines.append("|---|---|---|---|---|---|---|")
    for a in ok:
        lines.append(f"| {a['symbol']} | ${a['price']:,.4f} | {a['change24h_pct']:+.1f}% | ${a['sma20']:,.4f} | {a['rsi14']} | {a['atr14']} | {a['trend']} |")
    lines.append("")
    lines.append("## 三、链上异动信号（ChainRadar）")
    lines.append("")
    if onchain:
        for o in onchain[:12]:
            if "error" not in o:
                lines.append(f"- [{o['chain']}] {o['name']}（{o['source']}）  24h **{o['change24']}%**  成交 ${o['vol24']:,.0f}")
    else:
        lines.append("- 暂无链上信号")
    lines.append("")
    lines.append("## 四、风险提示")
    lines.append("")
    lines.append("> 本报告由 Binance Agent OS 数据分析 Agent 自动生成，仅供研究参考，**不构成投资建议**。数字资产价格波动剧烈，请自行判断(DYOR)。")
    return "\n".join(lines)

def main():
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT"]
    print(">>> 拉取币安行情 + 技术分析 ...", file=sys.stderr)
    analysis = [analyze_symbol(s) for s in symbols]
    ok = [a for a in analysis if not a.get("error")]
    print(f">>> 成功分析 {len(ok)}/{len(symbols)} 个币种", file=sys.stderr)
    db = os.path.expanduser("~/chainradar/data/signals.db")
    onchain = onchain_signals(db)
    print(f">>> 链上信号 {len([o for o in onchain if 'error' not in o])} 条", file=sys.stderr)
    report = build_report(analysis, onchain)
    os.makedirs("output", exist_ok=True)
    with open("output/report.md", "w") as f: f.write(report)
    with open("output/analysis.json", "w") as f: json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(report)

if __name__ == "__main__":
    main()
