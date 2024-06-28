from . import db
from flask_login import UserMixin
from datetime import datetime
import re


pattern = "[^\w+]"

def slugify(title):
    return re.sub(pattern, "-", title)

class User(db.Model, UserMixin):
    username = db.Column(db.String(50), primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.String(150), default="")
    profile = db.Column(db.Text, default="profiles/default_profile.png")
    socials = db.Column(db.JSON, default={"instagram" : "", "facebook" : "", "linkedIn" : "", "twitter" : "", "youtube" : ""})
    joined = db.Column(db.Date, default=datetime.now())

    def get_id(self):
        return self.username


Posts_Tags = db.Table("posts_tags",
                      db.Column("pid", db.Integer, db.ForeignKey("post.pid")),
                      db.Column("tid", db.Integer, db.ForeignKey("tag.tid"))
)


class Post(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    sample_content = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    header_image = db.Column(db.Text)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    author_id = db.Column(db.String(50), db.ForeignKey("user.username"))
    created = db.Column(db.DateTime, default=datetime.now())
    views = db.Column(db.Integer, default=0)
    tags = db.relationship("Tag", secondary=Posts_Tags, backref=db.backref("posts"), lazy="dynamic")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        slugs = [row[0] for row in db.session.query(Post.slug).all()]
        slug = slugify(self.title)
        i = 1
        while slug in slugs:
            slug = slugify(self.title + str(i))
            i += 1
        self.slug = slug


class Tag(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer, unique=True)
    created = db.Column(db.Date, default=datetime.now())

