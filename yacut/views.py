from . import app, db

@app.route('/')
def index_view():
    return 'Совсем скоро тут будет случайное мнение о фильме!'

if __name__ == '__main__':
    app.run()