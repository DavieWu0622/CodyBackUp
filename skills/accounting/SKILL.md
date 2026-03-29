---
name: accounting
description: Personal bookkeeping skill for SQLite-based local accounting. Use when creating, refining, or operating a personal expense tracker with conversational Chinese inputs like “今天午饭花了38元”, monthly budgets, statistical reports, SVG charts, or CSV exports.
---

# Accounting

个人本地记账 skill，面向单人使用，基于 SQLite 保存数据，支持：

- 对话式记账
- 月预算提醒
- 统计报表
- ASCII / SVG 图表
- CSV 导出

## 何时使用

当用户要做这些事时使用本 skill：

- 记录收入/支出
- 分析本月、上月、今年的收支
- 设置分类预算并检查是否超支
- 生成记账图表或月报
- 导出数据到 CSV

## 核心文件

- 主脚本：`scripts/accounting.py`
- 数据库：`~/.openclaw/accounting.db`
- 预算文件：`~/.openclaw/accounting_budget.json`
- 导出文件：`~/.openclaw/accounting_export.csv`
- 图表目录：`~/.openclaw/accounting_charts/`

## 快速命令

### 对话式记账
```bash
python3 scripts/accounting.py parse "今天午饭花了38元"
python3 scripts/accounting.py parse "工资收入12000，奖金500"
```

### 手动记账
```bash
python3 scripts/accounting.py add_expense 38 餐饮 午饭
python3 scripts/accounting.py add_income 12000 工资 3月工资
```

### 预算
```bash
python3 scripts/accounting.py budget 餐饮 2000
python3 scripts/accounting.py budgets
```

### 统计与图表
```bash
python3 scripts/accounting.py stats 本月
python3 scripts/accounting.py chart 本月
python3 scripts/accounting.py pie 本月
python3 scripts/accounting.py bar 本月
python3 scripts/accounting.py report 本月
```

### 导出
```bash
python3 scripts/accounting.py export
```

## 说明

- `parse` 支持一句话多条：`中午吃饭32，晚上打车24`
- 当前图表输出为 SVG，稳定且无第三方依赖
- 当前为单用户本地账本，不含多账户/多人协作

## 进一步扩展

如果需要继续增强，优先做：

1. 账户维度（现金/微信/支付宝/信用卡）
2. 标签维度（工作/生活/学习）
3. 对话直连（在 Telegram 里直接记账）
4. 定时周报 / 月报
