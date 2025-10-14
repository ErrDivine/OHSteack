from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL, ValidationError
from datetime import date


class TeamForm(FlaskForm):
    """团队表单"""
    name = StringField('团队名称', validators=[
        DataRequired(message='请输入团队名称'),
        Length(min=2, max=100, message='团队名称长度必须在2-100个字符之间')
    ])
    description = TextAreaField('团队描述', validators=[
        Optional(),
        Length(max=1000, message='团队描述不能超过1000个字符')
    ])
    competition_name = StringField('竞赛名称', validators=[
        Optional(),
        Length(max=200, message='竞赛名称不能超过200个字符')
    ])
    competition_url = StringField('竞赛链接', validators=[
        Optional(),
        URL(message='请输入有效的URL'),
        Length(max=500, message='链接不能超过500个字符')
    ])
    start_date = DateField('开始日期', validators=[Optional()])
    end_date = DateField('结束日期', validators=[Optional()])
    status = SelectField('状态', choices=[
        ('active', '活跃'),
        ('completed', '已完成'),
        ('paused', '暂停')
    ], default='active')
    submit = SubmitField('保存')
    
    def validate_end_date(self, field):
        """验证结束日期必须晚于开始日期"""
        if field.data and self.start_date.data:
            if field.data < self.start_date.data:
                raise ValidationError('结束日期必须晚于开始日期')


class InviteMemberForm(FlaskForm):
    """邀请成员表单"""
    user_identifier = StringField('用户名或邮箱', validators=[
        DataRequired(message='请输入要邀请的用户的用户名或邮箱')
    ])
    role = SelectField('角色', choices=[
        ('member', '成员'),
        ('leader', '领导')
    ], default='member')
    submit = SubmitField('邀请')
