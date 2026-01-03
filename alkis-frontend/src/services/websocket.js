import { io } from 'socket.io-client';
import { WS_URL } from '../utils/constants';

// WebSocket service for real-time chat updates (needs to be connected to backend)

class WebSocketService {
    constructor() {
        this.socket = null;
    }

    connect() {
        this.socket = io(WS_URL, {
            transports: ['websocket'],
            reconnection: true,
        });

        this.socket.on('connect', () => {
            console.log('WebSocket connected');
        });

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
        });

        return this.socket;
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }

    on(event, callback) {
        if (this.socket) {
            this.socket.on(event, callback);
        }
    }

    emit(event, data) {
        if (this.socket) {
            this.socket.emit(event, data);
        }
    }
}

export default new WebSocketService();