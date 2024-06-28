from flask import Blueprint, render_template, redirect, request, flash, url_for, jsonify
from flask_login import current_user, login_required
from .models import Post, User, Tag
from . import db
import os


views = Blueprint("views", __name__)

@views.route("/")
def home():
    query = request.args.get("query", "")
    posts = Post.query.filter(Post.title.contains(query) | Post.sample_content.contains(query) | Post.content.contains(query)).order_by(Post.views.desc())
    page = request.args.get("page", 1, type=int)
    pages = posts.paginate(page=page, per_page=3, error_out=False)

    if not pages.items:
        flash("Page does not exists !")
        return redirect(url_for("views.home", page=pages.pages))
    return render_template("index.html", pages=pages, User=User, query=query)


@views.route("/blog/<slug>")
def view_blog(slug):
    post = Post.query.filter_by(slug=slug).first()
    if not post:
        flash("No post exists with this URL !", category="error")
        return redirect("/")
    post.views += 1
    db.session.commit()
    author = User.query.filter_by(username = post.author_id).first()
    return render_template("blog.html", post=post, Post=Post, author=author)


@views.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == "POST":
        profile_pic = request.files.get("profile_pic")
        ext = profile_pic.filename.split(".")[-1]
        path = rf"profiles/{current_user.username}.{ext}"
        print(path)
        profile_pic.save(os.path.join(r"app/static/", path))
        # app\static\profiles\default_profile.png
        current_user.profile = path
        db.session.commit()
        flash("Profile Picture Updated !", category="success")
        return redirect(url_for("views.profile"))
    return render_template("profile.html")


@views.route("/profile/remove", methods=['GET', 'POST'])
@login_required
def profile_remove():
    if current_user.profile == "profiles/default_profile.png":
        return redirect(url_for("views.profile"))
    path = current_user.profile
    current_user.profile = "profiles/default_profile.png"
    os.remove(rf"app/static/{path}")
    db.session.commit()
    flash("Profile Picture Removed !", category="success")
    return redirect(url_for("views.profile"))


@views.route("/tag/<name>")
def group_by_tag(name):
    tag = Tag.query.filter_by(name=name).first()
    if not tag:
        flash("This tag does not exists !")
        return redirect("/")
    return render_template("posts_with_tag.html", tag=tag, User=User)


@views.route("/user/@<username>")
def user_profile(username):
    author = User.query.filter_by(username=username).first()
    if not author:
        flash("This user does not exists !", category="error")
        return redirect("/")
    posts = Post.query.filter_by(author_id=author.username).order_by(Post.created.desc()).all()
    print(posts)
    return render_template("user_blogs.html", author=author, posts=posts)


@views.route("/add-blog", methods=['GET', 'POST'])
@login_required
def add_post():
    from .forms import AddBlogForm
    form = AddBlogForm()
    if form.validate_on_submit():
        title = form.title.data
        sample = form.sample.data
        content = form.content.data
        tag_ids = form.tags.data.split(",")
        post = Post(title=title, content=content, sample_content=sample, author_id=current_user.username)
        if tag_ids != [""]:
            for id in tag_ids:
                tag = Tag.query.filter_by(tid=id).first()
                post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
        flash("Your Blog has been added !", category="success")
        return redirect(url_for("views.view_blog", slug=post.slug))
    return render_template("add_blog.html", form=form)


@views.route('/developer/jsonify_data/all-tags', methods=['GET'])
def fetch_tags():
    query = request.args.get('query', '')
    tags = Tag.query.filter(Tag.name.ilike(f'%{query}%')).all()
    tags = [{'id': tag.tid, 'name': tag.name} for tag in tags]
    return jsonify(tags=tags)