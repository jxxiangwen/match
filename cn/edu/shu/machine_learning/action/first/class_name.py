__author__ = '祥文'
import nltk
class Class_Name(object):
    def __init__(self,arg):
        super(Class_Name,self).__init__()
        self.arg = arg

instance = Class_Name('NAME')

print(dir(Class_Name))
print(dir(instance))
print(Class_Name.__dict__)