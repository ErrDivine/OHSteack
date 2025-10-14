#!/bin/bash
# OHSteack 生产环境更新脚本

set -e  # 遇到错误立即退出

echo "========================================="
echo "OHSteack 生产环境更新脚本"
echo "========================================="

# 配置变量
APP_DIR="/var/www/ohsteack"
BACKUP_DIR="/var/backups/ohsteack"
BRANCH="main"
USER="www-data"
GROUP="www-data"

# 检查是否以root权限运行
if [[ $EUID -ne 0 ]]; then
   echo "此脚本需要root权限运行" 
   exit 1
fi

cd $APP_DIR

# 创建备份
echo "正在创建备份..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" \
    --exclude='venv' \
    --exclude='logs' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='static/uploads' \
    .

echo "✓ 备份已创建: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"

# 设置维护模式（可选）
# echo "正在启用维护模式..."
# touch maintenance.flag

# 拉取最新代码
echo "正在更新代码..."
sudo -u $USER git fetch origin
sudo -u $USER git pull origin $BRANCH

# 更新依赖
echo "正在更新Python依赖..."
sudo -u $USER $APP_DIR/venv/bin/pip install -r requirements.txt

# 运行数据库迁移
echo "正在检查数据库迁移..."
sudo -u $USER $APP_DIR/venv/bin/flask db upgrade

# 收集静态文件（如果需要）
# echo "正在收集静态文件..."
# sudo -u $USER $APP_DIR/venv/bin/python manage.py collectstatic --noinput

# 清理缓存
echo "正在清理缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# 重新加载应用
echo "正在重新加载应用..."
supervisorctl restart ohsteack_group:*

# 重新加载Nginx（如果配置有更改）
if git diff HEAD@{1} HEAD --name-only | grep -q "nginx"; then
    echo "检测到Nginx配置更改，正在重新加载..."
    cp deployment/nginx/ohsteack.conf /etc/nginx/sites-available/
    nginx -t && systemctl reload nginx
fi

# 关闭维护模式（可选）
# echo "正在关闭维护模式..."
# rm -f maintenance.flag

# 健康检查
echo "正在进行健康检查..."
sleep 5
if curl -f -s -o /dev/null http://localhost; then
    echo "✓ 应用运行正常"
else
    echo "✗ 应用可能存在问题，请检查日志"
    echo "回滚命令: tar -xzf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz -C $APP_DIR"
fi

# 清理旧备份（保留最近7天）
echo "正在清理旧备份..."
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo ""
echo "========================================="
echo "✓ 更新完成！"
echo "========================================="
echo ""
echo "更新信息："
echo "- 备份位置: $BACKUP_DIR/backup_$TIMESTAMP.tar.gz"
echo "- 查看日志: tail -f /var/log/supervisor/ohsteack_stdout.log"
echo "- 回滚命令: tar -xzf $BACKUP_DIR/backup_$TIMESTAMP.tar.gz -C $APP_DIR"
echo ""
