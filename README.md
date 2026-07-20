# 新闻日报（NewsDaily）

基于 last30days + WebSearch 双数据源的本地新闻日报系统。自动聚合 AI、量化、财经、科技、自媒体五个赛道的最近 30 天新闻，提供分类筛选、关键词搜索、日报摘要等功能。

---

## 项目结构

```
D:\Last30Days\NewsDaily\
├── news-daily.html      # 日报页面（浏览器直接打开）
├── news-data.js         # 新闻数据（页面自动加载）
├── news-data.json       # 新闻数据（JSON 格式，备用）
├── parse_news.py        # 数据解析脚本
└── README.md            # 本文件
```

数据源目录（last30days 输出）：

```
D:\Last30Days\
├── artificial-intelligence-raw-v3*.md   # AI 方向
├── agent-raw-v3*.md                     # 量化方向
├── last30days-raw-v3*.md                # 财经 / 科技方向
├── ai-raw-v3*.md                        # 自媒体方向
└── ...
```

---



**页面功能：**
- 顶部统计栏：总条数、覆盖天数、分类数
- 分类筛选：点击 AI / 量化 / 财经 / 科技 / 自媒体 过滤
- 关键词搜索：实时搜索标题、摘要、来源，结果高亮
- 日期筛选：选择起止日期范围
- AI 日报摘要：点击展开，自动统计各分类数量 + 今日要闻
- 快捷键：Ctrl+K 聚焦搜索框，Esc 清除所有筛选

---

## 数据源

### 数据源 A：last30days（手动触发）

在 Claude Code 中依次运行以下五个命令，结果自动写入 `D:\Last30Days\`：

```
/last30days --deep --emit=html 人工智能
/last30days --deep --emit=html agent量化开发
/last30days --deep --emit=html 财经股市经济
/last30days --deep --emit=html 科技芯片新能源
/last30days --deep --emit=html 自媒体短视频AI创作
```

每次执行后自动生成 `*-raw-v3*.md` 文件，解析脚本通过文件名和标题行自动识别归类。

### 数据源 B：WebSearch（自动触发）

定时任务 `news-daily-update` 每天早上 10:30 自动搜索 AI、量化、财经、科技、自媒体各一次，提取新闻条目。

### 数据合并规则

- 两个数据源合并，按 `sourceUrl` 去重
- WebSearch 结果优先（更新），last30days 结果补充
- 按日期降序排列

---

## 构建方式

### 解析 last30days 数据

```bash
python D:\Last30Days\NewsDaily\parse_news.py \
  --input-dir D:\Last30Days \
  --output D:\Last30Days\NewsDaily\news-data.json
```

输出：
- `news-data.json` — JSON 数组
- `news-data.js` — `window.NEWS_DATA = [...];` 格式，页面直接加载

### 手动更新 WebSearch 数据

在 Claude Code 中使用 WebSearch 工具搜索五个方向，将结果整理为以下格式写入：

```json
{
  "date": "YYYY-MM-DD",
  "title": "新闻标题",
  "summary": "摘要（不超过 300 字）",
  "source": "来源名称",
  "sourceUrl": "https://...",
  "category": "AI|量化|财经|科技|自媒体"
}
```

写入 `D:\Last30Days\NewsDaily\news-data.json` 和 `news-data.js`。

---

## 自动更新（定时任务）

| 项目 | 内容 |
|---|---|
| 任务名 | `news-daily-update` |
| 执行时间 | 每天 10:30（北京时间） |
| 执行内容 | ① 解析 last30days 的 `*-raw-v3*.md` 文件<br>② WebSearch 搜索 5 个方向<br>③ 合并去重写入 `news-data.js` |

### 为什么是 10:30

用户通常在 10:00 前手动运行 `/last30days` 命令完成数据采集，10:30 定时任务自动读取最新数据并搜索补充，确保日报数据完整。

---

## 分类体系

| 分类 | 颜色 | 数据来源 |
|---|---|---|
| AI | 绿色 | last30days `人工智能` + WebSearch |
| 量化 | 紫色 | last30days `agent量化开发` + WebSearch |
| 财经 | 橙色 | last30days `财经股市经济` + WebSearch |
| 科技 | 蓝色 | last30days `科技芯片新能源` + WebSearch |
| 自媒体 | 粉色 | last30days `自媒体短视频AI创作` + WebSearch |

---

## 文件说明

| 文件 | 说明 |
|---|---|
| `news-daily.html` | 单文件 HTML，内嵌 CSS + JS，零依赖。<br>通过 `<script src="news-data.js">` 加载数据，支持 `file://` 协议本地打开。 |
| `news-data.js` | `window.NEWS_DATA = [...]` 格式，由解析脚本或定时任务自动生成。 |
| `news-data.json` | JSON 数组，格式同上，供程序化读取。 |
| `parse_news.py` | Python 3 脚本，解析 last30days 的 Markdown 报告，提取新闻条目并输出 JS/JSON。<br>自动识别分类：先匹配文件名关键词，再匹配文件第一行标题。 |

---



## 部署到服务器（可选）

1. 将 `D:\Last30Days\NewsDaily\` 整个目录上传到服务器
2. 配置 Nginx/Apache 指向该目录
3. 设置 cron 定时任务，每天 10:30 运行 `parse_news.py` + WebSearch 更新流程
4. 或将定时任务 `news-daily-update` 的输出目录改为服务器路径
 
