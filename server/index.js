const users = {};

const http = require('http').createServer();

const io = require('socket.io')(http, {
    cors: { origin: '*' }
});

io.on('connection', (socket) => {
    // Add the user's session ID to the users object
    users[socket.id] = { sessionId: socket.id, timestamp: new Date().toISOString() };
    console.log('A user connected:', users[socket.id]);

    // Listen for messages from the client
    socket.on('message', (message) => {
        console.log('Message received:', message);
        io.emit('message', `${socket.id.substr(0, 2)} said: ${message}`);
    });

    // Handle user disconnection
    socket.on('disconnect', () => {
        console.log('A user disconnected:', users[socket.id]);
        delete users[socket.id]; // Remove user session from the object
    });
});

http.listen(8080, () => console.log('Listening on http://192.168.137.116:8080'));
