<template>
    <div>
        <div v-if="chartData.length > 0">
            <GChart
            type="ColumnChart"
            :data="chartData"
            :options="chartOptions"
            />

        </div>

        <label>subreddit: </label>
        <input
        type="text"
        v-model="subreddit">

        <label>start date: </label>
        <input type="date"
        v-model="start">

        <label>end date: </label>
        <input type="date"
        v-model="end">

        <button v-on:click="genChart()">Generate Chart</button>
    </div>
</template>

<script>
import { GChart } from 'vue-google-charts'
import { getSentiment } from '../assets/endpointService'

export default {
    name: 'SentimentChart',
    components: {
        GChart
    },
    props: {
    },
    data () {
        return {
            chartsLib: null,
            subreddit: '',
            start: '',
            end: '',
            chartData: [],
            chartOptions: {}
        }
    },
    methods: {
        genChart: async function(){
            let data = await getSentiment(this.subreddit, this.start, this.end)
            this.chartData = data.data
            this.chartOptions = data.chartOptions.chart
        }
    }
}
</script>