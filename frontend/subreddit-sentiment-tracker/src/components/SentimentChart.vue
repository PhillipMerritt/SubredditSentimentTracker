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
        <div id="inputs" v-else-if="requiredRequests > 0">
            <vue-ellipse-progress 
            :progress="progress">
            <!-- :legend="true"
            :legendValue="completedRequests"
            :legend-formatter="legend" -->
                <!-- <span slot="legend-value">{{legend}}</span> -->
            </vue-ellipse-progress>
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
import Bottleneck from "bottleneck"

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
            chosenModel: null,
            limiter: new Bottleneck({
                maxConcurrent: 2,
                minTime: 1000
            }),
            requiredRequests: 0,
            completedRequests: 0
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
        },
        progress: function () {
            return Math.floor(this.completedRequests / this.requiredRequests * 100);
        }
    },
    methods: {
        genChart: async function(){
            let bins = await this.getComments(this.subreddit, this.start, this.end)
            let data = await getSentiment(this.subreddit, this.start, this.end, bins)
            this.chartData = data.data
            this.chartOptions = data.chartOptions.chart
            this.chosenModel = Object.keys(this.chartData)[0]
        },
        selectOption: function(option){
            console.log(option)
            this.chosenModel = option
        },
        getComments: async function (subreddit, start, end) {
            let posix_start = Math.floor(new Date(start).getTime() / 1000)
            let s = posix_start
            let e = Math.floor(new Date(end).getTime() / 1000)
            let days = Math.floor((e - s) / 86400)

            this.completedRequests = 0
            this.requiredRequests = days * 24            

            let requests = []

            while (s < e) {
                requests.push({url: `https://api.pushshift.io/reddit/search/comment/?size=100&sort=desc&sort_type=score&after=${s}&before=${s + 3600}&subreddit=${subreddit}`,
                config: {"method": 'GET', "mode": "cors", "Referrer-Policy": "no-referrer"}
            })

                s += 3600
            }

            const responses = await Promise.all(requests.map(x => this.limiter.schedule(this.processRequest, x)));

            let comments = [];
            let response_jsons = [];

            responses.forEach(x => response_jsons.push(x.json()));
            await Promise.all(response_jsons).then(result => result.forEach(sub_arr => {
                sub_arr.data.forEach(x => {
                if (x.body != "[removed]" && x.body != "[deleted]")
                    comments.push([x.created_utc, x.body.replace(',', '')])
                })
            }));

            let bins = [];

            for (let i=0; i<days*4; i++)
                bins.push([])

            for (let i=0; i<comments.length; i++)
                bins[this.getBinIdx(posix_start, comments[i][0])].push(comments[i][1])

            this.completedRequests = 0
            this.requiredRequests = 0

            return bins;
        },
        getBinIdx: function (start, current) 
        {
            return Math.floor((current - start) / 21600)
        },
        processRequest: async function(params) 
        {
            let response = await fetch(params.url, params.config);

            while (response.status != 200)
                response = await fetch(params.url, params.config);
            
            this.completedRequests += 1
            return response
        },
        legend: function (current_value) {
            return `${current_value}/${this.requiredRequests}`
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