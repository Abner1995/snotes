---
name: git
description: 自动生成 conventional commit 提交信息并推送到 GitHub
---

# Git 自动提交并推送

自动分析 git diff 和 staged changes，按项目规范生成提交信息，提交并推送到 GitHub。

## 执行步骤

### 1. 查看当前状态

```bash
git status
```

```bash
git diff --stat
```

```bash
git diff --cached --stat
```

### 2. 分析变更生成提交信息

根据变更内容，遵循 conventional commits 规范：

- 格式：`docs(<scope>): <中文描述>`
- type：本项目为纯文档仓库，统一使用 `docs`
- scope：变更涉及的模块目录，如 `dotnet`、`Linux`、`SSH`、`python`、`PHP`、`MySQL`、`redis`、`docker`、`git`、`stock`、`fund`、`CLAUDE`
- 描述：一句话说明做了什么，用中文

**已有提交参考：**

```
docs(SSH): 添加SSH密钥配置文档
docs(Linux/debug): 添加V2Ray服务调试命令
docs(python): 添加conda安装使用文档并更新目录索引
docs(CLAUDE): 添加项目级CLAUDE.md指导文件
```

### 3. 提交

```bash
git add <files>
```

```bash
git commit -m "$(cat <<'EOF'
docs(<scope>): <描述>
EOF
)"
```

### 4. 推送到 GitHub

```bash
git push origin main
```

推送前确认远程地址：`origin  https://github.com/Abner1995/snotes.git`

## 注意事项

- 不要 `git add -A` 或 `git add .`，始终明确指定文件
- 推送前确认用户意图（尤其是 force push 绝不执行）
- 如果有未跟踪文件，询问用户是否纳入提交
- commit message 遵循 conventional commits 规范
- `docs/build/` 下的构建产物通常随文档内容一起提交
- 新增文档时确认对应的 `index.md` toctree 已更新
