<template>
    <div>
        <GChart
        :settings="{packages: ['bar']}"
        :data="chartData"
        :options="chartOptions"
        :createChart="(el, google) => new google.charts.Bar(el)"
        @ready="onChartReady"
        />
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
            chartData: [
                ['Time Frame', 'Sentiment'],
                ['10/20 am', 0.5],
                ['10/20 pm', 0.65],
                ['10/21 am', 0.7],
                ['10/21 pm', 0.3],
                ['10/22 am', 0.1],
                ['10/22 pm', -0.2],
                ['10/23 am', -0.5],
                ['10/23 pm', -0.3]
            ],
            chartParams: {
                title: '/r/gaming sentiment 10/20-23'
            }
        }
    },
    computed : {
        chartOptions () {
            if (!this.chartsLib) return null
            return this.chartsLib.charts.Bar.convertOptions({
                chart: {
                    title: this.chartParams.title
                }
            })
        }
    },
    methods: {
        genChart: function(){
            let data = getSentiment(this.subreddit, this.start, this.end)
            this.chartData = data.data
            this.chartParams = data.chartOptions.chart
        },
        onChartReady (chart, google) {
            this.chartsLib = google
        }
    }
}
</script>