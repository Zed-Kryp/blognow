from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from models import db, User, Blog, Comment, Like
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
import re
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Handle Render's PostgreSQL URL format
database_url = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    logger.info("Using PostgreSQL database")
else:
    logger.info("Using SQLite database")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')

db.init_app(app)

def init_db():
    try:
        with app.app_context():
            # Test database connection
            db.engine.connect()
            logger.info("Successfully connected to database")
            
            # Drop all tables if using PostgreSQL
            if database_url.startswith('postgresql://'):
                logger.info("Dropping all tables for PostgreSQL database")
                db.drop_all()
            
            # Create tables
            db.create_all()
            logger.info("Database tables created")
            
            # Add sample users if none exist
            if not User.query.first():
                users = [
                    User(
                        username='John Doe',
                        email='john@example.com',
                        role='author',
                        bio='Tech enthusiast and writer'
                    ),
                    User(
                        username='Jane Smith',
                        email='jane@example.com',
                        role='moderator',
                        bio='Community moderator'
                    ),
                    User(
                        username='Admin User',
                        email='admin@example.com',
                        role='admin',
                        bio='System administrator'
                    )
                ]
                
                # Set default passwords for sample users
                for user in users:
                    user.set_password('password123')
                
                db.session.add_all(users)
                db.session.commit()
                logger.info("Sample users added to database")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

# Initialize database
init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/signup.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('auth/signup.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Successfully logged out.', 'success')
    return redirect(url_for('home'))

@app.route('/')
def home():
    try:
        sort_by = request.args.get('sort', 'latest')
        blogs = Blog.query.filter_by(published=True)
        
        if sort_by == 'latest':
            blogs = blogs.order_by(Blog.created_at.desc())
        elif sort_by == 'most_liked':
            blogs = blogs.order_by(Blog.likes.desc())
        
        return render_template('home.html', blogs=blogs.all())
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return render_template('error.html', error="An error occurred while loading the home page"), 500

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog.html', blog=blog)

@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
def create_blog():
    if request.method == 'POST':
        blog = Blog(
            title=request.form['title'],
            content=request.form['content'],
            tags=request.form['tags'],
            author_id=session['user_id'],
            published=request.form.get('publish') == 'true'
        )
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('blog_detail', blog_id=blog.id))
    
    return render_template('editor.html')

@app.route('/blog/<int:blog_id>/edit', methods=['GET', 'POST'])
def edit_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if session['user_id'] not in ['moderator', 'admin'] and blog.author_id != session['user_id']:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        blog.title = request.form['title']
        blog.content = request.form['content']
        blog.tags = request.form['tags']
        blog.published = request.form.get('publish') == 'true'
        db.session.commit()
        return redirect(url_for('blog_detail', blog_id=blog.id))
    
    return render_template('editor.html', blog=blog)

@app.route('/blog/<int:blog_id>/like', methods=['POST'])
@login_required
def like_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    existing_like = Like.query.filter_by(user_id=session['user_id'], blog_id=blog_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'liked': False, 'count': len(blog.likes) - 1})
    
    like = Like(user_id=session['user_id'], blog_id=blog_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({'liked': True, 'count': len(blog.likes)})

@app.route('/blog/<int:blog_id>/comment', methods=['POST'])
@login_required
def add_comment(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    comment = Comment(
        content=request.form['content'],
        author_id=session['user_id'],
        blog_id=blog_id
    )
    db.session.add(comment)
    db.session.commit()
    
    return redirect(url_for('blog_detail', blog_id=blog_id))

@app.route('/profile/<username>')
def profile(username):
    try:
        user = User.query.filter_by(username=username).first_or_404()
        return render_template('profile.html', user=user)
    except Exception as e:
        logger.error(f"Error in profile route: {str(e)}")
        return render_template('error.html', error="An error occurred while loading the profile"), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error.html', error="Internal server error"), 500

@app.context_processor
def inject_user():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return {'current_user': user}
    return {'current_user': None}

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or User.query.get(session['user_id']).role != 'admin':
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_blogs': Blog.query.count(),
        'total_comments': Comment.query.count(),
        'total_likes': Like.query.count()
    }
    
    users = User.query.order_by(User.created_at.desc()).all()
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         users=users,
                         blogs=blogs,
                         comments=comments)

@app.route('/admin/user/<int:user_id>/update-role', methods=['POST'])
@login_required
@admin_required
def admin_update_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role in ['user', 'author', 'moderator', 'admin']:
        user.role = new_role
        db.session.commit()
        flash(f'User role updated to {new_role}', 'success')
    else:
        flash('Invalid role selected', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == session.get('user_id'):
        return jsonify({'success': False, 'error': 'Cannot delete your own account'})
    
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/blog/<int:blog_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_blog_status(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    
    try:
        blog.published = not blog.published
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/blog/<int:blog_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    
    try:
        db.session.delete(blog)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/comment/<int:comment_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def admin_toggle_comment_status(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        comment.approved = not comment.approved
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    try:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 