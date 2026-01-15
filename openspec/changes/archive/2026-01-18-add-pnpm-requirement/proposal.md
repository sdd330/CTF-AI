# Change: 规范化前端包管理器使用 pnpm

## Why
项目已经在使用 pnpm 作为前端包管理器（package.json 中有 `"packageManager": "pnpm@9.0.0"` 配置，存在 pnpm-lock.yaml 和 .npmrc），但在 frontend spec 中没有明确的要求。需要在规范中正式确立 pnpm 作为唯一的包管理器，确保团队成员和 CI/CD 环境使用一致的工具。

## What Changes
- 在 frontend spec 中新增 "Package Manager" requirement
- 明确规定必须使用 pnpm 而不是 npm 或 yarn
- 规定 package.json 中必须包含 packageManager 字段
- 规定必须提交 pnpm-lock.yaml 到版本控制

## Impact
- 受影响的规范: frontend
- 受影响的代码: 无（项目已经在使用 pnpm，此变更仅规范化要求）
- 文档影响: 可能需要在 README 或开发文档中说明如何安装和使用 pnpm
