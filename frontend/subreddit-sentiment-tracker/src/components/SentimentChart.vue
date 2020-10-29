<template>
    <div>
        <div v-if="chosenModel != null">
            <GChart
            type="ColumnChart"
            :data="selectedData"
            :options="chartOptions"
            :events="chartEvents"
            ref="gChart"
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
            :progress="progress"
            :legend-formatter="legend"
            >
                <template v-slot:legend-value>
                    <span slot="legend-value">/{{requiredRequests}}</span>
                </template>
                <template v-slot:legend-caption>
                    <p slot="legend-caption">Requests Completed</p>
                </template>
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

        <div id="links" v-if="selectedColumn > -1">
            <a :href="selectedPos">Most Positive Thread</a>
            <a :href="selectedNeg">Most Negative Thread</a>
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
            end: '2020-10-07',
            chartData: [],
            chartOptions: {},
            tooltipData: {},
            chosenModel: null,
            limiter: new Bottleneck({
                maxConcurrent: 4,
                minTime: 1000
            }),
            requiredRequests: 0,
            completedRequests: 0,
            selectedColumn: -1,
            chartEvents: {
                'select': () => {
                    const table = this.$refs.gChart.chartObject;
                    const selection = table.getSelection();
                    this.selectedColumn = selection[0].row   
                }
            }
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
        selectedPos: function () {
            return this.tooltipData[this.chosenModel][this.selectedColumn].most_positive
        },
        selectedNeg: function () {
            return this.tooltipData[this.chosenModel][this.selectedColumn].most_negative
        },
        progress: function () {
            return Math.floor(this.completedRequests / this.requiredRequests * 100);
        }
    },
    mounted: function () {
        // Listen to the "failed" event
        this.limiter.on("failed", async (error, jobInfo) => {
            const id = jobInfo.options.id;
            console.warn(`Job ${id} failed: ${error}`);
            
            if (jobInfo.retryCount === 0) { // Here we only retry once
                console.log(`Retrying job ${id} in 25ms!`);
                return 25;
        }
        });
        
        // Listen to the "retry" event
        this.limiter.on("retry", (error, jobInfo) => console.log(`Now retrying ${jobInfo.options.id}`));
    },
    methods: {
        genChart: async function(){
            let bins = await this.getComments(this.subreddit, this.start, this.end)
            let data = await getSentiment(this.subreddit, this.start, this.end, bins)
            this.chartData = data.data
            this.chartOptions = data.chartOptions.chart
            this.tooltipData = data.tooltips
            this.chosenModel = Object.keys(this.chartData)[0]
        },
        selectOption: function(option){
            console.log(option)
            this.selectedColumn = -1
            this.chosenModel = option
        },
        getUTCseconds: function(date) {
            return Math.floor((date.getTime() + date.getTimezoneOffset()*60*1000)/1000)
        },
        getDateLabel: function(timestamp) {
            let date = new Date(0)
            date.setUTCSeconds(timestamp)
            return `${date.getMonth() + 1}/${date.getDate()}`
        },
        getComments: async function (subreddit, start, end) {
            let posix_start = this.getUTCseconds(new Date(start))
            let s = posix_start
            let e = this.getUTCseconds(new Date(end))
            let days = Math.floor((e - s) / 86400)
            //let timeZoneOffset = start.getTimeZoneOffset()

            this.completedRequests = 0
            this.requiredRequests = days * 24
            this.selectedColumn = -1
            this.chosenModel = null     

            let requests = []
            let labels = []
            

            while (s < e) {
                if (s % 86400 == 0)
                {
                    labels.push(this.getDateLabel(s))
                }
                requests.push({
                    url: `https://api.pushshift.io/reddit/search/comment/?size=100&sort=desc&sort_type=score&after=${s}&before=${s + 3600}&subreddit=${subreddit}`,
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
                    comments.push([x.created_utc, this.slicePerma(x.permalink), x.body.replace(',', '')])
                })
            }));

            let bins = [];

            for (let i=0; i<days*4; i++)
            {
                if (i % 4 == 0)
                    bins.push({label: labels[Math.floor(i / 4)], comments: []})
                else
                    bins.push({label: "", comments: []})
            }
                

            for (let i=0; i<comments.length; i++)
                bins[this.getBinIdx(posix_start, comments[i][0])].comments.push([comments[i][1], comments[i][2]])

            this.completedRequests = 0
            this.requiredRequests = 0

            return bins;
        },
        slicePerma: function (link) // returns the thread permalink without the comment id
        {
            return link.slice(0, link.length - 8)
        },
        getBinIdx: function (start, current) 
        {
            return Math.floor((current - start) / 21600)
        },
        processRequest: async function(params) 
        {
            let response = await fetch(params.url, params.config);

            if (response.status === 200)
                this.completedRequests += 1
            
            return response
        },
        legend: function () {
            return `${this.completedRequests}`
        }
    }
}
</script>

<style> 
    #inputs {
        display: flex;
        justify-content: center;
    }
    #links {
        display: flex;
        justify-content: center;
        flex-direction: column;
    }
</style>