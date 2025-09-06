// server/server.js
import express from "express";
import http from "http";
import { Server } from "socket.io";
import cors from "cors";

const app = express();
// permit CORS in dev; change in production
app.use(cors());

const server = http.createServer(app);

const io = new Server(server, {
  cors: {
    origin: process.env.CLIENT_ORIGIN || "*",
    methods: ["GET", "POST"]
  }
});

let sharedState = { message: "Hello everyone" };

io.on("connection", (socket) => {
  console.log("connected:", socket.id);
  socket.emit("state", sharedState);

  socket.on("update", (newState) => {
    // basic replacement — validate/merge in real apps
    sharedState = newState;
    io.emit("state", sharedState);
  });

  socket.on("disconnect", () => console.log("disconnected:", socket.id));
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server listening on ${PORT}`));
