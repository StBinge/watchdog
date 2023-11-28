<script setup lang="ts">
import { onMounted, ref,defineEmits, computed } from 'vue';
import { get_task, add_or_update_task, TaskInfo, EmptyTask,run_task,TaskState} from '../task';

const props = defineProps<{
  task: TaskInfo
}>()

const emits=defineEmits<{
  (e:'close'):void,
  (e:'added',data:TaskInfo):void,
  (e:'updated',data:TaskInfo):void,
}>()
// const panel=ref<HTMLElement>()
const task = ref<TaskInfo>(EmptyTask)

const is_new_task=computed(()=>task.value.id==-1)

async function add_new_task() {
  if (!task.value.name) {
    alert('Task name can not be empty!')
    return
  }
  if (!task.value.command){
    alert("Task command can not be empty!")
    return
  }
  if (task.value.cron.trim().split(' ').length!=5){
    alert('Task Cron can not be empty or invalid formation!')
    return
  }
  const new_task = await add_or_update_task(-1,task.value.name, task.value.command, task.value.cron)
  if (new_task){
    task.value=new_task
    emits('added',new_task)
  }
}

async function update_task() {
  const updated_task=await add_or_update_task(task.value.id,task.value.name,task.value.command,task.value.cron)
  if (updated_task) {
    task.value=updated_task
    emits('updated',updated_task)
  }
}

async function refresh_task_info(){
  const res=await get_task(task.value.id)
  if (res){
    task.value=res
    emits('updated',res)
  }
}

async function run_task_now(id:number){
  const res=await run_task(id)
  if (res) {
    task.value.state=TaskState.Running
    emits('updated',task.value)
  }
}

onMounted(async () => {
  // if (props.taskid >= 0) {
  //   task.value = await get_task(props.taskid)
  // }
  task.value=props.task
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
          <input id="name" type="text" class="value" v-model="task.name">
        </p>
        <p class="info-panel-row">
          <label for="command" class="label">Command</label>
          <input id="command" type="text" class="value" v-model="task.command">
        </p>
        <p class="info-panel-row">
          <label for="cron" class="label">Cron</label>
          <input id="cron" type="text" class="value" v-model="task.cron">
        </p>
        <p class="info-panel-row" :class="{disabled:is_new_task}">
          <label for="next_time" class="label">Next Time</label>
          <input id="next_time" type="text" class="value" v-model="task.next_time">
        </p>
        <p class="info-panel-row" :class="{disabled:is_new_task}">
          <label for="last_time" class="label">Last Time</label>
          <input id="last_time" type="text" class="value" v-model="task.last_time">
        </p>
        <p class="info-panel-row" :class="{disabled:is_new_task}">
          <label for="state" class="label">state</label>
          <input id="state" type="text" class="value" v-model="task.state">
        </p>
        <p class="info-panel-row" :class="{disabled:is_new_task}">
          <label for="result" class="label">Result</label>
          <textarea id="result" rows="6" class="value" v-bind:value="task.result"></textarea>
        </p>
      </div>

      <p id="info-panel-footer">
        <span v-if="is_new_task" class="btn" @click="add_new_task">Add</span>
        <span v-else class="btn" @click="update_task">Update</span>
        <span v-if="!is_new_task" class="btn" @click="refresh_task_info">Refresh</span>
        <span class="btn" @click="run_task_now(task.id)">Run</span>
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
}
.corner-btn{
  position: absolute;
  right: 10px;
  top: 10px;
  font-size: 20px;
}
</style>