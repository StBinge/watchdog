export interface Env{
    key:string
    value:string
}

export async function set_env(key:string,value:string) {
    const api='/api/env'
    const data={
        key:key,
        value:value,
    }
    const res=await fetch(api,{
        method:'POST',
        body:JSON.stringify(data),
        headers:{
            'content-type':'application/json'
        }
    })
    if (res.ok) {
        return await res.json() as Env
    } else {
        alert('Set Env failed!')
        console.error(await res.text())
        return null
    }
}

export async function get_envs() {
    const api='/api/env'
    const res=await fetch(api)
    if (res.ok) {
        return await res.json() as Env[]
    } else {
        alert('Get envs failed!')
        console.error(await res.text())
        return []
    }
}

export async function delete_env(key:string) {
    const api='/api/env?key='+key
    const res=await fetch(api,{
        method:"DELETE"
    })
    if (res.ok) {
        return true
    } else {
        alert('Delete Env failed!')
        console.error(await res.text())
        return false
    }
}

