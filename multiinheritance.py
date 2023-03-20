class A:
  def __init__(self, text):
    self.text = text

class B:
  def __init__(self, num):
    self.num = num

  def do_something(self, *args):
    pass

class C(B,A):
  def __init__(self, num ,text):
    A.__init__(self, text)
    B.__init__(self, num)
    print(f'text: {self.text}, num: {self.num}')

  def do_something2(self, num, num2):
    return f"num: {num}, num2: {num2}"

c = C(1, 'ahoj')
print(f'{c}')
print(f'{c.do_something(1,2)}')
