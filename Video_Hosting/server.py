# from waitress import serve
from app import app, db
from urls import add_urls
from jinja_funcs import add_jinja_funcs


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    add_jinja_funcs()
    add_urls()
    app.run(debug=True)
