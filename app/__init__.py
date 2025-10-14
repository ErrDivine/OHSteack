from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from config import config

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()


def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    
    # 配置登录管理器
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面。'
    login_manager.login_message_category = 'info'
    
    # 创建上传文件夹
    import os
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # 注册蓝图
    from app.views.main import main_bp
    from app.views.auth import auth_bp
    from app.views.team import team_bp
    from app.views.resource import resource_bp
    from app.views.result import result_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(team_bp, url_prefix='/team')
    app.register_blueprint(resource_bp, url_prefix='/resource')
    app.register_blueprint(result_bp, url_prefix='/result')
    
    # 注册模板过滤器
    from app.utils.filters import register_filters
    register_filters(app)
    
    # 注册错误处理器
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)
    
    # 配置用户加载函数
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))
    
    return app
