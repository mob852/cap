#!/usr/bin/env python3
import gi
import os
import time
import datetime
import threading
from collections import deque
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

class ComprehensiveLatencyMonitor:
    """Monitors and analyzes latency across all aspects of the video pipeline"""
    def __init__(self):
        # Store timing data for each frame as it moves through the pipeline
        self.frame_timings = {}
        # Keep track of buffer levels at each stage
        self.buffer_levels = {}
        # Rolling window of end-to-end latency measurements
        self.end_to_end_latency = deque(maxlen=30)
        # Track frame dropping
        self.dropped_frames = 0
        self.total_frames = 0
        
        # Define all pipeline stages we want to monitor
        self.stages = ['src', 'dec', 'conv', 'enc', 'pay0']
        
        # Initialize statistics for each stage
        self.stage_stats = {}
        for stage in self.stages:
            self.stage_stats[stage] = {
                'processing_time': deque(maxlen=30),  # Recent processing times
                'queue_time': deque(maxlen=30),       # Time spent in queue
                'buffer_level': 0,                    # Current buffer fullness
                'dropped_frames': 0                   # Frames dropped at this stage
            }
    
    def update_stage(self, stage_name, frame_id, timestamp, buffer_size=None):
        """Record timing data for a frame at a specific pipeline stage"""
        if frame_id not in self.frame_timings:
            self.frame_timings[frame_id] = {}
        
        # Record timestamp for this stage
        self.frame_timings[frame_id][stage_name] = {
            'timestamp': timestamp,
            'buffer_size': buffer_size
        }
        
        # Calculate and store processing time if we have previous stage data
        self._calculate_stage_latency(frame_id, stage_name)
        
        # Clean up old frame data to prevent memory growth
        if len(self.frame_timings) > 100:
            oldest_frame = min(self.frame_timings.keys())
            del self.frame_timings[oldest_frame]
    
    def _calculate_stage_latency(self, frame_id, current_stage):
        """Calculate processing and queuing time for a stage"""
        frame_data = self.frame_timings[frame_id]
        stages = list(frame_data.keys())
        
        if len(stages) >= 2:
            current_idx = stages.index(current_stage)
            if current_idx > 0:
                previous_stage = stages[current_idx - 1]
                
                # Calculate processing time for this stage
                processing_time = (frame_data[current_stage]['timestamp'] - 
                                 frame_data[previous_stage]['timestamp'])
                
                self.stage_stats[previous_stage]['processing_time'].append(processing_time)

class RTSPServer:
    def __init__(self):
        Gst.init(None)
        self.monitor = ComprehensiveLatencyMonitor()
        
        # Enable detailed GStreamer debugging
        Gst.debug_set_active(True)
        Gst.debug_set_default_threshold(1)
        
        self.server = GstRtspServer.RTSPServer()
        self.server.set_service("8554")
        
        self.factory = GstRtspServer.RTSPMediaFactory()
        
        # Enhanced pipeline with strict buffer management and monitoring points
        pipeline = (
            "( v4l2src name=src device=/dev/video0 "
            "io-mode=2 do-timestamp=true "
            # Camera capture with minimal buffering
            "! queue name=q1 max-size-time=0 max-size-bytes=0 "
            "max-size-buffers=1 leaky=downstream "
            "! image/jpeg,width=1280,height=720,framerate=30/1 "
            # JPEG decoder with monitoring
            "! jpegdec name=dec "
            "! queue name=q2 max-size-time=0 max-size-bytes=0 "
            "max-size-buffers=1 leaky=downstream "
            # Format conversion with monitoring
            "! videoconvert name=conv "
            "! video/x-raw,format=I420 "
            # H264 encoder optimized for low latency
            "! x264enc name=enc tune=zerolatency speed-preset=ultrafast "
            "rc-lookahead=0 sliced-threads=true key-int-max=15 threads=4 "
            "qp-max=35 intra-refresh=true "
            # Network output stage with minimal buffering
            "! queue name=q3 max-size-time=0 max-size-bytes=0 "
            "max-size-buffers=1 leaky=downstream "
            "! rtph264pay name=pay0 pt=96 config-interval=1 "
            # Force minimal network buffering
            "! application/x-rtp,media=video,encoding-name=H264,payload=96 )"
        )
        
        self.factory.set_launch(pipeline)
        self.factory.set_shared(True)
        self.factory.set_latency(0)  # Request minimal latency
        self.factory.set_enable_rtcp(True)  # Enable RTCP for network monitoring
        
        # Connect signals for monitoring
        self.factory.connect('media-constructed', self.on_media_constructed)
        
        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/test", self.factory)
        
        self.server.attach(None)
        print("\nStream ready at rtsp://192.168.2.2:8554/test")
        print("Enhanced latency monitoring active...")

    def on_media_constructed(self, factory, media):
        """Set up comprehensive monitoring for the pipeline"""
        pipeline = media.get_element()
        frame_id = [0]  # Use list for nonlocal modification
        
        def create_probe_callback(stage_name):
            def callback(pad, probe_info):
                # Get buffer and timing information
                buf = probe_info.get_buffer()
                pts = buf.pts if buf else 0
                
                # Get queue information if available
                queue_name = f"q{self.monitor.stages.index(stage_name)}" if stage_name != 'pay0' else 'q3'
                queue = pipeline.get_by_name(queue_name)
                buffer_level = queue.get_property('current-level-buffers') if queue else None
                
                # Update monitoring data
                self.monitor.update_stage(stage_name, frame_id[0], time.time(), buffer_level)
                
                # Track frame progression
                if stage_name == 'pay0':
                    frame_id[0] += 1
                
                return Gst.PadProbeReturn.OK
            return callback
        
        # Add monitoring probes to all pipeline stages
        for stage in self.monitor.stages:
            element = pipeline.get_by_name(stage)
            if element:
                pad = element.get_static_pad('src')
                if pad:
                    pad.add_probe(
                        Gst.PadProbeType.BUFFER,
                        create_probe_callback(stage)
                    )
        
        # Start statistics reporting thread
        self.stats_thread = threading.Thread(target=self.print_statistics, daemon=True)
        self.stats_thread.start()
        return True

    def print_statistics(self):
        """Print comprehensive pipeline statistics periodically"""
        while True:
            time.sleep(5)  # Update every 5 seconds
            print("\n=== Comprehensive Pipeline Analysis ===")
            print(f"Time: {datetime.datetime.now().strftime('%H:%M:%S')}")
            
            # Print statistics for each stage
            for stage in self.monitor.stages:
                stats = self.monitor.stage_stats[stage]
                if stats['processing_time']:
                    avg_time = sum(stats['processing_time']) / len(stats['processing_time']) * 1000
                    max_time = max(stats['processing_time']) * 1000
                    min_time = min(stats['processing_time']) * 1000
                    
                    print(f"\n{stage.upper()} Stage:")
                    print(f"  Processing Time (ms):")
                    print(f"    Average: {avg_time:.1f}")
                    print(f"    Min: {min_time:.1f}")
                    print(f"    Max: {max_time:.1f}")
                    print(f"  Buffer Level: {stats['buffer_level']}")
                    
                    # Calculate cumulative latency up to this stage
                    cumulative = sum(sum(self.monitor.stage_stats[s]['processing_time']) / 
                                   len(self.monitor.stage_stats[s]['processing_time'])
                                   for s in self.monitor.stages[:self.monitor.stages.index(stage)+1]
                                   if self.monitor.stage_stats[s]['processing_time']) * 1000
                    print(f"  Cumulative Latency: {cumulative:.1f}ms")

if __name__ == "__main__":
    server = RTSPServer()
    loop = GLib.MainLoop()
    
    try:
        print("\nPress Ctrl+C to stop")
        loop.run()
    except KeyboardInterrupt:
        print("\nGracefully stopping server...")
    except Exception as e:
        print(f"\nError: {e}")