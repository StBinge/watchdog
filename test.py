import datetime
import time
import os
from task import Task
from enum import Enum

os.environ['env0'] = 'value0'
task1 = Task(
    0, 'python C:\code_project\watchdog\TestScripts\script1.py', '* * * * *')
task2 = Task(0, 'node C:\code_project\watchdog\TestScripts\js1.js', '* * * * *')
# task1.execute_async()
print(task1.info())
task2.execute_sync()
print(task2.info())
time.sleep(1)
os.environ['env1'] = 'value1'
os.environ['env0'] = 'value0-1'
time.sleep(10)
print(task1.info())
print(task2.info())


class TaskState(Enum):
    Idle = 1
    Runing = 2
    Completed = 3
    Error = 4
