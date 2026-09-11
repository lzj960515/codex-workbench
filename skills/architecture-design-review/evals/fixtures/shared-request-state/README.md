# 报告生成公共模块
ReportEngine 在程序启动时创建一次，供同一进程中多个请求并发复用。ReportConfig 的 template 是初始化后不变的渲染配置。Render 调用必须能并发进行，各自返回本次request_id；不要求恢复进程中断的请求。
renderer 是可await的依赖；真实实现会在I/O期间让出执行权。本地 interleave.py 用两个事件控制交错，仅复现共享实例并发，不访问外部服务。
本轮目标是确定模型和修复方向，保留 render(request_id) 这个对外使用方式。模板热更新、分布式执行和持久化恢复没有需求。
