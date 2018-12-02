import sys
sys.path.append('..')
from web.app.models import *
from web.config import config, G
import datetime


db = SimplifyMysql(config['SQL_HOSTNAME'], config['SQL_USERNAME'], config['SQL_PASSWORD'], config['SQL_DATABASE'])
db.connect()
BaseModel.set_db(db)

test_code = r'''
#include<stdio.h>

int main ()
{
  int i;
  for(i=0; i<100000000; i++)
    continue;
  printf("2\n");
  return 0;
}
'''

submit = dict()

submit['submit_id'] = 1000
submit['problem_id'] = 100
submit['language'] = G.LANG_C
submit['username'] = 'test'
submit['time'] = datetime.datetime.now()
submit['source_code'] = test_code

submit_count = 1

for i in range(submit_count):
    submit['submit_id'] = 1000
    SubmitModel().add(submit)
