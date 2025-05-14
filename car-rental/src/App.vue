<template>
  <div id="app">
    <NavBar />
    <router-view />
    <!-- <CarShowcase /> -->
    <!-- <StoreLocator /> -->
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';
import Hero from './components/Hero.vue';
import CarRentalSelector from './components/CarRentalSelector.vue';
//import CarShowcase from './components/CarShowcase.vue';
// import StoreLocator from './components/StoreLocator.vue';

export default {
  name: 'App',
  components: {
    NavBar,
    Hero,
    CarRentalSelector
    // CarShowcase,
    // StoreLocator
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 40px;
  padding: 0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
}
</style>
