import asyncio
from concurrent.futures import ThreadPoolExecutor
from sched import scheduler
from task import NotifierType, Task, TaskState
from DB import Database,TaskData
import time
import datetime
import threading
import os

db = Database()
pool=ThreadPoolExecutor()

class Schedule:
    def __init__(self,notifier:NotifierType=None, interval=60) -> None:
        self.tasks: dict[int, Task] = {}
        self.interval = interval
        self.thread = None
        self.stopped = False
        self.notifier=notifier
        self.envs = {}
        self._load_task()
        self._load_envs()

    def _create_task(self,task:TaskData):
        self.tasks[task.id] = Task(task.id, task.name, task.cmd, task.cron,self.notifier)


    def _load_task(self):
        for task in db.get_all_tasks():
            self._create_task(task)

    def _load_envs(self):
        for item in db.get_all_envs():
            key, val = item.key, item.value
            self.envs[key] = val
            os.environ[key] = val
            print('Set Env:', key, val)

    def add_task(self, name: str, cmd: str, cron: str):
        task = db.add_task(name, cmd, cron)
        self._create_task(task)
        return self.tasks[task.id]

    def update_task(self, tid: int, name, cmd, cron):
        task = db.update_task(tid, name, cmd, cron)
        if task:
            self.tasks[tid] = Task(tid, name, cmd, cron)
        return self.tasks[tid]

    def remove_task(self, tid: int):
        db.delete_task(tid)
        self.tasks.pop(tid)
        return tid

    # def get_all_envs(self):
    #     return self.envs

    def add_or_update_env(self, key, val):
        db.add_or_update_env(key, val)
        self.envs[key] = val
        os.environ[key] = val
        return {'key':key,'value':val}

    def remove_env(self, key):
        db.delete_env(key)
        del self.envs[key]
        del os.environ[key]
        return True

    def _run(self):
        while not self.stopped:
            cur_timestamp = time.time()
            print(f'{datetime.datetime.fromtimestamp(cur_timestamp)}:running loops...')
            for task in self.tasks.values():
                if cur_timestamp > task.next_timestamp:
                    # print('Execute:'+task.cmd_args)
                    task.execute_async()

            time.sleep(self.interval)

    async def loop(self):
        while not self.stopped:
            cur_timestamp = time.time()
            print(f'{datetime.datetime.fromtimestamp(cur_timestamp)}:running loops...')
            for task in self.tasks.values():
                if cur_timestamp > task.next_timestamp:
                    # print('Execute:'+task.cmd_args)
                    pool.submit(task.execute_sync)

            await asyncio.sleep(self.interval)

    def start_loop(self):
        asyncio.run(self.loop())

    def start_loop_async(self):
        pool.submit(self.start_loop)

    def run(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.stopped = True
        # self.thread.join()
        print('Schedule Stopped!')
