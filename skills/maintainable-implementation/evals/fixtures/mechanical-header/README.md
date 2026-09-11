# 本地诊断响应
build_headers 用于命令行工具的输出元数据。当前变更只把请求ID对应的键从 Request-Id 改为 X-Request-Id；值、内容类型和入口保持一致。已有客户端确认只使用新键。
