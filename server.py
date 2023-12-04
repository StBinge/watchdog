from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect,WebSocketState
from pydantic import BaseModel
from Schedule import Schedule
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse,PlainTextResponse
from pathlib import Path
import asyncio
from task import Task


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

def task_notifier(task:Task):
    global ws
    print(f'Notify task[{task.name}]')
    if ws and ws.application_state==WebSocketState.CONNECTED:
        data=task.info()
        try:
            t=ws.send_json(data)
            asyncio.run(t)
            print(f'Send task[{task.name}] data')
        except WebSocketDisconnect:
            print('ws is closed, send task data failed!')
            ws=None
    else:
        print('ws not ready:',ws,ws.application_state.name)

schedule = Schedule(task_notifier,60)

# backgroud=BackgroundTasks()

# def execute(tasks:list[Task]):
#     cur_timestamp = time.time()
#     print(f'{datetime.datetime.now()}:Executing loops...')
#     for task in tasks:
#         if cur_timestamp > task.next_timestamp:
#             # print('Execute:'+task.cmd_args)
#             task.execute_async()

# async def start_schedule():
#     while not schedule.stopped:
#         backgroud.add_task(execute,args=(schedule.tasks.values(),))
#         await asyncio.sleep(schedule.interval)


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
        try:
            # await ws.receive()
            await asyncio.sleep(10)
            if not ws or ws.application_state!=WebSocketState.CONNECTED:
                return
        except:
            await ws.close()
            print('ws is closed.')
            ws=None

if __name__ == '__main__':
    # schedule.run()
    schedule.start_loop_async()
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=9191)
