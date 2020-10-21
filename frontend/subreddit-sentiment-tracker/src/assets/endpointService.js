import * as dateMath from 'date-arithmetic'
import date from 'date-and-time'

let getSentiment = function (subreddit, start, end) {
    let data = [['Time Frame', 'Sentiment']]
    let val = .5

    let start_date = new Date(start)
    let end_date = new Date(end)
    
    let length = dateMath.diff(start_date, end_date, "day", false)

    const pattern = date.compile("MM/DD")


    let days = []
    start_date = dateMath.add(start_date, 1, "day")
    while(dateMath.lte(start_date, end_date))
    {
        days.push(date.format(start_date, pattern))
        start_date = dateMath.add(start_date, 1, "day")
    }


    for(var i=0; i < length * 4; i++)
    {
        if (i % 4 == 0)
            data.push([`${days[i / 4]}`, val])
        else
            data.push(['', val])

        val += Math.random() * .4 - .2

        if (val > 1.0)
            val = 1.0
        else if (val < -1.0)
            val = -1.0
    }

    return {
        data: data,
        chartOptions: {
            chart: {
                title: `/r/${subreddit} sentiment ${start} to ${end}`
            }
        }
    }
}

export { getSentiment }