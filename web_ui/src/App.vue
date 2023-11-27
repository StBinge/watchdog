<script setup lang="ts">
import {ref,computed} from 'vue'
import EnvPanel from './components/EnvPanel.vue';
import TaskPanel from './components/TaskPanel.vue'


const active_menu_idx=ref(1)
const panel_names=[TaskPanel,EnvPanel,'SettingsPanel']
const active_panel_name=computed(()=>panel_names[active_menu_idx.value-1])
const menu_item_click=(e:MouseEvent)=>{
  const item=e.target as HTMLElement
  if (!item) return
  active_menu_idx.value=parseInt(item.id)
  
}
</script>

<template>
<div id="container">
  <div id="menu" @click="menu_item_click">
    <div class="menu-item" :class="{active:active_menu_idx==1}" id="1">Task</div>
    <div class="menu-item" id="2" :class="{active:active_menu_idx==2}">Env</div>
    <!-- <div class="menu-item" id="3" :class="{active:active_menu_idx==3}">Settings</div> -->
  </div>
  <div id="panel">
    <KeepAlive>
      <component :is="active_panel_name"></component>
    </KeepAlive>
  </div>
</div>
</template>

<style>
#container{
  width: 100%;
  height: 100%;
  /* overflow: hidden; */
  display: flex;
  flex-direction: row;
  gap: 10px;
  padding: 10px;
  box-sizing: border-box;
  min-width: 1000px;
  background-color: black;
}
#menu{
  width: 100px;
  height: 100%;
  background-color: var(--item-background);
  flex: 0 0 200px;
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  /* gap: 10px; */
  /* justify-content: center; */
  align-items: center;
  padding: 10px 0;
  box-sizing: border-box;
}
#panel{
  width: 100%;
  height: 100%;
  background-color: var(--item-background);
  flex:1 1 100%;
  border-radius: 5px;
}
.menu-item{
  width: 90%;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
  height: 40px;
  line-height: 40px;
  color:var(--highlight-color);
  border-bottom: var(--highlight-color) 1px solid;
  /* background-color: dodgerblue; */
}
.menu-item:hover,.active{
  color:var(--item-background);
  background-color: var(--highlight-color);
}

</style>
