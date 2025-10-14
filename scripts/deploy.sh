#!/bin/bash
# OHSteack 生产环境部署脚本

set -euo pipefail  # 遇到错误立即退出

echo "========================================="
echo "OHSteack 生产环境部署脚本"
echo "========================================="

# 配置变量
APP_DIR="/var/www/ohsteack"
REPO_URL="https://github.com/yourusername/ohsteack.git"  # 修改为实际的仓库地址
BRANCH="main"
USER="www-data"
GROUP="www-data"

# 检查是否以root权限运行
if [[ $EUID -ne 0 ]]; then
   echo "此脚本需要root权限运行" 
   exit 1
fi

# 更新系统包
echo "正在更新系统包..."
apt-get update
apt-get upgrade -y

# 安装系统依赖
echo "正在安装系统依赖..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    mysql-server \
    mysql-client \
    libmysqlclient-dev \
    nginx \
    supervisor \
    git \
    build-essential \
    libssl-dev \
    libffi-dev

# 创建应用目录
echo "正在创建应用目录..."
mkdir -p "$APP_DIR"
cd "$APP_DIR"

# 克隆或更新代码
if [ -d ".git" ]; then
    echo "正在更新代码..."
    git pull origin "$BRANCH"
else
    echo "正在克隆代码..."
    git clone -b "$BRANCH" "$REPO_URL" .
fi

# 设置目录权限
chown -R "$USER":"$GROUP" "$APP_DIR"

# 创建虚拟环境
if [[ -d "venv" ]]; then
    echo "✓ 检测到已存在的虚拟环境，跳过创建"
else
    echo "正在创建虚拟环境..."
    sudo -u "$USER" python3 -m venv venv
fi

# 激活虚拟环境并安装依赖
echo "正在安装Python依赖..."
sudo -u "$USER" "$APP_DIR"/venv/bin/pip install --upgrade pip
sudo -u "$USER" "$APP_DIR"/venv/bin/pip install -r requirements.txt

# 创建必要的目录
echo "正在创建必要的目录..."
sudo -u "$USER" mkdir -p logs
sudo -u "$USER" mkdir -p instance
sudo -u "$USER" mkdir -p static/uploads

# 复制配置文件
echo "正在配置Nginx..."
cp deployment/nginx/ohsteack.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/ohsteack.conf /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo "正在配置Supervisor..."
cp deployment/supervisor/ohsteack.conf /etc/supervisor/conf.d/

# 创建生产环境配置
if [ ! -f .env ]; then
    echo "正在创建生产环境配置..."
    cat > .env << EOL
# Flask配置
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# 数据库配置
DATABASE_URL=mysql+pymysql://ohsteack:password@localhost/ohsteack?charset=utf8mb4

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@ohsteack.com
EOL
    chown "$USER":"$GROUP" .env
    chmod 600 .env
    echo "✓ 请编辑 .env 文件配置数据库密码等信息"
fi

# 配置MySQL
echo "正在配置MySQL..."
mysql << EOF
CREATE DATABASE IF NOT EXISTS ohsteack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'ohsteack'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON ohsteack.* TO 'ohsteack'@'localhost';
FLUSH PRIVILEGES;
EOF

# 运行数据库迁移
echo "正在运行数据库迁移..."
sudo -u "$USER" "$APP_DIR"/venv/bin/flask db upgrade

# 收集静态文件（如果需要）
# sudo -u $USER $APP_DIR/venv/bin/python manage.py collectstatic --noinput

# 设置日志目录权限
mkdir -p /var/log/nginx
mkdir -p /var/log/supervisor
chown -R "$USER":"$GROUP" logs/

# 测试Nginx配置
echo "测试Nginx配置..."
nginx -t

# 重启服务
echo "正在重启服务..."
systemctl restart nginx
supervisorctl reread
supervisorctl update
supervisorctl restart ohsteack

# 配置防火墙（如果使用ufw）
if command -v ufw >/dev/null 2>&1; then
    echo "配置防火墙..."
    ufw allow 'Nginx Full'
    ufw allow OpenSSH
else
    echo "未检测到ufw，跳过防火墙配置。"
fi

echo ""
echo "========================================="
echo "✓ 部署完成！"
echo "========================================="
echo ""
echo "重要提醒："
echo "1. 编辑 /var/www/ohsteack/.env 配置数据库密码等信息"
echo "2. 修改 /etc/nginx/sites-available/ohsteack.conf 中的域名"
echo "3. 配置SSL证书（推荐使用Let's Encrypt）"
echo "4. 修改MySQL中ohsteack用户的密码"
echo ""
echo "常用命令："
echo "- 查看应用状态: supervisorctl status"
echo "- 重启应用: supervisorctl restart ohsteack"
echo "- 查看日志: tail -f /var/log/supervisor/ohsteack_stdout.log"
echo ""
