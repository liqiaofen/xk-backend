import pandas as pd

mydata = {
    'sites': ['google', 'runoob', 'wiki'],
    'number': [1, 2, 3]
}
myvar = pd.DataFrame(mydata)
print(myvar)

# Series 类似表格中和的一列，类似一维数组，由索引和列组成
print('--------------------')

a = [1, 2, 'c']

# index 指定索引，默认从0开始
a_ser = pd.Series(a, index=['x', 'y', 'z'])
print(a_ser['x'])
print('----------------------')
d = {'s': "Google", 'r': "Runoob", 'w': "Wiki"}
dict_ser = pd.Series(d, index=['r', 'w'], name='xxx')
print(dict_ser)
d['r'] = '1411'
print(d)
print(dict_ser)
