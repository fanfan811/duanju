const express = require('express');
const request = require('request');
const app = express();

app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    next();
});

app.get('/api', (req, res) => {
    const msg = req.query.msg;
    if (!msg) {
        return res.status(400).send('Missing msg parameter');
    }

    const url = `http://api.yujn.cn/api/moli.php?msg=${encodeURIComponent(msg)}`;
    console.log('Proxying request to:', url);

    request(url, (error, response, body) => {
        if (!error && response.statusCode === 200) {
            console.log('API response:', body);
            res.send(body);
        } else {
            console.error('Proxy error:', error || response.statusCode);
            res.status(500).send('Error connecting to API server');
        }
    });
});

app.get('/ff', (req, res) => {
    const msg = req.query.msg;
    if (!msg) {
        return res.status(400).send('Missing msg parameter');
    }

    const url = `https://api.yujn.cn/api/ff.php?msg=${encodeURIComponent(msg)}`;
    console.log('Proxying request to:', url);

    request(url, (error, response, body) => {
        if (!error && response.statusCode === 200) {
            console.log('API response:', body);
            res.send(body);
        } else {
            console.error('Proxy error:', error || response.statusCode);
            res.status(500).send('Error connecting to API server');
        }
    });
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Proxy server running on http://localhost:${PORT}`);
}).on('error', (err) => {
    console.error('Server failed to start:', err);
}); 