from flask import request, render_template, g, make_response, jsonify
from . import manager
from ..models import *
from web.lib.flask_extend import *
from web.config import G
import hashlib


@manager.route('/', methods=['GET'])
@UserController.login_required
@UserController.middle_identity_required
def index():
    action = request.args.get('action')

    if action == 'user':
        url = '/manager/?action=user'
        page_controller = PageController(
            url,
            UserModel(),
            20,
        )

        return render_template(
            'manager_user.html',
            user_ls=page_controller.get_items(),
            urls=page_controller.get_urls(),
            user=UserController(UserModel()).user_get()
        )

    elif action == 'problem':
        url = '/manager/?action=problem'
        page_controller = PageController(
            url,
            ProblemModel(),
            20,
            filter_='problem_status!=' + str(G.STATUS_HIDDEN),
            order_by='problem_id'
        )

        return render_template(
            'manager_problem.html',
            problem_ls=page_controller.get_items(),
            urls=page_controller.get_urls(),
            user=UserController(UserModel()).user_get()
        )

    elif action == 'competition':
        user_ = UserController(UserModel()).user_get()
        url = '/manager/?action=competition'
        page_controller = PageController(
            url,
            CompetitionModel(),
            20,
            order_by='competition_id'
        )

        if user_['identity'] == UserController.HIGH_IDENTITY:
            group_ls = GroupModel().query.all()
        else:
            group_ls = GroupModel().query.filter('username=' + user_['username']).all()

        return render_template(
            'manager_competition.html',
            competition_ls=page_controller.get_items(),
            group_ls=group_ls,
            urls=page_controller.get_urls(),
            user=user_
        )

    elif action == 'group':
        url = '/manager/?action=group'
        page_controller = PageController(
            url,
            GroupModel(),
            20,
            order_by='group_id'
        )

        return render_template(
            'manager_group.html',
            group_ls=page_controller.get_items(),
            urls=page_controller.get_urls(),
            user=UserController(UserModel()).user_get()
        )

    else:
        url = '/manager/?action=news'
        page_controller = PageController(
            url,
            NewsModel(),
            20,
            order_by='news_id'
        )

        return render_template(
            'manager_news.html',
            news_ls=page_controller.get_items(),
            urls=page_controller.get_urls(),
            user=UserController(UserModel()).user_get()
        )


@manager.route('/news/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@UserController.login_required
@UserController.middle_identity_required
def news():
    username = UserController(UserModel()).user_get()['username']

    news_form = FormController()
    news_form.set_item('title', str, max_len=40)
    news_form.set_item('content', str)

    if request.method == 'GET':
        news_id = request.args.get('news_id')

        return jsonify(NewsModel().query.filter('news_id=' + news_id).one())

    elif request.method in ['POST', 'PUT']:
        try:
            form = news_form.get_form()

            if request.method == 'POST':
                insert_sql = '''INSERT INTO news (username, title, content, date) VALUES (%s, %s, %s, curdate())'''
                g.db.execute(insert_sql, (username, form['title'], form['content']))
                g.db.commit()

            elif request.method == 'PUT':
                news_id = request.args.get('news_id')

                NewsModel().query.filter('news_id=' + news_id).update(form)

                return make_response('', 200)

            return render_template('empty.html')
        except FormError:
            return make_response('', 400)

    elif request.method == 'DELETE':
        news_id = request.form.get('news_id')
        news_ = NewsModel().query.filter('news_id=' + news_id).one()

        if username == news_['username'] or UserController(UserModel).user_get()['identity'] <= \
                UserController.HIGH_IDENTITY:
            NewsModel().query.filter('news_id=' + news_id).delete()

            return make_response('', 200)
        else:
            return make_response('', 400)


@manager.route('/user/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@UserController.login_required
@UserController.middle_identity_required
def user():
    user_form = FormController()
    user_form.set_item('username', str, min_len=1, max_len=20)
    user_form.set_item('password', str, min_len=1, max_len=20)
    user_form.set_item('identity', int, min_len=int(UserController(UserModel()).user_get()['identity'] + 1))

    if request.method == 'POST':
        try:
            form = user_form.get_form()
            form['password'] = hashlib.md5(bytes(form['password'].encode('utf-8'))).hexdigest()

            UserModel().add(form)

            return render_template('empty.html')
        except FormError:
            return make_response('', 400)

    elif request.method == 'DELETE':
        if UserController(UserModel()).user_get()['identity'] > UserController.HIGH_IDENTITY:
            return make_response('', 400)

        username = request.form.get('username')
        if username:
            UserModel().query.filter('username=' + username).delete()

            return make_response('', 200)
        else:
            return make_response('', 400)


@manager.route('/problem/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@UserController.login_required
@UserController.middle_identity_required
def problem():
    problem_form = FormController()
    problem_form.set_item('problem_id', int, min_value=0)
    problem_form.set_item('title', str, max_len=40)
    problem_form.set_item('description', str)
    problem_form.set_item('time_limit', int, min_value=0, is_required=False)
    problem_form.set_item('memory_limit', int, min_value=0, is_required=False)
    problem_form.set_item('input_specification', str)
    problem_form.set_item('output_specification', str)
    problem_form.set_item('sample_input', str, is_required=False)
    problem_form.set_item('sample_output', str)
    problem_form.set_item('test_input', str, is_required=False)
    problem_form.set_item('test_output', str)
    problem_form.set_item('test_point_score', str)
    problem_form.set_item('problem_status', int)

    if request.method == 'GET':
        problem_id = request.args.get('problem_id')

        return jsonify(ProblemModel().query.filter('problem_id=' + problem_id).one())

    elif request.method in ['POST', 'PUT']:
        try:
            form = problem_form.get_form()
            form['author'] = UserController(UserModel()).user_get()['username']

            total_score = 0
            for score in form['test_point_score'].split(';'):
                total_score += int(score)
            form['total_score'] = total_score

            if request.method == 'POST':
                ProblemModel().add(form)
            elif request.method == 'PUT':
                problem_id = request.args.get('problem_id')

                ProblemModel().query.filter('problem_id=' + problem_id).update(form)

                return make_response('', 200)
            return render_template('empty.html')
        except FormError:
            return make_response('', 400)

    elif request.method == 'DELETE':
        problem_id = request.form.get('problem_id')
        if problem_id:
            ProblemModel().query.filter('problem_id=' + problem_id).delete()

            return make_response('', 200)
        else:
            return make_response('', 400)


@manager.route('/competition/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@UserController.login_required
@UserController.middle_identity_required
def competition():
    username = UserController(UserModel()).user_get()['username']

    competition_form = FormController()
    competition_form.set_item('title', str, max_len=40)
    competition_form.set_item('begin_date_year', int)
    competition_form.set_item('begin_date_month', int)
    competition_form.set_item('begin_date_day', int)
    competition_form.set_item('begin_date_hour', int)
    competition_form.set_item('begin_date_min', int)
    competition_form.set_item('end_date_year', int)
    competition_form.set_item('end_date_month', int)
    competition_form.set_item('end_date_day', int)
    competition_form.set_item('end_date_hour', int)
    competition_form.set_item('end_date_min', int)
    competition_form.set_item('problem_ls', str)
    competition_form.set_item('group_id', int)

    if request.method == 'GET':
        competition_id = request.args.get('competition_id')

        return jsonify(CompetitionModel().query.filter('competition_id=' + competition_id).one())

    elif request.method in ['POST', 'PUT']:
        try:
            form = competition_form.get_form()

            if form['group_id'] == 0:
                form['competition_status'] = G.STATUS_PUBLIC
            else:
                form['competition_status'] = G.STATUS_PRIVATE

            begin_date_str = '{:04d}{:02d}{:02d}{:02d}{:02d}'.format(
                form['begin_date_year'],
                form['begin_date_month'],
                form['begin_date_day'],
                form['begin_date_hour'],
                form['begin_date_min']
            )

            end_date_str = '{:04d}{:02d}{:02d}{:02d}{:02d}'.format(
                form['end_date_year'],
                form['end_date_month'],
                form['end_date_day'],
                form['end_date_hour'],
                form['end_date_min']
            )

            if request.method == 'PUT':
                competition_id = request.args.get('competition_id')

                update_sql = '''UPDATE competition SET title=%s, begin_date=str_to_date(%s, '%%Y%%m%%d%%H%%i'),
                end_date=str_to_date(%s, '%%Y%%m%%d%%H%%i'), group_id=%s, competition_status=%s WHERE competition_id=%s
                '''

                values = (form['title'], begin_date_str, end_date_str, form['group_id'], form['competition_status'],
                          competition_id)

                g.db.execute(update_sql, values)
                g.db.commit()

                return make_response('', 200)

            insert_sql = '''INSERT INTO competition (title, username, begin_date, end_date, problem_ls, group_id, 
            competition_status) VALUES ('{}', '{}', str_to_date('{}', '%Y%m%d%H%i'), str_to_date('{}', '%Y%m%d%H%i'), 
            '{}', {}, {})'''.format(
                form['title'],
                username,
                begin_date_str,
                end_date_str,
                form['problem_ls'],
                form['group_id'],
                form['competition_status']
            )

            g.db.execute(insert_sql)
            g.db.execute('SELECT LAST_INSERT_ID()')
            competition_id = g.db.fetchone()[0]
            g.db.commit()

            problem_model = ProblemModel()

            for i, problem_id in enumerate(form['problem_ls'].split(';')):
                problem_ = problem_model.query.filter('problem_id=' + problem_id).one()
                problem_['accepted'] = 0
                problem_['submit'] = 0
                problem_['submit_users'] = ''
                problem_['accepted_users'] = ''
                problem_['problem_id'] = competition_id * 10000 + i + 1
                problem_['problem_status'] = G.STATUS_HIDDEN

                problem_model.add(problem_)

            return render_template('empty.html')
        except FormError:
            return make_response('', 400)

    elif request.method == 'DELETE':
        competition_id = request.form.get('competition_id')
        competition_filter = 'problem_id>' + str(int(competition_id) * G.PROBLEM_ID_DIVISION) + \
                             ';problem_id<' + str((int(competition_id) + 1) * G.PROBLEM_ID_DIVISION)

        competition_ = CompetitionModel().query.filter('competition_id=' + competition_id).one()

        if username == competition_['username'] or UserController(UserModel).user_get()['identity'] <= \
                UserController.HIGH_IDENTITY:

            CompetitionModel().query.filter('competition_id=' + competition_id).delete()
            ProblemModel().query.filter(competition_filter).delete()

            return make_response('', 200)
        else:
            return make_response('', 400)


@manager.route('/group/', methods=['GET', 'POST', 'PUT', 'DELETE'])
@UserController.login_required
@UserController.middle_identity_required
def group():
    username = UserController(UserModel()).user_get()['username']
    group_form = FormController()
    group_form.set_item('group_name', str)
    group_form.set_item('user_ls', str, is_required=False)
    group_form.set_item('student_id_ls', str, is_required=False)

    if request.method == 'GET':
        group_id = request.args.get('group_id')

        return jsonify(GroupModel().query.filter('group_id=' + group_id).one())

    elif request.method == 'POST':
        try:
            form = group_form.get_form()
            form['username'] = username

            GroupModel().add(form)

            return render_template('empty.html')
        except FormError:
            return make_response('', 400)

    elif request.method == 'PUT':
        try:
            group_id = request.args.get('group_id')
            form = group_form.get_form()

            GroupModel().query.filter('group_id=' + group_id).update(form)

            return make_response('', 200)
        except FormError:
            return make_response('', 400)

    elif request.method == 'DELETE':
        group_id = request.form.get('group_id')
        group_ = GroupModel().query.filter('group_id=' + group_id).one()

        if username == group_['username'] or UserController(UserModel()).user_get()['identity'] <= \
                UserController.HIGH_IDENTITY:
            GroupModel().query.filter('group_id=' + group_id).delete()

            return make_response('', 200)
        else:
            return make_response('', 400)
