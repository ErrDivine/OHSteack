import os
import markdown2
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Team, Resource
from app.forms.resource import ResourceForm

resource_bp = Blueprint('resource', __name__)


def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


@resource_bp.route('/team/<int:team_id>')
@login_required
def list_resources(team_id):
    """团队资源列表"""
    team = Team.query.get_or_404(team_id)
    
    # 检查权限
    if not team.has_member(current_user) and not current_user.is_admin:
        flash('您没有权限查看此团队的资源。', 'error')
        return redirect(url_for('team.list_teams'))
    
    # 获取查询参数
    category = request.args.get('category')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    
    # 构建查询
    query = team.resources
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            db.or_(
                Resource.title.contains(search),
                Resource.description.contains(search),
                Resource.tags.contains(search)
            )
        )
    
    # 排序：置顶资源优先，然后按创建时间
    query = query.order_by(Resource.is_pinned.desc(), Resource.created_at.desc())
    
    # 分页
    pagination = query.paginate(
        page=page,
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    resources = pagination.items
    
    # 获取所有分类
    categories = db.session.query(Resource.category).filter(
        Resource.team_id == team_id,
        Resource.category.isnot(None)
    ).distinct().all()
    categories = [c[0] for c in categories]
    
    return render_template('resource/list.html',
                         team=team,
                         resources=resources,
                         pagination=pagination,
                         categories=categories,
                         current_category=category,
                         search_query=search)


@resource_bp.route('/create/<int:team_id>', methods=['GET', 'POST'])
@login_required
def create(team_id):
    """创建资源"""
    team = Team.query.get_or_404(team_id)
    
    # 检查权限
    if not team.has_member(current_user):
        flash('您必须是团队成员才能添加资源。', 'error')
        return redirect(url_for('team.detail', team_id=team_id))
    
    form = ResourceForm()
    
    if form.validate_on_submit():
        resource = Resource(
            team=team,
            creator=current_user,
            title=form.title.data,
            description=form.description.data,
            content=form.content.data,
            resource_type=form.resource_type.data,
            url=form.url.data,
            category=form.category.data
        )
        
        # 处理标签
        tags = form.tags.data.split(',') if form.tags.data else []
        resource.set_tags(tags)
        
        # 处理文件上传
        if form.file.data:
            file = form.file.data
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # 创建团队专属目录
                team_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f'team_{team_id}')
                if not os.path.exists(team_folder):
                    os.makedirs(team_folder)
                
                # 保存文件
                file_path = os.path.join(team_folder, filename)
                file.save(file_path)
                resource.file_path = os.path.relpath(file_path, current_app.config['UPLOAD_FOLDER'])
        
        db.session.add(resource)
        db.session.commit()
        
        flash('资源创建成功！', 'success')
        return redirect(url_for('resource.detail', resource_id=resource.id))
    
    return render_template('resource/create.html', form=form, team=team)


@resource_bp.route('/<int:resource_id>')
@login_required
def detail(resource_id):
    """资源详情"""
    resource = Resource.query.get_or_404(resource_id)
    
    # 检查权限
    if not resource.team.has_member(current_user) and not current_user.is_admin:
        flash('您没有权限查看此资源。', 'error')
        return redirect(url_for('team.list_teams'))
    
    # 增加浏览次数
    resource.increment_view_count()
    
    # 渲染Markdown内容
    if resource.content:
        resource.rendered_content = markdown2.markdown(
            resource.content,
            extras=['fenced-code-blocks', 'tables', 'strike', 'toc']
        )
    
    return render_template('resource/detail.html', resource=resource)


@resource_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(resource_id):
    """编辑资源"""
    resource = Resource.query.get_or_404(resource_id)
    
    # 检查权限
    if not resource.is_editable_by(current_user):
        flash('您没有权限编辑此资源。', 'error')
        return redirect(url_for('resource.detail', resource_id=resource_id))
    
    form = ResourceForm(obj=resource)
    
    # 设置标签
    if request.method == 'GET' and resource.tags:
        form.tags.data = resource.tags
    
    if form.validate_on_submit():
        resource.title = form.title.data
        resource.description = form.description.data
        resource.content = form.content.data
        resource.resource_type = form.resource_type.data
        resource.url = form.url.data
        resource.category = form.category.data
        
        # 处理标签
        tags = form.tags.data.split(',') if form.tags.data else []
        resource.set_tags(tags)
        
        # 处理新文件上传
        if form.file.data:
            file = form.file.data
            if file and allowed_file(file.filename):
                # 删除旧文件
                if resource.file_path:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resource.file_path)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)
                
                # 保存新文件
                filename = secure_filename(file.filename)
                team_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f'team_{resource.team_id}')
                if not os.path.exists(team_folder):
                    os.makedirs(team_folder)
                
                file_path = os.path.join(team_folder, filename)
                file.save(file_path)
                resource.file_path = os.path.relpath(file_path, current_app.config['UPLOAD_FOLDER'])
        
        db.session.commit()
        
        flash('资源更新成功！', 'success')
        return redirect(url_for('resource.detail', resource_id=resource_id))
    
    return render_template('resource/edit.html', form=form, resource=resource)


@resource_bp.route('/<int:resource_id>/delete', methods=['POST'])
@login_required
def delete(resource_id):
    """删除资源"""
    resource = Resource.query.get_or_404(resource_id)
    team_id = resource.team_id
    
    # 检查权限
    if not resource.is_editable_by(current_user):
        flash('您没有权限删除此资源。', 'error')
        return redirect(url_for('resource.detail', resource_id=resource_id))
    
    # 删除文件
    if resource.file_path:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resource.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(resource)
    db.session.commit()
    
    flash('资源已删除。', 'info')
    return redirect(url_for('resource.list_resources', team_id=team_id))


@resource_bp.route('/<int:resource_id>/pin', methods=['POST'])
@login_required
def pin(resource_id):
    """置顶/取消置顶资源"""
    resource = Resource.query.get_or_404(resource_id)
    
    # 检查权限（只有团队领导可以置顶）
    if not current_user.is_team_leader(resource.team):
        flash('只有团队领导可以置顶资源。', 'error')
        return redirect(url_for('resource.detail', resource_id=resource_id))
    
    resource.is_pinned = not resource.is_pinned
    db.session.commit()
    
    flash(f'资源已{"置顶" if resource.is_pinned else "取消置顶"}。', 'success')
    return redirect(url_for('resource.detail', resource_id=resource_id))


@resource_bp.route('/<int:resource_id>/download')
@login_required
def download(resource_id):
    """下载资源文件"""
    resource = Resource.query.get_or_404(resource_id)
    
    # 检查权限
    if not resource.team.has_member(current_user) and not current_user.is_admin:
        flash('您没有权限下载此资源。', 'error')
        return redirect(url_for('team.list_teams'))
    
    if not resource.file_path:
        flash('该资源没有附件。', 'error')
        return redirect(url_for('resource.detail', resource_id=resource_id))
    
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resource.file_path)
    if not os.path.exists(file_path):
        flash('文件不存在。', 'error')
        return redirect(url_for('resource.detail', resource_id=resource_id))
    
    return send_file(file_path, as_attachment=True)
