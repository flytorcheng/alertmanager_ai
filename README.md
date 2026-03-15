# AlertManager Webhook 配置管理系统

基于 Django5 + Vue3 构建的 AlertManager Webhook 告警配置管理系统，支持接收人管理和告警分组配置。

## 功能特性

- **接收人管理**：支持邮件、Webhook、钉钉、企业微信、Slack等多种通知方式
- **告警分组**：基于标签的灵活匹配规则，精准路由告警到对应的接收人
- **Webhook接收**：接收 AlertManager 发送的告警，自动解析并存储
- **告警历史**：完整记录告警生命周期，支持状态追踪
- **科技感UI**：深色主题，现代化设计风格

## 项目结构

```
.
├── backend/                # Django5 后端
│   ├── alertmanager/       # Django项目配置
│   ├── apps/
│   │   └── alert/          # 告警管理应用
│   │       ├── models.py   # 数据模型
│   │       ├── views.py    # API视图
│   │       ├── serializers.py
│   │       └── urls.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/               # Vue3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── api/            # API接口
│   │   ├── router/         # 路由配置
│   │   └── assets/styles/  # 样式文件
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## 快速开始

### 后端安装

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动服务
python manage.py runserver 8000
```

### 前端安装

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

## API接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/receivers/` | GET, POST | 接收人列表/创建 |
| `/api/receivers/{id}/` | GET, PUT, DELETE | 接收人详情/更新/删除 |
| `/api/receivers/{id}/toggle_active/` | POST | 切换接收人状态 |
| `/api/alert-groups/` | GET, POST | 告警分组列表/创建 |
| `/api/alert-groups/{id}/` | GET, PUT, DELETE | 分组详情/更新/删除 |
| `/api/alert-groups/{id}/receivers/` | GET, POST | 分组接收人管理 |
| `/api/alert-history/` | GET | 告警历史列表 |
| `/api/webhook/` | POST | AlertManager Webhook 接收接口 |
| `/api/webhook/<receiver_name>/` | POST | 带接收器名称的 Webhook 接口 |
| `/api/webhook/test/` | POST | Webhook 连通性测试接口 |

## AlertManager 配置

在 AlertManager 的 `alertmanager.yml` 中添加 webhook 接收器配置：

```yaml
route:
  receiver: 'webhook-receiver'
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 1h

receivers:
  - name: 'webhook-receiver'
    webhook_configs:
      - url: 'http://your-server:8000/api/webhook/'
        send_resolved: true
```

### Webhook 数据格式

AlertManager 发送的 Webhook 数据格式示例：

```json
{
  "receiver": "webhook-receiver",
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "HighCPUUsage",
        "severity": "critical",
        "instance": "server-01"
      },
      "annotations": {
        "summary": "CPU使用率过高",
        "description": "服务器 server-01 CPU使用率超过90%"
      },
      "startsAt": "2024-01-01T12:00:00.000Z",
      "endsAt": "0001-01-01T00:00:00.000Z"
    }
  ]
}
```

### 告警分组匹配

系统会根据告警的 `labels` 自动匹配已配置的告警分组：

1. 如果告警标签完全匹配某个分组的匹配规则，则关联到该分组
2. 匹配规则支持多个标签，必须全部匹配才能关联
3. 匹配成功后，可在前端查看告警关联的分组和接收人信息

## 技术栈

### 后端
- Django 5.0
- Django REST Framework
- django-cors-headers
- SQLite (可切换至PostgreSQL/MySQL)

### 前端
- Vue 3.4
- Vue Router 4
- Pinia
- Element Plus
- Axios
- Vite
- Sass

## 环境要求

- Python 3.10+
- Node.js 18+
- npm 9+

## 访问地址

- 前端: http://localhost:3000
- 后端API: http://localhost:8000/api
- Django Admin: http://localhost:8000/admin

## 许可证

MIT License