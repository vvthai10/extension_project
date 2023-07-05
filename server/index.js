// Author: vvthai
// Description: Run websocket by js: node index.js

const WebSocket = require("ws");

const wss = new WebSocket.Server({ port: 8082 });

wss.on("connection", (ws) => {
  console.log("New client connected!");
  ws.send("Hello from server!");

  // Nhận dữ liệu từ extension
  ws.on("message", (message) => {
    console.log("Received message from extension: ", message);

    // Xử lý dữ liệu nhận được từ extension

    // Gửi dữ liệu từ server tới extension
    ws.send("Hello from server!");
  });

  ws.on("close", () => {
    console.log("Client has disconnected");
  });
});

// const ws = new WebSocket("ws://localhost:8082");

// ws.addEventListener("open", () => {
//   console.log("We are connected");
// });
