import threading
def hello():
    print "hello, world"

t = threading.Timer(5.0, hello)
t.start() # aft
print "Hello before"
t.stop()
t.start()