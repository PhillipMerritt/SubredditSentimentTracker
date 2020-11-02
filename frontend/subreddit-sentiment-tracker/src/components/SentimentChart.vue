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
                @input="selectedNeg = null"
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
            animation="default 500 40"
            >
                <template v-slot:legend-value>
                    <span slot="legend-value">/{{requiredRequests}}</span>
                </template>
                <template v-slot:legend-caption>
                    <p slot="legend-caption" :style="'font-size: 1rem; color: ' + colors[0] + ';'">Comment Batches</p>
                </template>
            </vue-ellipse-progress>

            <vue-ellipse-progress 
            :progress="sentimentProgress"
            :legend-formatter="sentimentLegend"
            :color="colors[2]"
            :colorFill="colors[1]"
            :fontColor="colors[0]"
            thickness="7%"
            animation="default 500 40"
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
                    :href="selectedPos.link"
                    target=”_blank”>
                    {{selectedPos.title}}
                </a>
                <div style="grid-column: 1 / 2; grid-row: 2 / 3; justify-self: end; padding: 10px;">
                    Most Negative Thread: 
                </div>
                <a style="grid-column: 2 / 3; grid-row: 2 / 3; justify-self: start; padding: 10px;" 
                    :href="selectedNeg.link"
                    target=”_blank”>
                    {{selectedNeg.title}}
                </a>
            </div>
        </div>

        <!-- <APIcontrols 
        :dayRange="dayRange"
        v-bind:top.sync="top"
        v-bind:timeFrame.sync="timeFrame"
        v-bind:perTimeFrame.sync="perTimeFrame"
        /> -->
        <APIcontrols 
        :dayRange="dayRange"
        @updateSort="updateSort"
        @updateTf="updateTf"
        @updateLimit="updateLimit"
        />
        <!-- @updateSort="updateSort"
        @updateTf="updateTf"
        @updateLimit="updateLimit" -->
        
    </div>
</template>

<script>
import { GChart } from 'vue-google-charts'
import Bottleneck from "bottleneck"
import axios from 'axios'
import APIcontrols from './APIcontrols'

export default {
    name: 'SentimentChart',
    components: {
        GChart,
        APIcontrols
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
                maxConcurrent: 2,
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
                    this.getSubmission(this.tooltipData[this.chosenModel][selection[0].row].most_positive, this.tooltipData[this.chosenModel][selection[0].row].most_negative)
                }
            },
            top: true,
            timeFrame: 'hour',
            perTimeFrame: '100',
            tfDict: { ten_min: '10', twenty_min: '20', thirty_min: '30', hour: '60', two_hour: '120', three_hour: '180', six_hours: '360' }
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
        },
        dayRange: function () {
            let s = this.getUTCseconds(new Date(this.start))
            let e = this.getUTCseconds(new Date(this.end))
            return Math.floor((e - s) / 86400)
        },
        tfPerCol: function () {
            return Math.floor(360 / parseInt(this.tfDict[this.timeFrame]))
        },
        perColumn: function () {
            return this.tfPerCol * parseInt(this.perTimeFrame)
        },
        totalReq: function () {
            return this.reqPerTf * this.tfPerCol * 4 * this.dayRange
        }
    },
    mounted: function () {
        // Listen to the "failed" event
        this.limiter.on("failed", async (error, jobInfo) => {
            const id = jobInfo.options.id;
            console.warn(`Job ${id} failed: ${error}`);
            
            if (jobInfo.retryCount < 10) { // Here we only retry once
                console.log(`Retrying job ${id} in 25ms!`);
                return 25;
            } else {
                console.log('Request failed 10 times. Stopping retries...')
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
            setTimeout(this.chosenModel = Object.keys(this.chartData)[0], 40)
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
            this.requiredRequests = this.requiredSentimentRequests * this.tfPerCol
            this.selectedPos = null
            this.selectedNeg = null
            this.chosenModel = null

            let request_bins = []
            let labels = []
            let sentimentResponses = []

            let req_count = 0
            let tfSize = parseInt(this.tfDict[this.timeFrame]) * 60
            
            while (s < e) {
                if (req_count % this.tfPerCol === 0) // if this is the beginning of a column
                {
                    if (req_count % (this.tfPerCol * 4) === 0)
                        labels.push(this.getDateLabel(s))
                    else
                        labels.push("")

                    request_bins.push([])
                    sentimentResponses.push([])
                }
                request_bins[request_bins.length - 1].push({
                    "start": s,
                    "end": s+tfSize
                })

                s += tfSize
                req_count += 1
            }

            
            let models = []
            let processComments = async (commentBatches, bin_idx) => {
                let comments = []

                commentBatches.forEach(batch => comments.push(...batch))

                let response = this.sentimentRequest(comments)
                sentimentResponses[bin_idx] = response
                response.then(result => { 
                    this.completedSentimentRequests += 1 
                    if (models.length === 0)
                        models = Object.keys(result.data.data)
                })
            }

            let commentBatches = []
            for (let i=0; i<request_bins.length; i++)
            {
                commentBatches = await Promise.all(request_bins[i].map(x => this.collectComments(x)));
                processComments(commentBatches, i)
            }

            function ensureSentimentSize(sentimentResponses, requiredSentimentRequests) {
                return new Promise(function (resolve, rejectIgnored) { // eslint-disable-line no-unused-vars
                    (function waitForSentiments(){
                        if (sentimentResponses.length === requiredSentimentRequests)
                        {
                            console.log("size fulfilled!")
                         return resolve();
                        }
                        setTimeout(waitForSentiments, 30);
                    })();
            });
}

            await ensureSentimentSize(sentimentResponses, this.requiredSentimentRequests)

            let final_data = {}

            await Promise.all(sentimentResponses).then(result => final_data = { 
                "responses": result,
                "models": models,
                "labels": labels
            })
            console.log('sentiments collected')

            return final_data
        },
        buildUrl: function (start, end, limit) {
            let url = `https://api.pushshift.io/reddit/search/comment/?size=${limit}&sort_type=score&after=${start}&before=${end}&subreddit=${this.subreddit}`
            if (this.top)
                url += '&sort=desc'
            return url
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
        processRequest: async function(url) 
        {
            let response = await fetch(url, {"method": 'GET', "mode": "cors", "Referrer-Policy": "no-referrer"});

            
            
            return response
        },
        collectComments: async function(params)
        {
            let totalRequired = parseInt(this.perTimeFrame)
            let commentsRequired = totalRequired > 100 ? 100 : totalRequired
            let url = this.buildUrl(params.start, params.end, commentsRequired)
            let response = await this.limiter.schedule(this.processRequest, url);

            let response_json = await response.json()
            let comments = []
            let maxTime = 0
            let needMore = (response_json.data.length < totalRequired && !this.top)
            response_json.data.forEach(x => {
                if (x.body != "[removed]" && x.body != "[deleted]") {
                    comments.push([this.slicePerma(x.permalink), x.body.replace(',', '')])
                    if (needMore && x.created_utc > maxTime)
                        maxTime = x.created_utc
                }
                
            })

            let left = 0

            while (needMore)
            {
                left = totalRequired - comments.length
                commentsRequired = left > 100 ? 100 : left
                url = this.buildUrl(maxTime, params.end, commentsRequired)
                response = await this.limiter.schedule(this.processRequest, url)
                response_json = await response.json()
                needMore = response_json.data.length < left
                response_json.data.forEach(x => {
                    if (x.body != "[removed]" && x.body != "[deleted]") {
                        comments.push([this.slicePerma(x.permalink), x.body.replace(',', '')])
                        if (needMore && x.created_utc > maxTime)
                            maxTime = x.created_utc
                    }
                })

                if (response_json.data.length === 0)
                    needMore = false

            }
            
            this.completedRequests += 1
            return comments
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
        getSubmission: async function (pos_id, neg_id) {
            let requests = [`https://api.pushshift.io/reddit/search/submission/?ids=${pos_id}`,
                            `https://api.pushshift.io/reddit/search/submission/?ids=${neg_id}`]
            
            let responses = await Promise.all(requests.map(x => this.limiter.schedule(this.processRequest, x)));
            
            responses[0].json().then(result => this.selectedPos = {title: result.data[0].title, link: result.data[0].full_link})
            responses[1].json().then(result => {
                this.selectedNeg = {title: result.data[0].title, link: result.data[0].full_link}
                this.loading = false
            })
        },
        onChartReady: function () {
            const table = this.$refs.gChart.chartObject
            console.log(table)
        },
        updateSort: function (value) {
            this.top = value
        },
        updateTf: function (value) {
            this.timeFrame = value
        },
        updateLimit: function (value) {
            this.perTimeFrame = value
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