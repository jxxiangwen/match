__author__ = 'jxxia'

from multiprocessing import Process, Queue
import os, time, random


def write(q):
    print('process %s writing!' % os.getpid())
    for value in ['a', 'b', 'c']:
        q.put(value)
        print('put %s to queue...' % value)
        time.sleep(random.random())


def read(q):
    print(('process %s reading' % os.getpid()))
    while True:
        value = q.get(True)
        print('get %s from queue' % value)


if __name__ == '__main__':
    q = Queue()
    readProcess = Process(target=read, args=(q,))
    writeProcess = Process(target=write, args=(q,))

    writeProcess.start()
    readProcess.start()

    writeProcess.join()

    readProcess.terminate()
