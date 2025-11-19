/**
 * WebSocket Service for Real-Time Communication
 *
 * Handles bidirectional WebSocket communication with the Bazzite Optimizer server
 */

import {EventEmitter} from 'events';

export interface SystemMetrics {
  cpu_usage: number;
  cpu_temp: number;
  ram_usage: number;
  gpu_usage: number;
  gpu_temp: number;
  power_watts: number;
  fps: number | null;
  timestamp: string;
}

export interface WebSocketMessage {
  type: string;
  data?: any;
  timestamp?: string;
}

class WebSocketServiceClass extends EventEmitter {
  private ws: WebSocket | null = null;
  private serverUrl: string = '';
  private deviceId: string = '';
  private token: string = '';
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectDelay: number = 2000;
  private pingInterval: NodeJS.Timeout | null = null;

  constructor() {
    super();
    this.setMaxListeners(20); // Increase max listeners
  }

  /**
   * Connect to WebSocket server
   */
  connect(deviceId: string, token: string, host: string = '192.168.1.100', port: number = 8081): void {
    this.deviceId = deviceId;
    this.token = token;
    this.serverUrl = `ws://${host}:${port}/ws/${deviceId}`;

    console.log(`Connecting to WebSocket: ${this.serverUrl}`);

    try {
      this.ws = new WebSocket(this.serverUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.emit('connected');

        // Start ping/pong for keepalive
        this.startPingInterval();

        // Subscribe to metrics stream
        this.send({type: 'subscribe_metrics'});
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          this.handleMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.emit('error', error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.emit('disconnected');
        this.stopPingInterval();

        // Attempt reconnection
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`Reconnecting... Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);

          setTimeout(() => {
            this.connect(this.deviceId, this.token, host, port);
          }, this.reconnectDelay * this.reconnectAttempts);
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.emit('error', error);
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.stopPingInterval();
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Send message to server
   */
  send(message: WebSocketMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected. Cannot send message:', message);
    }
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: WebSocketMessage): void {
    const {type, data} = message;

    switch (type) {
      case 'connected':
        console.log('Server acknowledged connection');
        break;

      case 'authenticated':
        console.log('Authentication successful');
        this.emit('authenticated', data);
        break;

      case 'auth_failed':
        console.error('Authentication failed:', data?.reason);
        this.emit('auth_failed', data);
        break;

      case 'metrics_update':
        this.emit('metrics', data as SystemMetrics);
        break;

      case 'profile_switched':
        console.log('Profile switched:', data?.profile);
        this.emit('profile_switched', data);
        break;

      case 'alert':
        console.log('Alert received:', data);
        this.emit('alert', data);
        break;

      case 'pong':
        // Server responded to ping
        break;

      default:
        console.warn('Unknown message type:', type);
    }
  }

  /**
   * Start ping/pong keepalive
   */
  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      this.send({type: 'ping', timestamp: new Date().toISOString()});
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Stop ping/pong keepalive
   */
  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Switch gaming profile remotely
   */
  switchProfile(profileName: string): void {
    this.send({
      type: 'switch_profile',
      data: {profile_name: profileName, device_id: this.deviceId},
    });
  }

  /**
   * Request current metrics
   */
  requestMetrics(): void {
    this.send({type: 'request_metrics'});
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Singleton instance
export const WebSocketService = new WebSocketServiceClass();
