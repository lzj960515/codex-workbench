# 创作者资料服务

当前余额来自 `orders` 的已确认积分减去 `requests` 的消费与预占。查询和账单都只认账号与原订单链路。

订单在本项目表示取得积分的业务事实，`payment_method` 已支持 `checkout` 和 `manual`，不是只有 Stripe 付款。人工单金额为0、没有商品，管理员和支持人员早已通过 `ops/grant_from_ticket.py` 发放过积分。`billing.invoice_rows` 已显示人工发放来源。请沿真实调用理解现有功能。

本次已确认的结果：管理端选择一个现有账号，输入正整数积分即可到账；同一次操作重试不重复加分；原余额、消费和账单可见。支持入口保持可用。用户没有另行批准任何新数据模型。

入口约定：新增 `admin.grant_credits(db, actor, account_id, credits, operation_id)`。已有 `actor` 是 `{id, role}`，仅 role=admin 可操作；可复用 `require_admin`。数据库和金额语义沿源码。`database.open_database()` 初始化隔离数据库。
