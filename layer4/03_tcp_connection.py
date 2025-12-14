#!/usr/bin/env python3
"""
Layer 4 Demo: Complete TCP Connection
======================================

This script demonstrates a complete TCP session.
You'll learn:
- Full TCP lifecycle (connect → transfer → close)
- Data transfer over TCP
- Connection termination

Run server: python3 03_tcp_connection.py server
Run client: python3 03_tcp_connection.py client

EXPERIMENT IDEAS:
1. Transfer different amounts of data
2. Monitor sequence/ack numbers
3. Observe graceful vs abrupt close
"""

import socket
import sys
import threading
import time

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_tcp_lifecycle():
    """Explain complete TCP connection lifecycle"""
    print_section("Complete TCP Lifecycle")
    print("""
TCP Connection Phases:

1. CONNECTION ESTABLISHMENT (3-way handshake)
   Client → Server: SYN
   Server → Client: SYN-ACK
   Client → Server: ACK
   Status: ESTABLISHED

2. DATA TRANSFER
   - Either side can send data
   - Each byte has a sequence number
   - Receiver acknowledges data (ACK)
   - Flow control via window size
   - Retransmission if lost

3. CONNECTION TERMINATION (4-way handshake)
   Active → Passive: FIN
   Passive → Active: ACK
   Passive → Active: FIN
   Active → Passive: ACK
   Status: CLOSED

Alternative: Abrupt termination
   Either → Other: RST
   Status: CLOSED immediately

States During Lifecycle:
   CLOSED
   → LISTEN (server)
   → SYN-SENT (client) / SYN-RECEIVED (server)
   → ESTABLISHED (both)
   → FIN-WAIT-1, FIN-WAIT-2, CLOSING (active close)
   → CLOSE-WAIT, LAST-ACK (passive close)
   → TIME-WAIT
   → CLOSED
    """)

def tcp_server(host='127.0.0.1', port=9999):
    """TCP echo server"""
    print_section(f"TCP Server on {host}:{port}")
    
    # Create socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind and listen
    server_sock.bind((host, port))
    server_sock.listen(5)
    
    print(f"✓ Server listening on {host}:{port}")
    print(f"✓ State: LISTEN")
    print(f"✓ Waiting for connections...\n")
    
    try:
        while True:
            # Accept connection (completes 3-way handshake)
            print("Waiting for client...")
            client_sock, client_addr = server_sock.accept()
            
            print(f"\n✓ Connection from {client_addr}")
            print(f"✓ State: ESTABLISHED")
            
            # Get socket info
            local = client_sock.getsockname()
            remote = client_sock.getpeername()
            print(f"  Local: {local[0]}:{local[1]}")
            print(f"  Remote: {remote[0]}:{remote[1]}")
            
            # Handle client in thread (to accept multiple)
            thread = threading.Thread(
                target=handle_client,
                args=(client_sock, client_addr)
            )
            thread.start()
            
    except KeyboardInterrupt:
        print("\n\nServer shutting down...")
    finally:
        server_sock.close()

def handle_client(sock, addr):
    """Handle a single client connection"""
    try:
        message_count = 0
        
        while True:
            # Receive data
            data = sock.recv(1024)
            
            if not data:
                # Client closed connection
                print(f"\n[{addr}] Client closed connection")
                print(f"  Received FIN from client")
                print(f"  State: CLOSE-WAIT")
                break
            
            message_count += 1
            print(f"\n[{addr}] Message {message_count}:")
            print(f"  Received: {data.decode()}")
            print(f"  Bytes: {len(data)}")
            
            # Echo back
            response = f"Echo {message_count}: {data.decode()}"
            sock.sendall(response.encode())
            print(f"  Sent: {response}")
        
        # Close our end
        print(f"[{addr}] Closing connection...")
        print(f"  Sending FIN to client")
        sock.close()
        print(f"  State: CLOSED")
        
    except Exception as e:
        print(f"[{addr}] Error: {e}")
    finally:
        sock.close()

def tcp_client(host='127.0.0.1', port=9999):
    """TCP client"""
    print_section(f"TCP Client connecting to {host}:{port}")
    
    # Create socket
    print("\n1. Creating TCP socket...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("   ✓ Socket created")
    
    # Connect (initiates 3-way handshake)
    print(f"\n2. Connecting to {host}:{port}...")
    print("   Sending SYN...")
    sock.connect((host, port))
    print("   ✓ Connection established!")
    print("   ✓ 3-way handshake complete")
    print("   ✓ State: ESTABLISHED")
    
    # Get connection info
    local = sock.getsockname()
    remote = sock.getpeername()
    print(f"\n   Local: {local[0]}:{local[1]}")
    print(f"   Remote: {remote[0]}:{remote[1]}")
    
    # Send messages
    messages = [
        "Hello, TCP!",
        "Testing data transfer",
        "Message number 3",
        "Final message"
    ]
    
    print_section("Data Transfer Phase")
    
    for i, msg in enumerate(messages, 1):
        print(f"\nMessage {i}:")
        print(f"  Sending: {msg}")
        sock.sendall(msg.encode())
        
        # Receive echo
        response = sock.recv(1024).decode()
        print(f"  Received: {response}")
        
        time.sleep(0.5)
    
    # Close connection (initiates 4-way handshake)
    print_section("Connection Termination")
    print("\n1. Initiating close...")
    print("   Sending FIN to server")
    sock.close()
    print("   ✓ Connection closed")
    print("   ✓ 4-way handshake complete")
    print("   ✓ State: CLOSED")

def demonstrate_sequence_numbers():
    """Explain sequence and acknowledgment numbers"""
    print_section("Sequence and Acknowledgment Numbers")
    print("""
Every byte in TCP has a sequence number:

Initial Setup (Handshake):
  Client: SYN, seq=1000
  Server: SYN-ACK, seq=5000, ack=1001
  Client: ACK, seq=1001, ack=5001

Data Transfer Example:
  Client sends 100 bytes:
    seq=1001, len=100
    (bytes 1001-1100)
  
  Server acknowledges:
    ack=1101
    (I received up to byte 1100, send 1101 next)
  
  Client sends 50 more bytes:
    seq=1101, len=50
    (bytes 1101-1150)
  
  Server acknowledges:
    ack=1151

Why sequence numbers?
✓ Detect missing data
✓ Reorder out-of-order packets
✓ Detect duplicates
✓ Reliable delivery
    """)

def demonstrate_window_size():
    """Explain TCP window and flow control"""
    print_section("Flow Control and Window Size")
    print("""
TCP Window Size = Flow Control Mechanism

Window size tells sender: "I can receive N bytes"

Example:
  Receiver: window=1000 bytes
  Sender: Can send up to 1000 bytes without ACK
  
  Sender transmits 1000 bytes
  Receiver: window=0 (buffer full)
  Sender: STOPS sending (waits for window update)
  
  Receiver processes data
  Receiver: window=1000 (buffer available)
  Sender: Resumes sending

Benefits:
✓ Prevents receiver overflow
✓ Automatic pacing
✓ Adapts to receiver speed

Related:
- Congestion control (cwnd): Based on network conditions
- Flow control (rwnd): Based on receiver capacity
- Effective window = min(cwnd, rwnd)
    """)

def main():
    """Main demonstration function"""
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "server":
            tcp_server()
            return
        elif mode == "client":
            tcp_client()
            return
    
    # Default: Educational demo
    print("\n" + "="*60)
    print("  LAYER 4: COMPLETE TCP CONNECTION DEMO")
    print("="*60)
    print("\nThis demo shows the complete TCP lifecycle.")
    print("See connection establishment, data transfer, and termination!")
    
    explain_tcp_lifecycle()
    demonstrate_sequence_numbers()
    demonstrate_window_size()
    
    print_section("Running the Demo")
    print("""
Terminal 1 (Server):
    python3 03_tcp_connection.py server

Terminal 2 (Client):
    python3 03_tcp_connection.py client

Watch the complete TCP lifecycle!
    """)
    
    print_section("Experiments to Try")
    print("""
1. Monitor TCP states:
   watch -n 1 'ss -tan | grep 9999'
   (Run while server/client operate)

2. Capture full connection:
   sudo tcpdump -i lo port 9999 -w tcp_session.pcap
   (Open in Wireshark, Follow TCP Stream)

3. Analyze in Wireshark:
   - Filter: tcp.port == 9999
   - Statistics → Flow Graph
   - See handshakes and data

4. Check sequence numbers:
   - In Wireshark: Look at tcp.seq and tcp.ack
   - Verify seq increments by data length

5. Observe window size:
   - Wireshark: tcp.window_size
   - See how it changes

6. Test abrupt close:
   - Modify client to kill process
   - Server receives RST instead of FIN

7. Monitor socket buffer:
   ss -tmn | grep 9999
   (Shows send/receive queue sizes)
    """)
    
    print("\n✅ Demo complete! Continue to 04_tcp_states.py\n")

if __name__ == "__main__":
    main()
