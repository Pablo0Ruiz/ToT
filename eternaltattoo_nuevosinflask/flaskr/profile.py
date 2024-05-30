import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, current_app, url_for, abort
)
from flask import Flask
from flaskr.auth import login_required
from flaskr.db import get_db
from werkzeug.security import generate_password_hash
from flaskr.followers import get_users_followers

bp = Blueprint('profile', __name__, url_prefix='/profile')

# Define get_user_posts function
def get_user_posts(user_id):
    db = get_db()
    posts = db.execute(
        "SELECT p.id, p.title, p.body, p.created, pi.filename AS image_filename "
        "FROM post p "
        "JOIN user u ON p.author_id = u.id "
        "LEFT JOIN post_image pi ON p.id = pi.post_id "
        "WHERE p.author_id = ? "
        "ORDER BY p.created DESC",
        (user_id,)
    ).fetchall()

    return posts

@bp.route('/view/<int:user_id>', methods=['GET'])
def view_profile(user_id):
    db = get_db()
    user = db.execute(
        "SELECT id, username FROM user WHERE id = ?",
        (user_id,)
    ).fetchone()
    if user is None:
        abort(404, f"User id {user_id} doesn't exist.")

    user_posts = get_user_posts(user_id)
    img = get_profile_picture(user_id)
    followers = get_users_followers(user_id)
    try:
        if user_id == g.user['id']:
            return render_template('profile/profile.html', img=img, error=None, username=g.user['username'], user_posts=user_posts, followers=followers)
    except TypeError:
        return render_template('profile/view_profile.html', user=user, img=img, user_posts=user_posts, followers=followers)
    return render_template('profile/view_profile.html', user=user, img=img, user_posts=user_posts, followers=followers)

@bp.route('/account', methods=('GET', 'POST'))
@login_required
def account():
    error = None
    user_posts = get_user_posts(g.user['id'])  # Fetch user's posts
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:
            db = get_db()
            try:
                db.execute(
                    "UPDATE user SET username = ?, password = ? WHERE id = ?",
                    (username, generate_password_hash(password), g.user['id'])
                )
                db.commit()

                return redirect(url_for("profile.account"))
            except db.IntegrityError:
                error = f"Username {username} is already taken."
    followers = get_users_followers(g.user['id'])
    img = get_profile_picture(g.user['id'])#renderiza la foto de perfil,  pone la imagen por defecto si no existe
    return render_template('profile/profile.html', img=img, error=error, username=g.user['username'], user_posts=user_posts, followers=followers)



@bp.route('/update', methods=('GET', 'POST'))
@login_required
def update_profile():#actualizar el perfil 
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        profile_pic = request.files['profile_pic']  # Esto toma la imagen que se sube desde el html desde los forms
        #no me preguntes como funcionan los forms que tampoco se, solo se que alli esta la imgen que se sube
        
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "UPDATE user SET username = ?, password = ? WHERE id = ?",
                    (username, generate_password_hash(password), g.user['id'])
                )
                db.commit()
                
                # Se guarda en static
                if profile_pic:
                    save_profile_picture(profile_pic)  # Se guarda la foto de perfil en static, si ya hay una la reemplaza por los momentos
                

                return redirect(url_for("profile.account"))
            except db.IntegrityError:
                error = f"Username {username} is already taken."

        flash(error)

    elif request.method == 'GET':
        username = g.user['username']

    return render_template('profile/account.html')

# Define update_profile_picture function
def save_profile_picture(image):
    picture_fn = f"profile_img_{g.user['id']}.jpg"
    pic_path = os.path.join(current_app.root_path, 'static', picture_fn)
    image.save(pic_path)
    return picture_fn


def get_profile_picture(user_id):
    with current_app.app_context():
        filename = f"profile_img_{user_id}.jpg"
        static_folder = os.path.join(current_app.root_path, 'static')
        profile_picture_path = os.path.join(static_folder, filename)
        
        if os.path.exists(profile_picture_path):
            return filename
        else:
            return 'profile_def.png'