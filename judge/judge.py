import sys
sys.path.append('..')
import os
import time
from web.config import config
from web.lib.flask_extend import SimplifyMysql
from web.config import G


class Judge(object):
    def __init__(self, submit):
        self.submit_id = submit[0]
        self.problem_id = submit[1]
        self.language = submit[2]
        self.username = submit[3]
        self.time = submit[4]
        self.source_code = submit[5]

        self.db = None

        self.test_input = ''
        self.test_output = ''
        self.time_limit = 0
        self.memory_limit = 0
        self.submit_users = ''
        self.accepted_users = ''

        self.result_status = ''
        self.compile_info = ''

        self.run_path = 'work/'

        self.echo_s = ''

        self.echo('submit_id:' + str(self.submit_id))
        self.echo('problem_id:' + str(self.problem_id))
        self.echo('language:' + str(self.language))
        self.echo('username:' + self.username)
        self.echo('time:' + self.time.strftime("%Y-%m-%d %H:%M:%S"))

        self.start_time = time.time()
        self.begin_time = time.time()

    def echo(self, s):
        if not self.echo_s:
            self.echo_s += '-' * 20 + '\n'
        self.echo_s += s + '\n'

    def echo_log(self):
        self.echo_s += '-' * 20 + '\n'
        print(self.echo_s)

    def get_problem(self):
        table = 'problem'
        conditions = [['problem_id', '=', str(self.problem_id)]]

        problem = self.db.select(table, conditions)[0]

        self.test_input = problem[8]
        self.test_output = problem[9]
        self.time_limit = problem[10]
        self.memory_limit = problem[11]
        self.submit_users = problem[17] if problem[17] else ''
        self.accepted_users = problem[18] if problem[18] else ''

    def put_result(self):
        table = 'result'

        data = dict()
        data['submit_id'] = self.submit_id
        data['problem_id'] = self.problem_id
        data['language'] = self.language
        data['username'] = self.username
        data['time'] = self.time
        data['result_status'] = self.result_status
        data['source_code'] = self.source_code
        data['compile_info'] = self.compile_info

        submit_users_ls = self.submit_users.split(';')
        accepted_users_ls = self.accepted_users.split(';')

        is_submit = False
        for user in submit_users_ls:
            if user == self.username:
                is_submit = True
                break

        is_accepted = False
        for user in accepted_users_ls:
            if user == self.username:
                is_accepted = True
                break

        is_accept = True
        for f in self.result_status.split(';')[0].split(','):
            if not f == str(G.OJ_AC):
                is_accept = False
                break

        self.db.insert(table, data)

        if not is_submit:
            if submit_users_ls:
                submit_users_ls.append(self.username)
            else:
                submit_users_ls = [self.username]

            self.db.execute('''UPDATE problem SET submit=submit+1, submit_users=%s WHERE problem_id=%s''',
                            (';'.join(submit_users_ls), self.problem_id))
            self.db.execute('''UPDATE user SET submit=submit+1 WHERE username=%s''', (self.username,))

        if (not is_accepted) and is_accept:
            if accepted_users_ls:
                accepted_users_ls.append(self.username)
            else:
                accepted_users_ls = [self.username]

            self.db.execute('''UPDATE problem SET accepted=accepted+1, accepted_users=%s WHERE problem_id=%s''',
                            (';'.join(accepted_users_ls), self.problem_id))
            self.db.execute('''UPDATE user SET accepted=accepted+1 WHERE username=%s''', (self.username,))

        self.db.commit()

    def compile_code(self):
        if not os.path.exists(self.run_path + str(self.submit_id)):
            os.mkdir(self.run_path + str(self.submit_id))

        if self.language == G.LANG_C:
            with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.c', 'w') as f:
                f.write(self.source_code)

            path_header = self.run_path + str(self.submit_id) + '/' + str(self.submit_id)
            os.system('gcc -w {0}.c -o {0} > {0}.log 2>&1'.format(path_header))

        elif self.language == G.LANG_CPP:
            with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.cpp', 'w') as f:
                f.write(self.source_code)

            path_header = self.run_path + str(self.submit_id) + '/' + str(self.submit_id)
            os.system('g++ -w {0}.cpp -o {0} > {0}.log 2>&1'.format(path_header))

        elif self.language == G.LANG_JAVA:
            with open(self.run_path + str(self.submit_id) + '/' + 'Main' + '.java', 'w') as f:
                f.write(self.source_code)

            path_header = self.run_path + str(self.submit_id) + '/'
            os.system('javac {0}Main.java > {0}{1}.log 2>&1'.format(path_header, self.submit_id))

        elif self.language == G.LANG_PYTHON3:
            with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.py', 'w') as f:
                f.write(self.source_code)
            return True

        with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.log', 'r') as f:
            self.compile_info = ''.join(f.readlines())
        if self.compile_info:
            return False

        return True

    def create_shell(self):
        shell_header = r'''#! /bin/bash
function getTiming() {
start=$1
end=$2

start_s=$(echo $start | cut -d '.' -f 1)
start_ns=$(echo $start | cut -d '.' -f 2)
end_s=$(echo $end | cut -d '.' -f 1)
end_ns=$(echo $end | cut -d '.' -f 2)

time=$(( ( 10#$end_s - 10#$start_s ) * 1000 + ( 10#$end_ns / 1000000 - 10#$start_ns / 1000000 ) ))

echo "$time"
}
'''
        shell_content = r'''
start=$(date +%s.%N)
{0} < {1}.in > {1}.out
if [ "$?" != "0" ]
then
    echo '{2}' > {1}.out
fi
end=$(date +%s.%N)

ret=$(getTiming $start $end)
echo "$ret" > {1}.time
'''
        startup_program = ''
        path_header = './' + self.run_path + str(self.submit_id) + '/' + str(self.submit_id)

        if self.language == G.LANG_C or self.language == G.LANG_CPP:
            startup_program = './' + self.run_path + str(self.submit_id) + '/' + str(self.submit_id)
        elif self.language == G.LANG_JAVA:
            startup_program = 'java -cp ' + self.run_path + str(self.submit_id) + ' Main.class'
        elif self.language == G.LANG_PYTHON3:
            startup_program = 'python3 ' + './' + self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + \
                              '.py'

        with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.sh', 'w') as f:
            f.write(shell_header + shell_content.format(startup_program, path_header, G.RUNTIME_ERROR_FLAG))

    def run_docker(self):
        self.echo('run docker')
        run = 'docker run -d -v $PWD:/usr/src/myapp -w /usr/src/myapp --name=judge_{1} {0} bash ./{2}{1}.sh'.format(
                config['IMAGE_NAME'], self.submit_id, self.run_path + str(self.submit_id) + '/')
        os.system(run)

    def inspect_docker(self):
        t = time.time()
        docker_status = ''

        while time.time() - t < float(self.time_limit / 1000):
            p = os.popen('docker inspect -f={{.State.Running}} judge_' + str(self.submit_id))
            docker_status = p.read()
            p.close()
            if docker_status == 'false\n':
                break

        if docker_status != 'false\n':
            os.system('docker kill judge_{}'.format(self.submit_id))

        p = os.popen('docker inspect -f={{.State.ExitCode}} judge_' + str(self.submit_id))
        exit_code = p.read()
        p.close()

        os.system('docker rm judge_{} > /dev/null'.format(self.submit_id))

        if exit_code != '0\n':
            return '-2'

        with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.time', 'r') as f:
            run_time = f.readline().strip('\n')

        if not run_time or float(run_time) > float(self.time_limit):
            run_time = '-1'
        return run_time

    def test_program(self):
        test_output_ls = self.test_output.split(G.TEST_POINT_DIVIDE)
        if self.test_input:
            test_input_ls = self.test_input.split(G.TEST_POINT_DIVIDE)
        else:
            test_input_ls = []
            for i in range(len(test_output_ls)):
                test_input_ls.append('')

        time_ls = []
        test_point_count = 0

        self.create_shell()

        self.echo('test point count:' + str(len(test_input_ls)))
        for (test_input, test_output) in zip(test_input_ls, test_output_ls):
            with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.in', 'w') as f:
                f.write(test_input)

            with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.out', 'w'):
                pass

            with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.time', 'w'):
                pass

            self.run_docker()

            time_ls.append(self.inspect_docker())
            if time_ls[-1] == '-1':
                self.result_status += str(G.OJ_TL) + ','
                time_ls[-1] = '0'
                continue
            elif time_ls[-1] == '-2':
                self.result_status += str(G.OJ_PE) + ','
                time_ls[-1] = '0'
                continue

            with open(self.run_path + str(self.submit_id) + '/' + str(self.submit_id) + '.out', 'r') as f:
                output = ''.join(f.readlines())

            output = output.strip('\n').strip('\r\n').strip('\r')
            test_output = test_output.strip('\n').strip('\r\n').strip('\r').replace('\r\n', '\n')

            if output == G.RUNTIME_ERROR_FLAG:
                self.result_status += str(G.OJ_PE)
            elif output == test_output:
                self.result_status += str(G.OJ_AC)
            else:
                self.result_status += str(G.OJ_WA)
            self.result_status += ','

            self.echo('test point {}:'.format(test_point_count))
            test_point_count += 1
            self.echo('correct output:')
            self.echo(test_output)
            self.echo('output:')
            self.echo(output)

            self.echo("test point {} time: ".format(test_point_count) + str((time.time() - self.begin_time) * 100)
                      + " ms")
            self.begin_time = time.time()

        self.result_status = self.result_status[:-1] + ';'
        self.result_status += ','.join(time_ls)

    def clear_file(self):
        os.system('rm -rf ./' + self.run_path + str(self.submit_id))

    def close_db(self):
        self.db.close()

    def run(self):
        self.db = SimplifyMysql(config['SQL_HOSTNAME'], config['SQL_USERNAME'], config['SQL_PASSWORD'],
                                config['SQL_DATABASE'])
        self.db.connect()

        self.echo("connect db time: " + str((time.time() - self.begin_time) * 100) + " ms")
        self.begin_time = time.time()

        if not os.path.exists(self.run_path):
            os.mkdir(self.run_path)

        self.echo('get problem')
        self.get_problem()

        self.echo("get problem time: " + str((time.time() - self.begin_time) * 100) + " ms")
        self.begin_time = time.time()

        self.echo('compile code')
        if not self.compile_code():
            self.echo('compile error')
            self.result_status = str(G.OJ_CE)
        else:
            self.echo("compile code time: " + str((time.time() - self.begin_time) * 100) + " ms")
            self.begin_time = time.time()

            self.echo('test program')
            self.test_program()

        self.echo('result_status:')
        self.echo(self.result_status)
        self.echo('put result')
        self.put_result()

        self.echo("put result time: " + str((time.time() - self.begin_time) * 100) + " ms")
        self.begin_time = time.time()

        self.clear_file()
        self.close_db()

        self.echo("total time time: " + str((time.time() - self.start_time) * 100) + " ms")

        self.echo_log()


if __name__ == '__main__':
    db = SimplifyMysql(config['SQL_HOSTNAME'], config['SQL_USERNAME'], config['SQL_PASSWORD'], config['SQL_DATABASE'])
    db.connect()

    judge_table = 'submit'
    judge_submit = db.select(judge_table, limit=1)[0]
    db.close()

    judge = Judge(judge_submit)
    judge.run()
