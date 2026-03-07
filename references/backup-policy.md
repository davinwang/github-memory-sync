# 备份策略与安全建议

## 📁 文件分类

### 🔒 高敏感度（必须加密/私有仓库）

这些文件包含个人敏感信息，**必须**使用私有仓库：

| 文件 | 内容 | 风险 |
|------|------|------|
| **MEMORY.md** | 用户偏好、地址、习惯 | 隐私泄露 |
| **memory/*.md** | 日常对话记录、待办 | 隐私泄露 |
| **USER.md** | 用户姓名、时区、笔记 | 个人信息 |
| **TOOLS.md** | SSH 密钥、摄像头位置、设备信息 | 安全风险 |
| **SOUL.md** | AI 人格设定 | 中等 |
| **IDENTITY.md** | AI 身份定义 | 中等 |

### 🟡 中敏感度（建议私有）

| 文件 | 内容 | 风险 |
|------|------|------|
| **HEARTBEAT.md** | 定时任务、检查项 | 可能暴露习惯 |
| **AGENTS.md** | 工作流指南 | 低 |
| **skills/** | 自定义技能 | 可能包含 API keys |

### ⚪ 低敏感度（可公开）

| 文件 | 内容 |
|------|------|
| **BOOTSTRAP.md** | 初始化脚本 |
| **avatars/** | 头像图片 |

## 🚫 绝对不要同步的文件

### 凭证和密钥

```
❌ ~/.openclaw/openclaw.json     # 包含所有通道凭证
❌ ~/.openclaw/agents/           # 会话数据
❌ *.env                         # 环境变量
❌ .ssh/                         # SSH 密钥
❌ credentials.json              # 任何凭证文件
```

### 大型数据

```
❌ sessions/                     # 会话数据（可能很大）
❌ node_modules/                 # 依赖包
❌ *.log                         # 日志文件
❌ cache/                        # 缓存
```

## 🔐 安全最佳实践

### GitHub 仓库设置

1. **必须设为私有 (Private)**
   ```
   Settings → Visibility → Change to Private
   ```

2. **启用分支保护**
   ```
   Settings → Branches → Add branch protection rule
   - Require pull request reviews
   - Require status checks
   ```

3. **启用安全警报**
   ```
   Settings → Security & analysis → Enable all
   ```

### Token 管理

1. **使用细粒度 Personal Access Token**
   - 只给 `repo` 权限
   - 设置过期时间（建议 90 天）
   - 定期轮换

2. **Token 存储**
   - ✅ 使用环境变量
   - ✅ 使用配置文件（限制权限 600）
   - ❌ 不要硬编码在代码中
   - ❌ 不要提交到 Git

3. **Token 轮换流程**
   ```bash
   # 1. 生成新 Token
   # 2. 更新配置
   export GITHUBTOKEN="ghp_new_token"
   
   # 3. 测试同步
   python sync_to_github.py status
   
   # 4. 删除旧 Token
   ```

### 备份频率建议

| 场景 | 频率 | 方式 |
|------|------|------|
| 日常使用 | 每天 | 自动推送 |
| 重要对话后 | 立即 | 手动推送 |
| 配置更改后 | 立即 | 手动推送 |
| 服务器迁移前 | 必须 | 完整备份 |

## 📦 备份验证

### 定期验证

每月至少验证一次备份完整性：

```bash
# 1. 检查远程仓库
git ls-remote origin

# 2. 拉取到临时目录验证
git clone <repo> /tmp/verify-backup

# 3. 检查关键文件
ls -la /tmp/verify-backup/*.md
cat /tmp/verify-backup/MEMORY.md

# 4. 清理
rm -rf /tmp/verify-backup
```

### 恢复测试

每季度进行一次恢复测试：

```bash
# 1. 创建测试目录
mkdir /tmp/test-restore

# 2. 执行迁移
BACKUP_DIR=/tmp/test-restore python sync_to_github.py migrate

# 3. 验证文件
diff -r /tmp/test-restore /root/.openclaw/workspace

# 4. 清理
rm -rf /tmp/test-restore
```

## 🚨 应急响应

### 如果 Token 泄露

1. **立即撤销 Token**
   ```
   GitHub → Settings → Developer settings → Personal access tokens → Revoke
   ```

2. **生成新 Token**
   ```bash
   # 生成新的细粒度 Token
   ```

3. **更新配置**
   ```bash
   export GITHUBTOKEN="ghp_new_token"
   ```

4. **检查仓库活动**
   ```
   GitHub → Insights → Traffic
   ```

### 如果仓库意外公开

1. **立即设为私有**
   ```
   GitHub → Settings → Visibility → Change to Private
   ```

2. **轮换所有凭证**
   - GitHub Token
   - 任何可能暴露的 API keys
   - 通道凭证

3. **审查访问记录**
   ```
   GitHub → Settings → Security → Audit log
   ```

## 📋 备份检查清单

### 每次推送前

- [ ] 审查要提交的文件（`git status`）
- [ ] 确认没有敏感凭证
- [ ] 确认 .gitignore 正确
- [ ] 确认仓库是私有的

### 每次推送后

- [ ] 在 GitHub 上验证文件
- [ ] 检查提交记录
- [ ] 确认文件大小合理

### 定期（每月）

- [ ] 验证备份完整性
- [ ] 检查 Token 是否即将过期
- [ ] 审查仓库访问权限
- [ ] 更新备份策略文档

## 🌐 多云备份（可选）

对于重要数据，考虑多重备份：

```
OpenClaw Workspace
       │
       ├──→ GitHub (主要备份)
       │
       ├──→ 本地 NAS/硬盘
       │
       └──→ 另一云存储（Google Drive, Dropbox 等）
```

### 使用 rclone 备份到多云

```bash
# 安装 rclone
curl https://rclone.org/install.sh | sudo bash

# 配置云存储
rclone config

# 备份到多个云
rclone sync /root/.openclaw/workspace remote1:backup/openclaw
rclone sync /root/.openclaw/workspace remote2:backup/openclaw
```

## 📞 需要帮助？

- OpenClaw 文档：https://docs.openclaw.ai
- GitHub 安全：https://docs.github.com/en/authentication
- 社区支持：https://discord.com/invite/clawd

---

**记住**: 备份的目的是保护数据，不是制造新的安全风险。始终优先考虑安全性！
