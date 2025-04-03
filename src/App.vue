<template>
  <div class="w-full h-full flex flex-col">
    <ElConfigProvider :size="size" :z-index="zIndex">
      <RouterView />
    </ElConfigProvider>
  </div>
</template>

<script>
import { reactive } from 'vue';

export default {
  name: 'App',
  setup() {
    const state = reactive({
      zIndex: 3000,
      size: 'small'
    });
    return {
      size: state.size,
      zIndex: state.zIndex
    };
  }
};
</script>