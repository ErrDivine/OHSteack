from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models import Team

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """首页"""
    if current_user.is_authenticated:
        # 获取用户的团队
        user_teams = current_user.get_teams()

        # 汇总用户的核心统计数据
        profile_stats = {
            'team_count': len(user_teams),
            'resource_count': current_user.created_resources.count(),
            'result_count': current_user.created_results.count(),
            'iteration_count': current_user.result_iterations.count()
        }

        return render_template(
            'index.html',
            user_teams=user_teams,
            profile_stats=profile_stats
        )
    else:
        # 展示公开信息
        active_teams = Team.query.filter_by(status='active').order_by(Team.created_at.desc()).limit(6).all()
        return render_template('landing.html', active_teams=active_teams)


@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')


@main_bp.route('/dashboard')
def dashboard():
    """用户仪表板"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # 获取用户统计信息
    user_teams = current_user.get_teams()
    total_resources = 0
    total_results = 0
    
    for team in user_teams:
        stats = team.get_statistics()
        total_resources += stats['resource_count']
        total_results += stats['result_count']
    
    from datetime import date
    stats = {
        'team_count': len(user_teams),
        'resource_count': total_resources,
        'result_count': total_results,
        'days_active': (current_user.last_login - current_user.created_at).days if current_user.last_login else 0
    }
    
    return render_template('dashboard.html', stats=stats, teams=user_teams, today=date.today())
