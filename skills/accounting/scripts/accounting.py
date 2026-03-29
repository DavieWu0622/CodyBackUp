#!/usr/bin/env python3
"""Personal accounting skill with SQLite, conversational input, charts and budgets."""

from __future__ import annotations

import csv
import json
import math
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DB_PATH = Path.home() / ".openclaw" / "accounting.db"
BUDGET_FILE = Path.home() / ".openclaw" / "accounting_budget.json"
EXPORT_FILE = Path.home() / ".openclaw" / "accounting_export.csv"
CHART_DIR = Path.home() / ".openclaw" / "accounting_charts"

EXPENSE_KEYWORDS = {
    "餐饮": ["吃饭", "早餐", "早饭", "午餐", "午饭", "晚餐", "晚饭", "咖啡", "奶茶", "餐饮", "外卖", "宵夜"],
    "交通": ["地铁", "打车", "公交", "高铁", "车费", "交通", "加油", "停车"],
    "购物": ["买", "购物", "淘宝", "衣服", "鞋", "日用", "超市"],
    "娱乐": ["电影", "游戏", "娱乐", "KTV", "桌游", "演出"],
    "住宿": ["酒店", "住宿", "民宿"],
    "医疗": ["医院", "药", "看病", "医疗", "挂号"],
    "教育": ["课程", "书", "培训", "教育", "学费"],
}

INCOME_KEYWORDS = {
    "工资": ["工资", "发薪", "薪资"],
    "奖金": ["奖金", "绩效", "提成"],
    "红包": ["红包", "转账"],
    "副业": ["副业", "稿费", "外快", "咨询费"],
}

COLORS = [
    "#4F46E5", "#06B6D4", "#10B981", "#F59E0B", "#EF4444",
    "#8B5CF6", "#EC4899", "#84CC16", "#14B8A6", "#F97316",
]


@dataclass
class ParsedRecord:
    type: str
    amount: float
    category: str
    note: str


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
            amount REAL NOT NULL CHECK(amount >= 0),
            category TEXT NOT NULL,
            note TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
        """
    )
    conn.commit()
    conn.close()


def load_budgets() -> dict:
    if not BUDGET_FILE.exists():
        return {}
    try:
        return json.loads(BUDGET_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_budgets(budgets: dict) -> None:
    BUDGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    BUDGET_FILE.write_text(json.dumps(budgets, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_amount(text: str) -> Optional[float]:
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else None


def infer_category(text: str, mapping: dict, fallback: str) -> str:
    for category, keywords in mapping.items():
        if any(keyword in text for keyword in keywords):
            return category
    return fallback


def split_segments(text: str) -> list[str]:
    parts = re.split(r"[，,；;、和并且然后再]\s*", text.strip())
    return [part.strip() for part in parts if part.strip()]


def parse_segment(text: str) -> Optional[ParsedRecord]:
    raw = text.strip()
    amount = normalize_amount(raw)
    if amount is None:
        return None

    income_markers = ["收入", "收到", "工资", "奖金", "报销", "赚了", "进账"]
    expense_markers = ["花", "用了", "支出", "消费", "付了", "买了", "花费"]

    is_income = any(marker in raw for marker in income_markers)
    is_expense = any(marker in raw for marker in expense_markers)

    if not is_income and not is_expense:
        if any(k in raw for words in EXPENSE_KEYWORDS.values() for k in words):
            is_expense = True
        elif any(k in raw for words in INCOME_KEYWORDS.values() for k in words):
            is_income = True

    if is_income and not is_expense:
        category = infer_category(raw, INCOME_KEYWORDS, "其他收入")
        return ParsedRecord("income", amount, category, raw)

    if is_expense or not is_income:
        category = infer_category(raw, EXPENSE_KEYWORDS, "其他")
        return ParsedRecord("expense", amount, category, raw)

    return None


def parse_conversation(text: str) -> list[ParsedRecord]:
    return [record for part in split_segments(text) if (record := parse_segment(part))]


def month_range(period: str) -> tuple[str, str, str]:
    now = datetime.now()
    if period == "本月":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=32)).replace(day=1)
    elif period == "上月":
        end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start = (end - timedelta(days=1)).replace(day=1)
    elif period == "今年":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now
    else:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = (start + timedelta(days=32)).replace(day=1)
        period = "本月"
    return period, start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")


def fetch_category_totals(kind: str, period: str) -> list[tuple[str, float]]:
    period, start, end = month_range(period)
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT category, SUM(amount) total
        FROM transactions
        WHERE type = ? AND created_at >= ? AND created_at < ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (kind, start, end),
    )
    rows = [(category, float(total)) for category, total in cursor.fetchall()]
    conn.close()
    return rows


def fetch_income_expense_totals(period: str) -> tuple[str, float, float]:
    period, start, end = month_range(period)
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0)
        FROM transactions
        WHERE created_at >= ? AND created_at < ?
        """,
        (start, end),
    )
    income, expense = cursor.fetchone()
    conn.close()
    return period, float(income), float(expense)


def add_transaction(type_: str, amount: float, category: str, note: str = "") -> str:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO transactions (type, amount, category, note) VALUES (?, ?, ?, ?)",
        (type_, float(amount), category, note),
    )
    conn.commit()
    conn.close()

    label = "支出" if type_ == "expense" else "收入"
    result = f"✅ 已记录{label}: {float(amount):.2f}元（{category}）"
    if note:
        result += f"\n📝 备注：{note}"
    if type_ == "expense":
        alert = check_budget(category)
        if alert:
            result += f"\n⚠️ {alert}"
    return result


def add_multiple(records: list[ParsedRecord]) -> str:
    if not records:
        return "❌ 没有识别到可记账内容。"
    outputs = [add_transaction(r.type, r.amount, r.category, r.note) for r in records]
    return "\n\n".join(outputs)


def set_budget(category: str, amount: float) -> str:
    budgets = load_budgets()
    budgets[category] = float(amount)
    save_budgets(budgets)
    return f"✅ 已设置 {category} 月预算：{float(amount):.2f}元"


def list_budgets() -> str:
    budgets = load_budgets()
    if not budgets:
        return "📭 还没有设置任何预算。"
    lines = ["📌 当前预算："]
    for category, amount in budgets.items():
        lines.append(f"- {category}: {float(amount):.2f}元/月")
    return "\n".join(lines)


def check_budget(category: str) -> str:
    budgets = load_budgets()
    if category not in budgets:
        return ""

    _, start, end = month_range("本月")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE type = 'expense' AND category = ? AND created_at >= ? AND created_at < ?
        """,
        (category, start, end),
    )
    spent = float(cursor.fetchone()[0] or 0)
    conn.close()

    budget = float(budgets[category])
    if budget <= 0:
        return ""
    ratio = spent / budget
    if ratio >= 1:
        return f"预算超支：{category} 已用 {spent:.2f}/{budget:.2f} 元（{ratio * 100:.1f}%）"
    if ratio >= 0.8:
        return f"预算预警：{category} 已用 {spent:.2f}/{budget:.2f} 元（{ratio * 100:.1f}%）"
    return ""


def get_stats(period: str = "本月") -> str:
    period, start, end = month_range(period)
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT category, SUM(amount) total, COUNT(*) count
        FROM transactions
        WHERE type='expense' AND created_at >= ? AND created_at < ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (start, end),
    )
    expenses = cursor.fetchall()

    cursor.execute(
        """
        SELECT category, SUM(amount) total, COUNT(*) count
        FROM transactions
        WHERE type='income' AND created_at >= ? AND created_at < ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (start, end),
    )
    incomes = cursor.fetchall()

    cursor.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0)
        FROM transactions
        WHERE created_at >= ? AND created_at < ?
        """,
        (start, end),
    )
    total_income, total_expense = cursor.fetchone()
    conn.close()

    balance = float(total_income) - float(total_expense)
    lines = [
        f"📊 {period}统计",
        "",
        f"💰 总收入：{float(total_income):.2f}元",
        f"💸 总支出：{float(total_expense):.2f}元",
        f"📈 结余：{balance:.2f}元",
    ]

    if expenses:
        lines += ["", "📉 支出明细："]
        for cat, total, count in expenses:
            lines.append(f"- {cat}: {float(total):.2f}元（{count}笔）")

    if incomes:
        lines += ["", "📈 收入明细："]
        for cat, total, count in incomes:
            lines.append(f"- {cat}: {float(total):.2f}元（{count}笔）")

    return "\n".join(lines)


def generate_chart(period: str = "本月") -> str:
    expenses = fetch_category_totals("expense", period)
    if not expenses:
        return f"📊 {period}暂无支出数据"

    total = sum(float(amount) for _, amount in expenses)
    max_amount = max(float(amount) for _, amount in expenses)
    width = 20
    lines = [f"📊 {period}支出图表", ""]
    for category, amount in expenses:
        amount = float(amount)
        pct = amount / total * 100 if total else 0
        bar_len = max(1, round(amount / max_amount * width)) if max_amount else 1
        lines.append(f"{category:<6} {'█' * bar_len:<20} {amount:8.2f} ({pct:5.1f}%)")
    lines += ["", f"💸 总计：{total:.2f}元"]
    return "\n".join(lines)


def export_data() -> str:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, amount, category, note, created_at FROM transactions ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    EXPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with EXPORT_FILE.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Type", "Amount", "Category", "Note", "Created At"])
        writer.writerows(rows)

    return f"✅ 数据已导出到：{EXPORT_FILE}"


def polar_to_cartesian(cx: float, cy: float, r: float, angle_deg: float) -> tuple[float, float]:
    rad = math.radians(angle_deg)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def svg_pie_path(cx: float, cy: float, r: float, start_angle: float, end_angle: float) -> str:
    x1, y1 = polar_to_cartesian(cx, cy, r, start_angle)
    x2, y2 = polar_to_cartesian(cx, cy, r, end_angle)
    large_arc = 1 if end_angle - start_angle > 180 else 0
    return f"M {cx:.2f} {cy:.2f} L {x1:.2f} {y1:.2f} A {r:.2f} {r:.2f} 0 {large_arc} 1 {x2:.2f} {y2:.2f} Z"


def render_expense_pie_svg(period: str = "本月") -> str:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    data = fetch_category_totals("expense", period)
    if not data:
        return "📭 暂无支出数据，无法生成饼图。"

    total = sum(amount for _, amount in data)
    width, height = 960, 640
    cx, cy, r = 260, 300, 180
    angle = -90.0
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="40" y="50" font-size="28" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#111827">{period}支出分类饼图</text>',
        f'<text x="40" y="85" font-size="16" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#6B7280">总支出：{total:.2f} 元</text>',
    ]

    for i, (category, amount) in enumerate(data):
        sweep = 360 * amount / total if total else 0
        end_angle = angle + sweep
        path = svg_pie_path(cx, cy, r, angle, end_angle)
        color = COLORS[i % len(COLORS)]
        parts.append(f'<path d="{path}" fill="{color}" stroke="#ffffff" stroke-width="2"/>')
        angle = end_angle

    legend_y = 140
    for i, (category, amount) in enumerate(data):
        color = COLORS[i % len(COLORS)]
        pct = amount / total * 100 if total else 0
        y = legend_y + i * 34
        parts.append(f'<rect x="520" y="{y-14}" width="18" height="18" rx="4" fill="{color}"/>')
        parts.append(f'<text x="550" y="{y}" font-size="16" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#111827">{category}</text>')
        parts.append(f'<text x="760" y="{y}" font-size="16" text-anchor="end" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#374151">{amount:.2f}元</text>')
        parts.append(f'<text x="900" y="{y}" font-size="16" text-anchor="end" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#6B7280">{pct:.1f}%</text>')

    parts.append('</svg>')
    path = CHART_DIR / f"expense_pie_{period}.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    return f"✅ 已生成支出饼图：{path}"


def render_summary_bar_svg(period: str = "本月") -> str:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    period, income, expense = fetch_income_expense_totals(period)
    if income == 0 and expense == 0:
        return "📭 暂无数据，无法生成收支柱状图。"

    width, height = 900, 560
    chart_left, chart_bottom = 120, 430
    chart_top = 120
    bar_width = 140
    max_value = max(income, expense, 1)

    income_height = (income / max_value) * (chart_bottom - chart_top)
    expense_height = (expense / max_value) * (chart_bottom - chart_top)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="40" y="50" font-size="28" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#111827">{period}收支柱状图</text>',
        f'<text x="40" y="85" font-size="16" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#6B7280">结余：{income - expense:.2f} 元</text>',
        f'<line x1="{chart_left}" y1="{chart_top}" x2="{chart_left}" y2="{chart_bottom}" stroke="#9CA3AF" stroke-width="2"/>',
        f'<line x1="{chart_left}" y1="{chart_bottom}" x2="760" y2="{chart_bottom}" stroke="#9CA3AF" stroke-width="2"/>',
    ]

    for idx, value in enumerate([income, expense]):
        y = chart_bottom - (value / max_value) * (chart_bottom - chart_top)
        label = f"{value:.0f}"
        parts.append(f'<text x="90" y="{y + 5:.2f}" font-size="13" text-anchor="end" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#6B7280">{label}</text>')
        parts.append(f'<line x1="{chart_left}" y1="{y:.2f}" x2="760" y2="{y:.2f}" stroke="#E5E7EB" stroke-width="1"/>')

    income_x = 220
    expense_x = 470
    parts.append(f'<rect x="{income_x}" y="{chart_bottom - income_height:.2f}" width="{bar_width}" height="{income_height:.2f}" rx="10" fill="#10B981"/>')
    parts.append(f'<rect x="{expense_x}" y="{chart_bottom - expense_height:.2f}" width="{bar_width}" height="{expense_height:.2f}" rx="10" fill="#EF4444"/>')
    parts.append(f'<text x="{income_x + bar_width/2}" y="{chart_bottom + 35}" text-anchor="middle" font-size="18" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#111827">收入</text>')
    parts.append(f'<text x="{expense_x + bar_width/2}" y="{chart_bottom + 35}" text-anchor="middle" font-size="18" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#111827">支出</text>')
    parts.append(f'<text x="{income_x + bar_width/2}" y="{chart_bottom - income_height - 15:.2f}" text-anchor="middle" font-size="16" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#065F46">{income:.2f}</text>')
    parts.append(f'<text x="{expense_x + bar_width/2}" y="{chart_bottom - expense_height - 15:.2f}" text-anchor="middle" font-size="16" font-family="Arial, PingFang SC, Microsoft YaHei" fill="#991B1B">{expense:.2f}</text>')
    parts.append('</svg>')

    path = CHART_DIR / f"income_expense_bar_{period}.svg"
    path.write_text("\n".join(parts), encoding="utf-8")
    return f"✅ 已生成收支柱状图：{path}"


def monthly_report(period: str = "本月") -> str:
    period, income, expense = fetch_income_expense_totals(period)
    expense_rows = fetch_category_totals("expense", period)
    budgets = load_budgets()
    lines = [
        f"🧾 {period}记账月报",
        "",
        f"- 总收入：{income:.2f}元",
        f"- 总支出：{expense:.2f}元",
        f"- 结余：{income - expense:.2f}元",
    ]

    if expense_rows:
        lines += ["", "📌 支出 Top 分类："]
        for category, amount in expense_rows[:3]:
            lines.append(f"- {category}: {amount:.2f}元")

    alerts = []
    for category, budget in budgets.items():
        spent = next((amount for cat, amount in expense_rows if cat == category), 0.0)
        if budget and spent / budget >= 1:
            alerts.append(f"- {category} 超支：{spent:.2f}/{budget:.2f}元")
        elif budget and spent / budget >= 0.8:
            alerts.append(f"- {category} 预警：{spent:.2f}/{budget:.2f}元")

    if alerts:
        lines += ["", "⚠️ 预算提醒：", *alerts]

    if income == 0 and expense == 0:
        lines += ["", "本期暂无数据。"]
    elif income >= expense:
        lines += ["", "✅ 总体收支健康，当前结余为正。"]
    else:
        lines += ["", "⚠️ 当前支出已超过收入，建议复盘高支出分类。"]

    return "\n".join(lines)


def usage() -> str:
    return (
        "Usage: accounting.py <command> [args...]\n"
        "Commands:\n"
        "  parse <text>                  解析自然语言并记账（支持多条）\n"
        "  add_expense <amt> <cat> [note]\n"
        "  add_income <amt> <cat> [note]\n"
        "  stats [本月|上月|今年]\n"
        "  chart [本月|上月]\n"
        "  budget <category> <amount>   设置预算\n"
        "  budgets                       查看预算\n"
        "  export                        导出 CSV\n"
        "  pie [本月|上月]               生成支出分类 SVG 饼图\n"
        "  bar [本月|上月|今年]          生成收支 SVG 柱状图\n"
        "  report [本月|上月|今年]       生成文字月报\n"
    )


def main() -> None:
    if len(sys.argv) < 2:
        print(usage())
        return

    command = sys.argv[1]

    if command == "parse":
        if len(sys.argv) < 3:
            print("Usage: accounting.py parse <text>")
            return
        text = " ".join(sys.argv[2:])
        parsed = parse_conversation(text)
        if not parsed:
            print("❌ 无法解析。试试：'今天午饭花了38元'、'今天打车花了25块'、'工资收入12000'、'中午吃饭32，晚上打车24'")
            return
        print(add_multiple(parsed))
        return

    if command == "add_expense":
        if len(sys.argv) < 4:
            print("Usage: accounting.py add_expense <amount> <category> [note]")
            return
        amount, category = sys.argv[2], sys.argv[3]
        note = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        print(add_transaction("expense", float(amount), category, note))
        return

    if command == "add_income":
        if len(sys.argv) < 4:
            print("Usage: accounting.py add_income <amount> <category> [note]")
            return
        amount, category = sys.argv[2], sys.argv[3]
        note = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        print(add_transaction("income", float(amount), category, note))
        return

    if command == "stats":
        period = sys.argv[2] if len(sys.argv) > 2 else "本月"
        print(get_stats(period))
        return

    if command == "chart":
        period = sys.argv[2] if len(sys.argv) > 2 else "本月"
        print(generate_chart(period))
        return

    if command == "budget":
        if len(sys.argv) < 4:
            print("Usage: accounting.py budget <category> <amount>")
            return
        print(set_budget(sys.argv[2], float(sys.argv[3])))
        return

    if command == "budgets":
        print(list_budgets())
        return

    if command == "export":
        print(export_data())
        return

    if command == "pie":
        period = sys.argv[2] if len(sys.argv) > 2 else "本月"
        print(render_expense_pie_svg(period))
        return

    if command == "bar":
        period = sys.argv[2] if len(sys.argv) > 2 else "本月"
        print(render_summary_bar_svg(period))
        return

    if command == "report":
        period = sys.argv[2] if len(sys.argv) > 2 else "本月"
        print(monthly_report(period))
        return

    print(f"Unknown command: {command}\n\n{usage()}")


if __name__ == "__main__":
    main()
