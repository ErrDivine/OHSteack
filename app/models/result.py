from datetime import datetime
from app import db


class Result(db.Model):
    """成果模型（堆）- 团队产生的成果"""
    __tablename__ = 'results'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # Markdown格式的详细内容
    
    result_type = db.Column(db.String(50), default='document')  # document, code, design, model, dataset
    status = db.Column(db.String(20), default='draft')  # draft, in_progress, review, final
    
    # 版本信息
    version = db.Column(db.String(20), default='1.0')
    current_iteration_id = db.Column(db.Integer)  # 当前迭代版本ID
    
    # 附件和链接
    attachments = db.Column(db.Text)  # JSON格式的附件列表
    repository_url = db.Column(db.String(500))  # 代码仓库链接
    demo_url = db.Column(db.String(500))  # 演示链接
    
    # 标签和分类
    category = db.Column(db.String(50))
    tags = db.Column(db.String(500))
    
    # 统计信息
    view_count = db.Column(db.Integer, default=0)
    star_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)  # 最终提交时间
    
    # 关系
    team = db.relationship('Team', back_populates='results')
    creator = db.relationship('User', back_populates='created_results')
    iterations = db.relationship('ResultIteration', back_populates='result', lazy='dynamic', 
                               cascade='all, delete-orphan', order_by='ResultIteration.created_at.desc()')
    
    def __repr__(self):
        return f'<Result {self.title}>'
    
    def add_iteration(self, user, changes_description, content=None):
        """添加新的迭代版本"""
        # 获取下一个版本号
        last_iteration = self.iterations.first()
        if last_iteration:
            version_parts = last_iteration.version.split('.')
            version_parts[-1] = str(int(version_parts[-1]) + 1)
            new_version = '.'.join(version_parts)
        else:
            new_version = self.version
        
        iteration = ResultIteration(
            result=self,
            creator=user,
            version=new_version,
            changes_description=changes_description,
            content=content or self.content
        )
        
        db.session.add(iteration)
        self.current_iteration_id = iteration.id
        self.version = new_version
        if content:
            self.content = content
        
        return iteration
    
    def get_current_iteration(self):
        """获取当前迭代版本"""
        if self.current_iteration_id:
            return ResultIteration.query.get(self.current_iteration_id)
        return self.iterations.first()
    
    def get_tags_list(self):
        """获取标签列表"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags(self, tags_list):
        """设置标签"""
        if tags_list:
            self.tags = ','.join([tag.strip() for tag in tags_list if tag.strip()])
        else:
            self.tags = None
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()
    
    def is_editable_by(self, user):
        """检查用户是否可以编辑"""
        if not user.is_authenticated:
            return False
        return user.is_admin or user.id == self.creator_id or user.is_team_member(self.team)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'team_id': self.team_id,
            'creator': {
                'id': self.creator.id,
                'username': self.creator.username
            },
            'title': self.title,
            'description': self.description,
            'content': self.content,
            'result_type': self.result_type,
            'status': self.status,
            'version': self.version,
            'repository_url': self.repository_url,
            'demo_url': self.demo_url,
            'category': self.category,
            'tags': self.get_tags_list(),
            'view_count': self.view_count,
            'star_count': self.star_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'iterations_count': self.iterations.count()
        }


class ResultIteration(db.Model):
    """成果迭代版本模型"""
    __tablename__ = 'result_iterations'
    
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    version = db.Column(db.String(20), nullable=False)
    changes_description = db.Column(db.Text, nullable=False)  # 变更说明
    content = db.Column(db.Text)  # 该版本的内容快照
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    result = db.relationship('Result', back_populates='iterations')
    creator = db.relationship('User', back_populates='result_iterations')
    
    def __repr__(self):
        return f'<ResultIteration {self.result.title} v{self.version}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'result_id': self.result_id,
            'creator': {
                'id': self.creator.id,
                'username': self.creator.username
            },
            'version': self.version,
            'changes_description': self.changes_description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
