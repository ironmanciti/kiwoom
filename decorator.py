# -*- coding: utf-8 -*-
def decorator_function(original_function):
    def wrapper_function(*args, **kwargs):  #1
        print ('{} 함수가 실행되었습니다.'.format(original_function.__name__))
        return original_function(*args, **kwargs)  #2
    return wrapper_function

def display():
    pass
def display_info(name, age):
    print ('display_info({}, {}) 함수가 실행됐습니다.'.format(name, age))
display_1 = decorator_function(display)
display_info = decorator_function(display_info)

display_1()
display_info('John', 25)

# @decorator_function
# def display():
#     pass
#
# @decorator_function
# def display_info(name, age):
#     print ('display_info({}, {}) 함수가 실행됐습니다.'.format(name, age))
#
# display()
# print
# display_info('John', 25)

"""
display 함수가 실행되었습니다.
display_info 함수가 실행되었습니다.
display_info(John, 25) 함수가 실행됐습니다.
"""
