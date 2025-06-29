from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# 配置数据库 URI，使用 SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///competition.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用修改跟踪（提高性能）

db = SQLAlchemy(app)

# 测试数据库连接
@app.route('/')
def index():
    return "Database connected successfully!"

if __name__ == '__main__':
    app.run(debug=True)

# 定义数据库模型
class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 比赛ID
    title = db.Column(db.String(100), nullable=False)  # 比赛标题
    description = db.Column(db.String(255), nullable=True)  # 比赛描述
    status = db.Column(db.String(20), nullable=False)  # 比赛状态，'ongoing' 或 'ended'
    start_date = db.Column(db.Date, nullable=False)  # 开始日期
    end_date = db.Column(db.Date, nullable=False)  # 结束日期
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 提交记录ID
    participant_name = db.Column(db.String(100), nullable=False)  # 参赛者姓名
    hour = db.Column(db.Integer, nullable=False, default=0)  # 小时
    minute = db.Column(db.Integer, nullable=False, default=0)  # 分钟
    second = db.Column(db.Integer, nullable=False, default=0)  # 秒
    time = db.Column(db.Time, nullable=False)  # 比赛成绩
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)  # 比赛ID，外键关联
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 提交时间

    competition = db.relationship('Competition', backref=db.backref('submissions', lazy=True))

# 创建数据库
with app.app_context():
    db.create_all()
