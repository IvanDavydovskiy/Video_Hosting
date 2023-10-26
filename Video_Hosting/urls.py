from app import app
from views import (SingUp, SingIn, LogOut,
                   Home, UploadVideo, MainPage,
                   VideoPage, DeleteVideo, RespondToComment,
                   VerifyEmail, LikeView, Profile,
                   Subscribe, MySubscriptions)


def add_urls():
    app.add_url_rule('/sing-up', view_func=SingUp.as_view('sign-up'))
    app.add_url_rule('/sing-in', view_func=SingIn.as_view('sign-in'))
    app.add_url_rule('/logout', view_func=LogOut.as_view('logout'))
    app.add_url_rule('/upload', view_func=UploadVideo.as_view('upload'))
    app.add_url_rule('/', view_func=Home.as_view('home'))
    app.add_url_rule('/main', view_func=MainPage.as_view('main'))
    app.add_url_rule('/show_video/<int:video_id>', view_func=VideoPage.as_view('video'))
    app.add_url_rule('/delete_video/<int:video_id>', view_func=DeleteVideo.as_view('delete_video'))
    app.add_url_rule('/respond/<int:comment_id>/<int:video_id>', view_func=RespondToComment.as_view('respond'))
    app.add_url_rule('/verify_email/<string:token>', view_func=VerifyEmail.as_view('email_verify'))
    app.add_url_rule('/like/<int:video_id>', view_func=LikeView.as_view('like'))
    app.add_url_rule('/profile/<int:user_id>', view_func=Profile.as_view('profile'))
    app.add_url_rule('/subscribe/<int:user_id>', view_func=Subscribe.as_view('subscribe'))
    app.add_url_rule('/subscriptions', view_func=MySubscriptions.as_view('subscriptions'))