<template>
  <div id="app" :style="'--colorA: ' + colors[0] + '; --colorB: ' + colors[1] + '; --colorC: ' + colors[2] + '; --colorD: ' + colors[3]">
    <meta name="referrer" content="no-referrer" />
    <h1>Reddit Sentiment Tracker</h1>
    <SentimentChart v-bind:colors="colors"/>
  </div>
</template>

<script>
import SentimentChart from './components/SentimentChart.vue'
export default {
  name: 'App',
  components: {
    SentimentChart
  },
  data: function () {
    return {
      colors: ["#ecf4f3", "#68b0ab", "#006a71", "#ff7e67"]//["#00b8a9", "#f8f3d4", "#f6416c", "#ffd460"]//["#f6f5f5", "#ee6f57", "#1f3c88", "#070d59"]//["#ecf4f3", "#68b0ab", "#006a71", "#ff7e67"]
    }
  }

}
</script>

<style lang="scss">
@import '../node_modules/@braid/vue-formulate/themes/snow/snow.scss';

.formulate-input{
  font-family: Armata, Avenir, Helvetica, Arial, sans-serif;
}
.formulate-input[data-classification=text] input{
  font-family: Armata, Avenir, Helvetica, Arial, sans-serif;
  
}
.formulate-input[data-classification=button] button{
  font-family: Armata, Avenir, Helvetica, Arial, sans-serif;
  border:1px solid var(--colorB);
	background-color: var(--colorB);
  color: var(--colorA);
}
.formulate-input[data-classification=select] select{
  font-family: Armata, Avenir, Helvetica, Arial, sans-serif;
}

body, html {
  height: 100%;
  background-color: #f6f5f5;
}
#app {
  height: 100%; 
  font-family: Armata, Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
