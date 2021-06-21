#!/usr/bin/env python3

import threading
from subprocess import Popen, PIPE
from time import sleep as t_sleep
import sys


proc = Popen(['python', 'test_subproc.py'], bufsize=1,
             stdout=PIPE, stdin=PIPE, universal_newlines=True)
print('proc started')

t_sleep(2)

# print('done sleep')
# print(proc.stdout)
# print(proc.stdout.line_buffering)


def write_commands():
    proc.stdin.write(
        'add playlist:https://st01.sslstream.dlf.de/dlf/01/high/aac/stream.aac\n')
    proc.stdin.write(
        'add playlist:https://www.antennebrandenburg.de/live.m3u\n')
    proc.stdin.write('set playlist pos:0\n')
    proc.stdin.write('unmute:\nunpause:\n')

    proc.stdin.flush()

    while True:
        command = sys.stdin.readline()[:-1]
        print('send command: ' + command)
        proc.stdin.write(command + '\n')
        proc.stdin.flush()

        # t_sleep(10)

        # proc.stdin.write('prev:\n')
        # proc.stdin.flush()

        # t_sleep(10)


tag_thread = threading.Thread(target=write_commands)
tag_thread.start()


def read_proc():
    while True:
        data = proc.stdout.readline()[:-1]
        print('data from process:')
        print("'" + data + "'")


tag_thread = threading.Thread(target=read_proc)
tag_thread.start()


# asyncio.run(test())


# p = Popen(['python', 'test_subproc.py'], stderr=PIPE, universal_newlines=True)


# def execute(cmd):
#     popen = Popen(
#         cmd, stdout=PIPE, universal_newlines=True)
#     for stdout_line in iter(popen.stdout.readline, ""):
#         yield stdout_line
#     popen.stdout.close()
#     # return_code = popen.wait()
#     # if return_code:
#     #     raise subprocess.CalledProcessError(return_code, cmd)


# # Example
# for path in execute(['python', 'test_subproc.py']):
#     print(path, end="")


####
# with Popen(['python', 'test_subproc.py'], stdout=PIPE, bufsize=1,
#            universal_newlines=True) as p:
#     for line in p.stdout:
#         print(line, end='')


# p = Popen(['python', 'test_subproc.py'], stdout=PIPE, bufsize=1)
# print('proc started')
# with p.stdout:
#     for line in iter(p.stdout.readline, b''):
#         print(line)
# p.wait()  # wait for the subprocess to exit
