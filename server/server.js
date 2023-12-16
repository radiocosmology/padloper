let express = require('express');
let cors = require('cors');
const fetch = (...args) =>
    import('node-fetch').then(({default: fetch}) => fetch(...args));
let bodyParser = require('body-parser');

const CLIENT_ID = ""
const CLIENT_SECRET = ""

let app = express();

app.use(cors());
app.use(bodyParser.json());

// code passed from frontend
app.get('/getAccessToken', async function (req, res) {

    console.log(req.query.code);

    const params = `?client_id=${CLIENT_ID}&client_secret=${CLIENT_SECRET}&code=${req.query.code}`

    await fetch("https://github.com/login/oauth/access_token" + params, {
        method: "POST",
        headers: {
            "Accept": "application/json"
        }
    }).then((response) => {
        return response.json();
    }).then((data) => {
        console.log(data);
        res.json(data)
    });
});

// getUserData
// access token passed in as bearer token in auth header
app.get('/getUserData', async function(req, res) {
    req.get("Authorization");
    await fetch('https://api.github.com/user', {
        method: 'GET',
        headers: {
            "Authorization": req.get("Authorization")
        }
    }).then((response) => {
        return response.json();
    }).then((data) => {
        console.log(data);
        res.json(data);
    })
})

app.listen(4000, function() {
    console.log("CORS server running on port 4000");
});