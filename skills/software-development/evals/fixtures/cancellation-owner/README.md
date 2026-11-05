# 本地导出任务取消
web.cancel_export 和 cli.cancel_export 是两个已使用的入口，入参都是 repository 和 job_id，返回被取消的 job。repository.get 返回已存在任务的副本，repository.save 完成持久化。Missing ID 和保存错误沿调用链抛出。
当前只允许 pending -> cancelled。新需求已确认：queued 也允许取消，其他状态仍报 ValueError("job cannot be cancelled")，不得保存。成功取消只保存一次。两个入口行为必须保持一致。
项目全部任务状态为 pending、queued、running、completed、cancelled；这是进程内小工具，不运行独立队列消费者或重试服务。两个入口是已知全部调用方。
