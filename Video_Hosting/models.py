from app import db
from datetime import datetime


from User import User


class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer,
                   db.Identity(start=1),
                   primary_key=True,
                   unique=True)
    author_id = db.Column(db.Integer,
                          db.ForeignKey(User.id, ondelete='cascade'),
                          primary_key=True,
                          unique=False)
    title = db.Column(db.String(200),
                      nullable=False)
    description = db.Column(db.String(1000),
                            nullable=True)
    created_on = db.Column(db.DateTime,
                           default=datetime.now)
    comment_children = db.relationship('Comment',
                                       cascade="all, delete",
                                       backref="video",
                                       passive_deletes=True)
    like_children = db.relationship('Like',
                                    cascade="all, delete",
                                    backref="video",
                                    passive_deletes=True)

    view_children = db.relationship('Watch',
                                    cascade="all, delete",
                                    backref="video",
                                    passive_deletes=True)

    def __init__(self, author_id, title, description):
        self.author_id = author_id
        self.title = title
        self.description = description


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer,
                   db.Identity(start=1),
                   primary_key=True,
                   unique=True)
    author_name = db.Column(db.String(50),
                            unique=False)
    video_id = db.Column(db.Integer,
                         db.ForeignKey(Video.id, ondelete='cascade'),
                         primary_key=True,
                         unique=False)
    comment = db.Column(db.String(1000),
                        nullable=False)
    response_children = db.relationship('CommentResponse',
                                        cascade="all, delete",
                                        backref="video",
                                        passive_deletes=True)

    def __init__(self, author_name, video_id, comment):
        self.author_name = author_name
        self.video_id = video_id
        self.comment = comment


class CommentResponse(db.Model):
    __tablename__ = 'comment_response'
    id = db.Column(db.Integer,
                   db.Identity(start=1),
                   primary_key=True)
    responder_name = db.Column(db.String(50),
                               unique=False)
    video_id = db.Column(db.Integer,
                         db.ForeignKey(Video.id, ondelete='cascade'),
                         primary_key=True,
                         unique=False)
    comment_id = db.Column(db.Integer,
                           db.ForeignKey(Comment.id, ondelete='cascade'),
                           primary_key=True,
                           unique=False)
    response = db.Column(db.String(1000),
                         nullable=False)

    def __init__(self, responder_name, comment_id, video_id, response):
        self.responder_name = responder_name
        self.video_id = video_id
        self.response = response
        self.comment_id = comment_id


class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer,
                   db.Identity(start=1),
                   primary_key=True)
    video_id = db.Column(db.Integer,
                         db.ForeignKey(Video.id, ondelete='cascade'),
                         primary_key=True,
                         unique=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey(User.id, ondelete='cascade'),
                        primary_key=True,
                        unique=False)

    def __init__(self, video_id, user_id):
        self.video_id = video_id
        self.user_id = user_id


class Watch(db.Model):
    __tablename__ = 'view'
    id = db.Column(db.Integer,
                   db.Identity(start=1),
                   primary_key=True)
    video_id = db.Column(db.Integer,
                         db.ForeignKey(Video.id, ondelete='cascade'),
                         primary_key=True,
                         unique=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey(User.id, ondelete='cascade'),
                        primary_key=True,
                        unique=False)

    def __init__(self, video_id, user_id):
        self.video_id = video_id
        self.user_id = user_id


class Subscription(db.Model):
    __tablename__ = 'subscription'
    id = db.Column(db.Integer,
                   db.Identity(start=1),
                   primary_key=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey(User.id, ondelete='cascade'),
                        primary_key=True,
                        unique=False)
    subscribed_to = db.Column(db.Integer,
                              db.ForeignKey(User.id, ondelete='cascade'),
                              primary_key=True,
                              unique=False)
    notifications_on = db.Column(
        db.Boolean(),
        default=False
    )

    def __init__(self, user_id, subscribed_to):
        self.user_id = user_id
        self.subscribed_to = subscribed_to
