import { createRouter, createWebHistory } from 'vue-router'
import { LoadingPinia } from '../stores/LoadingPinia';



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
  ]
})



router.beforeEach( (to) => {

  const Loading = LoadingPinia();
  Loading.isLoading = true;

  

  if ( to.meta.requiresAuth ) {


    if ( !$cookies.isKey('token') ) {
      return '/';
    } 

    return true;

  } else {

    if ( to.path == '/' && $cookies.isKey('token') ) {

      return '/dashboard';
    }

    // mesma coisa que next()
    return true;
  }

});







export default router
