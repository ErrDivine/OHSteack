from datetime import datetime
from flask_login import UserMixin
from app import db, bcrypt


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关系
    team_memberships = db.relationship('TeamMember', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    created_resources = db.relationship('Resource', back_populates='creator', lazy='dynamic')
    created_results = db.relationship('Result', back_populates='creator', lazy='dynamic')
    result_iterations = db.relationship('ResultIteration', back_populates='creator', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """验证密码"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def get_teams(self):
        """获取用户所属的所有团队"""
        return [membership.team for membership in self.team_memberships if membership.is_active]
    
    def is_team_member(self, team):
        """检查是否是团队成员"""
        membership = self.team_memberships.filter_by(team_id=team.id, is_active=True).first()
        return membership is not None
    
    def is_team_leader(self, team):
        """检查是否是团队领导"""
        membership = self.team_memberships.filter_by(team_id=team.id, is_active=True).first()
        return membership and membership.role == 'leader'
    
    def can_edit_team(self, team):
        """检查是否可以编辑团队"""
        return self.is_admin or self.is_team_leader(team)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
