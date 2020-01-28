<template>
  <v-app>
    <v-content>
      <MapView/>
    </v-content>
  </v-app>
</template>


<script>
import MapView from './components/olu.vue'

export default {
  name: 'app',
  components: {
    MapView
  },
  methods: {
    logout: function(){
      this.$keycloak.logoutFn();
    }
  },
  created(){
    var user = JSON.parse(window.atob(this.$keycloak.token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')));
    this.user = user;
  }
}
</script>

<style>
</style>
