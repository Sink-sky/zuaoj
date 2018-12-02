config = {
    'SQL_HOSTNAME': 'localhost',
    'SQL_USERNAME': 'root',
    'SQL_PASSWORD': 'root',
    'SQL_DATABASE': 'zuaoj',
    'SECRET_KEY': 'j\x1c\t\x01\x9b,3\x02\xea\xc4\x96d\xbbDEa\x99\xda\xc5\xc8D\xcb\xf3\xc2',
    'SESSION_LIFETIME': 1,
    'STATIC_FOLDER': 'app/static',
    'SERVER_HOST': '0.0.0.0',
    'SERVER_PORT': '5000',
    'DEBUG': True,
    'LOGGER_PATH': 'app.log',
    'PROCESS_LIMIT': 8,
    'IMAGE_NAME': 'ubuntu-with-jdk'
}


class G(object):
    STATUS_PUBLIC = 0
    STATUS_PRIVATE = 1
    STATUS_HIDDEN = 2

    ALLOW_ACCESS = 3
    PERMISSION_DENIED = 4
    DATE_DENIED = 5
    DATE_PAST_DENIED = 6

    STAGE_NOT_STARTED = 6
    STAGE_RUNNING = 7
    STAGE_END = 8

    PROBLEM_ID_DIVISION = 10000

    OJ_AC = 0
    OJ_WA = 1
    OJ_PE = 2
    OJ_TL = 3
    OJ_ML = 4
    OJ_CE = 5
    OJ_WT = 6

    LANG_C = 0
    LANG_CPP = 1
    LANG_JAVA = 2
    LANG_PYTHON3 = 3

    RUNTIME_ERROR_FLAG = '#ERROR#'
    TEST_POINT_DIVIDE = '#NEXT#'
