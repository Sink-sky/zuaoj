from judge import Judge
import sys
sys.path.append('..')
import time
from multiprocessing import Pool
from web.config import config
from web.lib.flask_extend import SimplifyMysql
from datetime import datetime
import signal


class JudgeService(object):
    def __init__(self, is_test=False):
        self.db = SimplifyMysql(config['SQL_HOSTNAME'], config['SQL_USERNAME'], config['SQL_PASSWORD'],
                                config['SQL_DATABASE'])

        self.is_test = is_test
        self.pool = Pool(config['PROCESS_LIMIT'])
        self.submit = []
        self.submit_ls = []
        self.begin_date = None

    def pick_queen(self):
        self.db.connect()
        table = 'submit'

        self.submit_ls = self.db.select(table)

        if self.submit_ls:
            self.submit = self.submit_ls[0]
            condition = ['submit_id', '=', self.submit[0]]
            self.db.delete(table, [condition])
            self.db.commit()
        else:
            self.submit = []

        self.db.close()

    @staticmethod
    def judge_done(res):
        # print('a judge done')
        pass

    def start_judge(self):
        judge = Judge(self.submit)

        self.pool.apply_async(judge.run, callback=JudgeService.judge_done)

    def stop_service(self):
        self.pool.close()
        self.pool.join()

        end_date = datetime.now()
        print('end at:', end='')
        print(end_date)
        print('time:', end='')
        print((end_date - self.begin_date).seconds)

        exit(0)

    def run(self):
        signal.signal(signal.SIGINT, self.stop_service)

        self.begin_date = datetime.now()
        print('begin at:', end='')
        print(self.begin_date)

        while True:
            self.pick_queen()
            if self.submit:
                self.start_judge()
                self.submit = []
            else:
                time.sleep(0.5)


if __name__ == '__main__':
    judge_service = JudgeService()
    judge_service.run()
