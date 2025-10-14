from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, ValidationError


class LoginForm(FlaskForm):
    """登录表单"""
    login = StringField('用户名或邮箱', validators=[
        DataRequired(message='请输入用户名或邮箱')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码')
    ])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegisterForm(FlaskForm):
    """注册表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email(message='请输入有效的邮箱地址')
    ])
    full_name = StringField('姓名', validators=[
        Optional(),
        Length(max=100, message='姓名长度不能超过100个字符')
    ])
    password = PasswordField('密码', validators=[
        DataRequired(message='请输入密码'),
        Length(min=6, message='密码长度至少为6个字符')
    ])
    password_confirm = PasswordField('确认密码', validators=[
        DataRequired(message='请确认密码'),
        EqualTo('password', message='两次输入的密码必须一致')
    ])
    submit = SubmitField('注册')
    
    def validate_username(self, field):
        """验证用户名格式"""
        if not field.data.replace('_', '').replace('-', '').isalnum():
            raise ValidationError('用户名只能包含字母、数字、下划线和连字符')


class ProfileForm(FlaskForm):
    """个人资料表单"""
    username = StringField('用户名', validators=[
        DataRequired(message='请输入用户名'),
        Length(min=3, max=20, message='用户名长度必须在3-20个字符之间')
    ])
    email = StringField('邮箱', validators=[
        DataRequired(message='请输入邮箱'),
        Email(message='请输入有效的邮箱地址')
    ])
    full_name = StringField('姓名', validators=[
        Optional(),
        Length(max=100, message='姓名长度不能超过100个字符')
    ])
    bio = TextAreaField('个人简介', validators=[
        Optional(),
        Length(max=500, message='个人简介不能超过500个字符')
    ])
    current_password = PasswordField('当前密码', validators=[
        Optional()
    ])
    new_password = PasswordField('新密码', validators=[
        Optional(),
        Length(min=6, message='密码长度至少为6个字符')
    ])
    new_password_confirm = PasswordField('确认新密码', validators=[
        Optional(),
        EqualTo('new_password', message='两次输入的密码必须一致')
    ])
    submit = SubmitField('更新资料')
