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

OHSteack（Open Heap Stack Team Manager）是一个专为竞赛团队设计的协作管理平台。项目的设计灵感来源于计算机程序的运行机制：

- 📚 **资源是栈（Stack）**：团队收集的学习资源、参考资料就像栈中的变量，为创新提供基础支撑
- 🏆 **成果是堆（Heap）**：团队创造的成果就像堆中动态分配的数据，不断迭代演进

通过这种系统化的方式，帮助团队更好地管理知识资源和追踪项目成果。

## 功能特性

### 🎯 核心功能

- **团队管理**
  - 创建和管理竞赛团队
  - 成员邀请和角色分配
  - 项目进度追踪
  - 团队统计分析

- **资源管理（栈）**
  - 系统化组织学习资源
  - 支持多种资源类型：文档、链接、文件、代码
  - 标签分类和全文搜索
  - 资源置顶和访问统计

- **成果追踪（堆）**
  - 记录团队产出和创新成果
  - 版本控制和迭代历史
  - 支持附件和外部链接
  - 成果状态管理

- **协作工具**
  - Markdown编辑器
  - 文件上传和分享
  - 实时通知
  - 团队活动追踪

### ✨ 技术特性

- 🎨 **现代化UI**：Apple风格的简洁美观界面
- 📱 **响应式设计**：完美适配各种设备
- 🔒 **安全可靠**：密码加密、权限控制、安全防护
- ⚡ **高性能**：数据库优化、缓存机制、CDN支持
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

3. **配置环境变量**
   ```bash
   # 编辑 .env 文件，配置数据库连接等信息
   nano .env
   ```

4. **启动开发服务器**
   ```bash
   source venv/bin/activate
   flask run
   ```

5. **访问应用**
   
   打开浏览器访问：http://localhost:5000

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
- **样式**：原生CSS（Apple风格）
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
