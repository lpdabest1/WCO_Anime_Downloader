<template>
  <div id="app">
    <AnimeScraper />
  </div>
</template>

<script>
import AnimeScraper from './components/Scraper.vue';

export default {
  name: 'App',
  components: {
    AnimeScraper
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
  margin-top: 60px;
}
</style>
