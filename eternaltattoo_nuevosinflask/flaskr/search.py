from flask import Blueprint, request, render_template, current_app

from flaskr.db import get_db


bp = Blueprint("search", __name__, url_prefix="/search")


@bp.route("/")
def filtered_posts():
    query = request.args["q"]
    db = get_db()
    posts = db.execute(
        "SELECT p.id, p.title, p.body, p.created, p.author_id, u.username, pi.filename AS image_filename "
        " FROM post p"
        " JOIN user u ON p.author_id = u.id"
        " LEFT JOIN post_image pi ON p.id = pi.post_id "
        " WHERE p.title LIKE ?"
        " GROUP BY p.id"
        " ORDER BY p.created DESC",
        ("%" + query + "%", )
    ).fetchall()
    return render_template(
        "blog/index.html", posts=posts, search=query)
