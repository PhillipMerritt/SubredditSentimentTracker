<template>
    <div>
        <div v-if="chosenModel != null">
            <GChart
            type="ColumnChart"
            :data="selectedData"
            :options="chartOptions"
            />

            <div id="inputs">
                <FormulateInput
                v-model="chosenModel"
                :options="modelOptions"
                type="select"
                label="Select a model: "
                style="margin: 10px; padding: 10px;"
                />
            </div>
        </div>

        <div id="inputs">
            <FormulateInput
            type="text"
            v-model="subreddit"
            label="subreddit: "
            style="margin: 10px; padding: 10px;"/>

            <FormulateInput type="date"
            v-model="start"
            label="start date: "
            style="margin: 10px; padding: 10px;"/>

            <FormulateInput type="date"
            v-model="end"
            label="end date: "
            style="margin: 10px; padding: 10px;"/>
        </div>

        <div id="inputs">
            <FormulateInput 
            type="button" 
            label="Generate Chart"
            v-on:click="genChart()"
            style="margin: 10px; padding: 10px;"/>
        </div>
        
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
            subreddit: 'politics',
            start: '2020-10-05',
            end: '2020-10-06',
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
            return null
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
            console.log(option)
            this.chosenModel = option
        }
    }
}
</script>

<style> 
    #inputs {
        display: flex;
        justify-content: center;
    }
</style>