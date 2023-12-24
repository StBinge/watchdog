from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from Schedule import Schedule
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,PlainTextResponse
from pathlib import Path
import asyncio
from task import Task,TaskState
from threading import Lock
import json


class NewTaskItem(BaseModel):
    name:str
    command: str
    cron: str

class NewEnvItem(BaseModel):
    key:str
    value:str

Base_Dir=Path(__file__).parent
static_dir=Base_Dir/'dist'


app = FastAPI()
app.mount('/assets',StaticFiles(directory=static_dir/'assets'),name='assets')

# NotifyQueue:list[Task]=[]
TaskSet:set[int]=set()
QueueLock=Lock()

def task_notifier(task:Task):
    with QueueLock:
        TaskSet.add(task.id)

schedule = Schedule(task_notifier,60*60)

async def stop_schedule():
    print('Stopping schedule...')
    schedule.stop()
    # schedule.stopped=True


# app.add_event_handler('startup', start_schedule)
app.add_event_handler('shutdown', stop_schedule)

@app.get('/')
async def index():
    index_path=static_dir/'index.html'
    return FileResponse(index_path)

@app.get('/tasks')
async def get_all_tasks():
    with QueueLock:
        TaskSet.clear()
    return [t.info() for t in schedule.tasks.values()]


@app.post('/task')
async def add_or_update_task(id:int=-1,item:NewTaskItem=None):
    if id<0:
        ok,data= schedule.add_task(item.name,item.command, item.cron)
    else:
        ok,data=schedule.update_task(id,name=item.name,cmd=item.command,cron=item.cron)

    if ok:
        return data.info()
    else:
        return PlainTextResponse(content=data,status_code=400)
    
@app.get('/task')
async def get_task_info(id: int):
    return schedule.tasks[id].info()


@app.delete('/task')
async def delete_task(id: int):
    return schedule.remove_task(id)


@app.get('/execute')
async def execute_task(id: int):
    task=schedule.tasks[id]
    if task.state==TaskState.Running:
        return task.info()
    task.execute_async()
    return task.info()

@app.post('/env')
async def add_or_update_env(item:NewEnvItem):
    return schedule.add_or_update_env(key=item.key,val=item.value)

@app.get('/env')
async def get_envs():
    all_envs=schedule.envs
    return [{'key':k,'value':v} for k,v in all_envs.items()]

@app.delete('/env')
async def delete_env(key:str):
    return schedule.remove_env(key)


@app.websocket('/task')
async def connect_ws(websocket:WebSocket):
    await websocket.accept()
    print('ws connected.')
    while True:
        with QueueLock:
            task_ids=list(TaskSet)
            TaskSet.clear()
        for tid in task_ids:
            task=schedule.tasks[tid]
            print(f'Send Task{task.name} Data')
            await websocket.send_text(json.dumps(task.info()))
        
        await asyncio.sleep(1)
        

if __name__ == '__main__':
    schedule.run_async()
    # schedule.start_loop_async()

    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=9191)
