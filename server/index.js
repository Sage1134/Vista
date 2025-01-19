const users = {};

const http = require('http').createServer();

const io = require('socket.io')(http, {
    cors: { origin: '*' }
});

io.on('connection', (socket) => {
    // Listen for login events from the client
    socket.on('login', (email) => {
        if (users[email]) {
            console.log(`User with email ${email} is already logged in.`);
            socket.emit('login-error', 'This email is already logged in.');
        } else {
            // Add the user's email to the users object
            users[email] = { sessionId: socket.id, timestamp: new Date().toISOString() };
            console.log(`User with email ${email} has logged in.`);

            // Emit a success message
            socket.emit('login-success', `Welcome, ${email}!`);
        }
    });

    // Listen for messages from the client
    socket.on('message', (message) => {
        console.log('Message received:', message);
        io.emit('message', `${socket.id.substr(0, 2)} said: ${message}`);
    });

    // Handle user disconnection
    socket.on('disconnect', () => {
        // Find the email associated with this socket
        let userEmail = null;
        for (const email in users) {
            if (users[email].sessionId === socket.id) {
                userEmail = email;
                break;
            }
        }

        if (userEmail) {
            console.log(`User with email ${userEmail} disconnected.`);
            delete users[userEmail]; // Remove the user from the users object
        }
    });
});

http.listen(8080, () => console.log('Listening on http://192.168.137.116:8080'));
