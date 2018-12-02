import sys
sys.path.append('..')
from web.app import create_app
from flask import g
from web.config import config
from web.lib.flask_extend import SimplifyMysql, BaseModel
from pymysql.err import Error

app = create_app(config)
db = SimplifyMysql(config['SQL_HOSTNAME'], config['SQL_USERNAME'], config['SQL_PASSWORD'], config['SQL_DATABASE'])
BaseModel.set_db(db)


@app.before_request
def connect_db():
    if not hasattr(g, 'db'):
        db.connect()
        g.db = db


@app.teardown_request
def close_db(exception):
    try:
        pass
    except Error:
        pass


if __name__ == '__main__':
    app.run(host=config['SERVER_HOST'], port=config['SERVER_PORT'])
