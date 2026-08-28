# AI 原生 SDLC 产物目录设计

> 主笔记　[AI-native SDLC.md](AI-native%20SDLC.md)
>
> Skills Hub　[skills-hub.md](skills-hub.md)
>
> 完整译文　[2026-08-译文-AiNativeSdlcPlaybook.md](2026-08-译文-AiNativeSdlcPlaybook.md)

## 1. 设计目标

目录以一次变更为聚合单位。同一项变更的 `intent.md`、`spec.md` 和 `plan.md` 放在同一个稳定目录中，代码差异、测试、PR 和事故记录通过 ID、链接与 commit SHA 接入这条产物链。

这套结构遵循五项原则。

1. 每项变更拥有稳定且唯一的 change ID。
2. 产物路径不随阶段和状态变化。
3. Git 保存修订历史，不创建 `final`、`v2` 等文件副本。
4. 每类信息只指定一个唯一事实来源。
5. 事故独立归档，并与它生成的新意图双向关联。

## 2. 先区分三类文件

| 类别 | 文件或记录 | 生命周期 |
| --- | --- | --- |
| 单次变更产物 | `intent.md`、`spec.md`、`plan.md`、验证索引 | 随某项变更创建和批准 |
| 代码库级规则 | `CLAUDE.md`、`REVIEW.md`、Skills、Hooks | 长期生效并随代码库演进 |
| 外部权威记录 | Commit、CI 运行、PR、部署记录和事故系统记录 | 由 Git、CI/CD、PR 或事故系统管理 |

文章中的根目录 `REVIEW.md` 是长期生效的 PR 评审规则，记录评审轮次、严重程度和忽略项。第五阶段的产物是包含评审发现、修复记录和人工批准的 PR，不需要再复制成独立评审结论文件。

## 3. 推荐目录结构

```text
repository/
├── CLAUDE.md
├── REVIEW.md
├── .claude/
│   ├── skills/
│   │   ├── capture-intent/
│   │   ├── compose-spec/
│   │   ├── brand-guidelines/
│   │   ├── compliance-policy/
│   │   ├── ux-standards/
│   │   ├── security-policy/
│   │   ├── api-design-conventions/
│   │   └── secure-api-review/
│   └── commands/
│       └── compose-spec.md
└── docs/
    └── sdlc/
        ├── 00_Index.md
        ├── changes/
        │   ├── PROJ-142-claims-status/
        │   │   ├── 00_Index.md
        │   │   ├── intent.md
        │   │   ├── spec.md
        │   │   ├── plan.md
        │   │   ├── verification.md
        │   │   └── evidence/
        │   │       └── approved-prototype.png
        │   └── PROJ-143-payment-retry/
        │       └── ...
        └── incidents/
            └── INC-20260828-001-claims-api/
                ├── incident.md
                └── evidence/
                    ├── metrics.png
                    └── timeline.md
```

`verification.md` 是可选索引，用来汇总测试、构建、截图比较和安全检查的结果。原始日志继续保存在 CI 或可观测性系统中。

## 4. 六个阶段与目录的映射

| 阶段 | 正式产物 | 保存位置 | 唯一事实来源 | 触发的下一步 |
| --- | --- | --- | --- | --- |
| 规划 | `intent.md` | `changes/<change-id>/intent.md` | Git 中获批的文件 | 生成并评审 `spec.md` |
| 设计 | `spec.md` | `changes/<change-id>/spec.md` | Git 中获批的文件 | 进入 Claude Code 计划模式 |
| 构建 | `plan.md`，随后产生代码差异 | `changes/<change-id>/plan.md` 和 Git commit | Git 文件与 commit | 实现并进入验证循环 |
| 测试 | 代码差异、测试和验证证据 | Commit、CI，可选 `verification.md` | Git 和 CI | 创建 PR |
| 部署 | PR、评审发现和批准记录 | GitHub、GitLab 或同类系统 | PR 系统 | 合并后触发 CI/CD 与部署 |
| 维护 | 事故记录，必要时产生新 `intent.md` | 事故系统或 `incidents/<incident-id>/incident.md` | 指定的事故记录系统 | 将新意图送回规划阶段 |

流程关系如下。

```text
changes/<change-id>/intent.md
              ↓
changes/<change-id>/spec.md
              ↓
changes/<change-id>/plan.md
              ↓
Git commit 与 CI 验证
              ↓
PR、评审发现与人工批准
              ↓
部署或事故记录
              ↓
changes/<new-change-id>/intent.md
```

## 5. 为什么按变更建目录

按 `intent/`、`spec/` 和 `plan/` 分别建立阶段目录，会把同一项工作的上下文分散到不同位置。评审者需要依赖文件名或搜索才能重新拼出完整链条。

按 change ID 聚合后，同一项变更的前三个 Markdown 产物始终相邻，后续 commit、CI、PR 和事故也能从 `00_Index.md` 进入。状态变化只修改元数据，不需要移动文件。

## 6. 两级 `00_Index.md`

### 6.1 SDLC 总索引

`docs/sdlc/00_Index.md` 负责列出所有活动变更、近期完成项和事故。它不复制具体产物正文。

```markdown
# SDLC 总索引

## 活动变更

| Change ID | 主题 | 当前阶段 | 负责人 | 入口 |
| --- | --- | --- | --- | --- |
| PROJ-142 | 理赔状态自助查询 | 构建 | 张三 | [查看](changes/PROJ-142-claims-status/00_Index.md) |
| PROJ-143 | 支付重试 | 设计 | 李四 | [查看](changes/PROJ-143-payment-retry/00_Index.md) |

## 近期事故

| Incident ID | 主题 | 状态 | 入口 |
| --- | --- | --- | --- |
| INC-20260828-001 | 理赔 API 超时 | 已分流 | [查看](incidents/INC-20260828-001-claims-api/incident.md) |
```

总索引适合由自动任务维护。新变更目录创建、阶段批准或事故关闭时，任务更新对应行。

### 6.2 单项变更索引

每个 `changes/<change-id>/00_Index.md` 是这项变更的入口，记录当前状态、产物、批准人与外部记录。

```markdown
# PROJ-142　理赔状态自助查询

## 状态

当前阶段为构建。
负责人为张三。

## 产物

| 产物 | 状态 | 负责人或批准人 |
| --- | --- | --- |
| [intent.md](intent.md) | 已接受 | 产品负责人 |
| [spec.md](spec.md) | 已批准 | 产品负责人 |
| [plan.md](plan.md) | 待批准 | 工程师 |
| [verification.md](verification.md) | 未开始 | 代码负责人 |

## 外部记录

- 工单　PROJ-142
- Commit　待生成
- CI　待运行
- PR　待创建
- 事故　无
```

单项索引只保存定位信息和状态。需求、设计、计划与评审结论继续留在各自的权威产物中。

## 7. 目录和 ID 命名

### 7.1 优先复用现有记录 ID

如果 Jira、Linear、ServiceNow 或其他需求系统已经分配 ID，目录直接复用它。

```text
PROJ-142-claims-status
PAY-271-payment-retry
```

没有外部记录 ID 时，可以使用以下格式。

```text
CHG-20260828-001-claims-status
```

事故采用独立 ID。

```text
INC-20260828-001-claims-api
```

### 7.2 保持路径稳定

目录创建后不因标题、负责人或状态变化而改名。标题变化写入 `00_Index.md`，阶段变化写入元数据。稳定路径有利于工单、PR、CI 和事故系统长期引用。

## 8. 产物元数据

前三个 Markdown 产物使用一致的 YAML frontmatter，方便自动任务关联和检查。

```yaml
---
change_id: PROJ-142
artifact: spec
status: approved
owner: product-owner
approved_by: li-ming
approved_at: 2026-08-28
parent: ./intent.md
source_record: PROJ-142
policy_versions:
  compose-spec: 1.0.0
  security-policy: 1.2.0
  ux-standards: 2.1.0
---
```

建议固定以下字段。

| 字段 | 用途 |
| --- | --- |
| `change_id` | 关联同一项变更的全部产物 |
| `artifact` | 标识 `intent`、`spec` 或 `plan` |
| `status` | 记录 draft、approved、rejected 或 superseded |
| `owner` | 记录当前负责角色 |
| `approved_by` | 记录人工批准人 |
| `approved_at` | 记录批准时间 |
| `parent` | 链接上一阶段产物 |
| `source_record` | 链接 Jira、ServiceNow 或其他权威记录 |
| `policy_versions` | 保存生成和评审时使用的 Skill 版本 |

Git 已经保存完整修订历史，因此继续修改同一个文件并重新经过批准关卡。范围发生根本变化时，新建 change ID，并从旧变更索引链接到新变更。

## 9. 外部事实来源

### 9.1 代码差异和测试

代码差异以 commit 为唯一事实来源，测试和构建结果以 CI 为唯一事实来源。`verification.md` 只保存摘要和定位信息。

```markdown
# 验证记录

## 对应版本

Commit 为 abc1234。

## 自动检查

| 检查 | 结果 | 权威记录 |
| --- | --- | --- |
| 单元测试 | 通过 | CI run 1842 |
| 集成测试 | 通过 | CI run 1843 |
| 视觉比较 | 通过 | Screenshots artifact 92 |
| API 安全检查 | 通过 | CI run 1844 |

## 未解决问题

无。
```

### 9.2 PR 和评审发现

PR 系统保存评审发现、修复讨论、严重程度和人工批准。变更目录的 `00_Index.md` 只记录 PR URL、最终 commit SHA 和合并状态，不复制完整讨论。

根目录 `REVIEW.md` 保存评审规则。它规定评审轮次、Important 与 Nit 的定义、忽略项和人工阈值，所有 PR 使用同一版本。

### 9.3 部署记录

部署系统保存环境、版本、批准、开始时间、结束时间和回滚结果。`00_Index.md` 可以记录部署 ID 或 URL，但不维护第二份部署日志。

## 10. 事故与新意图

事故独立于变更目录，因为一次事故可能生成多个修复任务，一项变更也可能与多次事故有关。

```text
incidents/INC-20260828-001-claims-api/incident.md
                         ↓ 生成
changes/PROJ-188-fix-claims-timeout/intent.md
                         ↓
spec.md → plan.md → Commit 与测试 → PR
```

`incident.md` 至少记录触发时间、异常证据、影响范围、已经执行的动作、分流决定和生成的 change ID。新 `intent.md` 的 `source_record` 指向 incident ID。

修复发布后，事故记录补充 PR、commit、部署记录和永久评估用例的链接。忽略或暂缓处理同样需要保存决定人、时间和理由。

## 11. 跨代码库变更

单一产品优先把 SDLC 目录放在产品代码库中，让产物靠近最终代码。跨多个代码库的意图可以放在独立的意图或产物仓库中，每个相关代码库保存 change ID 和权威产物的 commit SHA。

独立产物仓库适合以下情况。

1. 一项意图经常横跨多个代码库。
2. 产品负责人无法访问各产品代码库。
3. 监管要求统一保留需求和批准记录。
4. 已有需求系统需要通过连接器与多个仓库同步。

即使使用独立仓库，每类产物仍应指定一个唯一事实来源。其他系统只保存副本或链接。

## 12. 落地检查清单

- [ ] 每项变更拥有稳定且唯一的 change ID。
- [ ] 同一项变更的 `intent.md`、`spec.md` 和 `plan.md` 位于同一目录。
- [ ] `docs/sdlc/00_Index.md` 可以定位所有活动变更和事故。
- [ ] 每个变更目录包含自己的 `00_Index.md`。
- [ ] 每份产物记录上一阶段文件和批准信息。
- [ ] Skill 版本随 `spec.md` 保存。
- [ ] Commit、CI、PR、部署和事故系统各自保持唯一事实来源。
- [ ] Markdown 文件只保存必要摘要、记录 ID、URL 和 commit SHA。
- [ ] 根目录 `REVIEW.md` 只保存评审规则。
- [ ] 事故记录与其生成的新 `intent.md` 双向关联。
- [ ] 状态变化只更新元数据，不移动或重命名产物目录。
