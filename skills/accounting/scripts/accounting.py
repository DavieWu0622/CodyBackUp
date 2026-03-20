#!/usr/bin/env python3
"""
Accounting Skill - Personal bookkeeping with SQLite
Features: conversational input, charts, budget alerts
"""

import sqlite3
import json
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path.home() / ".openclaw" / "accounting.db"
BUDGET_FILE = Path.home() / ".openclaw" / "accounting_budget.json"

def init_db():
    """Initialize SQLite database"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def parse_conversation(text):
    """Parse conversational input like '今天吃饭花了50块' or '工资收入10000'"""
    text = text.strip()
    
    # Expense patterns
    expense_patterns = [
        r'(?:花|用|消费|支出).*?(\d+(?:\.\d+)?).*?(?:块|元|块钱)',
        r'(?:吃饭|餐饮|购物|交通|娱乐).*?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?).*?(?:块|元|块钱).*?(?:吃饭|餐饮|购物|交通)',
    ]
    
    # Income patterns
    income_patterns = [
        r'(?:收入|收到|工资|奖金).*?(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?).*?(?:收入|工资|奖金)',
    ]
    
    # Try expense patterns
    for pattern in expense_patterns:
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            # Extract category
            categories = ['餐饮', '购物', '交通', '娱乐', '住宿', '医疗', '教育', '其他']
            category = '其他'
            for cat in categories:
                if cat in text:
                    category = cat
                    break
            return ('expense', amount, category, text)
    
    # Try income patterns
    for pattern in income_patterns:
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            category = '工资' if '工资' in text else ('奖金' if '奖金' in text else '其他收入')
            return ('income', amount, category, text)
    
    return None

def add_transaction(type_, amount, category, note=""):
    """Add a new transaction"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (type, amount, category, note)
        VALUES (?, ?, ?, ?)
    ''', (type_, float(amount), category, note))
    conn.commit()
    conn.close()
    
    # Check budget after adding expense
    alert = ""
    if type_ == 'expense':
        alert = check_budget(category)
    
    result = f"✅ 已记录{'支出' if type_ == 'expense' else '收入'}: {amount}元 ({category})"
    if alert:
        result += f"\n⚠️ {alert}"
    return result

def set_budget(category, amount):
    """Set monthly budget for a category"""
    BUDGET_FILE.parent.mkdir(parents=True, exist_ok=True)
    budgets = {}
    if BUDGET_FILE.exists():
        with open(BUDGET_FILE, 'r') as f:
            budgets = json.load(f)
    
    budgets[category] = float(amount)
    with open(BUDGET_FILE, 'w') as f:
        json.dump(budgets, f, ensure_ascii=False, indent=2)
    
    return f"✅ 已设置 {category} 月度预算: {amount}元"

def check_budget(category):
    """Check if spending exceeds budget"""
    if not BUDGET_FILE.exists():
        return ""
    
    with open(BUDGET_FILE, 'r') as f:
        budgets = json.load(f)
    
    if category not in budgets:
        return ""
    
    budget = budgets[category]
    
    # Get current month spending
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now()
    start = now.replace(day=1)
    end = (start + timedelta(days=32)).replace(day=1)
    
    cursor.execute('''
        SELECT SUM(amount) FROM transactions
        WHERE type = 'expense' AND category = ? AND created_at >= ? AND created_at < ?
    ''', (category, start.isoformat(), end.isoformat()))
    
    spent = cursor.fetchone()[0] or 0
    conn.close()
    
    if spent > budget:
        return f"预算超支！{category}已用 {spent:.2f}/{budget:.2f}元 ({spent/budget*100:.1f}%)"
    elif spent > budget * 0.8:
        return f"预算警告！{category}已用 {spent:.2f}/{budget:.2f}元 ({spent/budget*100:.1f}%)"
    
    return ""

def get_stats(period="本月"):
    """Get statistics for a period"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate date range
    now = datetime.now()
    if period == "本月":
        start = now.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
    elif period == "上月":
        end = now.replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
    elif period == "今年":
        start = now.replace(month=1, day=1)
        end = now
    else:
        start = now.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
    
    # Get expense stats
    cursor.execute('''
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM transactions
        WHERE type = 'expense' AND created_at >= ? AND created_at < ?
        GROUP BY category
        ORDER BY total DESC
    ''', (start.isoformat(), end.isoformat()))
    expenses = cursor.fetchall()
    
    # Get income stats
    cursor.execute('''
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM transactions
        WHERE type = 'income' AND created_at >= ? AND created_at < ?
        GROUP BY category
        ORDER BY total DESC
    ''', (start.isoformat(), end.isoformat()))
    incomes = cursor.fetchall()
    
    # Get totals
    cursor.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expense,
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income
        FROM transactions
        WHERE created_at >= ? AND created_at < ?
    ''', (start.isoformat(), end.isoformat()))
    totals = cursor.fetchone()
    
    conn.close()
    
    total_expense = totals[0] if totals else 0
    total_income = totals[1] if totals else 0
    balance = total_income - total_expense
    
    result = f"📊 {period}统计\n\n"
    result += f"💰 总收入: {total_income:.2f}元\n"
    result += f"💸 总支出: {total_expense:.2f}元\n"
    result += f"📈 结余: {balance:.2f}元\n\n"
    
    if expenses:
        result += "📉 支出明细:\n"
        for cat, total, count in expenses:
            result += f"  • {cat}: {total:.2f}元 ({count}笔)\n"
    
    if incomes:
        result += "\n📈 收入明细:\n"
        for cat, total, count in incomes:
            result += f"  • {cat}: {total:.2f}元 ({count}笔)\n"
    
    return result

def generate_chart(period="本月"):
    """Generate ASCII chart for expenses"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate date range
    now = datetime.now()
    if period == "本月":
        start = now.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
    elif period == "上月":
        end = now.replace(day=1)
        start = (end - timedelta(days=1)).replace(day=1)
    else:
        start = now.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
    
    # Get expense stats
    cursor.execute('''
        SELECT category, SUM(amount) as total
        FROM transactions
        WHERE type = 'expense' AND created_at >= ? AND created_at < ?
        GROUP BY category
        ORDER BY total DESC
    ''', (start.isoformat(), end.isoformat()))
    expenses = cursor.fetchall()
    conn.close()
    
    if    
    if not expenses:
        return f"📊 {period}暂无支出数据"
    
    result = f"📊 {period}支出图表\n\n"
    
    # Calculate total
    total = sum(amount for _, amount in expenses)
    
    # Generate ASCII bar chart
    max_amount = max(amount for _, amount in expenses)
    bar_width = 20
    
    for category, amount in expenses:
        percentage = amount / total * 100
        bar_length = int(amount / max_amount * bar_width)
        bar = "█" * bar_length
        result += f"{category:6s} {bar} {amount:8.2f} ({percentage:5.1f}%)\n"
    
    result += f"\n💸 总计: {total:.2f}元"
    return result

def export_data():
    """Export data to CSV"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    csv_path = Path.home() / ".openclaw" / "accounting_export.csv"
    with open(csv_path, 'w', encoding='utf-8') as f:
        f.write("ID,Type,Amount,Category,Note,Created At\n")
        for row in rows:
            f.write(",".join(str(x) for x in row) + "\n")
    
    return f"✅ 数据已导出到: {csv_path}"

def main():
    if len(sys.argv) < 2:
        print("Usage: accounting.py <command> [args...]")
        print("Commands:")
        print("  parse <text>           - Parse conversational input")
        print("  add_expense <amt> <cat> [note]")
        print("  add_income <amt> <cat> [note]")
        print("  stats [period]         - Show statistics")
        print("  chart [period]         - Show ASCII chart")
        print("  budget <cat> <amt>     - Set monthly budget")
        print("  export                 - Export to CSV")
        return
    
    command = sys.argv[1]
    
    if command == "parse":
        if len(sys.argv) < 3:
            print("Usage: accounting.py parse <text>")
            return
        text = " ".join(sys.argv[2:])
        result = parse_conversation(text)
        if result:
            type_, amount, category, note = result
            print(add_transaction(type_, amount, category, note))
        else:
            print("❌ 无法解析，请使用格式: '吃饭花了50块' 或 '工资收入10000'")
    
    elif command == "add_expense":
        if len(sys.argv) < 4:
            print("Usage: accounting.py add_expense <amount> <category> [note]")
            return
        amount = sys.argv[2]
        category = sys.argv[3]
        note = sys.argv[4] if len(sys.argv) > 4 else ""
        print(add_transaction("expense", amount, category, note))
    
    elif command == "add_income":
        if len(sys.argv) < 4:
            print("Usage: accounting.py add_income <amount> <category> [note]")
            return
        amount = sys.argv[2]
        category = sys.argv[3]
        note = sys.argv[4] if len(sys.argv) > 4 else ""
        print(add_transaction("income", amount, category, note))
    
    elif command == "stats":
        period = sys.argv[2] if len(sys.argv) > 2 else "本月"
        print(get_stats(period))
    
    elif command == "chart":
        period = sys.argv[2] if len(sys.argv) > 2 else "本月"
        print(generate_chart(period))
    
    elif command == "budget":
        if len(sys.argv) < 4:
            print("Usage: accounting.py budget <category> <amount>")
            return
        category = sys.argv[2]
        amount = sys.argv[3]
        print(set_budget(category, amount))
    
    elif command == "export":
        print(export_data())
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
