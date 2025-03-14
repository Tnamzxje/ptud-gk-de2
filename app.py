from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret-key-random'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'task.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Cấu hình upload file
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Tạo thư mục uploads nếu chưa tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    created = db.Column(db.DateTime, default=datetime.utcnow)
    finished = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

def current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@app.route('/')
def home():
    if not current_user():
        return redirect(url_for('login'))
    
    user = current_user()
    tasks = Task.query.filter_by(user_id=user.id).all()
    categories = Category.query.all()
    
    # Count overdue tasks
    overdue_tasks = Task.query.filter(
        Task.user_id == user.id,
        Task.status != 'completed',
        Task.due_date < datetime.utcnow()
    ).count()
    
    return render_template('index.html', 
                         user=user, 
                         tasks=tasks, 
                         categories=categories,
                         overdue_count=overdue_tasks,
                         posts=[])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect(url_for('register'))
        
        # Xử lý upload avatar
        avatar_url = None
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Thêm timestamp vào tên file để tránh trùng lặp
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                avatar_url = f"/static/uploads/{filename}"
        
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            avatar_url=avatar_url
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful!")
        return redirect(url_for('login'))
    
    return render_template('register.html', user=current_user())

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('home'))
        
        flash('Invalid username or password!')
    return render_template('login.html', user=current_user())

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category_id = request.form.get('category_id')
        due_date_str = request.form.get('due_date')
        due_time_str = request.form.get('due_time')
        
        if not title or not due_date_str or not due_time_str:
            flash('Vui lòng điền đầy đủ thông tin bắt buộc!')
            return redirect(url_for('tasks'))
            
        try:
            # Kết hợp ngày và giờ
            due_datetime = datetime.strptime(f"{due_date_str} {due_time_str}", "%Y-%m-%d %H:%M")
            
            # Kiểm tra thời gian không được trong quá khứ
            if due_datetime < datetime.now():
                flash('Thời gian hạn nộp không được trong quá khứ!')
                return redirect(url_for('tasks'))
            
            new_task = Task(
                title=title,
                description=description,
                due_date=due_datetime,
                category_id=category_id if category_id else None,
                user_id=current_user().id
            )
            
            db.session.add(new_task)
            db.session.commit()
            
            flash('Công việc đã được tạo thành công!')
            return redirect(url_for('tasks'))
            
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi tạo công việc!')
            return redirect(url_for('tasks'))
    
    # Lấy danh sách công việc của user hiện tại
    user_tasks = Task.query.filter_by(user_id=current_user().id).order_by(Task.created.desc()).all()
    categories = Category.query.all()
    
    # Đếm số công việc quá hạn
    overdue_count = Task.query.filter(
        Task.user_id == current_user().id,
        Task.due_date < datetime.now(),
        Task.status != 'completed'
    ).count()
    
    return render_template('tasks.html', 
                         tasks=user_tasks, 
                         categories=categories,
                         overdue_count=overdue_count)

@app.route('/task/<int:task_id>/complete')
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user().id:
        flash('Unauthorized!')
        return redirect(url_for('tasks'))
        
    task.status = 'completed'
    task.finished = datetime.utcnow()
    db.session.commit()
    flash('Task marked as complete!')
    return redirect(url_for('tasks'))

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if not current_user() or not current_user().is_admin:
        flash('Admin access required!')
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        name = request.form['name']
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('Category added successfully!')
        
    categories = Category.query.all()
    return render_template('categories.html', categories=categories, user=current_user())

@app.route('/admin')
def admin():
    if not current_user() or not current_user().is_admin:
        flash('Admin access required!')
        return redirect(url_for('home'))
    
    users = User.query.all()
    categories = Category.query.all()
    total_tasks = Task.query.count()
    current_user_obj = current_user()  # Lấy user hiện tại
    
    return render_template('admin.html', 
                         users=users, 
                         categories=categories, 
                         total_tasks=total_tasks,
                         user=current_user_obj,
                         current_user=current_user_obj)  # Truyền cả user và current_user

@app.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    if not current_user() or not current_user().is_admin:
        flash('Admin access required!')
        return redirect(url_for('home'))
    
    user_to_edit = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user_to_edit.username = request.form['username']
        user_to_edit.is_admin = 'is_admin' in request.form
        
        # Xử lý upload avatar mới
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                # Xóa avatar cũ nếu có
                if user_to_edit.avatar_url and user_to_edit.avatar_url.startswith('/static/uploads/'):
                    old_file = os.path.join(basedir, user_to_edit.avatar_url.lstrip('/'))
                    if os.path.exists(old_file):
                        os.remove(old_file)
                
                filename = secure_filename(file.filename)
                filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user_to_edit.avatar_url = f"/static/uploads/{filename}"
        
        if request.form.get('password'):
            user_to_edit.password = generate_password_hash(request.form['password'])
            
        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('admin'))
    
    return render_template('edit_user.html', 
                         user=user_to_edit,
                         current_user=current_user())

@app.route('/user/<int:user_id>/delete')
def delete_user(user_id):
    if not current_user() or not current_user().is_admin:
        flash('Admin access required!')
        return redirect(url_for('home'))
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user().id:
        flash('Cannot delete your own account!')
        return redirect(url_for('admin'))
    
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!')
    return redirect(url_for('admin'))

@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def edit_category(category_id):
    if not current_user() or not current_user().is_admin:
        flash('Admin access required!')
        return redirect(url_for('home'))
    
    category = Category.query.get_or_404(category_id)
    
    if request.method == 'POST':
        category.name = request.form['name']
        db.session.commit()
        flash('Category updated successfully!')
        return redirect(url_for('admin'))
    
    return render_template('edit_category.html', 
                         category=category,
                         user=current_user())

@app.route('/category/<int:category_id>/delete')
def delete_category(category_id):
    if not current_user() or not current_user().is_admin:
        flash('Admin access required!')
        return redirect(url_for('home'))
    
    category = Category.query.get_or_404(category_id)
    
    # Update tasks in this category to have no category
    for task in category.tasks:
        task.category_id = None
    
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('admin'),
                is_admin=True,
                avatar_url='https://avatar-placeholder.iran.liara.run/admin'
            )
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)
