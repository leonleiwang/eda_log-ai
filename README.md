# EDA Log AI

可离线演示的 EDA 日志分析助手原型，面向“本地 AI 工具件提高芯片/EDA 工程效率”的线下面试场景。

## 能力

- 解析 EDA 日志中的 `ERROR` / `WARN` / `FATAL` 和上下文行。
- 分类 SPICE 收敛、PDK/model、netlist subckt、license、DRC/LVS、资源限制等问题。
- 使用本地 `cases.json` 做历史案例检索，过滤弱相关结果。
- 默认离线运行；有 FastAPI 时提供 Web 页面和 `/analyze` API。
- 可选 qwen3-max 增强总结；没有 API key 时自动跳过，不影响演示。

## 快速演示

CLI：

```powershell
$env:PYTHONPATH="src"
D:\python\python.exe -m eda_log_ai.cli samples\logs\spice_convergence.log
```

静态前端：

```powershell
start frontend\index.html
```

FastAPI + 前端：

```powershell
$env:PYTHONPATH="src"
D:\python\python.exe -m uvicorn eda_log_ai.api:app --host 127.0.0.1 --port 8000
```

然后访问：

```text
http://127.0.0.1:8000
```

旧版、离线 Python 环境：

```powershell
D:\python\python.exe -m venv .venv
.\.venv\Scripts\python.exe setup.py develop
.\.venv\Scripts\eda-log-ai.exe samples\logs\spice_convergence.log
```

## qwen3-max 配置

复制 `.env.example` 为 `.env`，填入本机 key：

```powershell
Copy-Item .env.example .env
```

`.env` 示例：

```text
DASHSCOPE_API_KEY=your_key_here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3-max
```

前端勾选“请求 qwen3-max 增强”后，FastAPI 会调用 LLM。未配置 key 或网络不可用时，后端会返回失败说明，规则分析仍可正常展示。

## 测试

```powershell
powershell -ExecutionPolicy Bypass -File scripts\deploy_test.ps1
```

当前覆盖：

- 单元测试
- FastAPI `/health`、`/config`、`/analyze`
- 三个样例日志的 CLI 烟测

## 架构

```text
log text/file
  -> parser: severity、tool、error code、路径、器件/cell 名抽取
  -> classifier: EDA 场景规则分类
  -> case retriever: 本地历史案例库混合打分
  -> analyzer: 摘要、置信度、排查步骤、升级建议
  -> optional LLM: qwen3-max 只做总结增强
  -> CLI / FastAPI / static frontend
```

## 面试讲法

这个项目不是“让 AI 替工程师判断”，而是“程序解析 + 规则分类 + 本地知识库 + LLM 辅助表达”。关键事实来自 parser 和 case 库，LLM 只负责把结构化结果组织成更适合工程师阅读的排查说明。
