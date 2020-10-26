<template>
    <div>
        <div v-if="chosenModel != null">
            <GChart
            type="ColumnChart"
            :data="selectedData"
            :options="chartOptions"
            />

            <FormulateInput
            v-model="value"
            :options="modelOptions"
            type="select"
            label="Select a model: "
            @change="selectOption(option)"
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
            subreddit: '',
            start: '',
            end: '',
            chartData: [],
            chartOptions: {},
            chosenModel: null
        }
    },
    computed: {
        modelOptions: function () {
            let options = {}
            Object.keys(this.chartData).forEach(element => options[element] = element)
            return options
        },
        selectedData: function () {
            if (this.chartData != null && this.chartData[this.chosenModel] != null)
                return this.chartData[this.chosenModel]
        }
    },
    methods: {
        genChart: async function(){
            let data = await getSentiment(this.subreddit, this.start, this.end)
            this.chartData = data.data
            this.chartOptions = data.chartOptions.chart
            this.chosenModel = Object.keys(this.chartData)[0]
        },
        selectOption: function(option){
            this.chosenModel = option
        }
    }
}
</script>