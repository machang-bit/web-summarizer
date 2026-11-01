# 📄 网页 / 文章总结助手（Web Summarizer）

> 基于 **Python + LangChain + Streamlit** 的智能应用：粘贴一个网页 URL，自动抓取正文（剔除导航、页脚、广告等噪声），调用大模型生成 **300 字以内的简体中文核心摘要**。

支持在线大模型（**OpenAI / 智谱 GLM**）与本地离线模型（**Ollama**），通过 `.env` 一键切换；摘要链路支持 **map_reduce** 与 **refine** 两种模式，界面可自由切换。

开源仓库：<https://github.com/machang-bit/web-summarizer>

---

## 一、核心功能

| 功能 | 说明 |
|---|---|
| 网页正文抓取 | 使用 `trafilatura` 提取正文，自动剔除导航、页脚、广告、侧边栏推荐等噪声 |
| 长文切分 | `RecursiveCharacterTextSplitter`，`chunk_size=1000`、`chunk_overlap=100`，中文友好分隔符，避免超出模型上下文 Token 限制 |
| 智能摘要 | `load_summarize_chain` 构建摘要链路，支持 `map_reduce` / `refine` 两种模式，界面可切换 |
| 多模型支持 | OpenAI / 智谱 GLM / Ollama（本地离线），由 `.env` 中的 `LLM_PROVIDER` 统一切换 |
| 友好交互 | URL 输入框、提交按钮、spinner 加载动画、摘要展示区；抓取失败或内容为空时给出中文提示，不直接抛异常 |

## 二、技术栈

| 层次 | 技术选型 |
|---|---|
| 前端界面 | Streamlit |
| 应用框架 | LangChain、LangChain Community / OpenAI / Ollama |
| 网页抓取 | trafilatura（正文抽取，早期版本为 LangChain `WebBaseLoader`） |
| 文本切分 | `RecursiveCharacterTextSplitter`（langchain-text-splitters） |
| 摘要链路 | `load_summarize_chain`（map_reduce / refine） |
| 配置管理 | python-dotenv + `.env` |

## 三、项目结构

```
web-summarizer/
├── app.py              # 界面层：Streamlit 入口（输入、模式切换、spinner、结果展示）
├── crawler.py          # 抓取层：trafilatura 抓取网页正文
├── splitter.py         # 切割层：RecursiveCharacterTextSplitter 文本切块
├── summarizer.py       # 摘要层：load_summarize_chain（map_reduce / refine）
├── config.py           # 配置层：按 .env 构建大模型实例
├── .env.example        # 环境变量模板（复制为 .env 后填写，不含任何真实密钥）
├── requirements.txt    # 依赖清单
├── .gitignore          # 已忽略 .env / venv / __pycache__，密钥不会误提交
├── exportToHTML/       # 源码的 HTML 阅读版快照（便于在浏览器中查看代码）
└── README.md
```

数据流：`URL` → `crawler`（抓正文）→ `splitter`（切块）→ `summarizer`（摘要链）→ `app`（展示）

## 四、快速开始

### 4.1 环境准备

- Python **3.10 及以上**
- 建议使用虚拟环境（Windows / macOS / Linux 命令均已给出）

```bash
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate
# Windows (CMD)
venv\Scripts\activate.bat

# macOS / Linux
source venv/bin/activate
```

### 4.2 安装依赖

```bash
pip install -r requirements.txt
```

### 4.3 配置环境变量

复制模板文件并填写自己的密钥：

```bash
cp .env.example .env      # Windows 无 cp 命令时，直接用编辑器复制另存为 .env
```

在 `.env` 中设置 `LLM_PROVIDER` 即可切换模型提供方（**只保留所用那一组配置即可，其余可留空**）：

| 提供方 | `LLM_PROVIDER` 值 | 需要填写的变量 | 说明 |
|---|---|---|---|
| 智谱 GLM（推荐） | `zhipu` | `ZHIPU_API_KEY` | 默认模型 `glm-4-flash`，有免费额度，国内直连。[申请地址](https://open.bigmodel.cn/) |
| OpenAI | `openai` | `OPENAI_API_KEY` | 默认模型 `gpt-4o-mini`；用中转/网关时另填 `OPENAI_BASE_URL` |
| Ollama（本地离线） | `ollama` | 无需 Key | 默认模型 `qwen2.5:7b`，需先 `ollama pull qwen2.5:7b` |

最小可用示例（智谱）：

```ini
LLM_PROVIDER=zhipu
ZHIPU_API_KEY=你的智谱APIKey
ZHIPU_MODEL=glm-4-flash
```

> ⚠️ 安全说明：所有密钥只保存在 `.env` 中，**源码内不存在任何硬编码密钥**；`.env` 已被 `.gitignore` 忽略，不会被提交到仓库。

### 4.4 启动应用

```bash
streamlit run app.py
```

终端会输出访问地址，默认 <http://localhost:8501>，通常会自动打开浏览器。

## 五、使用说明

1. 在「网页 URL」输入框中粘贴目标文章链接（需以 `http://` 或 `https://` 开头）；
2. 选择摘要链路模式，并可按需调整 `chunk_size` / `chunk_overlap`；
3. 点击「🚀 生成摘要」，等待 spinner 结束即可看到摘要；
4. 展开下方折叠区域可查看抓取到的正文前 800 字，用于核对提取效果。

**两种摘要模式对比：**

| 模式 | 工作方式 | 适用场景 |
|---|---|---|
| `map_reduce` | 每个文本块先独立生成要点，再合并为最终摘要 | 长文、追求速度；各块互不依赖，不易超 Token |
| `refine` | 逐块滚动精炼已有摘要，不断补充修正 | 中短文、追求前后衔接自然；串行调用，稍慢 |

## 六、常见问题（FAQ）

**Q1：提示「网页抓取失败：链接已失效，或目标网站启用了反爬限制」？**
换一个公开可访问的文章页试试；部分站点（需要登录、有验证码或严格 UA 校验的）会拒绝程序化访问。`trafilatura` 对新闻 / 博客 / 文档类站点效果最好。

**Q2：提示「未能从该页面提取到有效正文」？**
页面可能依赖 JavaScript 动态渲染。可将 `crawler.py` 中的 `trafilatura` 替换为 `WebBaseLoader` / `UnstructuredURLLoader`，或改用 Selenium 渲染后再提取。

**Q3：提示「未检测到 ZHIPU_API_KEY / OPENAI_API_KEY」？**
`.env` 中未填写，或填写在了别的分组下。注意：**修改 `.env` 后必须重启 Streamlit** 才会生效。

**Q4：调用模型报 401 / 鉴权失败？**
API Key 无效、过期或余额不足。智谱 Key 可在 <https://open.bigmodel.cn/> 控制台查看与重新生成。

**Q5：Ollama 模式连接失败？**
确认 Ollama 已安装且服务在运行（`ollama serve`），并已拉取模型（`ollama pull qwen2.5:7b`）；若端口不是 `11434`，请在 `.env` 中设置 `OLLAMA_BASE_URL`。

**Q6：摘要偶尔超过 300 字？**
字数属于模型的「软约束」，个别模型可能略超。可在 `summarizer.py` 的 `COMBINE_TEMPLATE` / `REFINE_TEMPLATE` 中进一步强化约束，或对结果做二次截断。

**Q7：长文摘要很慢？**
改用 `map_reduce` 模式，并把 `chunk_size` 调大（如 2000）以减少分块数量；本地 Ollama 慢可换更小的模型（如 `qwen2.5:3b`）。

## 七、AI 使用说明

本项目在课程作业场景下完成：

- 项目整体架构（抓取 / 切割 / 摘要 / 界面四层分离）、关键参数（`chunk_size=1000`、`chunk_overlap=100`）与摘要链路选型，由 AI 编程助手（WorkBuddy）辅助生成，并参考 LangChain 官方文档核对；
- 抓取层由初期使用的 `WebBaseLoader` 迭代升级为 `trafilatura`，以改善正文提取准确率；
- 所有代码均经过本地实际运行与人工审阅、调试，非直接复制使用。

## 八、作业要求对照

| 作业要求 | 实现位置 |
|---|---|
| 输入 URL 抓取正文、剔除无关内容 | `crawler.py`（trafilatura） |
| 300 字以内中文摘要 | `summarizer.py`（COMBINE / REFINE Prompt） |
| `RecursiveCharacterTextSplitter` 且明确参数 | `splitter.py`（1000 / 100） |
| `load_summarize_chain` + 两种模式可切换 | `summarizer.py`、`app.py` 中的模式单选 |
| 在线 / 离线模型可配置 | `config.py` + `.env` |
| URL 输入框、按钮、spinner、结果区 | `app.py` |
| 密钥走 `.env`、提供 `.env.example` | `.env.example`、`.gitignore` |
| 模块化结构、requirements、README | 见「项目结构」 |
