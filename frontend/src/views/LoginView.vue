<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { LoadingPinia } from "../stores/LoadingPinia";
import { SessionPinia } from "../stores/SessionPinia";
import axios from "axios";




// ROUTER
const router = useRouter();

// PINIAS
const Loading = LoadingPinia();
Loading.isLoading = false;

const Session = SessionPinia();



const username = ref(null);
const password = ref(null);


const tryLoginHandler = () => {
  
  axios.post(`../api/checkUser`, {
  headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Methods': 'POST', 'Access-Control-Allow-Origin': '*' },
  data: {
    username: username.value.value,
    pass: password.value.value
  },
  }).then( (response) => {
    
    let code = response.data["code"];

    if ( code == "1" ) {
      Session.userToken = true
      router.push('/dashboard')
    } else {
      alert("Credenciais Incorretas ou usuário não existe!")
    }
  });

}

</script>

<template>
    
  <div class="h-full w-full flex flex-col justify-center items-center">
    <input id="username" ref="username" class="input input-primary my-2 w-64" type="text" placeholder="Username">
    <input id="password" ref="password" class="input input-primary my-2 w-64" type="password" placeholder="Password">
    <button @click="tryLoginHandler" type="submit" class="btn btn-primary text-white w-64 text-lg font-[700] mt-8"> Entrar
    </button>
  </div>

</template>