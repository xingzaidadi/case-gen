# vcb-case-gen Skill 设计进度记录

> 创建时间：2026-06-03
> 工作目录：E:\workspace\VCB\vibe-claw-bot

---

## 如何继续工作

重启后打开 Claude Code，切换到项目目录，直接说：

> **"继续设计 vcb-case-gen skill，上次已经确认了整体架构，接下来要设计第二段：三步扫描引擎 + VCB 规则库的详细内容。"**

Claude 会自动读取本文件夹的记录，从中断处继续。

---

## 已完成的内容

### 现状评估

| 能力 | 评分 | 说明 |
|------|------|------|
| AI Skill 用例生成（sentry-cases） | 8/10 | 成熟，专注 SKILL.md，不涉及 Java 后端 |
| Java 后端用例生成 | 3/10 | 全靠手写（02_单测方案-vcb.md、03_E2E方案-vcb.md），无自动化 |

### 决策记录

| 问题 | 决策 |
|------|------|
| 目标类型 | Java 后端（单测场景 + E2E 验收），AI Skill 继续用 sentry-cases |
| 主要输入 | Java 源码 + 规格/设计文档（双输入） |
| 主要输出 | Markdown 场景设计文档（单测矩阵 + E2E 清单） |
| 交互风格 | 默认直出 + 关键点确认 |
| 方案选择 | **方案 C：规则锚定式生成器** |

### 已确认的架构（第一段）

```
输入层
  ├── Java 源文件路径（Controller / Service）
  └── 规格/设计文档路径或内容

三步扫描引擎（核心）
  ├── Step 1 · 显性规则扫描  ── 从接口签名、注解、文档中提取明确规则
  ├── Step 2 · 流程规则扫描  ── 梳理请求路径，逐步问「这里可能失败吗？」
  └── Step 3 · 隐性规则推演  ── 结合 VCB 规则库，找「没写但不该有」的行为

VCB 规则库（独立维护）
  ├── 鉴权四层（身份/资源/Scope/幂等）
  ├── 审批链路规则（actor 过滤、四动作、审计字段）
  ├── Job 隔离规则（owner 校验、跨用户拦截）
  └── 可扩展：后续新增领域规则不改 skill 主体

场景生成引擎
  ├── 覆盖 8 类场景（happy_path / cross_user / scope / idempotency / audit / metrics / compatibility / e2e）
  └── 每个场景含：用例ID / 优先级 / 模块 / 场景描述 / 期望 / 测试类型

输出层
  ├── 单测场景矩阵（Markdown，含 Mock 建议 / 覆盖目标 / 退出标准）
  └── E2E 验收清单（Markdown，含 P0/P1 分级 / 观测指标 / 放行标准）

关键暂停点（仅两处）
  ├── ⏸ 规则提取完成后 → 展示规则列表，问「有遗漏吗？」
  └── ⏸ 发现高风险场景 → 展示并确认优先级，再输出最终文档
```

---

## 待完成的任务

按顺序进行，每段确认后再继续。

### [x] 第二段：三步扫描引擎详细设计
- 每一步的具体扫描逻辑是什么
- 输入是代码还是文档，如何混合读取
- 如何与 VCB 规则库交叉验证

### [x] 第三段：VCB 规则库内容设计
- 规则库的数据结构
- 初始内容（从现有手写文档中提炼，13 条规则）
- 规则库的维护机制（如何新增/更新规则）

### [x] 第四段：输出格式设计
- 单测场景矩阵的完整模板（对齐 02_单测方案-vcb.md 格式）
- E2E 验收清单的完整模板（对齐 03_E2E方案-vcb.md 格式）
- 两种输出的切换逻辑

### [x] 第五段：触发词 & description 设计
- Skill 的 description 要写得准确，不误触发
- 典型触发场景 / 不触发场景列举

### [x] 第六段：完整 SKILL.md 草稿
- 已写入 ~/.claude/skills/vcb-case-gen/SKILL.md

### [x] 写设计文档
- 保存到 docs/superpowers/specs/2026-06-03-vcb-case-gen-design.md ✅
- commit 到 git ✅（commit ce7c9e11）

### [x] 调用 writing-plans skill 生成实施计划
- 已保存到 docs/superpowers/plans/2026-06-03-vcb-case-gen.md ✅（commit 87d3961b）

---

## 参考文件

| 文件 | 用途 |
|------|------|
| `docs/mobile-center-v2/02_单测方案-vcb.md` | 单测场景矩阵模板样本 |
| `docs/mobile-center-v2/03_E2E方案-vcb侧验收清单.md` | E2E 验收清单模板样本 |
| `~/.claude/skills/SkillSentry/tools/sentry-cases/SKILL.md` | 参考：sentry-cases 的用例设计逻辑 |
| `~/.claude/skills/SkillSentry/SKILL.md` | 参考：SkillSentry 主调度器 |
