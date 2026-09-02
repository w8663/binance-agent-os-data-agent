# Binance Agent OS — Data & Analysis Agent

> 基于 **Binance Agent OS** 工具栈搭建的「数据&分析」AI Agent。拉取 Binance 公开市场行情 + 链上信号，做技术分析并输出结构化市场分析报告。**无需鉴权、不触碰真实交易**。

## 这是什么

Binance Agent OS 是一个把 AI Agent 接到币安能力的平台（Binance API + Wallet Agentic Hub + x402 + Skill Hub + MCP）。本项目用 **Agent OS 的 Binance 公开市场数据能力 + Agentic Wallet 技能**，搭建一个服务于「数据&分析」工作流的 Agent：**观察市场 → 计算技术指标 → 汇总链上异动 → 输出报告**。

> 对应赛道一工作流类别：**数据&分析**（报告 / 市场分析 / 投资组合洞察）。

## 分析能力

- **行情拉取**：Binance 公开 `api.binance.com`（K线 / 24h ticker）
- **技术指标**：SMA20 · RSI14 · ATR14 · 趋势判定（上行/下行/超买/超卖/盘整）
- **链上异动**：集成 ChainRadar 链上信号库（链 / 来源 / 涨幅 / 成交）
- **输出**：`output/report.md`（读得懂的市场分析报告）+ `output/analysis.json`（结构化数据）

## 快速开始

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

# 运行（若需代理: export HTTPS_PROXY=http://127.0.0.1:7890）
python3 agent.py
```

产物写入 `output/`。

## Agent 工作流

```
Binance 公开行情 (K线/ticker)  ┐
ChainRadar 链上信号库          ├──> 分析引擎(SMA/RSI/ATR/趋势) ──> market analysis report
                              ┘
```

## 可扩展（接入 Agent OS MCP）

本 agent 用**公开数据**（免鉴权）。如需**实时账户/下单**，可接 Binance Agent OS MCP server：
`https://agent.binance.com/mcp/agentic`（标准 MCP OAuth 授权，需用户扫码确认 Agentic 子账户）。

```yaml
# Hermes (~/.hermes/config.yaml)
mcp_servers:
  binance:
    url: "https://agent.binance.com/mcp/agentic"
```

## 目录

```
agent.py          # 主 agent：拉数据→分析→出报告
test_mcp.py       # 连 Binance MCP server 连通性测试(需鉴权)
requirements.txt  # 依赖
```

## 免责声明

本 Agent 输出由程序自动生成，仅供研究参考，**不构成投资建议**。数字资产价格波动剧烈，请自行判断（DYOR）。
