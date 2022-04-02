from queue import Queue
import threading
import random
import time


task_queue = Queue()

def do_task(queue):

    while not queue.empty():

        task = queue.get()
        time.sleep(task)
        queue.task_done()



    print('Stopping Queue empty')


num_workers = 5

random.seed(123)

# put tasks into the queue

for i in range(50):
    task_queue.put(random.uniform(0.1,1))

for i in range(num_workers):
    workers = [threading.Thread(name=str(i),target=do_task,args=[task_queue]) for i in range(num_workers)]
    for w in workers:
        w.start()
    for w in workers:
        w.join()



