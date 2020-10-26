import * as dateMath from 'date-arithmetic'
import date from 'date-and-time'
import FormData from 'form-data'
import axios from 'axios'

function HSLToHex(h,s,l) {
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
}

function heatMapColorforValue(value){
    var h = (1.0 - value) * 240
    return "color: " + HSLToHex(h, 100, 50);
}

async function getSentiment (subreddit, start, end) {
  let request_data = new FormData()

  request_data.append('subreddit', subreddit)
  request_data.append('start', start)
  request_data.append('end', end)
  let resp = await axios.post('http://127.0.0.1:5000/',
  request_data,
  {headers: {'Content-Type': 'multipart/form-data' }})

  let response_data = resp.data.sentiments

  let data = [['Time Frame', 'Sentiment', { role: 'style' }]]

  let start_date = new Date(start)
  let end_date = new Date(end)
  
  let length = dateMath.diff(start_date, end_date, "day", false)
  console.log(length)

  const pattern = date.compile("MM/DD")

  let days = []
  start_date = dateMath.add(start_date, 1, "day")
  while(dateMath.lte(start_date, end_date))
  {
      days.push(date.format(start_date, pattern))
      start_date = dateMath.add(start_date, 1, "day")
  }

  days.push(date.format(start_date, pattern))

  for(var i=0; i < length * 4; i++)
  {
      if (i % 4 == 0)
          data.push([`${days[i / 4]}`, response_data[i], heatMapColorforValue(((-1 * response_data[i]) + 1) / 2)])
      else
          data.push([' ', response_data[i], heatMapColorforValue(((-1 * response_data[i]) + 1) / 2)])
  }

  console.log(data)

  return {
      data: data,
      chartOptions: {
          chart: {
              title: `/r/${subreddit} sentiment ${start} to ${end}`
          }
      }
  }
}

function stubGetSentiment (subreddit, start, end) {
    let data = [['Time Frame', 'Sentiment', { role: 'style' }]]

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

    let val = .5

    for(var i=0; i < length * 4; i++)
    {
        if (i % 4 == 0)
            data.push([`${days[i / 4]}`, val, heatMapColorforValue(((-1 * val) + 1) / 2)])
        else
            data.push([' ', val, heatMapColorforValue(((-1 * val) + 1) / 2)])

        val += Math.random() * .4 - .2

        if (val > 1.0)
            val = 1.0
        else if (val < -1.0)
            val = -1.0
    }

    console.log(data)

    return {
        data: data,
        chartOptions: {
            chart: {
                title: `/r/${subreddit} sentiment ${start} to ${end}`
            }
        }
    }
}

export { getSentiment, stubGetSentiment }