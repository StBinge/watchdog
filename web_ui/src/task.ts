import { Ref, ref } from "vue"

export const tasks = ref<TaskInfo[]>([])
export const selected_task = ref<TaskInfo | null>()

export enum TaskState {
    Empty = 'empty',
    Idle = 'idle',
    Running = 'running',
    Error = 'error'
}

export interface TaskInfo {
    name: string
    id: number
    command: string
    cron: string
    next_time: string
    last_time: string
    result: string
    // error:string
    state: TaskState | string
    [k: string]: any
}

export function create_empty_task() {
    return {
        name: '',
        id: -1,
        command: '',
        cron: '',
        next_time: '',
        last_time: '',
        result: '',
        state: TaskState.Empty,
    } as TaskInfo
}

export async function get_task(id: number): Promise<TaskInfo> {
    let api = '/task?id=' + id
    if (import.meta.env.DEV) {
        api = '/api' + api
    }
    const res = await fetch(api)
    if (res.ok) {
        const task = await res.json() as TaskInfo
        console.debug('Get task:', task)
        return task
    }
    alert('Get task failed!')
    console.error(await res.text())
    return create_empty_task()
}

export async function get_all_tasks(): Promise<TaskInfo[]> {
    let api = '/tasks'
    if (import.meta.env.DEV) {
        api = '/api' + api
    }
    const res = await fetch(api)
    if (res.ok) {
        const tasks = await res.json() as TaskInfo[]
        console.debug(`Get tasks[${tasks.length}]`)
        return tasks
    }
    alert('Get task failed!')
    console.error(await res.text())
    return []
}

export async function add_or_update_task(tid: number, name: string, command: string, cron: string) {
    let api = '/task'
    if (import.meta.env.DEV) {
        api = '/api' + api
    }
    if (tid >= 0) {
        api += '?id=' + tid
    }
    const data = {
        name,
        command,
        cron,
    }
    const res = await fetch(api, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            // 'user-agent': 'Mozilla/4.0 MDN Example',
            'content-type': 'application/json'
        },
    })
    if (res.ok) {
        return await res.json() as TaskInfo
    }
    alert('Add or updated Task failed!')
    console.error(await res.text())
    return null
}

export async function run_task(taskid: number) {
    let api = '/execute?id=' + taskid
    if (import.meta.env.DEV) {
        api = '/api' + api
    }
    const res = await fetch(api)
    if (res.ok) {
        console.debug('Task is running.')
        const idx=tasks.value.findIndex(t=>t.id==taskid)
        tasks.value[idx].result=''
        return true
    } else {
        alert('Run task failed!')
        console.error(await res.text())
        return false
    }
}

export async function delete_task(tid: number) {
    let api = '/task?id=' + tid
    if (import.meta.env.DEV) {
        api = '/api' + api
    }
    const res = await fetch(api, {
        method: 'DELETE'
    })
    if (res.ok) {
        // alert('Task deleted.')
        return true
    } else {
        alert('Delete task failed!')
        console.error(await res.text())
        return false
    }
}

// interface ExecuteResult{
//     id:number,
//     state:string,
//     result:string,
// }

export function auto_update_task_info(tasks: Ref<TaskInfo[]>) {
    const ws = new WebSocket('ws://localhost:9191/task')
    ws.onopen = () => {
        console.debug('ws connected.')
    }
    ws.onclose = () => {
        console.debug('ws closed.')
        auto_update_task_info(tasks)
    }
    ws.onmessage = (e) => {
        // console.debug('receive ws data:',e.data)
        const result = JSON.parse(e.data) as TaskInfo
        const idx = tasks.value.findIndex(t => t.id == result.id)
        if (idx < 0) {
            console.error('No task matched:', result)
            return
        }
        const old_task = tasks.value[idx]
        for (const key in old_task) {
            if (Object.prototype.hasOwnProperty.call(old_task, key)) {
                old_task[key] = result[key]
            }
        }
        console.debug('Task info updated:', result)
    }
    window.onbeforeunload = () => {
        console.debug('closing ws...')
        ws.close()
    }
}