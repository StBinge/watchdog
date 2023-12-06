<script setup lang="ts">
import { onMounted, ref,defineEmits, computed } from 'vue';
import {  add_or_update_task,run_task,tasks,selected_task,update_task_info} from '../task';

// const props = defineProps<{
//   task: TaskInfo
// }>()
interface TaskFields{
  name:string
  cron:string
  command:string
}

const empty_task_fields:TaskFields={
  name:'',
  cron:'',
  command:'',
}
const emits=defineEmits<{
  (e:'close'):void,
  // (e:'added',data:TaskInfo):void,
  // (e:'updated',data:TaskInfo):void,
}>()
// const panel=ref<HTMLElement>()
// const task = ref<TaskInfo>(create_empty_task())
const task_fields=ref<TaskFields>(empty_task_fields)


const is_new_task=computed(()=>!selected_task.value ||selected_task.value.id<0)

function check_task_fields(){
  if (!task_fields.value.name) {
    alert('Task name can not be empty!')
    return false
  }
  if (!task_fields.value.command){
    alert("Task command can not be empty!")
    return false
  }
  if (task_fields.value.cron.trim().split(' ').length!=5){
    alert('Task Cron can not be empty or invalid formation!')
    return false
  }
  return true
}

async function add_new_task() {
  if (!check_task_fields()) {
    return
  }
  const new_task = await add_or_update_task(-1,task_fields.value.name, task_fields.value.command, task_fields.value.cron)
  if (new_task){
    tasks.value.push(new_task)
    selected_task.value=new_task
  }
}

async function update_task() {
  if (!check_task_fields()) {
    return 
  }

  const updated_task=await add_or_update_task(selected_task.value!.id,task_fields.value.name,task_fields.value.command,task_fields.value.cron)
  if (updated_task) {
    // const idx=tasks.value.findIndex(item=>item.id==updated_task.id)
    // tasks.value[idx]=updated_task
    // selected_task.value=updated_task
    update_task_info(selected_task.value!.id,updated_task)
  }
}

function reset_task_fields(){
  task_fields.value.name=selected_task.value?.name||""
  task_fields.value.cron=selected_task.value?.cron||""
  task_fields.value.command=selected_task.value?.command||''
}

// const can_run=computed(()=>{
//   return !is_new_task && selected_task.value?.state.toLowerCase()!='running'
// })
// async function execute_task() {
//   if (selected_task.value?.state.toLowerCase()=='running') {
//     alert(`Task[${selected_task.value!.name}] has been running already!`)
//     return
//   }
//   run_task(selected_task.value!.id)
// }

onMounted(() => {
  reset_task_fields()
})

function close_panel(){
  emits('close')
}

</script>
<template>
  <div id="cover">
    <div id="info-panel">
      <h1 id="info-panel-header">{{is_new_task?"New Task":"Task Information"}}</h1>
      <div id="info-panel-content">
        <p class="info-panel-row">
          <label for="name" class="label">Task Name</label>
          <input id="name" type="text" class="value" v-model="task_fields.name">
        </p>
        <p class="info-panel-row">
          <label for="command" class="label">Command</label>
          <input id="command" type="text" class="value" v-model="task_fields.command">
        </p>
        <p class="info-panel-row">
          <label for="cron" class="label">Cron</label>
          <input id="cron" type="text" class="value" v-model="task_fields.cron" placeholder="please enter valid cron formation">
        </p>
        <p class="info-panel-row" :class="{disabled:is_new_task}">
          <label for="next_time" class="label">Next Time</label>
          <span class="value" >{{ selected_task?.next_time||'' }}</span>
        </p>
        <p class="info-panel-row" :class="{disabled:is_new_task}">
          <label for="last_time" class="label">Last Time</label>
          <span class="value" >{{ selected_task?.last_time||'' }}</span>
        </p>
        <p class="info-panel-row" :class="{disabled:is_new_task}">
          <label for="state" class="label">state</label>
          <span class="value">{{ selected_task?.state||'' }}</span>
        </p>
        <p class="info-panel-row" :class="{disabled:is_new_task}">
          <label for="result" class="label">Result</label>
          <pre class="value" >{{ selected_task?.result||'' }}</pre>
        </p>
      </div>

      <p id="info-panel-footer">
        <span v-if="is_new_task" class="btn" @click="add_new_task">Add</span>
        <span v-else class="btn" @click="update_task">Update</span>
        <!-- <span v-if="!is_new_task" class="btn" @click="refresh_task_info">Refresh</span> -->
        <span class="btn" @click="reset_task_fields()">Reset</span>
        <span class="btn" @click="run_task(selected_task!.id)" v-if="!is_new_task" >Run</span>
      </p>
      <span class="corner-btn" @click="close_panel">❌</span>
    </div>
  </div>
</template>
<style>
#cover {
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  bottom: 0;
  background-color: rgba(.1, .1, .1, .8);
  backdrop-filter: blur(20px);
  display: flex;
  justify-content: center;
  align-items: center;
}

#info-panel {
  width: 600px;
  height: 800px;
  background-color: var(--item-background);
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  /* justify-content: center; */
  align-items: center;
  padding: 0 20px;
  box-sizing: border-box;
  position: relative;
}

#info-panel-header {
  color: var(--highlight-color);
  text-transform: uppercase;
  text-align: center;
  flex: 0 0 60px;
}

#info-panel-content{
  width: 100%;
  flex:1 1 100%;
  display:flex;
  flex-direction: column;
  /* justify-content: space-between; */
  gap: 5px;
}
#info-panel-footer{
  width: 100%;
  flex: 0 0 60px;
  display: flex;
  justify-content: end;
  align-items: center;
  gap:20px;
}
.info-panel-row {
  width: 100%;
  display: flex;
  font-size: 18px;
  border: 1px solid var(--highlight-color);
  /* padding: 2px 4px; */
  border-radius: 5px;
}

.info-panel-row.disabled{
  display: none;
}

.info-panel-row>.label {
  background-color: var(--highlight-color);
  color: var(--item-background);
  flex: 0 0 120px;
  text-transform: capitalize;
  font-weight: bold;
  /* text-align: right; */
  padding-right: 4px;
  vertical-align: center;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  /* min-height: 20px; */
  /* border-bottom: 1px solid var(--highlight-color); */
  /* padding: 2px 0; */
}

.info-panel-row>.value {
  width: 100%;
  flex: 1 1 100%;
  appearance: none;
  background-color: #333;
  /* border: 0 solid var(--highlight-color); */
  /* border-bottom-width: 1px; */
  border-width: 0;
  color:var(--item-font-color);
}
pre.value{
  word-wrap: break-word;
  /* word-break: break-all; */
  height: 160px;
  padding: 0;
  margin: 0;
  white-space: pre-wrap;
  overflow: auto;
}
.corner-btn{
  position: absolute;
  right: 10px;
  top: 10px;
  font-size: 20px;
}
</style>