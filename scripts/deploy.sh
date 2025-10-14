#!/bin/bash
# OHSteack 生产环境部署脚本

set -euo pipefail  # 遇到错误立即退出

echo "========================================="
echo "OHSteack 生产环境部署脚本"
echo "========================================="

# 配置变量
APP_DIR="/home/admin/OHSteack"
REPO_URL="git@github.com:ErrDivine/OHSteack.git"  # 修改为实际的仓库地址
BRANCH="cursor"
USER="admin"
GROUP="sudo"
DB_NAME="ohsteack"
DB_USER="admin"
DB_PASS="Sun1590044500"


# 检查是否以root权限运行
if [[ $EUID -ne 0 ]]; then
   echo "此脚本需要root权限运行" 
   exit 1
fi

# 确保部署用户和用户组存在
if ! getent group "$GROUP" >/dev/null 2>&1; then
    echo "正在创建用户组 $GROUP ..."
    groupadd "$GROUP"
fi

if ! id -u "$USER" >/dev/null 2>&1; then
    echo "正在创建部署用户 $USER ..."
    useradd -m -s /bin/bash "$USER"
fi

# 确保用户属于目标组
if ! id -nG "$USER" | grep -qw "$GROUP"; then
    usermod -a -G "$GROUP" "$USER"
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
    curl \
    python3-cryptography \
    build-essential \
    libssl-dev \
    libffi-dev

systemctl enable --now nginx
systemctl enable --now supervisor


# 校验并进入应用目录（需提前同步代码）
if [ ! -d "$APP_DIR" ]; then
    echo "未找到应用目录 $APP_DIR ，请先将项目代码放置到该路径后再运行部署脚本。"
    exit 1
fi

cd "$APP_DIR"

# 设置目录权限
chown -R "$USER":"$GROUP" "$APP_DIR"

# 创建虚拟环境
if [[ -d "venv" ]]; then
    echo "✓ 检测到已存在的虚拟环境，跳过创建"
else
    echo "正在创建虚拟环境..."
    sudo -u "$USER" python3 -m venv --system-site-packages venv
fi

# 确保虚拟环境可访问系统包（例如 python3-cryptography）
if [[ -f "venv/pyvenv.cfg" ]]; then
    if grep -q "^include-system-site-packages = false" venv/pyvenv.cfg; then
        sed -i "s/^include-system-site-packages = false/include-system-site-packages = true/" venv/pyvenv.cfg
    elif ! grep -q "^include-system-site-packages" venv/pyvenv.cfg; then
        echo "include-system-site-packages = true" >> venv/pyvenv.cfg
    fi
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

if [ -f /etc/nginx/sites-enabled/default ]; then
    echo "保留默认站点配置 /etc/nginx/sites-enabled/default，如不需要请手动删除"
fi

echo "正在配置Supervisor..."
cp deployment/supervisor/ohsteack.conf /etc/supervisor/conf.d/

# 创建或更新生产环境配置
if [ ! -f .env ]; then
    echo "正在创建生产环境配置..."
    cat > .env << EOL
# Flask配置
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# 数据库配置
DATABASE_URL=mysql+pymysql://$DB_USER:$DB_PASS@localhost/$DB_NAME?charset=utf8mb4

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
    echo "✓ 已创建 .env 文件"
else
    echo "检测到已有 .env，正在更新数据库配置..."
    if grep -q "^DATABASE_URL=" .env; then
        sed -i "s#^DATABASE_URL=.*#DATABASE_URL=mysql+pymysql://$DB_USER:$DB_PASS@localhost/$DB_NAME?charset=utf8mb4#g" .env
    else
        echo "DATABASE_URL=mysql+pymysql://$DB_USER:$DB_PASS@localhost/$DB_NAME?charset=utf8mb4" >> .env
    fi
    if ! grep -q "^FLASK_ENV=" .env; then
        echo "FLASK_ENV=production" >> .env
    fi
    chown "$USER":"$GROUP" .env
    chmod 600 .env
    echo "✓ 已刷新 .env 中的数据库连接串"
fi

# 配置MySQL
echo "正在配置MySQL..."
mysql << EOF
CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

# 运行数据库迁移
echo "正在运行数据库迁移..."
sudo -u "$USER" FLASK_APP=run.py FLASK_ENV=production "$APP_DIR"/venv/bin/flask db upgrade

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
if ! systemctl reload nginx; then
    systemctl restart nginx
fi
supervisorctl reread
supervisorctl update
if supervisorctl status ohsteack >/dev/null 2>&1; then
    supervisorctl restart ohsteack || supervisorctl start ohsteack
else
    supervisorctl start ohsteack
fi

# 配置防火墙（如果使用ufw）
if command -v ufw >/dev/null 2>&1; then
    echo "配置防火墙..."
    ufw allow 81/tcp
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
echo "1. 编辑 $APP_DIR/.env 确认数据库及其他敏感配置"
echo "2. 修改 /etc/nginx/sites-available/ohsteack.conf 中的域名"
echo "3. 配置SSL证书（推荐使用Let's Encrypt）"
echo "4. 确认MySQL用户 $DB_USER 的密码与 .env 中保持一致并及时更新"
echo ""
echo "常用命令："
echo "- 查看应用状态: supervisorctl status"
echo "- 重启应用: supervisorctl restart ohsteack"
echo "- 查看日志: tail -f /var/log/supervisor/ohsteack_stdout.log"
echo ""
