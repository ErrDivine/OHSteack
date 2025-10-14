from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired, Length, Optional, URL


class ResultForm(FlaskForm):
    """成果表单"""
    title = StringField('标题', validators=[
        DataRequired(message='请输入成果标题'),
        Length(min=2, max=200, message='标题长度必须在2-200个字符之间')
    ])
    description = TextAreaField('描述', validators=[
        DataRequired(message='请输入成果描述'),
        Length(max=1000, message='描述不能超过1000个字符')
    ])
    content = TextAreaField('详细内容（支持Markdown）', validators=[
        Optional()
    ], render_kw={'rows': 20})
    result_type = SelectField('成果类型', choices=[
        ('document', '文档'),
        ('code', '代码'),
        ('design', '设计'),
        ('model', '模型'),
        ('dataset', '数据集'),
        ('other', '其他')
    ], default='document')
    status = SelectField('状态', choices=[
        ('draft', '草稿'),
        ('in_progress', '进行中'),
        ('review', '审核中'),
        ('final', '最终版')
    ], default='draft')
    repository_url = StringField('代码仓库链接', validators=[
        Optional(),
        URL(message='请输入有效的URL'),
        Length(max=500, message='链接不能超过500个字符')
    ])
    demo_url = StringField('演示链接', validators=[
        Optional(),
        URL(message='请输入有效的URL'),
        Length(max=500, message='链接不能超过500个字符')
    ])
    category = SelectField('分类', choices=[
        ('', '未分类'),
        ('research', '研究'),
        ('development', '开发'),
        ('analysis', '分析'),
        ('presentation', '展示'),
        ('other', '其他')
    ], default='')
    tags = StringField('标签', validators=[
        Optional(),
        Length(max=500, message='标签总长度不能超过500个字符')
    ], render_kw={'placeholder': '用逗号分隔多个标签'})
    attachments = MultipleFileField('附件', validators=[
        Optional(),
        FileAllowed(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 
                    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 
                    'zip', 'rar', '7z', 'tar', 'gz'],
                   message='不支持的文件格式')
    ])
    changes_description = TextAreaField('变更说明', validators=[
        Optional(),
        Length(max=500, message='变更说明不能超过500个字符')
    ], render_kw={'placeholder': '如果修改了内容，请说明主要变更'})
    submit = SubmitField('保存')


class IterationForm(FlaskForm):
    """迭代版本表单"""
    changes_description = TextAreaField('变更说明', validators=[
        DataRequired(message='请说明此版本的主要变更'),
        Length(min=10, max=500, message='变更说明必须在10-500个字符之间')
    ])
    content = TextAreaField('内容（支持Markdown）', validators=[
        DataRequired(message='请输入内容')
    ], render_kw={'rows': 20})
    submit = SubmitField('创建新版本')
