from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.admin import admin_bp
from app.models import Admin, Feedback, NewsAnalysis
from app.database import db
from app.admin.forms import LoginForm

@admin_bp.route('/')
@login_required
def dashboard():
    """管理後台首頁"""
    # 統計資料
    total_analyses = NewsAnalysis.query.count()
    total_feedbacks = Feedback.query.count()
    recent_feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         total_analyses=total_analyses,
                         total_feedbacks=total_feedbacks,
                         recent_feedbacks=recent_feedbacks)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """管理員登入"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        print(f"嘗試登入: {form.username.data}")  # 除錯用
        admin = Admin.query.filter_by(username=form.username.data).first()
        print(f"找到管理員: {admin is not None}")  # 除錯用
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        else:
            flash('帳號或密碼錯誤', 'danger')
    
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    return redirect(url_for('admin.login'))

@admin_bp.route('/feedbacks')
@login_required
def feedbacks():
    """查看所有回饋"""
    page = request.args.get('page', 1, type=int)
    feedback_type = request.args.get('type', '')
    
    query = Feedback.query
    if feedback_type:
        query = query.filter_by(feedback_type=feedback_type)
    
    feedbacks = query.order_by(Feedback.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/feedbacks.html', feedbacks=feedbacks)

@admin_bp.route('/create-admin', methods=['GET', 'POST'])
def create_first_admin():
    """建立第一個管理員帳號（僅在沒有管理員時可用）"""
    if Admin.query.count() > 0:
        flash('管理員已存在', 'warning')
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        admin = Admin(username=username, email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        
        flash('管理員帳號建立成功！', 'success')
        return redirect(url_for('admin.login'))
    
    return render_template('admin/create_admin.html')