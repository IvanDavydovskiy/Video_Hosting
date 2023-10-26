import os


from flask import render_template, request, redirect, flash, url_for, current_app
from flask.views import MethodView, View
from flask_login import login_user, logout_user, current_user
from flask_mail import Message
from sqlalchemy.exc import IntegrityError


from User import User
from forms import RegistrationForm, AuthenticationForm, VideoForm, SearchForm, CommentForm, ResponseForm
from app import db, bcrypt, preview_uploads_dir, video_uploads_dir, cache, email, serializer
from models import Video, Comment, CommentResponse, Like, Watch, Subscription


def send_email(subject, recipients, html):
    msg = Message(
        subject=subject,
        recipients=recipients,
        html=html,
        sender=current_app.config['MAIL_USERNAME']
    )
    with current_app.app_context():
        email.send(msg)


def confirm_token(token, expiration=3600):
    _email = serializer.loads(
        token, salt=current_app.config["SECRET_KEY"], max_age=expiration
    )
    return _email


class SingUp(MethodView):
    def __init__(self):
        self.template = 'registration.html'

    def get(self):
        form = RegistrationForm()
        return render_template(self.template, form=form)

    def post(self):
        form = RegistrationForm(request.form)
        try:
            if form.validate_on_submit():
                hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                user = User(username=form.username.data,
                            password=hashed_password,
                            email=form.email.data)
                db.session.add(user)
                db.session.commit()
                token = serializer.dumps(form.email.data, salt=current_app.config["SECRET_KEY"])
                confirm_url = url_for('email_verify', token=token, _external=True)
                html = render_template('email_verify.html', confirm_url=confirm_url)
                send_email(
                      subject='Email confirmation',
                      recipients=[form.email.data],
                      html=html
                )
                return redirect(url_for('home'))
            return render_template(self.template, form=form)
        except IntegrityError:
            return redirect(url_for('sign-up'))


class VerifyEmail(MethodView):
    @staticmethod
    def get(token):
        _email = confirm_token(token)
        user = User.query.filter_by(email=_email).first_or_404()
        user.is_confirmed = True
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))


class SingIn(MethodView):
    def __init__(self):
        self.template = 'sign-in.html'

    def get(self):
        form = AuthenticationForm()
        return render_template(self.template, form=form)

    @staticmethod
    def post():
        username = request.form.get('username')
        input_password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if not user or not bcrypt.check_password_hash(user.password, input_password):
            return redirect(url_for('sign-in'))
        login_user(user)
        return redirect(url_for('home'))


class LogOut(View):
    def dispatch_request(self):
        logout_user()
        return redirect(url_for('sign-in'))


class Home(View):
    def __init__(self):
        self.template = 'home.html'

    def dispatch_request(self):
        videos = None
        user = False
        if current_user.is_authenticated and current_user.is_confirmed:
            user = User.query.filter_by(id=current_user.id).first_or_404()
            videos = Video.query.filter_by(author_id=current_user.id)
        return render_template(self.template, user=user, videos=videos)


class UploadVideo(MethodView):
    def __init__(self):
        self.template = 'upload.html'

    def get(self):
        if current_user.is_authenticated and current_user.is_confirmed:
            form = VideoForm()
            return render_template(self.template, form=form)
        return redirect(url_for('sign-in'))

    @staticmethod
    def post():
        if current_user.is_authenticated and current_user.is_confirmed:
            form = VideoForm(request.form)
            preview = request.files['preview']
            video_req = request.files['video']
            if form.validate_on_submit():
                video = Video(
                    author_id=current_user.id,
                    title=form.title.data,
                    description=form.description.data
                )
                db.session.add(video)
                db.session.commit()
                preview.save(os.path.join(preview_uploads_dir, str(video.id)+'.png'))
                video_req.save(os.path.join(video_uploads_dir, str(video.id) + '.mp4'))
                return redirect(url_for('home'))
            else:
                return redirect(url_for('upload'))
        return redirect(url_for('sign-in'))


class MainPage(MethodView):
    def __init__(self):
        self.template = 'main_page.html'
        self.form = SearchForm()

    @cache.cached(timeout=60)
    def get(self):
        videos = Video.query.all()
        return render_template(self.template, videos=videos, form=self.form)

    def post(self):
        search_input = request.form.get('search_bar')
        videos = Video.query.all()
        searched_videos = []
        for video in videos:
            if search_input in video.title:
                searched_videos.append(video)
        return render_template(self.template, searched_videos=searched_videos, form=self.form)


class VideoPage(MethodView):
    def __init__(self):
        self.template = 'video.html'

    @cache.cached(timeout=60)
    def get(self, video_id):
        comment_form = CommentForm()
        video = Video.query.filter_by(id=video_id).first_or_404()
        author = User.query.filter_by(id=video.author_id).first_or_404()
        comments, comments_id, responses = [], [], []
        for comment in Comment.query.all():
            if comment.video_id == video_id:
                comments.append(comment)
                comments_id.append(comment.id)
        for response in CommentResponse.query.all():
            if response.video_id == video_id and response.comment_id in comments_id:
                responses.append(response)
        like_count = 0
        for like in Like.query.all():
            if like.video_id == video_id:
                like_count += 1
        already_viewed = []
        views_count = 0
        for _view in Watch.query.all():
            if _view.user_id == current_user.id and _view.video_id == video_id:
                already_viewed.append(_view)
            if _view.video_id == video_id:
                views_count += 1
        if not already_viewed:
            view = Watch(
                video_id=video_id,
                user_id=current_user.id
            )
            db.session.add(view)
            db.session.commit()
        return render_template(self.template,
                               video=video,
                               author=author,
                               comment_form=comment_form,
                               comments=comments,
                               responses=responses,
                               like_count=like_count,
                               views_count=views_count)

    @staticmethod
    def post(video_id):
        if current_user.is_authenticated and current_user.is_confirmed:
            comment_content = request.form.get('comment_text')
            comment = Comment(
                video_id=video_id,
                author_name=current_user.username,
                comment=comment_content
            )
            db.session.add(comment)
            db.session.commit()
            return redirect(f'/show_video/{video_id}')
        else:
            flash('You must be a registered user to post comments!')
            return redirect(url_for('sign-in'))


class DeleteVideo(MethodView):
    @staticmethod
    def get(video_id):
        video_to_delete = Video.query.filter_by(id=video_id).first_or_404()
        if current_user.is_authenticated and current_user.is_confirmed and video_to_delete.author_id == current_user.id:
            db.session.delete(video_to_delete)
            db.session.commit()
            os.remove(video_uploads_dir + f'/{video_id}.mp4')
            os.remove(preview_uploads_dir + f'/{video_id}.png')
            return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))


class RespondToComment(MethodView):
    @staticmethod
    def get(comment_id, video_id):
        comment = Comment.query.filter_by(id=comment_id).first_or_404()
        form = ResponseForm()
        return render_template('response.html',
                               comment=comment,
                               form=form)

    @staticmethod
    def post(comment_id, video_id):
        response = CommentResponse(
            comment_id=comment_id,
            responder_name=current_user.username,
            response=request.form.get('response_text'),
            video_id=video_id
        )
        db.session.add(response)
        db.session.commit()
        return redirect(url_for('video', video_id=video_id))


class LikeView(MethodView):
    @staticmethod
    def get(video_id):
        like_exists = []
        for _like in Like.query.all():
            if _like.user_id == current_user.id and _like.video_id == video_id:
                like_exists.append(_like)
        if not like_exists:
            like = Like(
                user_id=current_user.id,
                video_id=video_id
            )
            db.session.add(like)
            db.session.commit()
            return redirect(url_for('video', video_id=video_id))
        else:
            return redirect(url_for('video', video_id=video_id))


class Profile(MethodView):
    @staticmethod
    def get(user_id):
        user = User.query.filter_by(id=user_id).first()
        if user:
            subscribers = Subscription.query.filter_by(subscribed_to=user_id).count()
            videos = Video.query.filter_by(author_id=user_id)
            total_views = 0
            total_likes = 0
            for video in videos:
                total_views += Watch.query.filter_by(video_id=video.id).count()
                total_likes += Like.query.filter_by(video_id=video.id).count()
            return render_template('profile.html', user=user, videos=videos,
                                   subscribers=subscribers, total_views=total_views,
                                   total_likes=total_likes)
        else:
            return redirect(url_for('home'))


class Subscribe(MethodView):
    @staticmethod
    def get(user_id):
        if current_user.is_authenticated and current_user.is_confirmed:
            already_subscribed = []
            for sub in Subscription.query.filter_by(subscribed_to=user_id):
                if sub.user_id == current_user.id:
                    already_subscribed.append(sub)
            if not already_subscribed:
                subscription = Subscription(
                    subscribed_to=user_id,
                    user_id=current_user.id
                )
                db.session.add(subscription)
                db.session.commit()
            return redirect(url_for('profile', user_id=user_id))
        else:
            return redirect(url_for('sign-in'))


class MySubscriptions(MethodView):
    @staticmethod
    def get():
        if current_user.is_authenticated and current_user.is_confirmed:
            author_id = []
            for sub in Subscription.query.filter_by(user_id=current_user.id):
                author_id.append(sub.subscribed_to)
            authors = []
            for user in User.query.all():
                if user.id in author_id:
                    authors.append(user)
            return render_template('my_subscriptions.html', authors=authors)
        else:
            return redirect(url_for('sign-in'))
