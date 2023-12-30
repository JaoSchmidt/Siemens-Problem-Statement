<script setup>
import { RouterLink, RouterView, useRoute } from 'vue-router'
import LoadingLayer from "./components/LoadingLayer.vue";
import { LoadingPinia } from './stores/LoadingPinia';



const Loading = LoadingPinia();
Loading.isLoading = true;






</script>

<template>

  <!-- Loading Layer -->
  <LoadingLayer v-show="Loading.isLoading" />
  <Suspense>
    <RouterView data-theme="sunset" class="min-h-[100vh] w-full flex"/>
  </Suspense>

</template>
