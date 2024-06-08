// server.js
const cors = require('cors');
const http = require('http');
const express = require('express');
const { Server } = require('socket.io');
const fs = require('fs');
const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: '*',
  }
});

const PORT = process.env.PORT || 3001;

let undoStack = [];
let redoStack = [];
app.use(express.static(__dirname));

let canvasData = '';

io.on('connection', (socket) => {
  console.log('A user connected');

  socket.on('draw', (data) => {
    undoStack.push(data);
    socket.broadcast.emit('draw', data);
  });

  socket.on('newMessage', (data) => {
    io.emit('newMessage', data);
  });
  
  socket.on('clearCanvas', () => {
    console.log("Event Clear");
    canvasData = '';
    undoStack = [];
    redoStack = [];
    io.emit('clearCanvas');
  });

  socket.on('getCanvas', () => {
    if (canvasData) {
      socket.emit('canvasData', canvasData);
    }
  });

  socket.on('undo', () => {
    const lastAction = undoStack.pop();
    if (lastAction) {
      redoStack.push(lastAction);
      io.emit('undo', lastAction);
    }
  });

  socket.on('redo', () => {
    const lastRedoAction = redoStack.pop();
    if (lastRedoAction) {
      undoStack.push(lastRedoAction);
      io.emit('redo', lastRedoAction);
    }
  });

  socket.on('disconnect', () => {
    console.log('A user disconnected');
  });
});

server.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
