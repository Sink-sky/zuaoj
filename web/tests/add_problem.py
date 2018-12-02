import sys
sys.path.append('..')
from web.app.models import *
from web.config import config, G


db = SimplifyMysql(config['SQL_HOSTNAME'], config['SQL_USERNAME'], config['SQL_PASSWORD'], config['SQL_DATABASE'])
db.connect()
BaseModel.set_db(db)

problem = dict()

problem['problem_id'] = 0
problem['title'] = ''
problem['author'] = ''
problem['description'] = ''
problem['input_specification'] = ''
problem['output_specification'] = ''
problem['sample_input'] = '1 1'
problem['sample_output'] = '2'
test_input_ls = list()
problem['test_input'] = G.TEST_POINT_DIVIDE.join(test_input_ls)
test_output_ls = list()
problem['test_output'] = G.TEST_POINT_DIVIDE.join(test_output_ls)
test_point_score = list()
problem['test_point_score'] = ';'.join(test_point_score)
problem['total_score'] = 0
problem['problem_status'] = 0
