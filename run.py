import os
import sys
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, Team, Resource, Result

# 加载环境变量
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# 创建应用
config_name = os.getenv('FLASK_ENV', 'default')
app = create_app(config_name)

# 创建shell上下文
@app.shell_context_processor
def make_shell_context():
    """为flask shell命令创建上下文"""
    return {
        'db': db,
        'User': User,
        'Team': Team,
        'Resource': Resource,
        'Result': Result
    }


@app.cli.command()
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库初始化完成！')


@app.cli.command()
def create_admin():
    """创建管理员账户"""
    from app.models import User
    
    email = input('请输入管理员邮箱: ')
    username = input('请输入管理员用户名: ')
    password = input('请输入管理员密码: ')
    
    if User.query.filter_by(email=email).first():
        print('该邮箱已被注册！')
        return
    
    if User.query.filter_by(username=username).first():
        print('该用户名已被使用！')
        return
    
    admin = User(
        email=email,
        username=username,
        is_admin=True
    )
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f'管理员账户 {username} 创建成功！')


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
