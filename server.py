from fastapi import FastAPI
from pydantic import BaseModel
from Schedule import Schedule


class TaskItem(BaseModel):
    cmd: str
    cron: str

class EnvItem(BaseModel):
    key:str
    val:str

app = FastAPI()
schedule = Schedule(10)


def stop_schedule():
    print('Stopping schedule...')
    schedule.stop()


app.add_event_handler('shutdown', stop_schedule)


@app.post('/task')
async def add_task(item: TaskItem):
    task = schedule.add_task(item.cmd, item.cron)
    return task.id


@app.get('/task')
async def get_task_info(id: int):
    return schedule.tasks[id].info()


@app.delete('/task')
async def delete_task(id: int):
    return schedule.remove_task(id)


@app.get('/execute')
async def execute_task(id: int):
    task=schedule.tasks[id]
    task.execute_sync()
    return task.info()

@app.post('/env')
async def add_or_update_env(item:EnvItem):
    return schedule.add_or_update_env(key=item.key,val=item.val)

@app.get('/env')
async def get_envs():
    return schedule.envs

@app.delete('/env')
async def delete_env(key:str):
    return schedule.remove_env(key)

if __name__ == '__main__':
    schedule.run()
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=9191)
