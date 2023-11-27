<script setup lang="ts">
import {ref,onMounted,onActivated} from 'vue'
import {Env,set_env,get_envs,delete_env} from '../Env'

const envs=ref<Env[]>([])
const new_key=ref<HTMLInputElement>()
const new_value=ref<HTMLInputElement>()
async function add_env() {
    const key=new_key.value?.value
    const value=new_value.value?.value
    if ( key&& value) {
        const new_env=await set_env(key,value)
        console.debug('Add new env:',new_env)
        if (new_env)envs.value.push(new_env)
    }
}
async function get_all_envs() {
    const res=await get_envs()
    console.debug('Get Envs count:',res.length)
    if (res.length) {

        envs.value=res
    } 
}

async function remove_env(key:string) {
    const res=await delete_env(key)
    if (res) {
        const idx=envs.value.findIndex(item=>item.key==key)
        envs.value.splice(idx,1)
    }
}

async function update_env(key:string){
    const new_value=prompt('Input new value:')
    if (new_value) {
        const res=await set_env(key,new_value)
        if (res) {
            const idx=envs.value.findIndex(item=>item.key==key)
            envs.value[idx].value=res.value
        }
    } 
}

onMounted(async()=>{
    await get_all_envs()
})
onActivated(async()=>{
    await get_all_envs()
})
</script>
<template>
<div class="panel-container env-panel">
    <div class="panel-header">
        <span class="panel-header-item">Key</span>
        <span class="panel-header-item">Value</span>
        <span class="panel-header-item">Operations</span>
    </div>
    <div class="panel-content">
        <h1 class="empty-content" v-if="envs.length==0">No Data</h1>
        <div class="env-row" v-for="env in envs">
            <span class="env-key">{{ env.key }}</span>
            <span class="env-value">{{ env.value }}</span>
            <p class="env-ops">
                <span class="emoji-btn" title="Edit value" @click="update_env(env.key)">✏️</span>
                <span class="emoji-btn" title="Delete item" @click="remove_env(env.key)">❌</span>
            </p>
        </div>
    </div>
    <div class="panel-footer">
        <label for="env-key">KEY:</label>
        <input class="panel-input" id="env-key" type="text" ref="new_key">
        <label for="env-value">VALUE:</label>
        <input id="env-value" type="text" class="panel-input" ref="new_value">
        <span class="btn" @click="add_env">Add</span>
        <!-- <span class="btn">Refresh</span> -->
    </div>
</div>
</template>
<style>
.env-panel> .panel-header{
    grid-template-columns: 200px 1fr 200px;
}
.env-panel>.panel-footer{
    display: grid;
    grid-template-columns: 60px 1fr 60px 2fr auto;
}
.panel-input{
    appearance: none;
    background-color: #333;
    border-width: 0;
}
.env-row{
    display: grid;
    grid-template-columns: 200px 1fr 200px;
    font-size: 18px;
    text-align: center;
    border-bottom: 1px solid var(--highlight-color);
    align-items: center;
}
.env-row>span{
    border-right: 1px solid var(--highlight-color);
}
.env-key{
    color: var(--highlight-color);
    font-weight: bold;
}
.env-ops{
    display: flex;
    justify-content: center;
    gap: 10px;
}
.panel-footer>label{
    text-align: right;
}
</style>