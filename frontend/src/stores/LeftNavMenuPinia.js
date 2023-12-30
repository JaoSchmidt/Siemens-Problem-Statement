import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const LeftNavMenuPinia = defineStore('LeftNavMenuPinia', () => {

  const toggle = ref(false);

  return { toggle }
})

export default LeftNavMenuPinia;