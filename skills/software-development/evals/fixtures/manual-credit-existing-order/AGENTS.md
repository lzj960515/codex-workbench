# 本地业务练习项目

这是使用 Python 标准库和 SQLite 的独立小项目。所有数据都是本地虚构数据，不连接外部服务；本次只操作当前项目文件与临时 SQLite 数据库。使用 `python3 -m unittest discover -s tests -v` 验证。

`README.md` 说明业务目标、当前入口和已经确认的决定。数据库结构以 `schema.sql` 为准。管理端 API 在本项目中用 `admin.py` 的公开函数表示，不需要搭建 HTTP 服务或前端。
