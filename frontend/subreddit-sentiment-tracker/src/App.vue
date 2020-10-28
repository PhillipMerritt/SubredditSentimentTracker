<template>
  <div id="app">
     <meta name="referrer" content="no-referrer" />
    <h1>Reddit Sentiment Tracker</h1>
    <SentimentChart/>
  </div>
</template>

<script>
import SentimentChart from './components/SentimentChart.vue'
export default {
  name: 'App',
  components: {
    SentimentChart
  }
}
</script>

<style lang="scss">
@import '../node_modules/@braid/vue-formulate/themes/snow/snow.scss';
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
