# 店铺笔记查询
before/ 为基线，after/ 为候选，改动目标是加速笔记查询。数据在进程生命周期中固定。
handle_request 对应已登录店铺的查询接口：authenticated_store 来自认证会话，query_note_id 来自请求查询参数。店铺只能读取自己的笔记，不可见与不存在都返回404。
两版本的现有测试均可运行 python3 -B -m unittest。
