<template>
    <div>
        <div v-if="chosenModel != null">
            <GChart
            type="ColumnChart"
            :data="selectedData"
            :options="chartOptions"
            :events="chartEvents"
            @ready="onChartReady"
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
            :progress="commentProgress"
            :legend-formatter="commentLegend"
            :color="colors[3]"
            :colorFill="colors[1]"
            :fontColor="colors[0]"
            thickness="7%"
            >
                <template v-slot:legend-value>
                    <span slot="legend-value">/{{requiredRequests}}</span>
                </template>
                <template v-slot:legend-caption>
                    <p slot="legend-caption" :style="'font-size: 1rem; color: ' + colors[0] + ';'">Comment Queries</p>
                </template>
            </vue-ellipse-progress>

            <vue-ellipse-progress 
            :progress="sentimentProgress"
            :legend-formatter="sentimentLegend"
            :color="colors[2]"
            :colorFill="colors[1]"
            :fontColor="colors[0]"
            thickness="7%"
            >
                <template v-slot:legend-value>
                    <span slot="legend-value">/{{requiredSentimentRequests}}</span>
                </template>
                <template v-slot:legend-caption>
                    <p slot="legend-caption" :style="'color: ' + colors[0] + ';'">Sentiment Queries</p>
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

        <div class="formulate-input" id="inputs">
            <FormulateInput 
            type="button" 
            label="Generate Chart"
            v-on:click="genChart()"
            style="margin: 10px; padding: 10px;"
            label-class="formLabels"/>
        </div>

        <div v-if="selectedNeg != null || loading">
            <div id="inputs" v-if="loading">
                Loading Most Positive and Negative Posts...
            </div>
            <div class="linksWrapper" v-else>
                <div style="grid-column: 1 / 2; grid-row: 1 / 2; justify-self: end; padding: 10px;">
                    Most Positive Thread: 
                </div>
                <a style="grid-column: 2 / 3; grid-row: 1 / 2; justify-self: start; padding: 10px;" 
                    :href="selectedPos.link">
                    {{selectedPos.title}}
                </a>
                <div style="grid-column: 1 / 2; grid-row: 2 / 3; justify-self: end; padding: 10px;">
                    Most Negative Thread: 
                </div>
                <a style="grid-column: 2 / 3; grid-row: 2 / 3; justify-self: start; padding: 10px;" 
                    :href="selectedNeg.link">
                    {{selectedNeg.title}}
                </a>
            </div>
        </div>
        
    </div>
</template>

<script>
import { GChart } from 'vue-google-charts'
import Bottleneck from "bottleneck"
import axios from 'axios'

export default {
    name: 'SentimentChart',
    components: {
        GChart
    },
    props: {
        colors: Array
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
            requiredSentimentRequests: 0,
            completedSentimentRequests: 0,
            selectedPos: null,
            selectedNeg: null,
            loading: false,
            chartEvents: {
                'select': async () => {
                    const table = this.$refs.gChart.chartObject;
                    const selection = table.getSelection();
                    this.loading = true
                    this.selectedPos = await this.getSubmission(this.tooltipData[this.chosenModel][selection[0].row].most_positive)
                    this.selectedNeg = await this.getSubmission(this.tooltipData[this.chosenModel][selection[0].row].most_negative)
                    this.loading = false
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
        commentProgress: function () {
            return 100 * this.completedRequests / this.requiredRequests
        },
        sentimentProgress: function () {
            return 100 * this.completedSentimentRequests / this.requiredSentimentRequests
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
            let sentimentData = await this.getSentiment(this.subreddit, this.start, this.end)
            let data = await this.createChart(this.subreddit, this.start, this.end, sentimentData)
            this.chartData = data.data
            this.chartOptions = data.chartOptions.chart
            this.tooltipData = data.tooltips
            this.chosenModel = Object.keys(this.chartData)[0]
            this.completedRequests = 0
            this.completedSentimentRequests = 0
            this.requiredSentimentRequests = 0
            this.requiredRequests = 0
        },
        selectOption: function(option){
            this.selectedPos = null
            this.selectedNeg = null
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
        getSentiment: async function (subreddit, start, end) {
            let posix_start = this.getUTCseconds(new Date(start))
            let s = posix_start
            let e = this.getUTCseconds(new Date(end))
            let days = Math.floor((e - s) / 86400)
            //let timeZoneOffset = start.getTimeZoneOffset()

            this.completedRequests = 0
            this.completedSentimentRequests = 0
            this.requiredSentimentRequests = days * 4
            this.requiredRequests = days * 24
            this.selectedPos = null
            this.selectedNeg = null
            this.chosenModel = null     

            let request_bins = []
            let labels = []

            let req_count = 0
            
            while (s < e) {
                if (req_count % 6 === 0) // if this is the beginning of a column
                {
                    if (req_count % 24 === 0)
                        labels.push(this.getDateLabel(s))
                    else
                        labels.push("")

                    request_bins.push([])
                }
                request_bins[request_bins.length - 1].push({
                    url: `https://api.pushshift.io/reddit/search/comment/?size=100&sort=desc&sort_type=score&after=${s}&before=${s + 3600}&subreddit=${subreddit}`,
                    config: {"method": 'GET', "mode": "cors", "Referrer-Policy": "no-referrer"}
                })

                s += 3600
                req_count += 1
            }

            let commentResponses = []
            let sentimentResponses = []
            let models = []
            let processComments = async (comments) => {
                let response = this.sentimentRequest(comments)
                sentimentResponses.push(response)
                response.then(result => { 
                    this.completedSentimentRequests += 1 
                    if (models.length === 0)
                        models = Object.keys(result.data.data)
                })
            }

            request_bins.forEach(async (requests) => {
                let comments = []
                let response_jsons = []

                let responses = Promise.all(requests.map(x => this.limiter.schedule(this.processRequest, x)));
                commentResponses.push(responses)
                await responses.then((result) => {
                    result.forEach(x => response_jsons.push(x.json()));
                })


                await Promise.all(response_jsons).then(result => result.forEach(sub_arr => {
                    sub_arr.data.forEach(x => {
                    if (x.body != "[removed]" && x.body != "[deleted]")
                        comments.push([this.slicePerma(x.permalink), x.body.replace(',', '')])
                    })
                }));

                /* for (let i=0; i<comments.length; i++)
                    bins[bin_idx].comments.push([comments[i][1], comments[i][2]]) */

                processComments(comments)
            })

            let final_data = {}

            await Promise.all(commentResponses)
            await Promise.all(sentimentResponses).then(result => final_data = {
                "responses": result,
                "models": models,
                "labels": labels
            })

            return final_data
        },
        createChart: async function (subreddit, start, end, sentimentData) {
            let responses = sentimentData.responses
            let models = sentimentData.models
            let labels = sentimentData.labels

            let data = {}
            let tooltips = {}

            models.forEach(model => {
                data[model] = [['Time Frame', 'Sentiment', { "role": 'style' }, { "role": 'tooltip' }]]
                tooltips[model] = []
            })

            let val
            let most_pos
            let most_neg

            for(var j=0; j < responses.length; j++)
            {
                await responses[j]

                for(var i=0; i < models.length; i++)
                {
                    val = responses[j].data.data[models[i]].sentiment
                    data[models[i]].push([labels[j], val, this.heatMapColorforValue(val), "Click me to load extreme posts!"])

                    most_pos = responses[j].data.data[models[i]].most_positive
                    most_neg = responses[j].data.data[models[i]].most_negative
                    tooltips[models[i]].push({"most_positive": most_pos, "most_negative": most_neg})
                }
            }

            return {
                data: data,
                tooltips: tooltips,
                chartOptions: {
                    chart: {
                        title: `/r/${subreddit} sentiment ${start} to ${end}`,
                        legend: { position: "none" },
                        fontName: 'Armata',
                        backgroundColor: this.colors[0]
                    }
                }
            }
        },
        heatMapColorforValue: function (value){
            /* var h = ((value * 4) + 1) * 120
            if (h > 240)
            h = 240
            else if (h < 0)
            h = 0
            return "color: " + this.HSLToHex(h, 100, 50); */
            if (value > 0)
                return this.colors[2]
            return this.colors[3]
        },
        HSLToHex: function (h,s,l) {
            s /= 100;
            l /= 100;
        
            let c = (1 - Math.abs(2 * l - 1)) * s,
                x = c * (1 - Math.abs((h / 60) % 2 - 1)),
                m = l - c/2,
                r = 0,
                g = 0,
                b = 0;
        
            if (0 <= h && h < 60) {
            r = c; g = x; b = 0;
            } else if (60 <= h && h < 120) {
            r = x; g = c; b = 0;
            } else if (120 <= h && h < 180) {
            r = 0; g = c; b = x;
            } else if (180 <= h && h < 240) {
            r = 0; g = x; b = c;
            } else if (240 <= h && h < 300) {
            r = x; g = 0; b = c;
            } else if (300 <= h && h < 360) {
            r = c; g = 0; b = x;
            }
            // Having obtained RGB, convert channels to hex
            r = Math.round((r + m) * 255).toString(16);
            g = Math.round((g + m) * 255).toString(16);
            b = Math.round((b + m) * 255).toString(16);
        
            // Prepend 0s, if necessary
            if (r.length == 1)
            r = "0" + r;
            if (g.length == 1)
            g = "0" + g;
            if (b.length == 1)
            b = "0" + b;
        
            return "#" + r + g + b;
        },
        slicePerma: function (link) // returns a slice of the permalink containing the thread id
        {
            let idx = link.indexOf('/comments/') + 10
            return link.slice(idx, idx + 6)
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
        sentimentRequest: async function(comments)
        {
            let request_data = new FormData()

            comments.forEach((item) => {
                request_data.append('links[]', item[0])
            })

            comments.forEach((item) => {
                request_data.append('comments[]', item[1])
            })

            return axios.post('http://127.0.0.1:5000/',
            request_data,
            {headers: {'Content-Type': 'multipart/form-data' }});
        },
        commentLegend: function () {
            return `${this.completedRequests}`
        },
        sentimentLegend: function () {
            return `${this.completedSentimentRequests}`
        },
        getSubmission: async function (id) {
            let url = `https://api.pushshift.io/reddit/search/submission/?ids=${id}`
            let response = await fetch(url, {"method": 'GET', "mode": "cors", "Referrer-Policy": "no-referrer"})
            response = await response.json()
            return {title: response.data[0].title, link: response.data[0].full_link}
        },
        onChartReady: function () {
            const table = this.$refs.gChart.chartObject
            table.animation.startup = true
            table.animation.duration = 15000
            /* table.hAxis.gridlines.color = this.colors[0]
            table.hAxis.minorGridlines.color = this.colors[0]
            table.vAxis.baselineColor = this.colors[0]
            table.vAxis.gridlines.color = this.colors[0]
            table.vAxis.minorGridlines.color = this.colors[0]
            table.hAxis.titleTextStyle = {color: this.colors[0], fontName: "Armata"}
            table.vAxis.titleTextStyle = {color: this.colors[0], fontName: "Armata"}
            table.hAxis.textStyle = {color: this.colors[0], fontName: "Armata"}
            table.vAxis.textStyle = {color: this.colors[0], fontName: "Armata"}
            table.titleTextStyle = {color: this.colors[0], fontName: "Armata"} */
        }
    }
}
</script>

<style> 
    #inputs {
        display: flex;
        justify-content: center;
    }
    .formWrapper {
        font-family: Armata, Avenir, Helvetica, Arial, sans-serif;
    }

    .linksWrapper {
        display: grid;
        grid-template-columns: 33% 77%;
        grid-template-rows: auto;
    }
</style>