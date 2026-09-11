# 候选说明
before/ 是基线，after/ 是候选。目标是将内部重试上限分支改为表查找，支持行为保持一致。app.run 是唯一公开调用入口，_retry_limit 是内部函数。两版本可分别运行 python3 -B -m unittest。
