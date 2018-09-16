a = 3
b = 4

def hap(a, b):
    return a+b+1

print("hap")
result = hap(a,b)

print('3+4=', result)

mylist1 = [0, 1,2,3]
mylist2 = ['a', 'b', 'c']

def debug_me(in_list):
    print(in_list[0])
    print(in_list[1])
    print(in_list[2])
    print(in_list[3])

debug_me(mylist1)
debug_me(mylist2)