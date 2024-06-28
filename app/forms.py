from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField


class AddBlogForm(FlaskForm):
    title = StringField("Blog Title", validators=[DataRequired()])
    content = CKEditorField("Content of Blog", validators=[DataRequired()])
    sample = TextAreaField("Sample Content", validators=[DataRequired()])
    tags = StringField("Selected Tags")
    submit = SubmitField("Post")

