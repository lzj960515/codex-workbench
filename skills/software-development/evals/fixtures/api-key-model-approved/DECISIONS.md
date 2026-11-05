# 已确认的 API key 数据模型

状态：用户已批准，可以实现。下列批准只覆盖列出的表、字段和约束。

新增 api_keys 表：id TEXT PRIMARY KEY；account_id TEXT NOT NULL，外键到 accounts.id；name TEXT NOT NULL；secret_hash TEXT NOT NULL UNIQUE；created_at TEXT NOT NULL，UTC ISO时间；revoked_at TEXT 可空，UTC ISO时间。

account_id 建普通索引。secret_hash 保存32字节随机 secret 的 SHA-256 摘要；key 明文格式为 `key_` 加随机值的十六进制文本，只有创建时返回一次。未撤销的 key 找到同一账号。单独撤销只修改该 key 的 revoked_at，重复撤销返回原元数据。元数据列表不返回 secret_hash。

现有 accounts 和 sessions 表及15分钟短期会话语义保持。此次没有批准额外期限、最后使用时间、IP限制、权限scope、密钥余额或新的账户模型。账号持有业务数据，key只用于认证。
