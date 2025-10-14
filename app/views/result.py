import os
import json
import markdown2
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Team, Result, ResultIteration
from app.forms.result import ResultForm, IterationForm

result_bp = Blueprint('result', __name__)


@result_bp.route('/team/<int:team_id>')
@login_required
def list_results(team_id):
    """团队成果列表"""
    team = Team.query.get_or_404(team_id)
    
    # 检查权限
    if not team.has_member(current_user) and not current_user.is_admin:
        flash('您没有权限查看此团队的成果。', 'error')
        return redirect(url_for('team.list_teams'))
    
    # 获取查询参数
    status = request.args.get('status')
    category = request.args.get('category')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    
    # 构建查询
    query = team.results
    
    if status:
        query = query.filter_by(status=status)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(
            db.or_(
                Result.title.contains(search),
                Result.description.contains(search),
                Result.tags.contains(search)
            )
        )
    
    # 排序：按更新时间降序
    query = query.order_by(Result.updated_at.desc())
    
    # 分页
    pagination = query.paginate(
        page=page,
        per_page=current_app.config['ITEMS_PER_PAGE'],
        error_out=False
    )
    
    results = pagination.items
    
    # 获取所有分类和状态
    categories = db.session.query(Result.category).filter(
        Result.team_id == team_id,
        Result.category.isnot(None)
    ).distinct().all()
    categories = [c[0] for c in categories]
    
    statuses = ['draft', 'in_progress', 'review', 'final']
    
    return render_template('result/list.html',
                         team=team,
                         results=results,
                         pagination=pagination,
                         categories=categories,
                         statuses=statuses,
                         current_status=status,
                         current_category=category,
                         search_query=search)


@result_bp.route('/create/<int:team_id>', methods=['GET', 'POST'])
@login_required
def create(team_id):
    """创建成果"""
    team = Team.query.get_or_404(team_id)
    
    # 检查权限
    if not team.has_member(current_user):
        flash('您必须是团队成员才能创建成果。', 'error')
        return redirect(url_for('team.detail', team_id=team_id))
    
    form = ResultForm()
    
    if form.validate_on_submit():
        result = Result(
            team=team,
            creator=current_user,
            title=form.title.data,
            description=form.description.data,
            content=form.content.data,
            result_type=form.result_type.data,
            status=form.status.data,
            version='1.0',
            repository_url=form.repository_url.data,
            demo_url=form.demo_url.data,
            category=form.category.data
        )
        
        # 处理标签
        if form.tags.data:
            result.set_tags(form.tags.data.split(','))
        
        # 处理附件上传
        attachments = []
        if form.attachments.data:
            team_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f'team_{team_id}', 'results')
            if not os.path.exists(team_folder):
                os.makedirs(team_folder)
            
            for file in form.attachments.data:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    file_path = os.path.join(team_folder, filename)
                    file.save(file_path)
                    
                    attachments.append({
                        'filename': file.filename,
                        'path': os.path.relpath(file_path, current_app.config['UPLOAD_FOLDER']),
                        'size': os.path.getsize(file_path)
                    })
        
        if attachments:
            result.attachments = json.dumps(attachments)
        
        db.session.add(result)
        db.session.flush()
        
        # 创建初始迭代
        initial_iteration = ResultIteration(
            result=result,
            creator=current_user,
            version='1.0',
            changes_description='初始版本',
            content=result.content
        )
        db.session.add(initial_iteration)
        db.session.flush()
        
        result.current_iteration_id = initial_iteration.id
        
        db.session.commit()
        
        flash('成果创建成功！', 'success')
        return redirect(url_for('result.detail', result_id=result.id))
    
    return render_template('result/create.html', form=form, team=team)


@result_bp.route('/<int:result_id>')
@login_required
def detail(result_id):
    """成果详情"""
    result = Result.query.get_or_404(result_id)
    
    # 检查权限
    if not result.team.has_member(current_user) and not current_user.is_admin:
        flash('您没有权限查看此成果。', 'error')
        return redirect(url_for('team.list_teams'))
    
    # 增加浏览次数
    result.increment_view_count()
    
    # 渲染Markdown内容
    if result.content:
        result.rendered_content = markdown2.markdown(
            result.content,
            extras=['fenced-code-blocks', 'tables', 'strike', 'toc']
        )
    
    # 获取迭代历史
    iterations = result.iterations.all()
    
    # 解析附件
    attachments = []
    if result.attachments:
        try:
            attachments = json.loads(result.attachments)
        except:
            pass
    
    return render_template('result/detail.html', 
                         result=result,
                         iterations=iterations,
                         attachments=attachments,
                         can_edit=result.is_editable_by(current_user))


@result_bp.route('/<int:result_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(result_id):
    """编辑成果"""
    result = Result.query.get_or_404(result_id)
    
    # 检查权限
    if not result.is_editable_by(current_user):
        flash('您没有权限编辑此成果。', 'error')
        return redirect(url_for('result.detail', result_id=result_id))
    
    form = ResultForm(obj=result)
    
    # 设置标签
    if request.method == 'GET' and result.tags:
        form.tags.data = result.tags
    
    if form.validate_on_submit():
        # 记录是否有内容变更
        content_changed = result.content != form.content.data
        
        result.title = form.title.data
        result.description = form.description.data
        result.content = form.content.data
        result.result_type = form.result_type.data
        result.status = form.status.data
        result.repository_url = form.repository_url.data
        result.demo_url = form.demo_url.data
        result.category = form.category.data
        
        # 处理标签
        if form.tags.data:
            result.set_tags(form.tags.data.split(','))
        
        # 如果内容有变更，创建新的迭代
        if content_changed and form.changes_description.data:
            result.add_iteration(
                current_user,
                form.changes_description.data,
                form.content.data
            )
        
        db.session.commit()
        
        flash('成果更新成功！', 'success')
        return redirect(url_for('result.detail', result_id=result_id))
    
    return render_template('result/edit.html', form=form, result=result)


@result_bp.route('/<int:result_id>/iteration', methods=['GET', 'POST'])
@login_required
def create_iteration(result_id):
    """创建新的迭代版本"""
    result = Result.query.get_or_404(result_id)
    
    # 检查权限
    if not result.is_editable_by(current_user):
        flash('您没有权限创建新的迭代版本。', 'error')
        return redirect(url_for('result.detail', result_id=result_id))
    
    form = IterationForm()
    
    # 预填充当前内容
    if request.method == 'GET':
        form.content.data = result.content
    
    if form.validate_on_submit():
        iteration = result.add_iteration(
            current_user,
            form.changes_description.data,
            form.content.data
        )
        
        db.session.commit()
        
        flash(f'新版本 {iteration.version} 创建成功！', 'success')
        return redirect(url_for('result.detail', result_id=result_id))
    
    return render_template('result/create_iteration.html', form=form, result=result)


@result_bp.route('/<int:result_id>/iteration/<int:iteration_id>')
@login_required
def view_iteration(result_id, iteration_id):
    """查看特定迭代版本"""
    result = Result.query.get_or_404(result_id)
    iteration = ResultIteration.query.get_or_404(iteration_id)
    
    # 检查权限
    if not result.team.has_member(current_user) and not current_user.is_admin:
        flash('您没有权限查看此迭代版本。', 'error')
        return redirect(url_for('team.list_teams'))
    
    # 检查迭代是否属于该成果
    if iteration.result_id != result_id:
        flash('迭代版本不存在。', 'error')
        return redirect(url_for('result.detail', result_id=result_id))
    
    # 渲染Markdown内容
    if iteration.content:
        iteration.rendered_content = markdown2.markdown(
            iteration.content,
            extras=['fenced-code-blocks', 'tables', 'strike', 'toc']
        )
    
    return render_template('result/iteration_detail.html', 
                         result=result,
                         iteration=iteration)


@result_bp.route('/<int:result_id>/delete', methods=['POST'])
@login_required
def delete(result_id):
    """删除成果"""
    result = Result.query.get_or_404(result_id)
    team_id = result.team_id
    
    # 检查权限（只有创建者和团队领导可以删除）
    if not (current_user.id == result.creator_id or current_user.is_team_leader(result.team)):
        flash('您没有权限删除此成果。', 'error')
        return redirect(url_for('result.detail', result_id=result_id))
    
    # 删除附件
    if result.attachments:
        try:
            attachments = json.loads(result.attachments)
            for attachment in attachments:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], attachment['path'])
                if os.path.exists(file_path):
                    os.remove(file_path)
        except:
            pass
    
    db.session.delete(result)
    db.session.commit()
    
    flash('成果已删除。', 'info')
    return redirect(url_for('result.list_results', team_id=team_id))


@result_bp.route('/<int:result_id>/submit', methods=['POST'])
@login_required
def submit(result_id):
    """提交成果为最终版本"""
    result = Result.query.get_or_404(result_id)
    
    # 检查权限
    if not current_user.is_team_leader(result.team):
        flash('只有团队领导可以提交最终版本。', 'error')
        return redirect(url_for('result.detail', result_id=result_id))
    
    result.status = 'final'
    result.submitted_at = datetime.utcnow()
    
    db.session.commit()
    
    flash('成果已提交为最终版本！', 'success')
    return redirect(url_for('result.detail', result_id=result_id))


def allowed_file(filename):
    """检查文件是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
