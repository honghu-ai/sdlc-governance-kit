# Skill 目录

## 1. 已实现：治理基础设施

### [`sdlc-scaffold`](../skills/sdlc-scaffold/SKILL.md)

初始化、补齐或审计代码库级 SDLC 治理结构。输出是新增文件清单、未修改文件清单和结构检查结果。它不创建单项变更目录和阶段产物，重复运行不会覆盖团队已有内容。

## 2. 已实现：产物生成

### [`capture-intent`](../skills/capture-intent/SKILL.md)

读取想法、工单或事故发现，生成结构化 `intent.md` 草稿。内容包括问题、期望结果、受影响对象、约束、范围外事项和未决问题。正式产物由发起人修正并由产品负责人接受。

### [`compose-spec`](../skills/compose-spec/SKILL.md)

读取已接受的 `intent.md`，加载适用政策 Skills，生成或校验完整的 `spec.md` 草稿。内容包括目标、范围、用户场景、功能需求、系统边界、非功能要求、政策约束、验收条件、风险和批准记录。

## 3. 已实现：领域政策

### [`brand-guidelines`](../skills/brand-guidelines/SKILL.md)

在变更包含客户可见界面、文案或品牌表达时，根据权威品牌材料提供或审核视觉规则、语气与术语、禁止用法、验收条件、违规、冲突和例外升级事项。输出不拥有完整 `spec.md`，不替品牌负责人批准。

### [`compliance-policy`](../skills/compliance-policy/SKILL.md)

在变更受到法律、监管、行业或组织合规政策约束时，根据权威材料提供或审核适用范围、合规义务、数据保留、审计证据、批准角色、政策冲突和例外流程。输出不是法律意见或正式合规批准。

### [`security-policy`](../skills/security-policy/SKILL.md)

根据系统边界、数据类型和权威安全政策，提供或审核身份授权、数据、密钥、依赖、网络、日志、供应链相关约束、威胁关注点、验收条件和升级事项。外部 API 专项检查仍交给 `secure-api-review`。

## 4. 计划中：领域政策与标准

### `ux-standards`

输出用户流程、界面状态、可访问性检查项和体验验收条件。

### `api-design-conventions`

输出 API 契约约束和设计检查结果，覆盖路径、字段、版本、Schema、分页、错误格式和兼容性。

## 5. 计划中：专项验证

### `secure-api-review`

输出 API 安全要求、按严重程度排列的问题和检查脚本结果，覆盖身份认证、输入校验、审计事件和 PII。

## 6. 共同要求

每个 Skill 都需要写清触发条件、排除条件、输入、输出、正式产物关系、人工负责人和政策来源。Skill 专用模板、界面元数据和评估用例与 Skill 放在同一目录。需要确定执行的规则必须配套 Hook 或 CI 检查。每次 Skill 变更都要通过评估用例，并由对应负责人评审。
