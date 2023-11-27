export interface TaskInfo{
    name:string
    id:number
    command:string
    cron:string
    next_time:string
    last_time:string
    result:string
    // error:string
    state:string
}

export const EmptyTask:TaskInfo={
    name:'',
    id:-1,
    command:'',
    cron:'',
    next_time:'',
    last_time:'',
    result:'',
    state:'',
}

export async function get_task(id:number):Promise<TaskInfo>{
    const api='/api/task?id='+id
    const res=await fetch(api)
    if (res.ok) {
        const task= await res.json() as TaskInfo
        console.debug('Get task:',task)
        return task
    }
    alert('Get task failed!')
    console.error(await res.text())
    return EmptyTask
}

export async function get_all_tasks():Promise<TaskInfo[]>{
    const api='/api/tasks'
    const res=await fetch(api)
    if (res.ok) {
        const tasks=await res.json() as TaskInfo[]
        console.debug(`Get tasks[${tasks.length}]`)
        return tasks
    }
    alert('Get task failed!')
    console.error(await res.text())
    return []
}

export async function add_or_update_task(tid:number,name:string,command:string,cron:string) {
    let api='/api/task'
    if (tid>=0) {
        api+='?id='+tid
    }
    const data={
        name,
        command,
        cron,
    }
    const res=await fetch(api,{
        method:'POST',
        body:JSON.stringify(data),
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

export async function run_task(taskid:number) {
    const api='/api/execute?id='+taskid
    const res= await fetch(api)
    if (res.ok) {
        alert('Task is running.')
    }else{
        alert('Run task failed!')
        console.error(await res.text())
    }
}

export async function delete_task(tid:number) {
    const api='/api/task?id='+tid
    const res=await fetch(api,{
        method:'DELETE'
    })
    if (res.ok) {
        // alert('Task deleted.')
        return true
    }else{
        alert('Delete task failed!')
        console.error(await res.text())
        return false
    }
}