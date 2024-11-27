#!/usr/bin/env python3
import gi
import os
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

class RTSPServer:
    def __init__(self):
        Gst.init(None)
        
        self.server = GstRtspServer.RTSPServer()
        self.server.set_service("8554")
        
        self.factory = GstRtspServer.RTSPMediaFactory()
        
        # Modified pipeline with buffer management
        pipeline = (
            "( v4l2src device=/dev/video0 "
            "io-mode=2 " # Memory mapping mode
            "do-timestamp=true "  # Ensure proper timestamps
            "! queue max-size-buffers=2 leaky=downstream "  # Small queue to prevent frame buildup
            "! image/jpeg,width=1920,height=1080,framerate=30/1 "
            "! jpegdec "
            "! queue max-size-buffers=2 leaky=downstream "  # Another queue after decode
            "! videoconvert "
            "! video/x-raw,format=I420 "  # Specify format for encoder
            "! x264enc tune=zerolatency bitrate=4000 speed-preset=superfast "
            "key-int-max=30 threads=4 qp-max=51 "  # Additional encoding parameters
            "! queue max-size-buffers=2 leaky=downstream "  # Queue before network
            "! rtph264pay name=pay0 pt=96 config-interval=1 "
            "! application/x-rtp,media=video,encoding-name=H264,payload=96 )"
        )
        
        self.factory.set_launch(pipeline)
        self.factory.set_shared(True)
        
        # Reduce network latency
        self.factory.set_latency(0)
        self.factory.set_enable_rtcp(True)  # Enable RTCP for better feedback
        
        # Configure buffer settings for the RTSP server
        self.server.set_service("8554")
        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/test", self.factory)
        
        # Apply RTSP settings
        self.server.attach(None)
        print("\nStream ready at rtsp://192.168.2.2:8554/test")
        print("\nPipeline settings:")
        print("- V4L2 IO Mode: memory mapping")
        print("- Buffer queues: max 2 buffers, leaky downstream")
        print("- Resolution: 1920x1080")
        print("- Framerate: 30 fps")
        print("- Encoder threads: 4")
        print("- QP Max: 51")
        print("- RTCP: enabled")

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

def apply_v4l2_settings():
    """Apply optimal V4L2 settings"""
    import subprocess
    try:
        # Set V4L2 buffer settings
        subprocess.run(['v4l2-ctl', '--set-parm=30'], check=True)  # Set framerate
        subprocess.run(['v4l2-ctl', '--set-ctrl=exposure_auto=1'], check=True)  # Manual exposure
        subprocess.run(['v4l2-ctl', '--set-ctrl=exposure_absolute=100'], check=True)  # Fast exposure
        print("Applied V4L2 settings successfully")
    except Exception as e:
        print(f"Error applying V4L2 settings: {e}")

if __name__ == "__main__":
    # Enable debug output
    os.environ["GST_DEBUG"] = "3,v4l2src:4,v4l2bufferpool:4"
    
    # Check camera capabilities first
    print("Checking camera capabilities...")
    caps = check_camera_caps()
    
    if caps is not None:
        proceed = input("Continue with starting the server? (y/n): ")
        if proceed.lower() == 'y':
            # Apply optimal V4L2 settings
            apply_v4l2_settings()
            
            # Start the server
            server = RTSPServer()
            loop = GLib.MainLoop()
            try:
                loop.run()
            except KeyboardInterrupt:
                print("\nStopping server...")
            except Exception as e:
                print(f"\nError: {e}")
                print("Stopping server...")