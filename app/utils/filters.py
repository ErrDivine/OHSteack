from datetime import datetime
import markdown2


def register_filters(app):
    """注册自定义模板过滤器"""
    
    @app.template_filter('datetime')
    def datetime_filter(dt, format='%Y-%m-%d %H:%M'):
        """格式化日期时间"""
        if dt:
            return dt.strftime(format)
        return ''
    
    @app.template_filter('date')
    def date_filter(dt):
        """格式化日期"""
        if dt:
            return dt.strftime('%Y-%m-%d')
        return ''
    
    @app.template_filter('timeago')
    def timeago_filter(dt):
        """显示相对时间"""
        if not dt:
            return ''
        
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days > 365:
            return f'{diff.days // 365}年前'
        elif diff.days > 30:
            return f'{diff.days // 30}个月前'
        elif diff.days > 0:
            return f'{diff.days}天前'
        elif diff.seconds > 3600:
            return f'{diff.seconds // 3600}小时前'
        elif diff.seconds > 60:
            return f'{diff.seconds // 60}分钟前'
        else:
            return '刚刚'
    
    @app.template_filter('markdown')
    def markdown_filter(text):
        """渲染Markdown文本"""
        if not text:
            return ''
        return markdown2.markdown(
            text,
            extras=['fenced-code-blocks', 'tables', 'strike', 'toc']
        )
    
    @app.template_filter('filesize')
    def filesize_filter(size):
        """格式化文件大小"""
        if not size:
            return '0 B'
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size)
        
        while size >= 1024.0 and unit_index < len(units) - 1:
            size /= 1024.0
            unit_index += 1
        
        if unit_index == 0:
            return f'{int(size)} {units[unit_index]}'
        else:
            return f'{size:.1f} {units[unit_index]}'
    
    @app.template_filter('truncate')
    def truncate_filter(text, length=100, suffix='...'):
        """截断文本"""
        if not text:
            return ''
        if len(text) <= length:
            return text
        return text[:length].rsplit(' ', 1)[0] + suffix
