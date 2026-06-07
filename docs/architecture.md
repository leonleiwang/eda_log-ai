# 架构设计

## 目标

构建一个可本地部署的 EDA 日志分析工具件，先覆盖高频低风险场景：日志定位、错误分类、历史 case 检索、排查建议生成。

## 模块

- `parser.py`：从日志中抽取 severity、line、tool、error code、path、cell/device/entity。
- `classifier.py`：用可审计规则把事件归入 EDA 场景分类。
- `cases.py`：读取本地历史案例库并进行轻量混合检索。
- `analyzer.py`：编排 parser、classifier、case retriever，生成最终结果。
- `cli.py`：离线演示入口。
- `api.py`：可选 FastAPI 部署入口。

## 边界行为

- 空日志或无错误日志：输出低风险和“无强规则命中”建议。
- 未知错误：归为 `unknown_eda_error`，保留证据行，建议升级给工具 owner。
- 长日志：当前原型只抽取 ERROR/WARN/FATAL 附近上下文，后续可增加按工具阶段切片。
- 弱相关 case：设置最小命中阈值，避免把仅词面相关的历史案例展示给工程师。
- 本地敏感数据：默认不调用外部网络服务，不上传日志。

## 后续扩展

- 增加 tool-specific parser：Spectre、HSPICE、Calibre、Innovus、Virtuoso。
- 增加 RAG：把 PDK 文档、工具手册、内部 runbook 分块索引，并要求回答带引用。
- 增加 Agent：生成 rerun command、检查 include 路径、生成 issue 草稿；修改文件前必须人工确认。
- 增加 UI：适合线下面试展示的单页上传/粘贴日志界面。
