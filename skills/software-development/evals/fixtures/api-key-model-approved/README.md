# 自动化数据查询账号

账号持有余额和历史查询。当前认证通过 `sessions` 的短期令牌找到账号，令牌固定15分钟有效。它们由已完成的 Google 登录签发，不是可长期命名和单独撤销的 API key；没有 API key 存储、组织或密钥托管服务。

已经确认的功能：同一账号可拥有多把命名 API key，可以列出不含秘密的元数据、独立撤销某一把，其他 key 不受影响。新凭据最终解析为原 account_id，原短期会话继续有效。

管理端公开入口约定：`admin.create_api_key(db, actor, account_id, name)` 返回至少 `id` 和 `secret`；`admin.list_api_keys(db, actor, account_id)`；`admin.revoke_api_key(db, actor, key_id)`。现有 `auth.authenticate(db, credential)` 继续接受短期令牌，并接入 API key。新的 key 明文只在创建返回一次，持久化内容不包含明文。

当前进度：用户已明确批准 DECISIONS.md 中的具体模型，授权按该方案直接实施。现有结构与业务语义请查 `schema.sql`、`auth.py`、`admin.py`。此项目只演示公开函数边界，不需网络服务、依赖安装或 Google 实际登录。
