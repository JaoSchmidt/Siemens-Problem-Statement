<script setup>
import { ref, watch, watchEffect } from 'vue';
import $ from 'jquery';
import { useRouter } from "vue-router";
import axios from "axios";
import { LoadingPinia } from "../stores/LoadingPinia";
import { SessionPinia } from "../stores/SessionPinia";



// ROUTER
const router = useRouter();

// PINIAS
const Loading = LoadingPinia();
//Loading.isLoading = false;

const Session = SessionPinia();

const LeftNav = LeftNavMenuPinia();

</script>


<template>
    
</template>