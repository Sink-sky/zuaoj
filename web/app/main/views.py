from flask import request, render_template, abort, redirect, url_for, g, jsonify, make_response
from . import main
from ..models import *
import time
from web.lib.flask_extend import *
from web.config import G
import hashlib


def str2md5(s):
    return hashlib.md5(bytes(s.encode('utf-8'))).hexdigest()


def username_format_inspect(username):
    allow_ch = list()
    allow_ch.append('_')

    for ch in username:
        if not (ch.isalnum() or ch in allow_ch):
            return False
    return True


def competition_identity_inspect(competition):
    user = UserController(UserModel()).user_get()

    if time.mktime(competition['begin_date'].timetuple()) > time.time():
        return G.DATE_DENIED

    if competition['group_id'] == 0:
        return G.ALLOW_ACCESS

    group = GroupModel().query.filter('group_id=' + str(competition['group_id'])).one()

    if group['username'] == user['username'] or user['identity'] == UserController.HIGH_IDENTITY:
        return G.ALLOW_ACCESS

    if time.mktime(competition['end_date'].timetuple()) < time.time():
        return G.DATE_PAST_DENIED

    if group:
        for username in group['user_ls'].split(';'):
            if username == user['username']:
                return G.ALLOW_ACCESS
        if user.get('student_id'):
            for student_id in group['student_id_ls'].split(';'):
                if student_id == user['student_id']:
                    return G.ALLOW_ACCESS
    return G.PERMISSION_DENIED


def sort_by_score(elem):
    if isinstance(elem, list) or isinstance(elem, tuple):
        return elem[5]
    return elem['total_score']


@main.route('/', methods=['GET'])
@main.route('/index/', methods=['GET'])
def index():
    news_model = NewsModel()
    news_ls = news_model.query.all(order_by='news_id', reverse=True)

    for news in news_ls:
        news['content'] = news['content'].replace('\n', '<br>')

    UserModel().query.all()

    return render_template(
        'index.html',
        news_ls=news_ls,
        user=UserController(UserModel()).user_get())


@main.route('/about/', methods=['GET'])
def about():
    return render_template(
        'about.html',
        user=UserController(UserModel()).user_get()
    )


@main.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template(
            'login.html',
            user=UserController(UserModel()).user_get()
        )
    else:
        login_form = FormController()
        login_form.set_item('username', str, min_len=1, max_len=20)
        login_form.set_item('password', str, min_len=1, max_len=20)

        try:
            form = login_form.get_form()
            form['password'] = str2md5(form['password'])

            user_controller = UserController(UserModel())

            if user_controller.user_login(form['username'], form['password']):
                return redirect(url_for('main.index'))
            else:
                script = 'alert(\'用户名或密码错误\')'
                return render_template(
                    'login.html',
                    user=UserController(UserModel()).user_get(),
                    script=script
                )
        except FormError:
            script = 'alert(\'请正确输入\')'
            return render_template(
                'login.html',
                user=UserController(UserModel()).user_get(),
                script=script
            )


@main.route('/logout/', methods=['GET'])
@UserController.login_required
def logout():
    user_controller = UserController(UserModel())
    user_controller.user_logout()

    return redirect(request.headers['Referer'])


@main.route('/rank/', methods=['GET'])
def rank():
    url = '/rank/'
    page_controller = PageController(url, UserModel(), 100, order_by='accepted', reverse=True)

    user_ls = page_controller.get_items()

    rank_count = 1
    last_score = user_ls[0]['accepted']
    for user in user_ls:
        if not user['accepted'] == last_score:
            last_score = user['accepted']
            rank_count += 1
        user['rank'] = rank_count

    return render_template(
        'rank.html',
        user_ls=user_ls,
        urls=page_controller.get_urls(),
        user=UserController(UserModel()).user_get()
    )


@main.route('/submit/', methods=['POST'])
@UserController.login_required
def submit():
    username = UserController(UserModel()).user_get()['username']

    submit_form = FormController()
    submit_form.set_item('problem_id', int)
    submit_form.set_item('source_code', str)
    submit_form.set_item('language', int)

    try:
        form = submit_form.get_form()

        submit_model = SubmitModel()
        submit_model.query.all()

        if form['problem_id'] > G.PROBLEM_ID_DIVISION:
            competition = CompetitionModel().query.filter(
                'competition_id=' + str(form['problem_id'] // G.PROBLEM_ID_DIVISION)).one()
            access = competition_identity_inspect(competition)

            if access == G.DATE_PAST_DENIED:
                return make_response('', 400)

        c = g.db.cursor
        c.execute('INSERT INTO submit (problem_id, username, source_code, time, language)VALUES(%s, %s, %s, now(), %s)',
                  (form['problem_id'], username, form['source_code'], form['language']))
        c.execute('SELECT LAST_INSERT_ID()')
        submit_id = c.fetchone()[0]
        g.db.commit()

        return make_response(str(submit_id))
    except FormError:
        return abort(404)


@main.route('/result/', methods=['GET'])
@UserController.login_required
def result():
    submit_id = request.args.get('submit_id')

    result_model = ResultModel()
    result_ = result_model.query.filter('submit_id=' + submit_id).one()

    if not result_:
        return abort(400)

    problem_ = ProblemModel().query.filter('problem_id=' + str(result_['problem_id'])).one()

    total_score = 0
    for status, point_score in \
            zip(result_['result_status'].split(';')[0].split(','), problem_['test_point_score'].split(';')):
        if int(status) == G.OJ_AC:
            total_score += int(point_score)
    result_['total_score'] = total_score

    return jsonify(result_)


@main.route('/last-submit', methods=['GET'])
@UserController.login_required
def last_submit():
    problem_id = request.args.get('problem_id')
    username = UserController(UserModel()).user_get()['username']

    last_submit_ = ResultModel().query.filter('problem_id=' + problem_id + ';username=' + username).one()

    if not last_submit_:
        return ''

    return jsonify(last_submit_)


@main.route('/user/register/', methods=['GET', 'POST'])
def user_register():
    if request.method == 'GET':
        return render_template('user_register.html',
                               user=UserController(UserModel()).user_get())
    else:
        login_form = FormController()
        login_form.set_item('username', str, min_len=1, max_len=20)
        login_form.set_item('password', str, min_len=1, max_len=20)

        try:
            form = login_form.get_form()
            form['identity'] = UserController.LOW_IDENTITY

            if not username_format_inspect(form['username']):
                raise FormError

            form['password'] = str2md5(form['password'])

            user_model = UserModel()

            if not user_model.query.filter('username=' + form['username']).one():
                user_model.add(form)
                return redirect(url_for('main.index'))
            else:
                script = 'alert(\'用户名已存在\')'
                return render_template(
                    'use_register.html',
                    user=UserController(UserModel()).user_get(),
                    script=script
                )
        except FormError:
            script = 'alert(\'用户名存在非法字符\')'
            return render_template(
                'user_register.html',
                user=UserController(UserModel()).user_get(),
                script=script
            )


@main.route('/user/information/', methods=['GET'])
@UserController.login_required
def user_information():
    return render_template(
        'user_information.html',
        user=UserController(UserModel()).user_get()
    )


@main.route('/user/information/bind-student-id/', methods=['POST'])
@UserController.login_required
def user_information_bind_student_id():
    username = UserController(UserModel()).user_get()['username']
    student_id_form = FormController()
    student_id_form.set_item('student_id', str, min_len=1, max_len=20)

    try:
        form = student_id_form.get_form()

        user_model = UserModel()

        if not user_model.query.filter('student_id=' + form['student_id']).all():
            user_model.query.filter('username=' + username).update('student_id=' + form['student_id'])

            return make_response('', 200)
        else:
            return make_response('', 400)
    except FormError:
        return make_response('', 400)


@main.route('/user/history/', methods=['GET'])
@UserController.login_required
def user_history():
    username = UserController(UserModel()).user_get()['username']
    url = '/user/history'
    page_controller = PageController(
        url,
        ResultModel(),
        20,
        filter_='username=' + username,
        order_by='submit_id',
        reverse=True
    )

    result_ls = page_controller.get_items()

    for result_ in result_ls:
        if result_['language'] == G.LANG_C:
            result_['type'] = 'C'
        elif result_['language'] == G.LANG_CPP:
            result_['type'] = 'C++'
        elif result_['language'] == G.LANG_JAVA:
            result_['type'] = 'Java'
        elif result_['language'] == G.LANG_PYTHON3:
            result_['type'] = 'Python3'

        if int(result_['result_status'][0]) == G.OJ_CE:
            result_['total_status'] = 3
            continue

        is_accept = 0
        is_wrong = 0
        for status in result_['result_status'].split(';')[0].split(','):
            if int(status) == G.OJ_AC:
                is_accept = 1
            else:
                is_wrong = 1

        if is_accept and not is_wrong:
            result_['total_status'] = 0
        elif is_accept and is_wrong:
            result_['total_status'] = 1
        elif not is_accept and is_wrong:
            result_['total_status'] = 2

    return render_template(
        'user_history.html',
        result_ls=result_ls,
        urls=page_controller.get_urls(),
        user=UserController(UserModel()).user_get()
    )


@main.route('/problem/', methods=['GET'])
def problem_list():
    url = '/problem/'
    page_controller = PageController(
        url,
        ProblemModel(),
        50,
        filter_='problem_status=' + str(G.STATUS_PUBLIC),
        order_by='problem_id'
    )

    return render_template(
        'problem_list.html',
        problem_ls=page_controller.get_items(),
        urls=page_controller.get_urls(),
        user=UserController(UserModel()).user_get()
    )


@main.route('/problem/<int:problem_id>/', methods=['GET'])
@UserController.login_required
def problem_information(problem_id):
    problem_model = ProblemModel()
    problem = problem_model.query.filter('problem_id=' + str(problem_id)).one()

    if not problem:
        return abort(404)

    if problem['problem_status'] != G.STATUS_PUBLIC:
        return abort(404)

    language_list = list()
    language_list.append({'language': 'C', 'information': 'gcc', 'value': 0})
    language_list.append({'language': 'C++', 'information': 'g++', 'value': 1})
    # language_list.append({'language': 'Java', 'information': 'jdk', 'value': 2})
    language_list.append({'language': 'Python', 'information': 'python 3', 'value': 3})

    problem['description'] = problem['description'].replace('\n', '<br>')
    problem['input_specification'] = problem['input_specification'].replace('\n', '<br>')
    problem['output_specification'] = problem['output_specification'].replace('\n', '<br>')
    problem['sample_input'] = problem['sample_input'].replace('\n', '<br>')
    problem['sample_output'] = problem['sample_output'].replace('\n', '<br>')

    return render_template(
        'problem_information.html',
        problem=problem,
        language_list=language_list,
        user=UserController(UserModel()).user_get(),
    )


@main.route('/competition/', methods=['GET'])
def competition_list():
    url = '/competition/'
    page_controller = PageController(
        url,
        CompetitionModel(),
        50,
        order_by='competition_id',
        reverse=True
    )

    competition_ls = page_controller.get_items()

    for competition in competition_ls:
        if time.mktime(competition['begin_date'].timetuple()) > time.time():
            competition['stage'] = G.STAGE_NOT_STARTED
        elif time.mktime(competition['end_date'].timetuple()) < time.time():
            competition['stage'] = G.STAGE_END
        else:
            competition['stage'] = G.STAGE_RUNNING

    return render_template(
        'competition_list.html',
        competition_ls=competition_ls,
        urls=page_controller.get_urls(),
        user=UserController(UserModel()).user_get()
    )


@main.route('/competition/<int:competition_id>/', methods=['GET'])
@UserController.login_required
def competition_information(competition_id):
    competition = CompetitionModel().query.filter('competition_id=' + str(competition_id)).one()
    user_ = UserController(UserModel()).user_get()

    if not competition:
        return abort(404)
    access = competition_identity_inspect(competition)
    if access == G.DATE_DENIED:
        script = 'alert("比赛未开始");'
        return render_template('empty.html', script=script)
    elif access == G.PERMISSION_DENIED:
        script = 'alert("权限不足");'
        return render_template('empty.html', script=script)

    problem_model = ProblemModel()
    problems = list()

    for i, problem_id in enumerate(competition['problem_ls'].split(';')):
        problem = problem_model.query.filter(
            'problem_id=' + str(competition_id * G.PROBLEM_ID_DIVISION + i + 1)
        ).one()
        problem['id'] = i + 1

        if user_['username'] in problem['accepted_users'].split(';'):
            problem['is_accepted'] = 1
        else:
            problem['is_accepted'] = 0

        problems.append(problem)

    competition['problem_count'] = len(problems)
    competition['problems'] = problems
    return render_template(
        'competition_information.html',
        competition=competition,
        user=user_
    )


@main.route('/competition/<int:competition_id>/<int:problem_id>/', methods=['GET'])
@UserController.login_required
def competition_problem(competition_id, problem_id):
    competition = CompetitionModel().query.filter('competition_id=' + str(competition_id)).one()

    if not competition:
        return abort(404)
    access = competition_identity_inspect(competition)
    if access == G.DATE_DENIED:
        script = 'alert("比赛未开始");'
        return render_template('empty.html', script=script)
    elif access == G.PERMISSION_DENIED:
        script = 'alert("权限不足");'
        return render_template('empty.html', script=script)

    problem = ProblemModel().query.filter(
        'problem_id=' + str(competition_id * G.PROBLEM_ID_DIVISION + int(problem_id))
    ).one()

    language_list = list()
    language_list.append({'language': 'C', 'information': 'gcc', 'value': 0})
    language_list.append({'language': 'C++', 'information': 'g++', 'value': 1})
    language_list.append({'language': 'Java', 'information': 'jdk', 'value': 2})
    language_list.append({'language': 'Python', 'information': 'python 3', 'value': 3})

    if problem:
        competition['problem'] = []
        competition['problem_items'] = []
        for p_id in competition['problem_ls'].split(';'):
            problem_item = dict()
            problem_item['no'] = len(competition['problem']) + 1
            problem_item['problem_id'] = int(p_id)
            problem_item['is_active'] = problem_id == int(p_id)

            competition['problem_items'].append(problem_item)
            competition['problem_count'] = len(competition['problem_items'])

        return render_template(
            'problem_information.html',
            problem=problem,
            language_list=language_list,
            user=UserController(UserModel()).user_get(),
            competition=competition,
        )


@main.route('/competition/<int:competition_id>/rank/', methods=['GET'])
@UserController.login_required
def competition_rank(competition_id):
    competition = CompetitionModel().query.filter('competition_id=' + str(competition_id)).one()

    if not competition:
        return abort(404)
    access = competition_identity_inspect(competition)
    if access == G.DATE_DENIED:
        script = 'alert("比赛未开始");'
        return render_template('empty.html', script=script)
    elif access == G.PERMISSION_DENIED:
        script = 'alert("权限不足");'
        return render_template('empty.html', script=script)

    problem_model = ProblemModel()
    result_model = ResultModel()

    if competition['competition_status'] != 0:
        competition['user_ls'] = GroupModel().query.filter(
            'group_id=' + str(competition['group_id'])).one()['user_ls'].split(';')
        competition['user_ls'].append(competition['username'])
    else:
        user_set = set()
        for problem_index in range(0, len(competition['problem_ls'].split(';'))):
            result_ls = result_model.query.filter('problem_id=' + str(competition_id * G.PROBLEM_ID_DIVISION +
                                                                      problem_index + 1)).all()
            for result_ in result_ls:
                user_set.add(result_['username'])
        competition['user_ls'] = list(user_set)

    problems = list()
    for i, problem_id in enumerate(competition['problem_ls'].split(';')):
        problem = problem_model.query.filter('problem_id=' + str(competition_id * G.PROBLEM_ID_DIVISION + i + 1)).one()
        problem['id'] = i + 1
        problems.append(problem)

    competition['problem_count'] = len(problems)
    competition['problems'] = problems

    problem_score = list()
    for problem_id in competition['problem_ls'].split(';'):
        problem_score.append(problem_model.query.filter('problem_id=' +
                                                        problem_id).one()['test_point_score'].split(';'))

    user_status_ls = list()

    username_ls = competition['user_ls']

    for username in username_ls:
        user_status = {'username': username, 'total_score': 0, 'score': [], 'rank': 0}

        for problem_index in range(0, len(problem_score)):
            user_status['score'].append('-')
            result_ls = result_model.query.filter('problem_id=' + str(competition_id * G.PROBLEM_ID_DIVISION +
                                                                      problem_index + 1)
                                                  + ';username=' + username).all()

            for result_ in result_ls:
                score = 0
                test_point_index = 0
                for status in result_['result_status'].split(';')[0].split(','):
                    if status == str(G.OJ_CE):
                        break
                    if status == str(G.OJ_AC):
                        score += int(problem_score[problem_index][test_point_index])
                    test_point_index += 1

                if user_status['score'][-1] == '-':
                    user_status['score'][-1] = score
                elif score > user_status['score'][-1]:
                    user_status['score'][-1] = score

            if user_status['score'][-1] != '-':
                user_status['total_score'] += user_status['score'][-1]
        user_status_ls.append(user_status)
    user_status_ls.sort(key=sort_by_score, reverse=True)

    rank_count = 1
    last_score = user_status_ls[0]['total_score'] if user_status_ls else 0
    for user_status in user_status_ls:
        if not user_status['total_score'] == last_score:
            last_score = user_status['total_score']
            rank_count += 1
        user_status['rank'] = rank_count

    return render_template(
        'competition_rank.html',
        user=UserController(UserModel()).user_get(),
        competition=competition,
        user_status_ls=user_status_ls
    )


@main.route('/competition/<int:competition_id>/history/', methods=['GET'])
@UserController.login_required
def competition_history(competition_id):
    competition = CompetitionModel().query.filter('competition_id=' + str(competition_id)).one()

    if not competition:
        return abort(404)
    access = competition_identity_inspect(competition)
    if access == G.DATE_DENIED:
        script = 'alert("比赛未开始");'
        return render_template('empty.html', script=script)
    elif access == G.PERMISSION_DENIED:
        script = 'alert("权限不足");'
        return render_template('empty.html', script=script)

    competition['problem_count'] = len(competition['problem_ls'].split(';'))

    url = '/competition/' + str(competition_id) + '/history/'
    competition_filter = 'problem_id>' + str(competition_id * G.PROBLEM_ID_DIVISION) + \
                         ';problem_id<' + str((competition_id + 1) * G.PROBLEM_ID_DIVISION)

    page_controller = PageController(
        url,
        ResultModel(),
        10,
        filter_=competition_filter,
        order_by='submit_id',
        reverse=True
    )

    result_ls = page_controller.get_items()

    for result_ in result_ls:
        if result_['language'] == G.LANG_C:
            result_['type'] = 'C'
        elif result_['language'] == G.LANG_CPP:
            result_['type'] = 'C++'
        elif result_['language'] == G.LANG_JAVA:
            result_['type'] = 'Java'
        elif result_['language'] == G.LANG_PYTHON3:
            result_['type'] = 'Python3'

        if int(result_['result_status'][0]) == G.OJ_CE:
            result_['total_status'] = 3
            continue

        is_accept = 0
        is_wrong = 0
        for status in result_['result_status'].split(';')[0].split(','):
            if int(status) == G.OJ_AC:
                is_accept = 1
            else:
                is_wrong = 1

        if is_accept and not is_wrong:
            result_['total_status'] = 0
        elif is_accept and is_wrong:
            result_['total_status'] = 1
        elif not is_accept and is_wrong:
            result_['total_status'] = 2

    return render_template(
        'competition_history.html',
        competition=competition,
        result_ls=result_ls,
        urls=page_controller.get_urls(),
        user=UserController(UserModel()).user_get()
    )
