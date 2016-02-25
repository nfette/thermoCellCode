import time
from threading import Timer

def print_time():
    print "From print_time", time.time()

def print_some_times2():
    print time.time()
    t1=Timer(5, print_time, ())
    t1.start()
    t2=Timer(10, print_time, ())
    t2.start()
    #time.sleep(11)  # sleep while time-delay events execute
    print time.time()
    return t1, t2

if __name__ == "__main__":
    #print_some_times()
    t1,t2=print_some_times2()
