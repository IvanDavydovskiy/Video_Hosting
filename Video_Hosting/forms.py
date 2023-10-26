from flask_wtf import RecaptchaField
from flask_wtf.form import FlaskForm
from wtforms import EmailField, StringField, PasswordField, SubmitField, TextAreaField, FileField, SearchField
from wtforms.validators import Length, Email, EqualTo, DataRequired
from flask_wtf.file import file_allowed


class RegistrationForm(FlaskForm):
    username = StringField('username',
                           validators=[Length(min=5, max=50)])
    password = PasswordField('password',
                             validators=[Length(min=8, max=100),
                                         EqualTo('password_confirmation',
                                         message='Passwords must match')])
    password_confirmation = PasswordField('password confirmation',
                                          validators=[Length(min=8, max=100)])
    email = EmailField('email',
                       validators=[Email(),
                                   DataRequired()])
    captcha = RecaptchaField()
    submit = SubmitField('sing-up')


class AuthenticationForm(FlaskForm):
    username = StringField('username',
                           validators=[Length(min=5, max=50)])
    password = PasswordField('password',
                             validators=[Length(min=8, max=100)])
    submit = SubmitField('sing-in')


class VideoForm(FlaskForm):
    title = StringField('title',
                        validators=[Length(min=1, max=200)])
    description = TextAreaField('description')
    preview = FileField('preview',
                        validators=[file_allowed(['png', 'jpg', 'jpeg'])])
    video = FileField('video',
                      validators=[file_allowed(['mp4'])])
    submit = SubmitField('upload')


class CommentForm(FlaskForm):
    comment_text = TextAreaField('comment',
                                 validators=[DataRequired()])
    submit = SubmitField('post')


class SearchForm(FlaskForm):
    search_bar = SearchField('Search bar')
    submit = SubmitField('search')


class ResponseForm(FlaskForm):
    response_text = TextAreaField('response',
                                  validators=[DataRequired()])
    submit = SubmitField('send')


class SubscriptionForm(FlaskForm):
    submit = SubmitField('subscribe')
