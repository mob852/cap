#!/usr/bin/env python3
import gi
import os
import time
import datetime
from threading import Thread
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib, GObject

class LatencyMonitor:
    def __init__(self):
        self.last_frame_time = 0
        self.frame_count = 0
        self.start_time = time.time()
        
    def update(self, timestamp):
        current_time = time.time()
        latency = (current_time - (timestamp / Gst.SECOND))
        self.frame_count += 1
        elapsed = current_time - self.start_time
        fps = self.frame_count / elapsed if elapsed > 0 else 0
        print(f"\rLatency: {latency*1000:.1f}ms | FPS: {fps:.1f}", end="")
        return True

class RTSPServer:
    def __init__(self):
        Gst.init(None)
        self.latency_monitor = LatencyMonitor()
        
        # Enable detailed debugging for pipeline elements
        Gst.debug_set_active(True)
        Gst.debug_set_default_threshold(1)
        
        self.server = GstRtspServer.RTSPServer()
        self.server.set_service("8554")
        
        self.factory = GstRtspServer.RTSPMediaFactory()
        
        # Fixed pipeline syntax with proper caps
        pipeline = (
            "( v4l2src device=/dev/video0 name=src "
            "io-mode=2 do-timestamp=true "
            "! queue name=q1 max-size-time=0 max-size-buffers=1 leaky=downstream "
            "! image/jpeg,width=1280,height=720,framerate=30/1 "
            "! jpegdec name=dec "
            "! queue name=q2 max-size-time=0 max-size-buffers=1 leaky=downstream "
            "! videoconvert name=conv "
            "! video/x-raw,format=I420 "
            "! x264enc name=enc tune=zerolatency speed-preset=ultrafast "
            "rc-lookahead=0 sliced-threads=true key-int-max=15 threads=4 "
            "qp-max=35 intra-refresh=true "
            "! queue name=q3 max-size-time=0 max-size-buffers=1 leaky=downstream "
            "! rtph264pay name=pay0 pt=96 config-interval=1 )"
        )
        
        self.factory.set_launch(pipeline)
        self.factory.set_shared(True)
        self.factory.set_latency(0)
        self.factory.set_enable_rtcp(True)
        
        # Connect to media prepared signal instead of configure
        self.factory.connect('media-constructed', self.on_media_constructed)
        
        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/test", self.factory)
        
        self.server.attach(None)
        print("\nStream ready at rtsp://192.168.2.2:8554/test")
        print("\nMonitoring latency and pipeline statistics...")
        
        # Start statistics thread
        self.running = True
        self.stats_thread = Thread(target=self.print_statistics, daemon=True)
        self.stats_thread.start()

    def on_media_constructed(self, factory, media):
        """Called when a new media pipeline is constructed"""
        # Get the pipeline using the correct method
        pipeline = media.get_element()
        
        # Add probes to monitor latency
        element_names = ['src', 'dec', 'conv', 'enc', 'pay0']
        for name in element_names:
            element = pipeline.get_by_name(name)
            if element:
                pad = element.get_static_pad('src')
                if pad:
                    pad.add_probe(
                        Gst.PadProbeType.BUFFER,
                        self.probe_callback,
                        name
                    )
        return True

    def probe_callback(self, pad, info, element_name):
        """Callback for pad probes to measure timing"""
        buf = info.get_buffer()
        pts = buf.pts
        
        if pts != Gst.CLOCK_TIME_NONE:
            current_time = time.time() * Gst.SECOND
            latency = (current_time - pts) / Gst.SECOND
            print(f"\n{element_name} Latency: {latency*1000:.1f}ms")
            
            # Update overall latency for the final element
            if element_name == 'pay0':
                self.latency_monitor.update(pts)
        
        return Gst.PadProbeReturn.OK

    def print_statistics(self):
        """Thread to print pipeline statistics periodically"""
        while self.running:
            time.sleep(5)
            print("\n--- Pipeline Statistics ---")
            try:
                # Get RTSP session statistics
                sessions = self.server.get_sessions()
                if sessions:
                    print(f"Active RTSP sessions: {len(sessions)}")
                    for session in sessions:
                        print(f"Session timeout: {session.get_timeout()}")
                        print(f"Session media status: {session.get_media()}")
            except Exception as e:
                print(f"Error getting statistics: {e}")

def measure_client_latency():
    """Utility function to measure client-side latency"""
    import cv2
    
    cap = cv2.VideoCapture("rtsp://192.168.2.2:8554/test")
    start_time = time.time()
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if ret:
            frame_count += 1
            current_time = time.time()
            elapsed = current_time - start_time
            fps = frame_count / elapsed
            
            # Add timing information to frame
            cv2.putText(frame, 
                       f"FPS: {fps:.1f} | Frame #{frame_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow('RTSP Stream', frame)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    server = RTSPServer()
    loop = GLib.MainLoop()
    
    try:
        loop.run()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.running = False
    except Exception as e:
        print(f"\nError: {e}")
        server.running = False