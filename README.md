# VectorBTC — BTC 5分钟涨跌预测系统

基于多AI模型的BTC 5分钟级涨跌预测系统，通过对比各模型胜率为实盘交易提供数据支撑。

## 技术栈

- **后端**: FastAPI + SQLAlchemy + SQLite + APScheduler
- **前端**: Vue 3 + TypeScript + Vant 4 + ECharts
- **数据**: 币安公开API (无需密钥)

## 快速开始

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build
```

### 访问

- 前端: http://localhost:5173
- API文档: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/ws

## 使用流程

1. 打开"设置"页面，添加AI模型（支持OpenAI兼容API）
2. 系统每5分钟自动：采集行情 → 计算指标 → AI预测 → 结算上轮
3. 在"行情"页查看实时价格和最新预测
4. 在"统计"页对比各模型胜率

## AI模型配置示例

| 参数 | 示例值 |
|------|--------|
| 名称 | DeepSeek-V3 |
| API地址 | https://api.deepseek.com/v1 |
| API Key | sk-xxx... |
| 模型名称 | deepseek-chat |
| Temperature | 0.3 |

支持任何兼容OpenAI接口的服务：OpenAI、DeepSeek、Claude (via proxy)、本地Ollama等。
