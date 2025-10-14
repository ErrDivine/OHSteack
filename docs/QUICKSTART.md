# OHSteack 快速开始指南

这份指南将帮助您在5分钟内启动并运行OHSteack。

## 前置要求

确保您的系统已安装：
- Python 3.8+
- MySQL 5.7+
- Git

## 快速开始

### 方式一：自动设置（推荐）

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd OHSteack

# 2. 运行自动设置脚本
bash scripts/setup.sh

# 3. 启动开发服务器
source venv/bin/activate
flask run

# 4. 访问应用
# 打开浏览器访问 http://localhost:5000
```

### 方式二：手动设置

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd OHSteack

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 创建数据库
mysql -u root -p << EOF
CREATE DATABASE ohsteack_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

# 5. 配置环境变量
cp .env.example .env
nano .env  # 编辑数据库连接信息

# 6. 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 7. 创建管理员账户
flask create-admin

# 8. 启动服务器
flask run
```

## 配置说明

编辑 `.env` 文件：

```env
# Flask配置
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# 数据库配置
DEV_DATABASE_URL=mysql+pymysql://root:password@localhost/ohsteack_dev?charset=utf8mb4

# 邮件配置（可选）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

## 首次使用

1. **注册账户**
   - 访问 http://localhost:5000
   - 点击"注册"
   - 填写用户信息

2. **创建团队**
   - 登录后点击"创建团队"
   - 填写团队信息和竞赛信息
   - 邀请成员加入

3. **添加资源**
   - 进入团队页面
   - 点击"资源"标签
   - 添加学习资料、参考文档等

4. **创建成果**
   - 点击"成果"标签
   - 创建项目成果
   - 记录迭代过程

## 常用命令

```bash
# 启动开发服务器
flask run

# 数据库迁移
flask db migrate -m "description"
flask db upgrade

# 创建管理员
flask create-admin

# 进入Python Shell
flask shell

# 运行测试
pytest
```

## 故障排除

### 数据库连接失败

```bash
# 检查MySQL服务
sudo systemctl status mysql

# 测试连接
mysql -u root -p

# 检查配置
cat .env | grep DATABASE
```

### 端口被占用

```bash
# 查看占用端口的进程
lsof -i :5000

# 使用其他端口
flask run --port 5001
```

### 依赖安装失败

```bash
# 升级pip
pip install --upgrade pip

# 清除缓存重新安装
pip cache purge
pip install -r requirements.txt
```

## 下一步

- 📖 阅读[完整文档](README.md)
- 🚀 查看[部署指南](DEPLOYMENT.md)
- 🔧 了解[维护手册](MAINTENANCE.md)
- 💡 查看[设计理念](idea.md)

## 获取帮助

遇到问题？

- 查看[文档](docs/)
- 提交[Issue](https://github.com/yourusername/ohsteack/issues)
- 发送邮件：contact@ohsteack.com

祝您使用愉快！🎉
