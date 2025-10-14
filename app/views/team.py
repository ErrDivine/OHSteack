from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Team, TeamMember, User, Resource, Result
from app.forms.team import TeamForm, InviteMemberForm

team_bp = Blueprint('team', __name__)


@team_bp.route('/')
@login_required
def list_teams():
    """团队列表"""
    # 获取用户的团队
    user_teams = current_user.get_teams()
    
    # 获取其他活跃团队（可选）
    other_teams = Team.query.filter(
        Team.status == 'active',
        ~Team.id.in_([t.id for t in user_teams])
    ).order_by(Team.created_at.desc()).limit(10).all()
    
    return render_template('team/list.html', 
                         user_teams=user_teams, 
                         other_teams=other_teams)


@team_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """创建团队"""
    form = TeamForm()
    
    if form.validate_on_submit():
        team = Team(
            name=form.name.data,
            description=form.description.data,
            competition_name=form.competition_name.data,
            competition_url=form.competition_url.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        
        db.session.add(team)
        db.session.flush()  # 获取team.id
        
        # 添加创建者为团队领导
        team.add_member(current_user, role='leader')
        
        db.session.commit()
        
        flash(f'团队 "{team.name}" 创建成功！', 'success')
        return redirect(url_for('team.detail', team_id=team.id))
    
    return render_template('team/create.html', form=form)


@team_bp.route('/<int:team_id>')
@login_required
def detail(team_id):
    """团队详情"""
    team = Team.query.get_or_404(team_id)
    
    # 检查用户是否有权限查看
    if not team.has_member(current_user) and not current_user.is_admin:
        flash('您没有权限查看此团队。', 'error')
        return redirect(url_for('team.list_teams'))
    
    # 获取团队成员
    members = team.get_active_members()
    leader = team.get_leader()
    
    # 获取团队统计
    stats = team.get_statistics()
    
    # 获取最近的资源和成果
    recent_resources = (
        team.resources.order_by(Resource.created_at.desc()).limit(5).all()
    )
    recent_results = (
        team.results.order_by(Result.updated_at.desc()).limit(5).all()
    )
    
    return render_template('team/detail.html', 
                         team=team,
                         members=members,
                         leader=leader,
                         stats=stats,
                         recent_resources=recent_resources,
                         recent_results=recent_results,
                         is_member=team.has_member(current_user),
                         is_leader=current_user.is_team_leader(team))


@team_bp.route('/<int:team_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(team_id):
    """编辑团队"""
    team = Team.query.get_or_404(team_id)
    
    # 检查权限
    if not current_user.can_edit_team(team):
        flash('您没有权限编辑此团队。', 'error')
        return redirect(url_for('team.detail', team_id=team_id))
    
    form = TeamForm(obj=team)
    
    if form.validate_on_submit():
        team.name = form.name.data
        team.description = form.description.data
        team.competition_name = form.competition_name.data
        team.competition_url = form.competition_url.data
        team.start_date = form.start_date.data
        team.end_date = form.end_date.data
        team.status = form.status.data
        
        db.session.commit()
        
        flash('团队信息更新成功！', 'success')
        return redirect(url_for('team.detail', team_id=team_id))
    
    return render_template('team/edit.html', form=form, team=team)


@team_bp.route('/<int:team_id>/invite', methods=['GET', 'POST'])
@login_required
def invite_member(team_id):
    """邀请团队成员"""
    team = Team.query.get_or_404(team_id)
    
    # 检查权限（只有团队领导可以邀请）
    if not current_user.is_team_leader(team):
        flash('只有团队领导可以邀请新成员。', 'error')
        return redirect(url_for('team.detail', team_id=team_id))
    
    form = InviteMemberForm()
    
    if form.validate_on_submit():
        # 查找用户
        user = User.query.filter(
            (User.email == form.user_identifier.data) | 
            (User.username == form.user_identifier.data)
        ).first()
        
        if not user:
            flash('未找到该用户。', 'error')
        elif team.has_member(user):
            flash('该用户已经是团队成员。', 'error')
        else:
            team.add_member(user, role=form.role.data)
            db.session.commit()
            
            flash(f'成功邀请 {user.username} 加入团队！', 'success')
            return redirect(url_for('team.detail', team_id=team_id))
    
    return render_template('team/invite.html', form=form, team=team)


@team_bp.route('/<int:team_id>/leave', methods=['POST'])
@login_required
def leave(team_id):
    """离开团队"""
    team = Team.query.get_or_404(team_id)
    
    if not team.has_member(current_user):
        flash('您不是该团队的成员。', 'error')
        return redirect(url_for('team.list_teams'))
    
    # 检查是否是唯一的领导
    if current_user.is_team_leader(team):
        active_leaders = TeamMember.query.filter_by(
            team_id=team_id,
            role='leader',
            is_active=True
        ).count()
        
        if active_leaders == 1:
            flash('您是团队唯一的领导，请先指定其他成员为领导后再离开。', 'error')
            return redirect(url_for('team.detail', team_id=team_id))
    
    team.remove_member(current_user)
    db.session.commit()
    
    flash(f'您已离开团队 "{team.name}"。', 'info')
    return redirect(url_for('team.list_teams'))


@team_bp.route('/<int:team_id>/member/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_member(team_id, user_id):
    """移除团队成员"""
    team = Team.query.get_or_404(team_id)
    user = User.query.get_or_404(user_id)
    
    # 检查权限
    if not current_user.is_team_leader(team):
        flash('只有团队领导可以移除成员。', 'error')
        return redirect(url_for('team.detail', team_id=team_id))
    
    if user.is_team_leader(team):
        flash('不能移除团队领导。', 'error')
        return redirect(url_for('team.detail', team_id=team_id))
    
    team.remove_member(user)
    db.session.commit()
    
    flash(f'已将 {user.username} 从团队中移除。', 'info')
    return redirect(url_for('team.detail', team_id=team_id))
