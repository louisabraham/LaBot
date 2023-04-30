const http = require('http');
const WebSocket = require('ws');

(async () => {
    console.log(await labot("/decode", {hex: "45450303ac1e"}));
    console.log(await labot("/decode", {hex: "3d3d0000000b1700154a476365444444444e3177364f4379516339233031"}));
    console.log(await labot("/decode", {
        hex: "3d3d0000000b1700154a476365444444444e3177364f4379516339233031",
        client: true
    }));
    console.log(await labot("/encode", {message: {__type__: 'ClientKeyMessage', key: 'JGceDDDDN1w6OCyQc9#01'}}));
    console.log(await labot("/encode", {message: {__type__: 'BasicAckMessage', lastPacketId: 3884, seq: 3}}));
})();

const ws = new WebSocket('ws://127.0.0.1:5000/ws');

ws.on('open', function () {
    ws.send(JSON.stringify({
        action: 'encode',
        message: {__type__: 'ClientKeyMessage', key: 'JGceDDDDN1w6OCyQc9#01'}
    }));
    ws.send(JSON.stringify({action: 'decode', hex: '45450303ac1e'}));
    ws.send(JSON.stringify({action: 'decode', hex: '3d3d0000000b1700154a476365444444444e3177364f4379516339233031'}));
    ws.send(JSON.stringify({
        action: 'decode',
        hex: '3d3d0000000b1700154a476365444444444e3177364f4379516339233031',
        client: true
    }));
});

ws.on('message', function message(data) {
    console.log(JSON.parse(data.toString()));
});

ws.on('error', function () {
});

ws.on('close', function () {
});

function labot(path, body) {
    return new Promise(function (resolve) {
        const content = JSON.stringify(body);
        const req = http.request({
            hostname: "127.0.0.1",
            port: 5000,
            path,
            method: 'POST'
        }, (res) => {
            let data = "";
            res.on('data', function (body) {
                data += body;
            });
            res.on('end', function () {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    resolve({error: true});
                }
            });
        }).on('error', function () {
            resolve({error: true});
        });
        req.setHeader('Content-Length', content.length);
        req.setHeader('Content-Type', 'application/json');
        req.write(content);
        req.end();
    });
}