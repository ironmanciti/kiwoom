# -*- coding: utf-8 -*-
import datetime
import time

def my_logger(original_function):
    import logging
    logging.basicConfig(filename='{}.log'.format(original_function.__name__), level=logging.INFO)

    def wrapper(*args, **kwarg):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        logging.info(
            '[{}] 실행결과 args - {}, kwarg - {}'.format(timestamp, args, kwarg)
        )
        return original_function(*args, **kwarg)

    return wrapper

@my_logger
def display_info(name, age):
    time.sleep(2)
    print('display_info ({}, {}) 함수가 실행되었습니다.'.format(name, age))

display_info('영제',50)
