from datetime import datetime
from app import db


class Resource(db.Model):
    """资源模型（栈）- 团队学习资源和参考资料"""
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text)
    content = db.Column(db.Text)  # Markdown格式的内容
    
    resource_type = db.Column(db.String(50), default='document')  # document, link, file, code
    url = db.Column(db.String(500))  # 外部链接
    file_path = db.Column(db.String(500))  # 上传文件的路径
    
    category = db.Column(db.String(50))  # 分类：tutorial, reference, tool, dataset等
    tags = db.Column(db.String(500))  # 逗号分隔的标签
    
    is_pinned = db.Column(db.Boolean, default=False)  # 是否置顶
    view_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    team = db.relationship('Team', back_populates='resources')
    creator = db.relationship('User', back_populates='created_resources')
    
    def __repr__(self):
        return f'<Resource {self.title}>'
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()
    
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
    
    def is_editable_by(self, user):
        """检查用户是否可以编辑此资源"""
        if not user.is_authenticated:
            return False
        return user.is_admin or user.id == self.creator_id or user.is_team_leader(self.team)
    
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
            'resource_type': self.resource_type,
            'url': self.url,
            'file_path': self.file_path,
            'category': self.category,
            'tags': self.get_tags_list(),
            'is_pinned': self.is_pinned,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
