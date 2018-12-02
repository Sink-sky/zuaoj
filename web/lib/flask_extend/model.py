

class BaseModel(object):
    table_name = ''
    db = None

    def __init__(self):
        self.query = self._Query(self.db, self.table_name)
        self.items = dict()
        self.key_list = list()
        self.db = BaseModel.db

    @staticmethod
    def set_db(db):
        BaseModel.db = db

    def set_column(self, key, value_type, primary_key=False, unique=False, not_null=False, auto_increment=False,
                   default=None):
        attribute = dict()
        attribute['value_type'] = value_type
        attribute['primary_key'] = primary_key
        attribute['unique'] = unique
        attribute['not_null'] = not_null
        attribute['auto_increment'] = auto_increment
        attribute['default'] = default
        attribute['value'] = None

        self.items[key] = attribute
        self.query.items[key] = attribute

        self.key_list.append(key)
        self.query.key_list.append(key)

    def create_table(self):
        self.db.create_table(self.table_name, self.key_list, self.items)

    def add(self, form):
        date = dict()

        for key, attribute in self.items.items():
            value = form.get(key) if key in form else attribute['default']

            if isinstance(value, type(None)):
                if attribute['not_null']:
                    return
                else:
                    continue

            date[key] = value

        self.db.insert(self.table_name, date)
        self.db.commit()

    class _Query(object):
        table_name = ''

        def __init__(self, db, table_name):
            self.db = db
            self.table_name = table_name
            self.conditions = []
            self.items = dict()
            self.key_list = list()

        def filter(self, filter_):
            if filter_:
                self.conditions.clear()
                for condition in filter_.split(';'):
                    self.conditions.append(self._decompose_expression(condition))
            return self

        def all(self, limit=0, offset=0, order_by='', reverse=False):
            items = []
            for values in self.db.select(self.table_name, self.conditions, limit, offset, order_by, reverse):
                item = dict()
                for key, value in zip(self.key_list, values):
                    item[key] = value
                items.append(item)

            return items

        def one(self):
            try:
                return self.all()[-1]
            except IndexError:
                return None

        def delete(self):
            self.db.delete(self.table_name, self.conditions)
            self.db.commit()
            return self

        def update(self, update_data):
            data = dict()

            if isinstance(update_data, str):
                for item in update_data.split(';'):
                    key = self._decompose_expression(item)[0]
                    value = self._decompose_expression(item)[2]

                    data[key] = value
            elif isinstance(update_data, dict):
                data = update_data

            self.db.update(self.table_name, data, self.conditions)

            self.db.commit()
            return self

        @staticmethod
        def _decompose_expression(expression):
            sign = ['==', '<=', '>=', '=', '<', '>']

            for s in sign:
                condition = expression.split(s)
                if len(condition) > 1:
                    if s == '==':
                        condition.insert(1, '=')
                    condition.insert(1, s)

                    condition[2] = condition[2].strip()

                    if condition[2][0] == '\'' and condition[2][-1] == '\'':
                        condition[2] = condition[2].strip('\'')
                    else:
                        condition[2] = condition[2]

                    return condition

            return []
