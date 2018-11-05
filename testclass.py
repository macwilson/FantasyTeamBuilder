class TestClass(object):
  def __init__(self,a):
    self.a = a
    self.b = a**2
    self.c = 'title'


  def print(self):
    print("The values of this object are:")
    print(self.a, self.b, self.c)