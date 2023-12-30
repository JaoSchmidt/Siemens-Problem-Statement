import { ref, computed } from "vue";
import { defineStore } from "pinia";

export const LoadingPinia = defineStore("LoadingPinia", () => {

    const isLoading = ref(false);


    return { isLoading };
});
