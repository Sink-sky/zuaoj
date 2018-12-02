import sys
sys.path.append('..')
from web.app.models import *
from web.config import config
import hashlib


db = SimplifyMysql(config['SQL_HOSTNAME'], config['SQL_USERNAME'], config['SQL_PASSWORD'], config['SQL_DATABASE'])
db.connect()
BaseModel.set_db(db)


UserModel().create_table()
SubmitModel().create_table()
ResultModel().create_table()
ProblemModel().create_table()
NewsModel().create_table()
CompetitionModel().create_table()
GroupModel().create_table()


admin = dict()
admin['username'] = 'sh4w'
admin['password'] = 'yang0911'
admin['password'] = hashlib.md5(bytes(admin['password'].encode('utf-8'))).hexdigest()
admin['identity'] = 0

a_add_b_problem = dict()
a_add_b_problem['problem_id'] = 1
a_add_b_problem['title'] = 'A + B'
a_add_b_problem['author'] = admin['username']
a_add_b_problem['description'] = 'A + B'
a_add_b_problem['input_specification'] = 'A B'
a_add_b_problem['output_specification'] = 'C'
a_add_b_problem['sample_input'] = '1 1'
a_add_b_problem['sample_output'] = '2'
a_add_b_problem['test_input'] = '1 1'
a_add_b_problem['test_output'] = '2'
a_add_b_problem['test_point_score'] = '10'
a_add_b_problem['total_score'] = 10
a_add_b_problem['problem_status'] = 0

UserModel().add(admin)
ProblemModel().add(a_add_b_problem)
