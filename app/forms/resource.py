from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL


class ResourceForm(FlaskForm):
    """资源表单"""
    title = StringField('标题', validators=[
        DataRequired(message='请输入资源标题'),
        Length(min=2, max=200, message='标题长度必须在2-200个字符之间')
    ])
    description = TextAreaField('描述', validators=[
        Optional(),
        Length(max=500, message='描述不能超过500个字符')
    ])
    content = TextAreaField('内容（支持Markdown）', validators=[
        Optional()
    ], render_kw={'rows': 15})
    resource_type = SelectField('资源类型', choices=[
        ('document', '文档'),
        ('link', '链接'),
        ('file', '文件'),
        ('code', '代码')
    ], default='document')
    url = StringField('外部链接', validators=[
        Optional(),
        URL(message='请输入有效的URL'),
        Length(max=500, message='链接不能超过500个字符')
    ])
    file = FileField('上传文件', validators=[
        Optional(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
                    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'md',
                    'zip', 'rar', '7z', 'tar', 'gz'],
                   message='不支持的文件格式')
    ])
    category = SelectField('分类', choices=[
        ('', '未分类'),
        ('tutorial', '教程'),
        ('reference', '参考资料'),
        ('tool', '工具'),
        ('dataset', '数据集'),
        ('paper', '论文'),
        ('other', '其他')
    ], default='')
    tags = StringField('标签', validators=[
        Optional(),
        Length(max=500, message='标签总长度不能超过500个字符')
    ], render_kw={'placeholder': '用逗号分隔多个标签，如：机器学习,深度学习,PyTorch'})
    submit = SubmitField('保存')
