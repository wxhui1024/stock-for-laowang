# 老王的股票分析系统

基于DeepSeek AI模型的个人股票分析和策略系统，实现盘中风险机会提醒，盘后复盘总结。

## 功能特性

- 实时数据获取（A股、港股、美股）
- AI驱动的股票分析（使用DeepSeek模型）
- 个性化投资策略
- 风险监控与预警
- 盘后复盘总结
- 多渠道通知（企业微信、Telegram等）

## 技术架构

- 数据层：基于Ashare的多源数据获取
- AI层：DeepSeek模型进行智能分析
- 应用层：Python后端服务
- 通知层：多渠道消息推送

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置API密钥：
```bash
export DEEPSEEK_API_KEY=your_deepseek_api_key
export DEEPSEEK_BASE_URL=https://api.deepseek.com
```

3. 运行系统：
```bash
python main.py
```

## 配置说明

系统使用配置文件 `config/settings.py` 进行参数配置，包括：
- API密钥
- 监控股票列表
- 策略参数
- 通知设置