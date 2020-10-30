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
    var h = ((value * 8) + 1) * 120
    if (h > 240)
      h = 240
    else if (h < 0)
      h = 0
    return "color: " + HSLToHex(h, 100, 50);
}

async function sentimentRequest(comments)
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
}

async function getSentiment (subreddit, start, end, bins) {
  let responses = []
  bins.forEach(bin => responses.push(sentimentRequest(bin.comments)))
  responses = await Promise.all(responses)
  
  let models = Object.keys(responses[0].data.data)

  let data = {}
  let tooltips = {}

  models.forEach(model => {
    data[model] = [['Time Frame', 'Sentiment', { "role": 'style' }, { "role": 'tooltip' }]]
    tooltips[model] = []
  })

  let val
  let most_pos
  let most_neg

  for(var i=0; i < models.length; i++)
  {
    for(var j=0; j < responses.length; j++)
    {
      val = responses[j].data.data[models[i]].sentiment
      data[models[i]].push([bins[j].label, val, heatMapColorforValue(val), "Click me to load extreme posts!"])

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
              fontName: 'Armata'
          }
      }
  }
}

function stubGetSentiment (subreddit, start, end) {
    let data = {"sentiments": {"model1": [["Time Frame", "Sentiment", { "role": "style" }], 
    ["10/05", 0.07427789473684211], 
    ["", 0.1258474747474748],
    ["", 0.22346881720430106],
    ["", 0.19327052631578945],
    ["10/06", 0.1445673684210526],
    ["", 0.0303391304347826],
    ["", 0.20081212121212128],
    ["", 0.1705742268041237]], 
    "model2": [["Time Frame", "Sentiment", { "role": "style" }], 
    ["10/05", 0.09241290322580643], 
    ["", 0.14102959183673466],
    ["", 0.18095744680851064],
    ["", 0.14809898989898992],
    ["10/06", 0.03467916666666665],
    ["", 0.05460760869565217],
    ["", 0.14182173913043478],
    ["", 0.10901313131313133]]}}

    let response_data = data.sentiments

    let keys = Object.keys(response_data)

    for(var i=0; i < keys.length; i++)
    {
      for(var j=1; j < response_data[keys[i]].length; j++)
      {
        response_data[keys[i]][j].push(heatMapColorforValue(((-1 * response_data[keys[i]][j][1]) + 1) / 2))
      }
    }

    return {
        data: response_data,
        chartOptions: {
            chart: {
                title: `/r/${subreddit} sentiment ${start} to ${end}`
            }
        }
    }
}

export { getSentiment, stubGetSentiment }