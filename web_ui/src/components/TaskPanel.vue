<script setup lang="ts">
import { ref,onMounted ,onActivated} from 'vue'
import { get_all_tasks,TaskInfo,run_task,delete_task, EmptyTask,auto_update_task_info} from '../task';
import TaskInfoModal from './TaskInfoModal.vue';

const selected_task=ref<TaskInfo>(EmptyTask)
const tasks=ref<TaskInfo[]>([])

onMounted(async ()=>{
  await refresh_all_tasks()
  auto_update_task_info(tasks)
})
onActivated(async()=>{
  await refresh_all_tasks()
})
const show_info_panel=ref(false)

function add_new_task(){
  selected_task.value=EmptyTask
  show_info_panel.value=true
}

async function refresh_all_tasks() {
  const res=await get_all_tasks()
  if (res.length) {
    tasks.value=res
  }
}

async function check_task_info(task:TaskInfo){
  // console.debug(taskid)
  selected_task.value=task
  show_info_panel.value=true
}

async function delete_selected_task(tid:number){
  if (confirm('Sure to delete task?')==false) {
    return
  }
  if (await delete_task(tid)) {
    const idx=tasks.value.findIndex(t=>t.id==tid)
    tasks.value.splice(idx,1)
  } 
}
function task_added(task:TaskInfo){
  tasks.value.push(task)
}
function task_updated(task:TaskInfo){
  const idx=tasks.value.findIndex(item=>item.id==task.id)
  tasks.value[idx]=task
}
</script>

<template>
  <div class="panel-container">
    <div class="panel-header">
      <span class="panel-header-item">Name</span>
      <span class="panel-header-item">State</span>
      <span class="panel-header-item">Next Time</span>
      <span class="panel-header-item">Last Time</span>
      <span class="panel-header-item">Operations</span>
    </div>
    <div class="panel-content">
      <h1 v-if="tasks.length==0" class="empty-content">No Data</h1>
      <div class="task-row" v-for="task in tasks">
        <span class="task-value" :title="task.name">{{ task.name }}</span>
        <span class="task-value">{{ task.state }}</span>
        <span class="task-value">{{ task.next_time }}</span>
        <span class="task-value">{{ task.last_time }}</span>
        <p class="task-operations">
          <span class="emoji-btn" title="check task" @click="check_task_info(task)">📖</span>
          <span class="emoji-btn" title="run task" @click="run_task(task.id)">▶️</span>
          <span class="emoji-btn" title="delete task" @click="delete_selected_task(task.id)">❌</span>
        </p>
      </div>
    </div>
    <div class="panel-footer">
      <span class="btn" @click="add_new_task">Add</span>
      <span class="btn" @click="refresh_all_tasks">Refresh</span>
    </div>
    <TaskInfoModal @close="show_info_panel=false" v-if="show_info_panel" :task="selected_task" @added="task_added" @updated="task_updated"></TaskInfoModal>
  </div>
</template>

<style>
.panel-container{
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 10px;
  box-sizing: border-box;
}
.panel-header{
  flex: 0 0 40px;
  line-height: 40px;
  display: grid;
  grid-template-columns: 1fr 0.5fr 1fr 1fr 0.5fr;
  border-radius: 5px 5px 0 0 ;
  background-color: var(--highlight-color);

}
.panel-header-item{
  color:var(--item-background);
  font-size: 18px;
  font-weight: bolder;
  text-align: center;
}
.panel-header-item:not(:last-child){
  border-right:1px solid var(--item-background);

}
.panel-content{
  width: 100%;
  height: 100%;
  flex: 1 1 100%;
  border: 1px solid var(--highlight-color);
  box-sizing: border-box;
  border-radius: 0 0 5px 5px;
}
.task-row{
  display: grid;
  grid-template-columns: 1fr 0.5fr 1fr 1fr 0.5fr;
  /* justify-content: center; */
  align-items: center;
  border-bottom: 1px solid var(--highlight-color);
  font-weight: bold;
  font-size: 18px;
}
.panel-footer{
  width: 100%;
  height: 40px;
  flex: 0 0 40px;
  /* background-color: var(--highlight-color); */
  border-radius: 0 0 5px 5px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 30px;
}
.task-value{
  text-align: center;
}
.task-value:not(last-child){
  border-right: 1px solid var(--highlight-color);
}
.task-operations{
  display: flex;
  justify-content: center;
}
.empty-content{
  text-align: center;
}
</style>
