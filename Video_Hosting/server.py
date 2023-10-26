# from waitress import serve
from app import app, db
from urls import add_urls


if __name__ == '__main__':
    add_urls()
    app.run(debug=True)
