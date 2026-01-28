# 老王股票分析系统

这是一个基于AI的股票分析和监控系统，使用DeepSeek作为AI模型来分析股票数据并提供投资建议。系统现在包含可视化Web界面，让您更方便地管理监控的股票。

## 功能特性

- AI驱动的股票分析
- 实时风险监控
- 自动化投资建议
- 定时盘后分析
- 股票池管理
- 多因子分析模型
- **全新可视化Web界面** - 方便添加和管理监控股票
- **实时图表展示** - 直观查看股票走势
- **AI分析结果展示** - 即时查看AI分析结果

## 技术栈

- Python 3.x
- DeepSeek API
- AkShare
- Pandas
- OpenAI
- Flask
- Chart.js
- Bootstrap

## 安装

1. 克隆项目
2. 安装依赖: `pip install -r requirements.txt`
3. 配置环境变量: `.env`

## 使用方法

### 启动Web界面（推荐）

```bash
# 方法1: 使用启动脚本
./start.sh --web

# 方法2: 直接运行
python main.py --web
```

启动后访问: http://localhost:5001

### 启动监控模式

```bash
./start.sh --monitor
```

## Web界面功能

- **添加监控股票**: 通过界面轻松添加想要监控的股票
- **实时数据图表**: 查看股票的实时价格走势
- **AI分析**: 一键获取AI对选定股票的分析结果
- **监控列表管理**: 添加/删除监控的股票
- **数据看板**: 查看市场概览和最新警报
- **警报中心**: 查看系统检测到的风险和机会

## 配置

在 `.env` 文件中配置您的API密钥:

```
DEEPSEEK_API_KEY=your_api_key_here
```

## 项目结构

```
stock-for-laowang/
├── main.py                 # 主应用入口
├── config/                 # 配置文件
├── data/                   # 数据处理模块
├── analysis/               # AI分析模块
├── monitoring/             # 监控模块
├── notification/           # 通知模块
├── web/                    # Web界面模块
│   ├── app.py              # Web应用主文件
│   ├── templates/          # HTML模板
│   └── static/             # 静态资源
└── requirements.txt        # 依赖包列表
```