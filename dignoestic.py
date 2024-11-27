#!/usr/bin/env python3
import gi
import time
import subprocess
from datetime import datetime
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib
import os

class EthernetRTSPServer:
    def __init__(self):
        # Initialize GStreamer first
        Gst.init(None)
        
        # Enable detailed debugging for session and media handling
        os.environ["GST_DEBUG"] = "3,rtspsrc:5,rtsp-server:5,rtsp-session:5,rtsp-media:5"
        
        # Create and configure the RTSP server
        self.server = GstRtspServer.RTSPServer()
        self.server.set_address("192.168.2.2")  # Bind to your Ethernet interface
        self.server.set_service("8554")
        
        # Set up session management
        self.session_pool = GstRtspServer.RTSPSessionPool()
        self.server.set_session_pool(self.session_pool)
        
        # Create and configure the media factory
        self.factory = GstRtspServer.RTSPMediaFactory()
        
        # Create a test pipeline that helps diagnose connection issues
        # We start with a test pattern to verify connectivity
        pipeline = (
            "( videotestsrc is-live=true pattern=ball ! "
            "video/x-raw,width=640,height=480,framerate=30/1 ! "
            "videoconvert ! "
            "x264enc tune=zerolatency bitrate=2000 speed-preset=superfast ! "
            "rtph264pay name=pay0 pt=96 )"
        )
        
        # Configure the media factory with our pipeline
        self.factory.set_launch(pipeline)
        self.factory.set_shared(True)
        self.factory.set_latency(100)  # Set a conservative latency value
        
        # Set up signal handlers to monitor connections
        self.server.connect('client-connected', self.on_client_connected)
        
        # Mount the media factory
        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/test", self.factory)
        
        # Start the server
        self.server.attach(None)
        print("\nRTSP Server Configuration:")
        print("==========================")
        print(f"Server URL: rtsp://192.168.2.2:8554/test")
        print("Initial test pattern enabled (moving ball)")
        print("Debug level: Enhanced session monitoring")
        print("\nConnection Instructions:")
        print("1. On client machine (192.168.2.1), try:")
        print("   ffplay -rtsp_transport tcp rtsp://192.168.2.2:8554/test")
    
    def on_client_connected(self, server, client):
        """Monitor and log client connections with enhanced debugging"""
        client_ip = client.get_connection().get_ip()
        print(f"\nConnection Event:")
        print(f"➤ New client connecting from: {client_ip}")
        
        # Set up monitoring for this client
        client.connect('closed', self.on_client_closed)
        client.connect('new-session', self.on_new_session)
    
    def on_client_closed(self, client):
        """Handle client disconnection events"""
        client_ip = client.get_connection().get_ip()
        print(f"\nDisconnection Event:")
        print(f"➤ Client {client_ip} disconnected")
        print("Checking for orphaned sessions...")
        
        # Clean up any remaining sessions
        for session in self.session_pool.filter(None):
            if session.get_connection().get_ip() == client_ip:
                print(f"Cleaning up session: {session.get_sessionid()}")
    
    def on_new_session(self, client, session):
        """Monitor session creation and configuration"""
        print(f"\nSession Creation Event:")
        print(f"➤ New session ID: {session.get_sessionid()}")
        print(f"➤ Client IP: {client.get_connection().get_ip()}")
        session.set_timeout(60)  # Set a 60-second timeout
        print("Session configured with 60s timeout")

    def switch_to_camera(self):
        """Helper method to switch to camera input once test pattern is working"""
        camera_pipeline = (
            "( v4l2src device=/dev/video0 ! "
            "video/x-raw,width=640,height=480,framerate=30/1 ! "
            "videoconvert ! "
            "x264enc tune=zerolatency bitrate=2000 speed-preset=superfast ! "
            "rtph264pay name=pay0 pt=96 )"
        )
        self.factory.set_launch(camera_pipeline)
        print("\nSwitched to camera input")

if __name__ == "__main__":
    print("Starting RTSP server with enhanced diagnostics...")
    server = EthernetRTSPServer()
    loop = GLib.MainLoop()
    
    try:
        loop.run()
    except KeyboardInterrupt:
        print("\nShutting down server gracefully...")
    except Exception as e:
        print(f"\nError encountered: {e}")