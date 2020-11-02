<template>
    <div class="optionsDiv">
        <vsa-list>
            <vsa-item>
                <vsa-heading>
                    Options
                </vsa-heading>
                <vsa-content class="accContainer">
                    <FormulateInput
                        v-model="top"
                        type="checkbox"
                        label="Sort by top"
                        @input="updateSort"
                        class="topBox"
                    />

                    <p class="formLabel" style="grid-row: 2/3"> Request Time Frame: </p>
                    <FormulateInput
                        type="select"
                        :value="timeFrame"
                        style="margin: 10px; padding: 10px; grid-column: 2 / 3;"
                        :options="timeFrameOptions"
                        @input="updateTf"
                        class="tfSelect"
                    />
                    
                    <p class="formLabel" style="grid-row: 3/4"> Comments per Time Frame:  </p>
                    <FormulateInput
                        :value="perTimeFrame"
                        type="text"
                        inputmode="numeric"
                        pattern="[0-9]*"
                        validation="rangeCheck"
                        :validation-rules="{
                            rangeCheck: numRule
                        }"
                        :validation-messages="{
                            rangeCheck: 'min: 10 and when sorting by top max: 100'
                        }"
                        @input="updateComLimit"
                        class="comSlider"
                    />

                    <p class="infoA">There will be {{tfPerCol}} batches of comments per 6 hour column for a total of {{perColumn}} comments per column.</p>
                    <p class="infoB">These parameters require {{reqPerTf * tfPerCol}} api requests per 6 hour column for a total of {{totalReq}} requests for the {{dayRange}} day range.</p>
                </vsa-content>
            </vsa-item>
        </vsa-list>
    </div>  
</template>

<script>
import 'vue-simple-accordion/dist/vue-simple-accordion.css';

export default {
    name: 'APIcontrols',
    props: {
        dayRange: Number,
        /* top: Boolean,
        timeFrame: String,
        perTimeFrame: String */
    },
    data () {
        return {
            timeFrameOptions: { ten_min: '10 min', twenty_min: '20 min', thirty_min: '30 min', hour: '1 hour', two_hour: '2 hours', three_hour: '3 hours', six_hours: '6 hours'},
            tfDict: { ten_min: '10', twenty_min: '20', thirty_min: '30', hour: '60', two_hour: '120', three_hour: '180', six_hours: '360' },
            top: true,
            timeFrame: 'hour',
            perTimeFrame: '100'
        }
    },
    computed: {
        perTimeFrameRange: function () {
            if (this.top)
                return { min: 10, max: 100 }
            
            return { min: 10, max: 1000 }
        },
        tfPerCol: function () {
            return Math.floor(360 / parseInt(this.tfDict[this.timeFrame]))
        },
        perColumn: function () {
            return this.tfPerCol * parseInt(this.perTimeFrame)
        },
        reqPerTf: function () {
            return Math.ceil(parseInt(this.perTimeFrame) / 100)
        },
        totalReq: function () {
            return this.reqPerTf * this.tfPerCol * 4 * this.dayRange
        }
    },
    methods: {
        updateSort: function (value) {
            this.top = value
            if (this.top && parseInt(this.perTimeFrame) > 100)
                this.perTimeFrame = '100'
                this.$emit('updateLimit', '100')
            this.$emit('updateSort', this.top)
        },
        updateTf: function (value) {
            this.timeFrame = value
            this.$emit('updateTf', this.timeFrame)
        },
        updateComLimit: function (value) {
            this.perTimeFrame = value
            this.$emit('updateLimit', this.perTimeFrame)
        },
        numRule: function (context) {
            let value = parseInt(context.value)
            if (value < 10)
            {
                this.perTimeFrame = '10'
                this.$emit('updateLimit', '10')
                return true
            }
            if (self.top && value > 100)
            {
                this.perTimeFrame = '100'
                this.$emit('updateLimit', '100')
                return true
            }
            return false
        }

    } 
}
</script>

<style>
    .optionsDiv {
        display: flex;
        justify-content: center;
    }

    .vsa-list {
        --vsa-max-width: 720px;
        --vsa-min-width: 300px;
        --vsa-bg-color: #ecf4f3;
        --vsa-highlight-color: #68b0ab;
    }

    .vsa-item__content {
        display: grid;
        grid-template-columns: 40%;
        grid-template-rows: 20% 20% 20% 20%;
    }

    .topBox{
        grid-row: 1 / 2;
        grid-column: 1 / 3; 
        justify-self: center;
        align-self: center;
        padding: 10px;
    }
    .formLabel {
        grid-column: 1 / 2; 
        padding: 10px;
    }
    .tfSelect {
        justify-self: center;
        align-self: center;
        grid-row: 2 / 3; 
        grid-column: 2 / 3; 
        padding: 10px;
    }
    .comSlider {
        grid-row: 3 / 4;
        grid-column: 2 / 3;  
        justify-self: center;
        align-self: center;
        padding: 10px;
    }
    .infoA {
        grid-row: 4 / 5;
        grid-column: 1 / 3; 
        justify-self: center;
        align-self: center;
        padding: 10px;
    }
    .infoB {
        grid-row: 5 / end;
        grid-column: 1 / 3; 
        justify-self: center;
        align-self: center;
        padding: 10px;
    }
</style>