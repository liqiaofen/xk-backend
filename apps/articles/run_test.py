class A:
    def fun(self):
        print('AAAAAAAAAAAA')


class B:
    def fun(self):
        print('BBBBBBBBBBBBBB')


class C(B, A):
    pass


C().fun()
