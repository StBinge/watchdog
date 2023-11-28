from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
from pydantic import BaseModel
from Schedule import Schedule
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import asyncio

from task import Task, TaskState

class NewTaskItem(BaseModel):
    name:str
    command: str
    cron: str

class NewEnvItem(BaseModel):
    key:str
    value:str

Base_Dir=Path(__file__).parent
static_dir=Base_Dir/'web_ui/dist'


app = FastAPI()
app.mount('/assets',StaticFiles(directory=static_dir/'assets'),name='assets')

def task_notifier(task:Task):
    global ws
    data=task.info()
    print('Notify task:',data)
    if ws:
        try:
            t=ws.send_json(data)
            asyncio.run(t)
            print('Send task data:',data)
        except WebSocketDisconnect:
            print('ws is closed, send msg failed!')
            ws=None
    else:
        print('ws not ready:',ws,ws.state)

schedule = Schedule(task_notifier,30)


def stop_schedule():
    print('Stopping schedule...')
    schedule.stop()


app.add_event_handler('shutdown', stop_schedule)

@app.get('/')
async def index():
    index_path=static_dir/'index.html'
    return FileResponse(index_path)

@app.get('/tasks')
async def get_all_tasks():
    return [t.info() for t in schedule.tasks.values()]

# @app.post('/task')
# async def add_task(item: NewTaskItem):
#     task = schedule.add_task(item.name,item.command, item.cron)
#     return task.info()

@app.post('/task')
async def add_or_update_task(id:int=-1,item:NewTaskItem=None):
    if id<0:
        return schedule.add_task(item.name,item.command, item.cron).info()
    return schedule.update_task(id,name=item.name,cmd=item.command,cron=item.cron).info()

@app.get('/task')
async def get_task_info(id: int):
    return schedule.tasks[id].info()


@app.delete('/task')
async def delete_task(id: int):
    return schedule.remove_task(id)


@app.get('/execute')
async def execute_task(id: int):
    task=schedule.tasks[id]
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

ws:WebSocket=None
@app.websocket('/task')
async def connect_ws(websocket:WebSocket):
    global ws
    await websocket.accept()
    print('ws connected.')
    ws=websocket
    while True:
        data=await websocket.receive_text()
        print('Receive ws:',data)

if __name__ == '__main__':
    schedule.run()
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=9191)
