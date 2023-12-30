<template>
	<img alt="Vue logo" src="./assets/logo.png">
	<HelloWorld msg="Welcome to Your Vue.js App" />
	<div id="app">
		<h1>Login</h1>
		<form @submit.prevent="login">
			<label for="username">Username:</label>
			<input type="text" v-model="username" required>
			<br>
			<label for="password">Password:</label>
			<input type="password" v-model="password" required>
			<br>
			<button type="submit">Login</button>
		</form>
		<div v-if="token">
			<h2>Welcome, {{ username }}!</h2>
			<button @click="logout">Logout</button>
		</div>
	</div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'

export default {
	name: 'App',
	components: {
		HelloWorld
	}
}
</script>

<style>
#app {
	font-family: Avenir, Helvetica, Arial, sans-serif;
	-webkit-font-smoothing: antialiased;
	-moz-osx-font-smoothing: grayscale;
	text-align: center;
	color: #2c3e50;
	margin-top: 60px;
}
</style>
