//import FormData from 'form-data'
import axios from 'axios'
//axios.defaults.headers.common['Access-Control-Allow-Origin'] = '*';
import Bottleneck from "bottleneck";

const limiter = new Bottleneck({
  maxConcurrent: 3,
  minTime: 1000
});

//const wrapped = limiter.wrap(processRequest);



async function getComments(subreddit, start, end) {
  let posix_start = Math.floor(new Date(start).getTime() / 1000)
  let s = posix_start
  let e = Math.floor(new Date(end).getTime() / 1000)
  //e = s + 43200
  let days = Math.floor((e - s) / 86400)
  let requests = []

  while (s < e) {
    requests.push({url: `https://api.pushshift.io/reddit/search/comment/?size=100&sort=desc&sort_type=score&after=${s}&before=${s + 3600}&subreddit=${subreddit}`,
    config: {"method": 'GET', "mode": "cors", "Referrer-Policy": "no-referrer"}
  })

    s += 3600
  }

  /* const responses = await limiter.schedule(() => {
    const allTasks = requests.map(x => wrapped(x));

    return Promise.all(allTasks);
  }); */
  const responses = await Promise.all(requests.map(x => limiter.schedule(processRequest, x)));
  //const responses = await limiter.schedule(() =>  processRequest(requests[0]));

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
    bins[getBinIdx(posix_start, comments[i][0])].push(comments[i][1])

  console.log(bins)

  return bins;
}

function getBinIdx(start, current) {
  return Math.floor((current - start) / 21600)
}

async function processRequest(params) {
  let response = await fetch(params.url, params.config);
  while (response.status != 200)
    response = await fetch(params.url, params.config);
  return response
}

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

async function sentimentRequest(comments)
{
  let request_data = new FormData()

  comments.forEach((item) => {
    request_data.append('comments[]', item)
  })
  /* let payload = {
    comments: comments
  } */
  return axios.post('http://127.0.0.1:5000/',
  request_data,
  {headers: {'Content-Type': 'multipart/form-data' }});
  /* return axios({
    url: 'http://127.0.0.1:5000/',
    method: 'post',
    data: payload
  }) */
}

async function getSentiment (subreddit, start, end) {
  let bins = await getComments(subreddit, start, end)
  let responses = []
  bins.forEach(bin => responses.push(sentimentRequest(bin)))
  responses = await Promise.all(responses)
  
  let models = Object.keys(responses[0].data.sentiment)

  let data = {}

  models.forEach(model => {data[model] = [['Time Frame', 'Sentiment', { "role": 'style' }]]}) 
  let val

  for(var i=0; i < models.length; i++)
  {
    for(var j=0; j < responses.length; j++)
    {
      val = responses[j].data.sentiment[models[i]]
      data[models[i]].push(['', val, heatMapColorforValue(((-1 * val) + 1) / 2)])
    }
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