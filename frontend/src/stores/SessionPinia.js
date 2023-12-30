import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const SessionPinia = defineStore('SessionPinia', () => {

  const userToken = ref("");

  return { userToken }
})

export default SessionPinia;