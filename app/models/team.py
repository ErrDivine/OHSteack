from datetime import datetime
from app import db


class Team(db.Model):
    """团队模型"""
    __tablename__ = 'teams'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    competition_name = db.Column(db.String(200))  # 参加的竞赛名称
    competition_url = db.Column(db.String(500))   # 竞赛链接
    start_date = db.Column(db.Date)               # 项目开始日期
    end_date = db.Column(db.Date)                 # 项目结束日期
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    logo_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    members = db.relationship('TeamMember', back_populates='team', lazy='dynamic', cascade='all, delete-orphan')
    resources = db.relationship('Resource', back_populates='team', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('Result', back_populates='team', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def add_member(self, user, role='member'):
        """添加团队成员"""
        membership = self.members.filter_by(user_id=user.id).first()

        if membership:
            if membership.is_active:
                return False

            membership.is_active = True
            membership.role = role
            membership.joined_at = datetime.utcnow()
            return True

        member = TeamMember(team=self, user=user, role=role)
        db.session.add(member)
        return True
    
    def remove_member(self, user):
        """移除团队成员"""
        member = self.members.filter_by(user_id=user.id).first()
        if member:
            member.is_active = False
            return True
        return False
    
    def has_member(self, user):
        """检查用户是否是团队成员"""
        return self.members.filter_by(user_id=user.id, is_active=True).first() is not None
    
    def get_leader(self):
        """获取团队领导"""
        leader_membership = self.members.filter_by(role='leader', is_active=True).first()
        return leader_membership.user if leader_membership else None
    
    def get_active_members(self):
        """获取所有活跃成员"""
        return [m.user for m in self.members.filter_by(is_active=True).all()]
    
    def get_statistics(self):
        """获取团队统计信息"""
        return {
            'member_count': self.members.filter_by(is_active=True).count(),
            'resource_count': self.resources.count(),
            'result_count': self.results.count(),
            'active_days': (datetime.utcnow() - self.created_at).days if self.created_at else 0
        }
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'competition_name': self.competition_name,
            'competition_url': self.competition_url,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'logo_url': self.logo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'statistics': self.get_statistics()
        }


class TeamMember(db.Model):
    """团队成员关系模型"""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(20), default='member')  # leader, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关系
    team = db.relationship('Team', back_populates='members')
    user = db.relationship('User', back_populates='team_memberships')
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('team_id', 'user_id', name='_team_user_uc'),
    )
    
    def __repr__(self):
        return f'<TeamMember {self.user.username} in {self.team.name}>'
