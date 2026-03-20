# Accounting Skill

Personal accounting/bookkeeping skill with SQLite storage and conversational interface.

## Features

- 💬 Conversational input (e.g., "今天吃饭花了50块")
- 💰 Track expenses and income
- 📊 Visual charts and monthly reports
- 🗄️ SQLite database storage
- 📱 Personal use only

## Commands

### Record Expense
```
记账 支出 <金额> <类别> [备注]
```

### Record Income
```
记账 收入 <金额> <来源> [备注]
```

### View Statistics
```
记账 统计 [本月|上月|今年]
```

### View Chart
```
记账 图表 [本月|上月]
```

### Export Data
```
记账 导出
```

## Database Schema

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL, -- 'expense' or 'income'
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Examples

```
记账 支出 50 餐饮 午餐
记账 收入 10000 工资 3月份工资
记账 统计 本月
记账 图表
```
