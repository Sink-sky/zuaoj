from flask import request, session, redirect
from functools import wraps
import sys


class PageController(object):

    def __init__(self, url, model, max_item, filter_='', order_by='', reverse=False):
        if url.find('?') != -1:
            self.url = url + '&'
        else:
            self.url = url + '?'
        self.model = model
        self.max_item = max_item
        self.filter_ = filter_
        self.order_by = order_by
        self.reverse = reverse
        self.page = 1

        if request.args.get('page'):
            self.page = int(request.args.get('page'))

        self.item_len = len(self.model.query.filter(self.filter_).all())

        self.max_page = self.item_len // self.max_item + 1 \
            if self.item_len % self.max_item else self.item_len // self.max_item

    def get_items(self):
        if self.filter_:
            return self.model.query.filter(self.filter_).all(limit=self.max_item,
                                                             offset=(self.page - 1) * self.max_item,
                                                             order_by=self.order_by,
                                                             reverse=self.reverse)
        return self.model.query.all(limit=self.max_item,
                                    offset=(self.page - 1) * self.max_item,
                                    order_by=self.order_by,
                                    reverse=self.reverse)

    def get_urls(self):
        urls = list()
        a_len = min(9, self.max_page)

        begin = max(self.page - a_len // 2, 1)
        if begin + a_len <= self.max_page:
            end = begin + a_len
        else:
            end = self.max_page + 1
            begin = self.max_page - a_len + 1

        for i in range(begin, end):
            url = dict()
            url['value'] = self.url + 'page='
            url['id'] = i
            if i == self.page:
                url['now'] = True
            else:
                url['now'] = False
            urls.append(url)

        return urls


class UserController(object):
    HIGH_IDENTITY = 0
    MIDDLE_IDENTITY = 1
    LOW_IDENTITY = 2

    login_url = '/login'

    def __init__(self, model):
        self.model = model

    def user_login(self, username, password):
        user = self.model.query.filter('username=' + username + ';password=' + password).one()

        if user:
            for key, value in user.items():
                session[key] = value
            return True
        return False

    def user_logout(self):
        user = self.model.query.filter('username=' + session.get('username') + ';password=' +
                                       session.get('password')).one()

        if user:
            for key in user.keys():
                session.pop(key)
            return True
        return False

    def user_get(self):
        if not session.get('username'):
            return None
        return self.model.query.filter('username=' + session.get('username') + ';password=' +
                                       session.get('password')).one()

    @staticmethod
    def is_login():
        if session.get['username']:
            return True
        return False

    @staticmethod
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('username'):
                return redirect(UserController.login_url)
            return f(*args, **kwargs)
        return decorated_function

    @staticmethod
    def middle_identity_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('identity') and session.get('identity') > UserController.MIDDLE_IDENTITY:
                return redirect(UserController.login_url)
            return f(*args, **kwargs)
        return decorated_function

    @staticmethod
    def high_identity_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('identity') and session.get('identity') > UserController.HIGH_IDENTITY:
                return redirect(UserController.login_url)
            return f(*args, **kwargs)

        return decorated_function


class FormController(object):
    def __init__(self):
        self.items = dict()
        self.attributes = dict()

    def set_item(self, key, value_type, min_len=0, max_len=sys.maxsize, min_value=-sys.maxsize, max_value=sys.maxsize,
                 is_required=True):
        self.items[key] = None

        attribute = dict()
        attribute['value_type'] = value_type
        attribute['min_len'] = min_len
        attribute['max_len'] = max_len
        attribute['min_value'] = min_value
        attribute['max_value'] = max_value
        attribute['is_required'] = is_required

        self.attributes[key] = attribute

    def get_form(self):
        for key in self.items.keys():
            if request.form.get(key):
                self.items[key] = request.form.get(key)
                if self.attributes[key]['value_type'] == str:
                    if len(self.items[key]) < self.attributes[key]['min_len'] or \
                            len(self.items[key]) > self.attributes[key]['max_len']:
                        raise FormLengthError(key, len(self.items[key]), self.attributes[key]['min_len'],
                                              self.attributes[key]['max_len'])
                elif self.attributes[key]['value_type'] == int:
                    try:
                        self.items[key] = int(self.items[key])
                        if self.attributes[key]['min_value'] > self.items[key] or \
                                self.attributes[key]['max_value'] < self.items[key]:
                            raise FormValueError(key)
                    except ValueError:
                        raise FormValueError(key)
            elif not self.attributes[key]['is_required']:
                pass
            else:
                raise FormValueError(key)

        return self.items

    def get_items(self):
        return self.items


class FormError(Exception):
    pass


class FormValueError(FormError):
    def __init__(self, key):
        self.key = key


class FormLengthError(FormError):
    def __init__(self, key, length, min_len, max_len):
        self.key = key
        self.length = length
        self.min_len = min_len
        self.max_len = max_len
