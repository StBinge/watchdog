from task import Task
from DB import Database
import time
import datetime
import threading
import os

db = Database()


class Schedule:
    def __init__(self, interval=60) -> None:
        self.tasks: dict[int, Task] = {}
        self.interval = interval
        self.thread = None
        self.stopped = False
        self._load_task()
        self.envs = {}
        self._load_envs()

    def _load_task(self):
        for task in db.get_all_tasks():
            self.tasks[task.id] = Task(task.id, task.name, task.cmd, task.cron)

    def _load_envs(self):
        for item in db.get_all_envs():
            key, val = item.key, item.value
            self.envs[key] = val
            os.environ[key] = val
            print('Set Env:', key, val)

    def add_task(self, name: str, cmd: str, cron: str):
        tid = db.add_task(name, cmd, cron)
        task = Task(tid, name, cmd, cron)
        self.tasks[tid] = task
        return task

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
        cur_timestamp = time.time()
        print(f'{datetime.datetime.now()}:running loops...')
        for task in self.tasks.values():
            if cur_timestamp > task.next_timestamp:
                # print('Execute:'+task.cmd_args)
                task.execute_sync()
        if self.stopped:
            return
        time.sleep(self.interval)
        if self.stopped:
            return
        self._run()

    def run(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        self.stopped = True
        self.thread.join()
        print('Schedule Stopped!')
