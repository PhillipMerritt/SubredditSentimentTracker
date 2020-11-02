import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import VueFormulate from '@braid/vue-formulate'
import VueEllipseProgress from 'vue-ellipse-progress';
import VueSimpleAccordion from 'vue-simple-accordion';
import 'vue-simple-accordion/dist/vue-simple-accordion.css';

Vue.use(VueSimpleAccordion, {
  // ... Options go here
});

Vue.use(VueEllipseProgress);

Vue.use(VueFormulate)/* , {
  classes: {
    outer: 'formWrapper',
  }
}) */

Vue.config.productionTip = false
Vue.prototype.$http = axios

new Vue({
  render: h => h(App),
}).$mount('#app')
