import datetime,time
import crontab as Crontab
import subprocess,threading
from enum import Enum

class TaskState(Enum):
    Idle=1
    Runing=2
    Completed=3
    Error=4

# class TaskInfo:
#     def __init__(self,task:'Task') -> None:
#         if task.state==TaskState.Runing:
#             self.state='running'
#         else:



class Task:
    def __init__(self,tid:int,cmd_args:list[str],cron:str,name=str) -> None:
        # self.task_id=int(datetime.datetime().now().timestamp())
        self.id=tid
        self.cmd_args=cmd_args
        self.cron=cron
        self.crontab=Crontab.parse(cron)
        self.stdout=''
        self.stderr=''
        self.state=TaskState.Idle
        self.next_time=str(self.crontab.next)
        self.prev_time=''
        self.next_run_timestamp=self.crontab.next.timestamp()
    
    # def calc_next_time(self,prev_timestamp:int):
    #     # cur_time=time.time()
    #     while True:
    #         nxt=self.crontab.next.timestamp()
    #         if nxt<=prev_timestamp:
    #             continue


    def _execute(self):
        '''执行任务,并更新下一次运行时间
        '''
        print(f'Executing task[{self.id}]:'+self.cmd_args)
        self.state=TaskState.Runing
        self.stdout, self.stderr = subprocess.Popen(self.cmd_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True).communicate()
        self.prev_time=str(datetime.datetime.now())
        self.next_run_timestamp=self.crontab.next.timestamp()
        self.next_time=str(datetime.datetime.fromtimestamp(self.next_run_timestamp))
        if self.stderr:
            self.state=TaskState.Error
        else:
            self.state=TaskState.Completed
        print(f'Task[{self.id}] Executed:\n',str(self.info()))
    
    def execute(self):
        thread=threading.Thread(target=self._execute)
        thread.start()
    
    def info(self):
        ret={}
        ret['id']=self.id
        if self.state==TaskState.Runing:
            ret['state']='running'
            ret['detail']=''
        elif self.state==TaskState.Idle:
            ret['state']='idle'
            ret['detail']=''
        elif self.state==TaskState.Completed:
            ret['state']='ok'
            ret['detail']=self.stdout
        elif self.state==TaskState.Error:
            ret['state']='error'
            ret['detail']=self.stderr
        else:
            ret['state']='unknown'
            ret['detail']=f'unknow task state [{self.state}]'

        return ret