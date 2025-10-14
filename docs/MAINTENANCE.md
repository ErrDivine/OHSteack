# OHSteack 维护指南

本文档为系统管理员和开发人员提供日常维护、故障排查和系统优化的指导。

## 目录

1. [日常维护](#日常维护)
2. [系统监控](#系统监控)
3. [故障排查](#故障排查)
4. [数据库维护](#数据库维护)
5. [性能优化](#性能优化)
6. [安全维护](#安全维护)

## 日常维护

### 每日检查清单

```bash
# 1. 检查应用状态
sudo supervisorctl status ohsteack

# 2. 检查Nginx状态
sudo systemctl status nginx

# 3. 检查数据库状态
sudo systemctl status mysql

# 4. 检查磁盘空间
df -h

# 5. 检查内存使用
free -m

# 6. 查看最近的错误日志
sudo tail -n 50 /var/log/supervisor/ohsteack_stderr.log
```

### 每周任务

1. **清理临时文件**
   ```bash
   # 清理Python缓存
   find /var/www/ohsteack -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
   find /var/www/ohsteack -type f -name "*.pyc" -delete 2>/dev/null
   
   # 清理旧日志（保留30天）
   find /var/www/ohsteack/logs -name "*.log" -mtime +30 -delete
   ```

2. **检查更新**
   ```bash
   cd /var/www/ohsteack
   sudo -u www-data git fetch
   sudo -u www-data git status
   ```

3. **验证备份**
   ```bash
   # 检查备份文件
   ls -lh /var/backups/ohsteack/
   
   # 测试数据库备份恢复（在测试环境）
   # gunzip < backup.sql.gz | mysql -u test test_db
   ```

### 每月任务

1. **系统更新**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   sudo apt-get autoremove
   ```

2. **数据库优化**
   ```bash
   # 优化所有表
   mysqlcheck -u ohsteack -p --optimize --all-databases
   ```

3. **安全审计**
   - 检查失败的登录尝试
   - 审查用户权限
   - 更新依赖包

4. **性能分析**
   - 分析慢查询日志
   - 检查资源使用趋势
   - 评估是否需要扩展

## 系统监控

### 实时监控命令

```bash
# 1. CPU和内存监控
htop

# 2. 磁盘I/O监控
iotop

# 3. 网络流量监控
iftop

# 4. 进程监控
watch -n 1 'ps aux | grep gunicorn'

# 5. 端口监听
sudo netstat -tulpn | grep LISTEN
```

### 日志监控

```bash
# 实时监控访问日志
sudo tail -f /var/log/nginx/ohsteack_access.log

# 实时监控错误日志
sudo tail -f /var/log/nginx/ohsteack_error.log
sudo tail -f /var/log/supervisor/ohsteack_stderr.log

# 查找特定错误
sudo grep "ERROR" /var/www/ohsteack/logs/*.log

# 统计访问量
sudo cat /var/log/nginx/ohsteack_access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -20
```

### 性能指标

监控以下关键指标：

1. **响应时间**
   - 平均响应时间 < 500ms
   - 95%请求 < 1s

2. **服务器资源**
   - CPU使用率 < 70%
   - 内存使用率 < 80%
   - 磁盘空间 > 20%可用

3. **数据库**
   - 查询响应时间 < 100ms
   - 连接数 < 最大连接数的80%

4. **错误率**
   - HTTP 5xx错误 < 1%
   - HTTP 4xx错误 < 5%

## 故障排查

### 应用无法访问

**症状**: 用户无法访问网站

**排查步骤**:

```bash
# 1. 检查Nginx状态
sudo systemctl status nginx
# 如果未运行：sudo systemctl start nginx

# 2. 检查应用状态
sudo supervisorctl status ohsteack
# 如果未运行：sudo supervisorctl start ohsteack

# 3. 检查端口
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# 4. 测试本地访问
curl http://localhost
curl http://localhost:8000

# 5. 检查防火墙
sudo ufw status
```

### 数据库连接错误

**症状**: 应用日志显示数据库连接失败

**排查步骤**:

```bash
# 1. 检查MySQL状态
sudo systemctl status mysql

# 2. 测试数据库连接
mysql -u ohsteack -p -h localhost

# 3. 检查数据库配置
cat /var/www/ohsteack/.env | grep DATABASE

# 4. 查看MySQL错误日志
sudo tail -f /var/log/mysql/error.log

# 5. 检查连接数
mysql -u root -p -e "SHOW PROCESSLIST;"
```

### 性能问题

**症状**: 应用响应缓慢

**排查步骤**:

```bash
# 1. 检查系统负载
uptime
top

# 2. 检查磁盘I/O
iostat -x 1 5

# 3. 检查内存
free -m
sudo dmesg | grep -i "out of memory"

# 4. 分析慢查询
sudo mysql -u root -p -e "SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 10;"

# 5. 检查Gunicorn工作进程
ps aux | grep gunicorn | wc -l
```

### 文件上传失败

**症状**: 用户无法上传文件

**排查步骤**:

```bash
# 1. 检查目录权限
ls -la /var/www/ohsteack/static/uploads/

# 2. 检查磁盘空间
df -h /var/www/ohsteack/

# 3. 检查Nginx上传限制
sudo grep client_max_body_size /etc/nginx/sites-available/ohsteack.conf

# 4. 检查应用日志
sudo tail -f /var/log/supervisor/ohsteack_stderr.log
```

### 内存泄漏

**症状**: 内存使用持续增长

**排查步骤**:

```bash
# 1. 监控内存使用
watch -n 1 'free -m'

# 2. 查看进程内存
ps aux --sort=-%mem | head -10

# 3. 重启应用释放内存
sudo supervisorctl restart ohsteack

# 4. 调整Gunicorn配置
# 编辑 gunicorn.conf.py
# 减少 workers 数量或添加 max_requests
```

## 数据库维护

### 备份和恢复

**创建备份**:

```bash
# 完整备份
mysqldump -u ohsteack -p ohsteack > backup_$(date +%Y%m%d).sql

# 压缩备份
mysqldump -u ohsteack -p ohsteack | gzip > backup_$(date +%Y%m%d).sql.gz

# 备份特定表
mysqldump -u ohsteack -p ohsteack teams resources > tables_backup.sql
```

**恢复备份**:

```bash
# 从SQL文件恢复
mysql -u ohsteack -p ohsteack < backup.sql

# 从压缩文件恢复
gunzip < backup.sql.gz | mysql -u ohsteack -p ohsteack

# 恢复到新数据库
mysql -u root -p -e "CREATE DATABASE ohsteack_restore;"
mysql -u ohsteack -p ohsteack_restore < backup.sql
```

### 数据库优化

```sql
-- 分析表
ANALYZE TABLE teams, resources, results;

-- 优化表
OPTIMIZE TABLE teams, resources, results;

-- 检查表
CHECK TABLE teams, resources, results;

-- 修复表
REPAIR TABLE teams;

-- 查看表大小
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE table_schema = 'ohsteack'
ORDER BY (data_length + index_length) DESC;
```

### 慢查询分析

```bash
# 启用慢查询日志
sudo mysql -u root -p << EOF
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow-query.log';
EOF

# 分析慢查询
sudo mysqldumpslow -s t -t 10 /var/log/mysql/slow-query.log
```

### 索引优化

```sql
-- 查看表索引
SHOW INDEX FROM teams;

-- 查看索引使用情况
SELECT 
    table_schema as database_name,
    table_name,
    index_name,
    cardinality,
    column_name
FROM information_schema.statistics
WHERE table_schema = 'ohsteack'
ORDER BY table_name, index_name;

-- 查找未使用的索引
SELECT 
    object_schema,
    object_name,
    index_name
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE index_name IS NOT NULL
    AND count_star = 0
    AND object_schema = 'ohsteack';
```

## 性能优化

### 应用层优化

1. **启用缓存**
   ```python
   # 安装Redis
   sudo apt-get install redis-server
   
   # 在requirements.txt添加
   # Flask-Caching
   # redis
   ```

2. **数据库连接池**
   ```python
   # 在config.py调整
   SQLALCHEMY_POOL_SIZE = 10
   SQLALCHEMY_POOL_RECYCLE = 3600
   SQLALCHEMY_MAX_OVERFLOW = 20
   ```

3. **静态文件CDN**
   - 使用CDN托管静态文件
   - 启用浏览器缓存

### Nginx优化

```nginx
# 添加到nginx配置

# 启用压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript;

# 启用缓存
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# 连接优化
keepalive_timeout 65;
keepalive_requests 100;

# 缓冲区优化
client_body_buffer_size 128k;
client_max_body_size 50m;
```

### 数据库优化

```sql
-- MySQL配置优化（编辑 /etc/mysql/mysql.conf.d/mysqld.cnf）

[mysqld]
# InnoDB优化
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2

# 查询缓存
query_cache_type = 1
query_cache_size = 128M

# 连接优化
max_connections = 200
wait_timeout = 300
```

### 系统级优化

```bash
# 增加文件描述符限制
sudo nano /etc/security/limits.conf
# 添加：
# www-data soft nofile 65536
# www-data hard nofile 65536

# 优化TCP参数
sudo nano /etc/sysctl.conf
# 添加：
# net.core.somaxconn = 1024
# net.ipv4.tcp_max_syn_backlog = 2048

# 应用更改
sudo sysctl -p
```

## 安全维护

### 安全审计

```bash
# 1. 检查失败的登录尝试
sudo grep "Failed password" /var/log/auth.log | tail -20

# 2. 检查sudo使用记录
sudo grep sudo /var/log/auth.log | tail -20

# 3. 检查开放端口
sudo netstat -tulpn | grep LISTEN

# 4. 检查运行的服务
sudo systemctl list-units --type=service --state=running

# 5. 查看最近登录
last -20
```

### 更新依赖

```bash
# 更新Python包
cd /var/www/ohsteack
source venv/bin/activate
pip list --outdated

# 更新特定包
pip install --upgrade package_name

# 更新所有包（谨慎操作）
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U
```

### SSL证书续期

```bash
# 检查证书到期时间
sudo certbot certificates

# 手动续期
sudo certbot renew

# 测试自动续期
sudo certbot renew --dry-run
```

## 应急响应

### 高负载应急

```bash
# 1. 快速重启应用
sudo supervisorctl restart ohsteack

# 2. 清理缓存
sudo redis-cli FLUSHALL  # 如果使用Redis

# 3. 临时增加资源
# 编辑 gunicorn.conf.py 增加workers

# 4. 限制访问（临时）
# 在Nginx添加速率限制
```

### 数据恢复

```bash
# 紧急恢复最新备份
cd /var/backups/ohsteack
LATEST_BACKUP=$(ls -t db_*.sql.gz | head -1)
gunzip < $LATEST_BACKUP | mysql -u ohsteack -p ohsteack
```

### 回滚部署

```bash
# 1. 恢复代码到上一个版本
cd /var/www/ohsteack
sudo -u www-data git log --oneline -5
sudo -u www-data git reset --hard COMMIT_HASH

# 2. 回滚数据库迁移
sudo -u www-data FLASK_APP=run.py ./venv/bin/flask db downgrade

# 3. 重启应用
sudo supervisorctl restart ohsteack
```

## 维护最佳实践

1. **定期备份**
   - 每日自动备份数据库
   - 每周备份应用代码和文件
   - 定期测试备份恢复

2. **监控告警**
   - 配置系统监控（如Prometheus）
   - 设置关键指标告警
   - 定期检查日志

3. **文档更新**
   - 记录所有配置变更
   - 更新操作文档
   - 记录故障处理经验

4. **安全加固**
   - 定期更新系统和依赖
   - 定期审计安全日志
   - 及时修复安全漏洞

5. **性能优化**
   - 定期分析性能瓶颈
   - 优化慢查询
   - 合理规划资源扩展

## 联系支持

如遇到无法解决的问题：

1. 收集以下信息：
   - 错误日志
   - 系统状态
   - 操作步骤

2. 联系方式：
   - GitHub Issues: https://github.com/yourusername/ohsteack/issues
   - Email: support@ohsteack.com
   - 技术文档: https://docs.ohsteack.com
