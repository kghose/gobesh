class A:
  def f1(self):
    print 'AF1'
    
class B(A):
  def f1(self):
    A.f1(self)
    print 'BF1'
    
b = B()
b.f1()