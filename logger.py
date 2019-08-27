#coding:utf-8
import logging
from datetime import datetime
import os
from config import LOGER_PATH

# error log
logger_debug = None
# action log
logger_action = None
# run time log
logger_time = None

def init_log(level=logging.DEBUG, type='debug'):
    logger = None
    if logger:
        return
    name = datetime.today().strftime('%Y-%m-%d')
    logger = logging.getLogger(type+'-'+name)
    logger.setLevel(level) #日志等级
    if not os.path.isdir(LOGER_PATH):
        os.mkdir(LOGER_PATH)

    fh = logging.FileHandler(os.path.join(LOGER_PATH,'%s_%s.log' % (name, type)))
    formatter = logging.Formatter('%(asctime)s-%(filename)s-L%(lineno)d-%(name)s:%(message)s \n'+ '-'*100)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    if type == 'debug':
        global logger_debug
        logger_debug = logger
        return logger_debug
    elif type == 'action':
        global logger_action
        logger_action = logger
        return logger_action
    elif type == 'time':
        global logger_time
        logger_time = logger
        return logger_time

def _get_debug_logger():
    global logger_debug
    if not logger_debug:
        logger_debug = init_log(type='debug')
    return logger_debug

def _get_action_logger():
    global logger_action
    if not logger_action:
        logger_action = init_log(type='action')
    return logger_action

def _get_time_logger():
    global logger_time
    if not logger_time:
        logger_time = init_log(type='time')
    return logger_time

def log_debug(message):
    print(message)
    _get_debug_logger().log(logging.DEBUG, message)

def log_action(message):
    print(message)
    _get_action_logger().log(logging.INFO, message)

def log_time(message):
    _get_time_logger().log(logging.INFO, message)


if __name__ == '__main__':
    log_time('test')