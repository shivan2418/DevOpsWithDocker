import  threading
import time
from threading import Lock

import queue

FILENAME = 'time.txt'

num = 0

def write_the_time(*arg):

    lock = Lock()

    for i in range(1000):

        print(f'Preparing to open file')
        try:
            # num = content[-1]
            # num = int(num)+1
            lock.acquire()
            global num
            num += 1
            lock.release()

        except Exception as e:
            print(e)
            num = 0

        with open(FILENAME,'a+') as file:
            #file.seek(0)
            #content = file.readlines()

            file.write(f'{num}\n')
            print(f'Writing {num}')
        time.sleep(1)
        print(f'{str(threading.currentThread())} sleeping for one 1 second')


t1 = threading.Thread(target=write_the_time,args=['T1'],name='T1',daemon=True)
t2 = threading.Thread(target=write_the_time,args=['T2'],name='T2',daemon=True)
t3 = threading.Thread(target=write_the_time,args=['T3'],name='T3',daemon=True)
t4 = threading.Thread(target=write_the_time,args=['T4'],name='T4',daemon=True)


t1.start()
t2.start()
t3.start()
t4.start()


time.sleep(600000)


