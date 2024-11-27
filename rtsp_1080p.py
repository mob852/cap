#!/usr/bin/env python3
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

class RTSPServer:
    def __init__(self):
        Gst.init(None)
        
        self.server = GstRtspServer.RTSPServer()
        self.server.set_service("8554")
        
        self.factory = GstRtspServer.RTSPMediaFactory()
        
        # Modified pipeline to use MJPG format
        pipeline = (
            "( v4l2src device=/dev/video0 ! "
            "image/jpeg,width=1920,height=1080,framerate=30/1 ! "
            "jpegdec ! "
            "videoconvert ! "
            "x264enc tune=zerolatency bitrate=4000 speed-preset=superfast "
            "key-int-max=30 ! "  # Keyframe every 30 frames
            "rtph264pay name=pay0 pt=96 config-interval=1 )"
        )
        
        self.factory.set_launch(pipeline)
        self.factory.set_shared(True)
        
        # Set latency settings
        self.factory.set_latency(0)
        
        # Attach factory to path
        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/test", self.factory)
        
        # Start server
        self.server.attach(None)
        print("\nStream ready at rtsp://192.168.2.2:8554/test")
        print("Use this URL in your media player or client")
        print("\nEncoding settings:")
        print("- Resolution: 1920x1080")
        print("- Framerate: 30 fps")
        print("- Format: MJPG → H264")
        print("- Bitrate: 4000 kbps")
        print("- Preset: superfast")
        print("- Tuning: zerolatency\n")

def check_camera_caps():
    """Check if camera supports 1080p"""
    import subprocess
    try:
        output = subprocess.check_output(['v4l2-ctl', '--device=/dev/video0', '--list-formats-ext']).decode()
        print("Available camera formats:")
        print(output)
        return output
    except Exception as e:
        print(f"Error checking camera capabilities: {e}")
        return None

if __name__ == "__main__":
    # Check camera capabilities first
    print("Checking camera capabilities...")
    caps = check_camera_caps()
    
    if caps is not None:
        proceed = input("Continue with starting the server? (y/n): ")
        if proceed.lower() == 'y':
            server = RTSPServer()
            loop = GLib.MainLoop()
            try:
                loop.run()
            except KeyboardInterrupt:
                print("\nStopping server...")
            except Exception as e:
                print(f"\nError: {e}")
                print("Stopping server...")