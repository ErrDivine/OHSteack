#!/bin/bash
# OHSteack 初始化设置脚本

set -euo pipefail  # 遇到错误立即退出

echo "========================================="
echo "OHSteack 初始化设置脚本"
echo "========================================="

# 检查是否以root权限运行
if [[ $EUID -eq 0 ]]; then
   echo "请不要使用root权限运行此脚本！" 
   exit 1
fi

# 检查Python版本
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
    echo "错误：需要Python $REQUIRED_VERSION或更高版本，当前版本为 $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python版本检查通过: $PYTHON_VERSION"

# 创建虚拟环境
if [[ -d "venv" ]]; then
    echo "✓ 检测到已存在的虚拟环境，跳过创建"
else
    echo "正在创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 升级pip
echo "正在升级pip..."
pip install --upgrade pip

# 安装依赖
echo "正在安装项目依赖..."
pip install -r requirements.txt

# 创建必要的目录
echo "正在创建目录结构..."
mkdir -p logs
mkdir -p instance
mkdir -p static/uploads

# 创建.env文件（如果不存在）
if [[ ! -f .env ]]; then
    echo "正在创建.env文件..."
    cat > .env <<EOL
# Flask配置
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# 数据库配置
# 开发默认使用SQLite，如需MySQL请替换为 mysql+pymysql://user:password@localhost/ohsteack_dev?charset=utf8mb4
DEV_DATABASE_URL=sqlite:///./local-dev.db
# 测试环境默认使用SQLite，如需覆盖请设置 TEST_DATABASE_URL
TEST_DATABASE_URL=
# 生产环境连接串（部署时修改为实际MySQL配置）
DATABASE_URL=mysql+pymysql://ohsteack:password@localhost/ohsteack?charset=utf8mb4

# 邮件配置（可选）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=noreply@ohsteack.com
EOL
    echo "✓ .env文件已创建，请编辑并填写正确的配置信息"
else
    echo "✓ .env文件已存在"
fi

# 可选的MySQL初始化
if command -v mysql >/dev/null 2>&1; then
    read -r -p "是否为MySQL创建开发/测试数据库？(y/n) " INIT_MYSQL
    if [[ "${INIT_MYSQL}" == "y" ]]; then
        read -r -s -p "请输入MySQL root密码（用于创建数据库）: " MYSQL_ROOT_PASSWORD
        echo
        echo "正在创建数据库..."
        if mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<'SQL'
CREATE DATABASE IF NOT EXISTS ohsteack_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ohsteack_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS ohsteack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SQL
        then
            echo "✓ MySQL 数据库创建完成"
        else
            echo "✗ MySQL 数据库创建失败，请检查root密码或权限"
            exit 1
        fi
    else
        echo "跳过MySQL数据库初始化。"
    fi
else
    echo "未检测到mysql命令，跳过MySQL数据库初始化。"
fi

# 应用迁移
echo "正在应用数据库迁移..."
export FLASK_APP=run.py
export FLASK_ENV=development
flask db upgrade

# 创建管理员账户
echo "是否创建管理员账户？(y/n)"
read -r CREATE_ADMIN

if [[ $CREATE_ADMIN == "y" ]]; then
    flask create-admin
fi

echo ""
echo "========================================="
echo "✓ 设置完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 编辑 .env 文件，配置数据库连接等信息"
echo "2. 运行 'source venv/bin/activate' 激活虚拟环境"
echo "3. 运行 'flask run' 启动开发服务器"
echo "4. 访问 http://localhost:5000"
echo ""
echo "生产环境部署请参考 docs/DEPLOYMENT.md"
