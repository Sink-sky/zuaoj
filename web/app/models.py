from web.lib.flask_extend import *


class UserModel(BaseModel):
    table_name = 'user'

    def __init__(self):
        super().__init__()
        self.set_column('username', 'CHAR(20)')
        self.set_column('password', 'CHAR(32)')
        self.set_column('student_id', 'CHAR(20)')
        self.set_column('identity', 'INT')
        self.set_column('submit', 'INT', default=0)
        self.set_column('accepted', 'INT', default=0)
        self.set_column('score', 'INT', default=0)


class SubmitModel(BaseModel):
    table_name = 'submit'

    def __init__(self):
        super().__init__()
        self.set_column('submit_id', 'INT', primary_key=True, auto_increment=True)
        self.set_column('problem_id', 'INT')
        self.set_column('language', 'INT')
        self.set_column('username', 'CHAR(20)')
        self.set_column('time', 'DATETIME')
        self.set_column('source_code', 'TEXT')


class ResultModel(BaseModel):
    table_name = 'result'

    def __init__(self):
        super().__init__()
        self.set_column('submit_id', 'INT')
        self.set_column('problem_id', 'INT')
        self.set_column('language', 'INT')
        self.set_column('username', 'CHAR(20)')
        self.set_column('time', 'DATETIME')
        self.set_column('result_status', 'CHAR(50)')
        self.set_column('source_code', 'TEXT')
        self.set_column('compile_info', 'TEXT')


class ProblemModel(BaseModel):
    table_name = 'problem'

    def __init__(self):
        super().__init__()
        self.set_column('problem_id', 'INT')
        self.set_column('title', 'CHAR(40)')
        self.set_column('author', 'CHAR(20)')
        self.set_column('description', 'TEXT')
        self.set_column('input_specification', 'TEXT')
        self.set_column('output_specification', 'TEXT')
        self.set_column('sample_input', 'TEXT', default='')
        self.set_column('sample_output', 'TEXT')
        self.set_column('test_input', 'TEXT', default='')
        self.set_column('test_output', 'TEXT')
        self.set_column('time_limit', 'INT', default=1000)
        self.set_column('memory_limit', 'INT', default=65535)
        self.set_column('total_score', 'INT')
        self.set_column('test_point_score', 'CHAR(40)')
        self.set_column('problem_status', 'INT')
        self.set_column('submit', 'INT', default=0)
        self.set_column('accepted', 'INT', default=0)
        self.set_column('submit_users', 'TEXT', default='')
        self.set_column('accepted_users', 'TEXT', default='')


class NewsModel(BaseModel):
    table_name = 'news'

    def __init__(self):
        super().__init__()
        self.set_column('news_id', 'INT', primary_key=True, auto_increment=True)
        self.set_column('username', 'CHAR(20)')
        self.set_column('title', 'CHAR(40)')
        self.set_column('content', 'TEXT')
        self.set_column('date', 'DATE')


class CompetitionModel(BaseModel):
    table_name = 'competition'

    def __init__(self):
        super().__init__()
        self.set_column('competition_id', 'INT', primary_key=True, auto_increment=True)
        self.set_column('username', 'CHAR(20)')
        self.set_column('title', 'CHAR(40)')
        self.set_column('problem_ls', 'TEXT')
        self.set_column('group_id', 'INT')
        self.set_column('begin_date', 'DATETIME')
        self.set_column('end_date', 'DATETIME')
        self.set_column('competition_status', 'INT')


class GroupModel(BaseModel):
    table_name = 'group_'

    def __init__(self):
        super().__init__()
        self.set_column('group_id', 'INT', primary_key=True, auto_increment=True)
        self.set_column('group_name', 'CHAR(20)')
        self.set_column('username', 'CHAR(20)')
        self.set_column('user_ls', 'TEXT', default='')
        self.set_column('student_id_ls', 'TEXT', default='')
