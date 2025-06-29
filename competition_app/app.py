from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate # 用于迁移数据库
import datetime

app = Flask(__name__)

# 配置数据库 URI，使用 SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///competition.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 禁用修改跟踪（提高性能）

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 定义数据库模型
class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 比赛ID
    title = db.Column(db.String(100), nullable=False)  # 比赛标题
    description = db.Column(db.String(255), nullable=True)  # 比赛描述
    status = db.Column(db.String(20), default="ongoing")  # 比赛状态，'ongoing' 或 'ended'
    start_date = db.Column(db.Date, nullable=False)  # 开始日期
    end_date = db.Column(db.Date, nullable=False)  # 结束日期
    score_format = db.Column(db.String(20), nullable=False, default="seconds")  # seconds/number （有的比赛提交成绩是计时（秒），有的是个数）
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # 提交记录ID
    participant_name = db.Column(db.String(100), nullable=False)  # 参赛者姓名
    score = db.Column(db.Integer, nullable=False)  # 可以存储时间（秒）或个数
    score_type = db.Column(db.String(20), nullable=False, default="seconds")  # 用来标记成绩类型 ("seconds" 或 "count")
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)  # 比赛ID，外键关联
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 提交时间

    competition = db.relationship('Competition', backref=db.backref('submissions', lazy=True))

# 创建数据库
with app.app_context():
    db.create_all()

# 首页展示
@app.route('/')
def index():
    competitions = Competition.query.all()  # 获取所有比赛
    return render_template('index.html', competitions=competitions)

# 创建比赛页面
@app.route('/create_competition', methods=['GET', 'POST'])
def create_competition():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        score_format = request.form['score_format']
        start_date_str = request.form['start_date']
        end_date_str = request.form['end_date']

        # 将字符串日期转换为 datetime.date 对象
        start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()

        new_competition = Competition(
            title=title,
            description=description,
            score_format=score_format,
            start_date=start_date,
            end_date=end_date
        )

        db.session.add(new_competition)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create_competition.html')

@app.route('/submit_score/<int:competition_id>', methods=['GET', 'POST'])
def submit_score(competition_id):
    competition = Competition.query.get_or_404(competition_id)

    if request.method == 'POST':
        participant_name = request.form['participant_name']
        score_type = competition.score_format  # 获取比赛要求的成绩格式

        # 如果成绩格式是时间，则将其转换为秒
        if score_type == 'seconds':
            hours = int(request.form['hours'])
            minutes = int(request.form['minutes'])
            seconds = int(request.form['seconds'])
            score = hours * 3600 + minutes * 60 + seconds  # 将时间转换为秒

        # 如果成绩格式是数字，则直接使用数字成绩
        elif score_type == 'count':
            score = int(request.form['number_score'])  # 直接使用数字成绩

        # 创建新的成绩提交记录
        new_submission = Submission(
            participant_name=participant_name,
            score=score,
            score_type=score_type,  # 保存成绩类型
            competition_id=competition.id
        )

        db.session.add(new_submission)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('submit_score.html', competition=competition)


if __name__ == '__main__':
    app.run(debug=True)