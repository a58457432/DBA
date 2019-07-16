#!/usr/bin/env python
## coding=utf-8
# Creator: shenjinhong
# UpdateTime:2019.6.10

import threading
import time

exitFlag = 0

class myThread(threading.Thread):
    def __init__(self, threadID, name , counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter


    def run(self):
        print("starting " + self.name)
        print("Exiting" + self.name)



thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)


thread1.start()
thread2.start()

print("Exiting Main Thread")
