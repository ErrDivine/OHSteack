# OHSteack - Open Heap Stack Team Manager

<div align="center">

**为竞赛团队打造的协作管理平台**

[![Python](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0+-red.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

[功能特性](#功能特性) • [快速开始](#快速开始) • [文档](#文档) • [贡献](#贡献)

</div>

---

## 项目简介

OHSteack（Open Heap Stack Team Manager）是一个专为竞赛团队设计的协作管理平台。界面围绕两个核心入口构建：

- 👤 **用户资料**：集中查看个人信息、历史贡献与参与统计；
- 🧩 **团队空间**：进入任一团队后，立即看到正在使用的「资源栈」与迭代中的「成果堆」，并掌握成员分工。

这种轻量的分层方式延续了“资源如栈、成果如堆”的设计灵感，让团队能在清晰的上下文中协同。

## 功能特性

### 🎯 工作空间体验

- **双入口导航**：登录后先在首页选择「用户资料」或「团队空间」，避免在冗余菜单中迷失。
- **一致的卡片布局**：资料、资源、成果和分工都采用同一信息密度，移动端也能迅速获取重点。

### 👤 用户资料

- 快速查看团队数量、资源/成果/迭代贡献数、加入天数
- 维护基本资料、头像、个人介绍与账号安全
- 回顾最近迭代记录并跳转到具体成果

### 🧠 资源栈

- 支持文档、链接、文件等多类型资源
- 在团队空间内按时间排序展示，强调当前上下文
- 快速进入详情页查看标签、附件与 Markdown 渲染内容
- 资源创建/编辑表单自带预览与上传助手

### 🧱 成果堆

- 以迭代历史呈现团队产出，显示状态、版本、更新时间
- 详情页提供迭代切换、附件下载和个人贡献标注
- 支持多附件上传，按白名单校验并归档到团队目录
- 通过迭代记录追踪团队当前正在推进的工作

### 🤝 团队协作

- 团队创建、信息维护与赛事链接管理
- 成员邀请、角色划分与退出/移除流程
- 成员分工面板统计个人资源、成果、迭代数量
- 管理员入口保留完整的激活/禁用与审计能力

### ✨ 技术特性

- 🎨 **简洁美观**：极简色板、柔和阴影与排版统一的详情卡片
- 📱 **响应式设计**：双栏/单栏布局自动切换，移动端体验一致
- 🔒 **安全可靠**：密码加密、角色校验、文件上传白名单
- ⚡ **高性能**：SQLAlchemy 优化查询、延迟加载、批量统计
- 🚀 **易部署**：自动化部署脚本、完整文档

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Nginx（生产环境）

### 本地开发

1. **克隆项目**
   ```bash
   git clone https://github.com/yourusername/ohsteack.git
   cd ohsteack
   ```

2. **运行设置脚本**
   ```bash
   bash scripts/setup.sh
   ```
   脚本会创建虚拟环境、安装依赖并生成默认的 `.env` 文件，同时可选择是否初始化本地 MySQL 数据库。

3. **配置环境变量**
   ```bash
   # 编辑 .env 文件，配置数据库连接等信息
   nano .env
   ```
   默认提供基于 SQLite 的开发/测试连接，如需 MySQL 请替换 `DEV_DATABASE_URL` 和 `TEST_DATABASE_URL`。

4. **启动开发服务器**
   ```bash
   source venv/bin/activate
   flask run
   ```

5. **访问应用**

   打开浏览器访问：http://localhost:5000

6. **运行测试**

   ```bash
   source venv/bin/activate
   pytest
   ```

   测试套件会使用独立的 SQLite 数据库和临时上传目录，验证用户注册、团队空间以及资源/成果工作流可以正常运行。

### 生产部署

使用自动化部署脚本（Ubuntu/Debian）：

```bash
sudo bash scripts/deploy.sh
```

详细部署说明请参考：[部署文档](docs/DEPLOYMENT.md)

## 项目结构

```
OHSteack/
├── app/                    # 应用主目录
│   ├── models/            # 数据模型
│   ├── views/             # 视图控制器
│   ├── forms/             # 表单定义
│   └── utils/             # 工具函数
├── static/                # 静态文件
│   ├── css/              # 样式文件
│   ├── js/               # JavaScript
│   └── images/           # 图片资源
├── templates/             # 模板文件
│   ├── auth/             # 认证相关
│   ├── team/             # 团队管理
│   ├── resource/         # 资源管理
│   └── result/           # 成果管理
├── deployment/            # 部署配置
│   ├── nginx/            # Nginx配置
│   └── supervisor/       # Supervisor配置
├── scripts/               # 脚本文件
├── docs/                  # 文档
├── migrations/            # 数据库迁移
├── config.py              # 配置文件
├── run.py                 # 启动文件
└── requirements.txt       # 依赖包
```

## 技术栈

### 后端
- **框架**：Flask 3.0
- **数据库**：MySQL + SQLAlchemy
- **迁移**：Flask-Migrate
- **认证**：Flask-Login + Flask-Bcrypt
- **表单**：Flask-WTF + WTForms

### 前端
- **样式**：原生CSS（极简风格）
- **JavaScript**：原生ES6+
- **图标**：Font Awesome
- **Markdown**：markdown2

### 部署
- **Web服务器**：Nginx
- **WSGI服务器**：Gunicorn
- **进程管理**：Supervisor
- **数据库**：MySQL

## 文档

- [部署指南](docs/DEPLOYMENT.md) - 详细的部署说明
- [维护手册](docs/MAINTENANCE.md) - 日常维护和故障排查
- [开发指南](docs/idea.md) - 项目设计理念和开发规范

## 使用场景

- 📝 **编程竞赛**：ACM、算法竞赛、黑客马拉松
- 💡 **创新大赛**：创业大赛、产品设计、创新挑战
- 🔬 **学术竞赛**：数学建模、科研竞赛、论文大赛
- 👥 **团队项目**：课程项目、毕业设计、开源协作

## 贡献

我们欢迎所有形式的贡献！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 开发路线图

- [x] 基础功能实现
- [x] 用户认证系统
- [x] 团队管理
- [x] 资源管理
- [x] 成果追踪
- [x] 部署脚本
- [ ] 实时通知
- [ ] API接口
- [ ] 移动端优化
- [ ] 数据统计和可视化
- [ ] 国际化支持

## 许可证

本项目采用 MIT 许可证

## 联系我们

- 📧 Email: contact@ohsteack.com
- 🐛 Issues: GitHub Issues
- 📖 文档: 在线文档

---

<div align="center">
Made with ❤️ by OHSteack Team
</div>
