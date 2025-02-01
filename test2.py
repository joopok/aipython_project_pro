'''
한국사람은 지ㅁ 이자에 없습니다.
'''

# print("hi python")


# def test():
#     for i in range(1, 10):
#         print(i * 2)


# test()


# def test2():
#     letter = "im boy"
#     print(letter + " {} {}은 프로그램을 싫어합니다.".format("java", "jsp"))


# test2()


scope = {"만수": "20", "철수": "22", "영희": "30"}
print(scope["철수"])

for i in scope:
    val = scope[i]
    print(val)


items = scope.items()
print(items)

itemsList = list(items)

print(itemsList)
