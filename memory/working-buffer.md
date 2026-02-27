# Working Buffer (Danger Zone Log)

**Status:** READY
**Purpose:** 捕获上下文 >60% 后的每一次对话，防止 compaction 丢失信息

---

## 使用规则

当会话上下文达到 60% 时：
1. 清空旧 buffer，重新开始记录
2. 每一条消息都记录：用户输入 + 我的回复摘要
3. 发生 compaction 后：先读 buffer 恢复上下文

---

## 日志区域

*暂无记录 - 等待进入危险区 (context > 60%)*

---

*最后重置: 2026-02-26*
