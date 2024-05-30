from sqlite3 import IntegrityError

from flask import Blueprint, request, redirect, url_for, g
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("followers", __name__, url_prefix="/followers")

def get_users_followers(user_id):
    db = get_db()

    followers = db.execute(
        "SELECT follower_user_id, followed_user_id FROM follower WHERE followed_user_id = ?",
        (user_id,)
    ).fetchall()
    follower_id = [follower["follower_user_id"] for follower in followers]
    return follower_id

@bp.route("/follow", methods=("POST",))
@login_required
def follow():
    profile_id=request.form["profile_id"]
    user_id = g.user["id"]

    db = get_db()
    try:
        db.execute(
            "INSERT INTO follower (follower_user_id, followed_user_id) "
            " VALUES (?, ?)",
            (user_id, profile_id)
        )
        db.commit()
    except IntegrityError:
        abort(403, "Already following.")

    return redirect(url_for("profile.view_profile", user_id=profile_id))

@bp.route("/unfollow", methods=("POST",))
@login_required
def unfollow():
    profile_id = request.form["profile_id"]
    user_id = g.user["id"]

    db = get_db()
    db.execute(
        "DELETE FROM follower WHERE follower_user_id = ? AND followed_user_id = ?",
        (user_id, profile_id)
    )
    db.commit()

    return redirect(url_for("profile.view_profile", user_id=profile_id))