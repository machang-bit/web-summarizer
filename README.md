# 📄 网页 / 文章总结助手

一个基于 **Python + LangChain + Streamlit** 的智能应用：输入网页 URL，自动抓取正文（剔除导航、页脚、广告等噪声），调用大模型生成 **300 字以内的中文核心摘要**。

支持在线大模型（OpenAI / 智谱 GLM）与本地离线模型（Ollama），通过 `.env` 一键切换。

## ✨ 功能特性

- 网页抓取：基于 LangChain `WebBaseLoader`（内部使用 BeautifulSoup 解析，自动剥离 script/style 等噪声标签）
- 文本切割：`RecursiveCharacterTextSplitter`，`chunk_size=1000`、`chunk_overlap=100`，中文友好分隔符
- 摘要链路：`load_summarize_chain`，支持 **map_reduce**（并行、适合长文）与 **refine**（滚动精炼、衔接自然）两种模式，界面可切换，避免超出上下文 Token 限制
- 模型配置：OpenAI / 智谱 GLM / Ollama 三种方式，API Key 全部走 `.env`，源码零硬编码
- 友好交互：URL 输入框、模式切换、spinner 加载动画、摘要展示区；抓取失败/内容为空时给出中文提示而非直接抛异常

## 📁 项目结构

```
web-summarizer/
├── app.py            # 界面层：Streamlit 入口
├── crawler.py        # 抓取层：WebBaseLoader 抓取网页、提取正文
├── splitter.py       # 切割层：RecursiveCharacterTextSplitter 文本切块
├── summarizer.py     # 摘要层：load_summarize_chain（map_reduce / refine）
├── config.py         # 配置层：按 .env 构建大模型实例
├── .env.example      # 环境变量模板（复制为 .env 后填写）
├── requirements.txt  # 依赖清单
├── .gitignore
└── README.md
```

## 🚀 快速开始

### 1. 安装依赖

建议使用虚拟环境（Python 3.10+）：

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. 配置环境变量

复制模板并填写：

```bash
cp .env.example .env
```

`.env` 关键配置（三选一，改 `LLM_PROVIDER` 即可）：

| 提供方 | LLM_PROVIDER | 需要的配置 |
|---|---|---|
| 智谱 GLM（推荐，国内可直接访问） | `zhipu` | `ZHIPU_API_KEY`（[申请地址](https://open.bigmodel.cn/)） |
| OpenAI | `openai` | `OPENAI_API_KEY`，可选 `OPENAI_BASE_URL` |
| Ollama（本地离线） | `ollama` | 无需 Key，先执行 `ollama pull qwen2.5:7b` |

### 3. 运行

```bash
streamlit run app.py
```

浏览器自动打开 `http://localhost:8501`，输入网页 URL → 选择摘要模式 → 点击「生成摘要」。

## ❓ 常见问题

**Q1：提示「网页抓取失败」？**
检查 URL 是否以 `http://` / `https://` 开头、网络是否正常；部分网站有反爬限制或需要登录，可换其他公开文章页测试。

**Q2：提示「未能提取到有效正文」？**
该页面可能依赖 JavaScript 动态渲染。可将 `crawler.py` 中的 `WebBaseLoader` 替换为 `UnstructuredURLLoader` 或基于 Selenium 的加载器。

**Q3：智谱 / OpenAI 调用报错 401？**
API Key 无效或未在 `.env` 中填写，注意 `.env` 保存后需重启 Streamlit 生效。

**Q4：Ollama 连接失败？**
确认已安装 Ollama 且服务在运行（`ollama serve`），并已拉取模型（`ollama pull qwen2.5:7b`）；端口不是 11434 时修改 `OLLAMA_BASE_URL`。

**Q5：map_reduce 和 refine 怎么选？**
长文、追求速度选 `map_reduce`；短文、追求摘要前后连贯选 `refine`。

**Q6：摘要超过了 300 字？**
模型对字数约束是「软性」的，个别模型可能略超。可在 `summarizer.py` 的 Prompt 中加强约束，或对结果做二次截断。

## 📝 AI 使用说明

本项目代码由 AI 编程助手（WorkBuddy）辅助生成，经人工审阅与调试；核心思路（分层架构、LangChain 摘要链路选型）遵循 LangChain 官方文档最佳实践。
