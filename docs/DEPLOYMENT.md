# OHSteack 部署指南

本文档详细说明了如何在生产环境中部署 OHSteack 应用。

## 目录

1. [系统要求](#系统要求)
2. [快速部署](#快速部署)
3. [手动部署](#手动部署)
4. [配置说明](#配置说明)
5. [SSL配置](#ssl配置)
6. [常见问题](#常见问题)

## 系统要求

### 硬件要求
- CPU: 2核心或更多
- 内存: 2GB RAM或更多（推荐4GB）
- 硬盘: 10GB可用空间（取决于上传文件数量）

### 软件要求
- 操作系统: Ubuntu 20.04 LTS或更高版本（也支持其他Linux发行版）
- Python: 3.8或更高版本
- MySQL: 5.7或更高版本
- Nginx: 1.18或更高版本
- Supervisor: 4.0或更高版本

## 快速部署

使用自动化部署脚本（适用于Ubuntu/Debian系统）：

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/ohsteack.git
cd ohsteack

# 2. 以root权限运行部署脚本
sudo bash scripts/deploy.sh

# 3. 编辑配置文件
sudo nano /var/www/ohsteack/.env

# 4. 重启服务
sudo supervisorctl restart ohsteack
```

## 手动部署

### 1. 安装系统依赖

```bash
# 更新系统
sudo apt-get update
sudo apt-get upgrade -y

# 安装必要的包
sudo apt-get install -y \
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
    build-essential
```

### 2. 配置MySQL数据库

```bash
# 登录MySQL
sudo mysql

# 创建数据库和用户
CREATE DATABASE ohsteack CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ohsteack'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON ohsteack.* TO 'ohsteack'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. 部署应用代码

```bash
# 创建应用目录
sudo mkdir -p /var/www/ohsteack
cd /var/www/ohsteack

# 克隆代码
sudo git clone https://github.com/yourusername/ohsteack.git .

# 创建虚拟环境
sudo python3 -m venv venv

# 安装Python依赖
sudo venv/bin/pip install -r requirements.txt

# 创建必要的目录
sudo mkdir -p logs instance static/uploads
```

### 4. 配置应用

创建 `.env` 文件：

```bash
sudo nano /var/www/ohsteack/.env
```

填写以下内容：

```env
# Flask配置
FLASK_APP=run.py
FLASK_ENV=production
SECRET_KEY=your_secret_key_here

# 数据库配置
DATABASE_URL=mysql+pymysql://ohsteack:your_password@localhost/ohsteack?charset=utf8mb4

# 邮件配置（可选）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=noreply@ohsteack.com
```

### 5. 初始化数据库

```bash
# 运行数据库迁移
cd /var/www/ohsteack
sudo venv/bin/flask db upgrade

# 创建管理员账户
sudo venv/bin/flask create-admin
```

### 6. 配置Nginx

```bash
# 复制配置文件
sudo cp deployment/nginx/ohsteack.conf /etc/nginx/sites-available/

# 修改配置中的域名
sudo nano /etc/nginx/sites-available/ohsteack.conf

# 启用站点
sudo ln -s /etc/nginx/sites-available/ohsteack.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

### 7. 配置Supervisor

```bash
# 复制配置文件
sudo cp deployment/supervisor/ohsteack.conf /etc/supervisor/conf.d/

# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动应用
sudo supervisorctl start ohsteack
```

### 8. 设置文件权限

```bash
# 设置正确的所有者
sudo chown -R www-data:www-data /var/www/ohsteack

# 设置目录权限
sudo chmod 755 /var/www/ohsteack
sudo chmod -R 755 /var/www/ohsteack/static
sudo chmod -R 750 /var/www/ohsteack/logs
sudo chmod -R 750 /var/www/ohsteack/instance
sudo chmod 600 /var/www/ohsteack/.env
```

## 配置说明

### Nginx配置要点

1. **域名配置**: 修改 `server_name` 为您的实际域名
2. **静态文件路径**: 确保 `root` 指向正确的应用目录
3. **上传文件大小**: 根据需要调整 `client_max_body_size`
4. **HTTPS配置**: 生产环境建议启用SSL

### Gunicorn配置

编辑 `gunicorn.conf.py`：

```python
# 工作进程数（根据服务器CPU核心数调整）
workers = multiprocessing.cpu_count() * 2 + 1

# 绑定地址
bind = "127.0.0.1:8000"

# 超时设置
timeout = 120
```

### Supervisor配置

主要配置项：
- `command`: Gunicorn启动命令
- `directory`: 应用工作目录
- `user`: 运行用户（www-data）
- `autostart`: 开机自启动
- `autorestart`: 异常自动重启

## SSL配置

### 使用Let's Encrypt（推荐）

```bash
# 安装Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自动续期（Certbot会自动配置）
sudo certbot renew --dry-run
```

### 手动配置SSL

如果使用其他SSL证书提供商：

1. 将证书文件上传到服务器
2. 编辑Nginx配置：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 其他配置...
}

# HTTP重定向到HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 更新应用

使用自动更新脚本：

```bash
sudo bash scripts/update.sh
```

或手动更新：

```bash
cd /var/www/ohsteack
sudo -u www-data git pull
sudo -u www-data venv/bin/pip install -r requirements.txt
sudo -u www-data venv/bin/flask db upgrade
sudo supervisorctl restart ohsteack
```

## 备份策略

### 数据库备份

```bash
# 创建备份脚本
cat > /usr/local/bin/backup-ohsteack-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ohsteack"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
mysqldump -u ohsteack -p'your_password' ohsteack | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
# 删除7天前的备份
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-ohsteack-db.sh

# 添加到crontab（每天凌晨2点执行）
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-ohsteack-db.sh") | crontab -
```

### 文件备份

```bash
# 备份上传的文件
tar -czf /var/backups/ohsteack/uploads_$(date +%Y%m%d).tar.gz \
    /var/www/ohsteack/static/uploads/
```

## 监控和日志

### 查看应用日志

```bash
# Supervisor日志
sudo tail -f /var/log/supervisor/ohsteack_stdout.log
sudo tail -f /var/log/supervisor/ohsteack_stderr.log

# Nginx日志
sudo tail -f /var/log/nginx/ohsteack_access.log
sudo tail -f /var/log/nginx/ohsteack_error.log

# 应用日志
sudo tail -f /var/www/ohsteack/logs/error.log
```

### 常用管理命令

```bash
# Supervisor
sudo supervisorctl status              # 查看状态
sudo supervisorctl restart ohsteack    # 重启应用
sudo supervisorctl stop ohsteack       # 停止应用
sudo supervisorctl start ohsteack      # 启动应用

# Nginx
sudo systemctl status nginx            # 查看状态
sudo systemctl restart nginx           # 重启Nginx
sudo nginx -t                          # 测试配置

# MySQL
sudo systemctl status mysql            # 查看状态
mysql -u ohsteack -p ohsteack         # 连接数据库
```

## 常见问题

### 1. 应用无法启动

**检查步骤：**
```bash
# 查看Supervisor日志
sudo tail -f /var/log/supervisor/ohsteack_stderr.log

# 检查端口占用
sudo netstat -tulpn | grep 8000

# 检查配置文件
sudo supervisorctl status
```

### 2. 数据库连接失败

**解决方案：**
- 检查 `.env` 文件中的数据库配置
- 确认MySQL服务运行正常：`sudo systemctl status mysql`
- 测试数据库连接：`mysql -u ohsteack -p`

### 3. 静态文件无法访问

**解决方案：**
- 检查Nginx配置中的静态文件路径
- 确认文件权限：`ls -la /var/www/ohsteack/static`
- 重启Nginx：`sudo systemctl restart nginx`

### 4. 文件上传失败

**解决方案：**
- 检查上传目录权限：`sudo chmod 755 /var/www/ohsteack/static/uploads`
- 检查Nginx配置中的 `client_max_body_size`
- 确认磁盘空间：`df -h`

### 5. 内存不足

**解决方案：**
- 减少Gunicorn工作进程数
- 添加swap空间
- 升级服务器配置

## 性能优化

### 1. 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_team_name ON teams(name);
CREATE INDEX idx_resource_team ON resources(team_id);
CREATE INDEX idx_result_team ON results(team_id);
```

### 2. 启用Redis缓存（可选）

安装Redis并配置Flask-Caching。

### 3. CDN配置

将静态文件托管到CDN以提高加载速度。

## 安全建议

1. **防火墙配置**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **定期更新系统**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   ```

3. **使用强密码**
   - 数据库密码
   - SECRET_KEY
   - 管理员账户

4. **限制失败登录**
   - 考虑使用Flask-Limiter

5. **定期备份**
   - 数据库每日备份
   - 文件定期备份

## 技术支持

如遇到问题：
1. 查看日志文件
2. 参考本文档的常见问题部分
3. 提交Issue到GitHub仓库
4. 联系技术支持团队
