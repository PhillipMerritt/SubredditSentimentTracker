let getSentiment = function (subreddit, start, end) {
    let data = [['Time Frame', 'Sentiment']]
    let val = .5
    let label = ''

    for(var i=0; i<30; i++)
    {
        if (i % 2 == 0)
            label = `am ${i}`
        else
            label = `pm ${i}`

        data.push([label, val])

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
                title: `/r/${subreddit} sentiment ${start} - ${end}`
            }
        }
    }
}

export { getSentiment }