data_str = '2022-11'
import datetime

c = datetime.datetime.strptime(data_str, "%Y-%m")
print(c)
