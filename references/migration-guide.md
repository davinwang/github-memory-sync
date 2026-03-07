# OpenClaw 服务器迁移指南

使用 `github-memory-sync` 技能将 OpenClaw 完整迁移到另一台服务器。

## 📋 迁移前准备

### 原服务器上

1. **确认同步内容**
   - SOUL.md - AI 人格
   - IDENTITY.md - AI 身份
   - USER.md - 用户信息
   - MEMORY.md - 长期记忆
   - TOOLS.md - 工具配置
   - HEARTBEAT.md - 心跳任务
   - memory/*.md - 日常记忆
   - skills/ - 自定义技能
   - avatars/ - 头像图片

2. **备份到 GitHub**
   ```
   用户："备份所有配置到 GitHub"
   ```

### 新服务器上

1. **安装 OpenClaw**
   ```bash
   # 按照官方文档安装
   npm install -g openclaw
   ```

2. **配置基础环境**
   - 确保 Node.js 已安装
   - 确保 pnpm 已安装
   - 配置必要的 API keys（web search 等）

## 🚀 迁移步骤

### 步骤 1：从 GitHub 恢复配置

在新服务器上执行：

```
用户："从 GitHub 恢复所有配置"
```

这会：
1. 克隆 GitHub 仓库到临时目录
2. 复制所有记忆和配置文件到 workspace
3. 保留新服务器的通道配置

### 步骤 2：重新配置通道凭证

⚠️ **重要**：为了安全，通道凭证（tokens、secrets）不应该同步到 GitHub。

需要在新服务器上重新配置：

#### 企业微信 (WeCom)
```bash
openclaw configure --channel wecom
# 输入 corpId, corpSecret, agentId 等
```

#### 飞书 (Feishu)
```bash
openclaw configure --channel feishu
# 输入 app_id, app_secret 等
```

#### 其他通道
根据提示重新配置各通道的凭证。

### 步骤 3：验证配置

```bash
# 检查状态
openclaw status

# 检查通道
openclaw status --all

# 重启服务
openclaw gateway restart
```

### 步骤 4：测试功能

1. **发送测试消息** - 在各通道发送消息测试
2. **检查记忆** - 确认 MEMORY.md 和 memory 文件已恢复
3. **测试技能** - 确认自定义技能可用
4. **验证配置** - 确认 TOOLS.md 中的配置生效

## 📝 手动迁移（备选方案）

如果自动迁移失败，可以手动操作：

### 1. 克隆仓库

```bash
cd /root/.openclaw/workspace
git clone https://github.com/username/repo.git temp-backup
```

### 2. 复制文件

```bash
# 复制核心文件
cp temp-backup/SOUL.md .
cp temp-backup/IDENTITY.md .
cp temp-backup/USER.md .
cp temp-backup/MEMORY.md .
cp temp-backup/TOOLS.md .
cp temp-backup/HEARTBEAT.md .
cp temp-backup/AGENTS.md .

# 复制目录
cp -r temp-backup/memory/ .
cp -r temp-backup/skills/ .
cp -r temp-backup/avatars/ .

# 清理临时目录
rm -rf temp-backup
```

### 3. 保留通道配置

```bash
# 不要覆盖 openclaw.json（包含通道凭证）
# 如果需要，可以手动合并配置
```

## 🔒 安全注意事项

### 不要同步的内容

以下文件**不应该**同步到 GitHub：

- `~/.openclaw/openclaw.json` - 包含 API keys 和通道凭证
- `~/.openclaw/agents/` - 可能包含敏感会话数据
- `*.env` - 环境变量文件
- 任何包含密码、token 的文件

### GitHub 仓库设置

1. **设为私有仓库**
   ```bash
   # 在 GitHub 上设置仓库为 Private
   ```

2. **启用两因素认证**
   - 保护 GitHub 账户

3. **使用细粒度 Token**
   - 只给必要的权限（`repo`）
   - 设置过期时间

4. **定期轮换 Token**
   - 每 3-6 个月更换一次

## 🛠️ 故障排除

### 问题 1：Git 冲突

**症状**: 推送时出现冲突

**解决**:
```bash
cd /root/.openclaw/workspace
git fetch origin
git merge origin/main
# 解决冲突后
git add .
git commit -m "Resolve conflicts"
git push
```

### 问题 2：文件权限问题

**症状**: 复制文件后无法读取

**解决**:
```bash
chown -R $USER:$USER /root/.openclaw/workspace
chmod 600 /root/.openclaw/workspace/*.md
chmod 700 /root/.openclaw/workspace/memory/
```

### 问题 3：通道配置丢失

**症状**: 迁移后通道无法使用

**解决**:
- 重新配置通道凭证
- 不要从备份恢复 openclaw.json
- 只恢复记忆和配置文件

### 问题 4：技能无法加载

**症状**: 自定义技能不工作

**解决**:
```bash
# 检查技能目录
ls -la /root/.openclaw/workspace/skills/

# 重新打包技能
cd /root/.openclaw/workspace/skills/skill-name
python package_skill.py .

# 重启服务
openclaw gateway restart
```

## ✅ 迁移检查清单

- [ ] 原服务器备份完成
- [ ] 新服务器 OpenClaw 安装完成
- [ ] 从 GitHub 恢复配置完成
- [ ] 通道凭证重新配置
- [ ] 服务重启成功
- [ ] 各通道测试通过
- [ ] 记忆文件验证完成
- [ ] 自定义技能测试通过
- [ ] 定时任务（cron）重新配置
- [ ] 新服务器备份配置完成

## 📞 需要帮助？

如果迁移过程中遇到问题：

1. 检查日志：`openclaw logs --follow`
2. 查看状态：`openclaw status`
3. 查阅文档：https://docs.openclaw.ai
4. 社区支持：https://discord.com/invite/clawd

---

**提示**: 迁移完成后，记得在新服务器上设置定期备份！
