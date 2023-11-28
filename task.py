import datetime
import time
import crontab as Crontab
import subprocess
import threading
from enum import Enum
from typing import Callable


class TaskState(Enum):
    Idle = 1
    Runing = 2
    Completed = 3
    Error = 4

# class TaskInfo:
#     def __init__(self,task:'Task') -> None:
#         if task.state==TaskState.Runing:
#             self.state='running'
#         else:
NotifierType=Callable[['Task'],None]

class Task:
    def __init__(self, id: int, name: str, command: str, cron: str,notifier:NotifierType=None) -> None:
        # self.task_id=int(datetime.datetime().now().timestamp())
        self.id = id
        self.name = name
        self.command = command
        self.cron = cron
        self.crontab = Crontab.parse(cron)
        self.result = ''
        # self.error=''
        self.state = TaskState.Idle
        self.next_timestamp = next(self.crontab.next()).timestamp()
        self.last_timestamp = -1
        self.notifier=notifier


    def execute_sync(self):
        '''执行任务,并更新下一次运行时间
        '''
        print(f'Executing task[{self.id}]:'+self.command)
        self.state = TaskState.Runing
        stdout, stderr = subprocess.Popen(
            self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True).communicate()
        now=datetime.datetime.now()
        self.last_timestamp = now.timestamp()
        for time in self.crontab.next():
            if time.timestamp()<self.last_timestamp:
                continue
            self.next_timestamp=time.timestamp()
            break
        # self.next_timestamp=str(datetime.datetime.fromtimestamp(self.next_run_timestamp))
        self.state = TaskState.Idle
        if stderr:
            self.result = stderr
            self.state=TaskState.Error
        else:
            self.result = stdout
        print(f'Task[{self.id}] Executed:\n', str(self.info()))
        if self.notifier:
            self.notifier(self)

    def execute_async(self):
        self.state=TaskState.Runing
        thread = threading.Thread(target=self.execute_sync)
        thread.start()


    def info(self):
        ret = {}
        info_keys = ['id', 'name', 'command', 'cron', 'result']
        for key in info_keys:
            ret[key] = self.__dict__.get(key, None)

        def convert_timestamp(stamp):
            if stamp is None or stamp < 0:
                return ''
            return str(datetime.datetime.fromtimestamp(int(stamp)))

        map_keys = [
            ['next_timestamp', 'next_time', convert_timestamp],
            ['last_timestamp', 'last_time', convert_timestamp],
            ['state', 'state', lambda x:x.name],
        ]
        for key, dst_key, convertor in map_keys:
            ret[dst_key] = convertor(self.__dict__.get(key, None))
        return ret
