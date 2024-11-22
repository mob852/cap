# sender.py
import cv2
import socket
import time
import pickle
import struct
import hashlib
from datetime import datetime

def calculate_checksum(data):
    return hashlib.md5(data).hexdigest()

def send_frame(sock, frame, addr, frame_sequence, max_chunk_size=65000):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-4]
    
    # Compress frame with high quality
    _, frame_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    # Create message
    message = {
        'timestamp': time.time(),
        'frame': frame_data,
        'local_time': current_time,
        'sequence': frame_sequence
    }
    
    # Serialize and add checksum
    serialized_data = pickle.dumps(message)
    checksum = calculate_checksum(serialized_data)
    
    # Calculate chunks
    total_chunks = (len(serialized_data) + max_chunk_size - 1) // max_chunk_size
    
    # Send metadata packet
    metadata = {
        'total_chunks': total_chunks,
        'total_size': len(serialized_data),
        'checksum': checksum,
        'sequence': frame_sequence
    }
    metadata_packet = pickle.dumps(metadata)
    sock.sendto(struct.pack('!I', len(metadata_packet)) + metadata_packet, addr)
    
    # Send chunks
    for i in range(total_chunks):
        start = i * max_chunk_size
        end = min(start + max_chunk_size, len(serialized_data))
        chunk = serialized_data[start:end]
        
        # Pack chunk with index and sequence number
        header = struct.pack('!IIQ', i, total_chunks, frame_sequence)
        packet = header + chunk
        sock.sendto(packet, addr)
        
        # Small delay between chunks
        time.sleep(0.0005)
    
    return total_chunks

def start_sender():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65507 * 2)
    receiver_address = ('192.168.1.67', 12346)  # Replace with receiver's IP
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    print(f"Camera resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    
    frame_sequence = 0
    try:
        frame_count = 0
        start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            chunks_sent = send_frame(sock, frame, receiver_address, frame_sequence)
            frame_sequence += 1
            
            frame_count += 1
            elapsed_time = time.time() - start_time
            if elapsed_time > 1.0:
                fps = frame_count / elapsed_time
                print(f"Sending FPS: {fps:.2f}, Chunks per frame: {chunks_sent}")
                frame_count = 0
                start_time = time.time()
            
            time.sleep(1/30)
            
    finally:
        cap.release()
        sock.close()

if __name__ == "__main__":
    start_sender()