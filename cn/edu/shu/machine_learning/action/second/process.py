__author__ = 'jxxia'

from multiprocessing import Process
import os


# child process do
def run_pro(name):
    print('child process %s,id : %s' % (name, os.getpid()))


if __name__ == '__main__':
    print('Parent process %s.' % os.getpid())
    p = Process(target=run_pro, args=('test',))
    print('child process will start!')
    p.start()
    p.join()
    print('child process end')
