from flask import Flask, render_template, request, jsonify, redirect, url_for
from models import db, User, Blog, Comment, Like
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
db.init_app(app)

# Mock current user (for development)
CURRENT_USER = {
    'id': 1,
    'username': 'John Doe',
    'role': 'author'
}

# Create database tables
with app.app_context():
    db.create_all()
    
    # Add sample users if none exist
    if not User.query.first():
        users = [
            User(username='John Doe', role='author', bio='Tech enthusiast and writer'),
            User(username='Jane Smith', role='moderator', bio='Community moderator'),
            User(username='Admin User', role='admin', bio='System administrator')
        ]
        db.session.add_all(users)
        db.session.commit()

@app.route('/')
def home():
    sort_by = request.args.get('sort', 'latest')
    blogs = Blog.query.filter_by(published=True)
    
    if sort_by == 'latest':
        blogs = blogs.order_by(Blog.created_at.desc())
    elif sort_by == 'most_liked':
        blogs = blogs.order_by(Blog.likes.desc())
    
    return render_template('home.html', blogs=blogs.all(), current_user=CURRENT_USER)

@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog.html', blog=blog, current_user=CURRENT_USER)

@app.route('/blog/new', methods=['GET', 'POST'])
def new_blog():
    if CURRENT_USER['role'] not in ['author', 'moderator', 'admin']:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        blog = Blog(
            title=request.form['title'],
            content=request.form['content'],
            tags=request.form['tags'],
            author_id=CURRENT_USER['id'],
            published=request.form.get('publish') == 'true'
        )
        db.session.add(blog)
        db.session.commit()
        return redirect(url_for('blog_detail', blog_id=blog.id))
    
    return render_template('editor.html', current_user=CURRENT_USER)

@app.route('/blog/<int:blog_id>/edit', methods=['GET', 'POST'])
def edit_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if CURRENT_USER['role'] not in ['moderator', 'admin'] and blog.author_id != CURRENT_USER['id']:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        blog.title = request.form['title']
        blog.content = request.form['content']
        blog.tags = request.form['tags']
        blog.published = request.form.get('publish') == 'true'
        db.session.commit()
        return redirect(url_for('blog_detail', blog_id=blog.id))
    
    return render_template('editor.html', blog=blog, current_user=CURRENT_USER)

@app.route('/blog/<int:blog_id>/like', methods=['POST'])
def like_blog(blog_id):
    if CURRENT_USER['role'] == 'guest':
        return jsonify({'error': 'Guests cannot like blogs'}), 403
    
    blog = Blog.query.get_or_404(blog_id)
    existing_like = Like.query.filter_by(user_id=CURRENT_USER['id'], blog_id=blog_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        return jsonify({'liked': False, 'count': len(blog.likes) - 1})
    
    like = Like(user_id=CURRENT_USER['id'], blog_id=blog_id)
    db.session.add(like)
    db.session.commit()
    return jsonify({'liked': True, 'count': len(blog.likes)})

@app.route('/blog/<int:blog_id>/comment', methods=['POST'])
def add_comment(blog_id):
    if CURRENT_USER['role'] == 'guest':
        return jsonify({'error': 'Guests cannot comment'}), 403
    
    blog = Blog.query.get_or_404(blog_id)
    comment = Comment(
        content=request.form['content'],
        author_id=CURRENT_USER['id'],
        blog_id=blog_id
    )
    db.session.add(comment)
    db.session.commit()
    
    return redirect(url_for('blog_detail', blog_id=blog_id))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user, current_user=CURRENT_USER)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 