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
        
        # Create pipeline
        pipeline = (
            "( v4l2src device=/dev/video0 ! "
            "video/x-raw,width=640,height=480,framerate=30/1 ! "
            "videoconvert ! "
            "x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! "
            "rtph264pay name=pay0 pt=96 )"
        )
        
        self.factory.set_launch(pipeline)
        self.factory.set_shared(True)
        
        # Attach factory to path
        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/test", self.factory)
        
        # Start server
        self.server.attach(None)
        print("\nStream ready at rtsp://192.168.2.2:8554/test")
        print("Use this URL in your media player or client\n")

if __name__ == "__main__":
    server = RTSPServer()
    loop = GLib.MainLoop()
    try:
        loop.run()
    except:
        print("Stopping server...")