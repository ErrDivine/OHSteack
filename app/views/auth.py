from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, ResultIteration
from app.forms.auth import LoginForm, RegisterForm, ProfileForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    is_valid = form.validate_on_submit()
    if is_valid:
        # 尝试通过邮箱或用户名查找用户
        user = User.query.filter(
            (User.email == form.login.data) | (User.username == form.login.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('您的账户已被禁用，请联系管理员。', 'error')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            # 获取下一个页面
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash(f'欢迎回来，{user.username}！', 'success')
            return redirect(next_page)
        else:
            current_app.logger.warning('Login attempt failed for %s', form.login.data)
            flash('登录失败，请检查用户名/邮箱和密码。', 'error')
    elif request.method == 'POST':
        current_app.logger.warning(
            'Login validation failed: errors=%s session_csrf=%s form_csrf=%s cookies=%s',
            form.errors,
            session.get('csrf_token'),
            form.csrf_token.data,
            dict(request.cookies)
        )
        flash('登录失败，请检查表单输入。', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    is_valid = form.validate_on_submit()
    if is_valid:
        # 检查用户名是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('该用户名已被使用，请选择其他用户名。', 'error')
            return redirect(url_for('auth.register'))
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=form.email.data).first():
            flash('该邮箱已被注册，请使用其他邮箱。', 'error')
            return redirect(url_for('auth.register'))
        
        # 创建新用户
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # 自动登录
        login_user(user)
        flash('注册成功！欢迎加入OHSteack！', 'success')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST' and not is_valid:
        current_app.logger.warning(
            'Register validation failed: errors=%s session_csrf=%s form_csrf=%s cookies=%s',
            form.errors,
            session.get('csrf_token'),
            form.csrf_token.data,
            dict(request.cookies)
        )
        flash('注册失败，请检查表单信息。', 'error')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    flash('您已成功退出登录。', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """用户个人资料"""
    form = ProfileForm(obj=current_user)

    user_teams = current_user.get_teams()
    profile_stats = {
        'team_count': len(user_teams),
        'resource_count': current_user.created_resources.count(),
        'result_count': current_user.created_results.count(),
        'iteration_count': current_user.result_iterations.count(),
        'days_since_join': (datetime.utcnow() - current_user.created_at).days if current_user.created_at else 0
    }

    latest_iterations = current_user.result_iterations.order_by(ResultIteration.created_at.desc()).limit(5).all()
    
    if form.validate_on_submit():
        # 检查用户名是否被其他用户使用
        if form.username.data != current_user.username:
            if User.query.filter_by(username=form.username.data).first():
                flash('该用户名已被使用。', 'error')
                return redirect(url_for('auth.profile'))
        
        # 检查邮箱是否被其他用户使用
        if form.email.data != current_user.email:
            if User.query.filter_by(email=form.email.data).first():
                flash('该邮箱已被使用。', 'error')
                return redirect(url_for('auth.profile'))
        
        # 更新用户信息
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        
        # 如果提供了新密码，更新密码
        if form.new_password.data:
            if current_user.check_password(form.current_password.data):
                current_user.set_password(form.new_password.data)
            else:
                flash('当前密码错误。', 'error')
                return redirect(url_for('auth.profile'))
        
        db.session.commit()
        flash('个人资料更新成功！', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template(
        'auth/profile.html',
        form=form,
        profile_stats=profile_stats,
        user_teams=user_teams,
        latest_iterations=latest_iterations
    )
