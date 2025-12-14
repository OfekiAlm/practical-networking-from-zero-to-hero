#!/usr/bin/env python3
"""
Layer 4 Demo: UDP Basics
=========================

This script demonstrates UDP (User Datagram Protocol).
You'll learn:
- UDP packet structure
- UDP vs TCP differences
- Simple client/server implementation

Run server: python3 01_udp_basics.py server
Run client: python3 01_udp_basics.py client

EXPERIMENT IDEAS:
1. Send messages of different sizes
2. Simulate packet loss
3. Compare with TCP behavior
"""

from scapy.all import UDP, IP, send, sniff
import socket
import sys
import threading
import time

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_udp():
    """Explain UDP fundamentals"""
    print_section("UDP (User Datagram Protocol)")
    print("""
UDP Characteristics:
✓ Connectionless - no handshake, just send
✓ Unreliable - no delivery guarantee
✓ No ordering - packets may arrive out of order
✓ Fast - minimal overhead (8-byte header)
✓ Lightweight - no connection state

UDP Header (only 8 bytes!):
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|            Length             |           Checksum            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            Data...                            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

When to use UDP:
✓ Speed is critical (gaming, VoIP)
✓ Broadcast/multicast needed
✓ Small requests (DNS queries)
✓ Loss is acceptable (video streaming)
✓ Custom reliability (QUIC, custom protocols)

When NOT to use UDP:
✗ Need guaranteed delivery (file transfer)
✗ Need ordering (HTTP requests)
✗ Need flow control (large data transfer)
    """)

def create_udp_packet():
    """Create and display UDP packet"""
    print_section("Creating a UDP Packet")
    
    # Create UDP packet
    packet = IP(dst="8.8.8.8")/UDP(sport=12345, dport=53)/"Hello UDP"
    
    print("\nComplete UDP Packet:")
    print(packet.show(dump=True))
    
    print("\n\nUDP Header Fields:")
    udp = packet[UDP]
    print(f"Source Port: {udp.sport}")
    print(f"Destination Port: {udp.dport}")
    print(f"Length: {udp.len} bytes (header + data)")
    print(f"Checksum: {udp.chksum:#06x}")
    
    print("\n\nPayload:")
    if hasattr(udp, 'load'):
        print(f"Data: {udp.load}")
    
    print("\n💡 Notice: Only 8 bytes of header overhead!")
    print("💡 Compare to TCP: 20 bytes minimum header")

def udp_server(host='127.0.0.1', port=9999):
    """Simple UDP echo server"""
    print_section(f"UDP Server on {host}:{port}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    
    print(f"✓ Server listening on {host}:{port}")
    print("✓ Waiting for UDP packets...\n")
    
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"Received from {addr}:")
            print(f"  Data: {data.decode()}")
            print(f"  Size: {len(data)} bytes")
            
            # Echo back
            response = f"Echo: {data.decode()}"
            sock.sendto(response.encode(), addr)
            print(f"  Sent echo response\n")
            
    except KeyboardInterrupt:
        print("\n\nServer shutting down...")
    finally:
        sock.close()

def udp_client(host='127.0.0.1', port=9999):
    """Simple UDP client"""
    print_section(f"UDP Client connecting to {host}:{port}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    messages = [
        "Hello, UDP Server!",
        "Message 2",
        "Testing UDP communication",
        "Final message"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"\nSending message {i}: '{msg}'")
        sock.sendto(msg.encode(), (host, port))
        
        # Wait for response
        sock.settimeout(2)
        try:
            data, server = sock.recvfrom(1024)
            print(f"✓ Received: {data.decode()}")
        except socket.timeout:
            print("✗ No response (timeout)")
        
        time.sleep(1)
    
    sock.close()
    print("\n✓ Client finished")

def demonstrate_udp_properties():
    """Demonstrate UDP characteristics"""
    print_section("UDP Properties Demonstration")
    
    print("""
Let's demonstrate UDP's key properties:

1. Connectionless:
   - No handshake before sending
   - Each packet is independent
   - No connection state
    """)
    
    print("\n2. No Reliability:")
    print("   - If packet is lost, sender doesn't know")
    print("   - No automatic retransmission")
    print("   - Application must handle losses")
    
    print("\n3. No Ordering:")
    print("   - Packets may arrive out of order")
    print("   - Application must reorder if needed")
    
    print("\n4. Speed:")
    print("   - Minimal overhead (8 bytes)")
    print("   - No acknowledgments")
    print("   - No congestion control")

def compare_udp_tcp():
    """Compare UDP and TCP"""
    print_section("UDP vs TCP Comparison")
    
    print(f"""
{'Feature':<25} {'UDP':<20} {'TCP':<20}
{'-'*65}
{'Connection':<25} {'Connectionless':<20} {'Connection-oriented':<20}
{'Reliability':<25} {'Unreliable':<20} {'Reliable':<20}
{'Ordering':<25} {'No guarantee':<20} {'Guaranteed':<20}
{'Speed':<25} {'Fast':<20} {'Slower':<20}
{'Header size':<25} {'8 bytes':<20} {'20-60 bytes':<20}
{'Overhead':<25} {'Low':<20} {'Higher':<20}
{'Flow control':<25} {'No':<20} {'Yes':<20}
{'Congestion control':<25} {'No':<20} {'Yes':<20}
{'Broadcasting':<25} {'Supported':<20} {'Not supported':<20}
{'Use cases':<25} {'DNS, VoIP, Gaming':<20} {'HTTP, Email, FTP':<20}
    """)

def show_common_udp_ports():
    """Display common UDP ports"""
    print_section("Common UDP Ports")
    
    ports = [
        (53, "DNS", "Domain Name System"),
        (67, "DHCP Server", "Dynamic Host Configuration Protocol"),
        (68, "DHCP Client", "Dynamic Host Configuration Protocol"),
        (69, "TFTP", "Trivial File Transfer Protocol"),
        (123, "NTP", "Network Time Protocol"),
        (161, "SNMP", "Simple Network Management Protocol"),
        (500, "IKE", "Internet Key Exchange (IPsec)"),
        (514, "Syslog", "System Logging"),
        (1900, "SSDP", "Simple Service Discovery Protocol"),
        (5353, "mDNS", "Multicast DNS"),
    ]
    
    print(f"\n{'Port':<8} {'Service':<20} {'Description'}")
    print("-" * 60)
    for port, service, desc in ports:
        print(f"{port:<8} {service:<20} {desc}")
    
    print("\n💡 UDP is popular for services that need speed over reliability")

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 4: UDP BASICS DEMO")
    print("="*60)
    print("\nThis demo explores UDP protocol.")
    print("See how connectionless communication works!")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "server":
            udp_server()
            return
        elif mode == "client":
            udp_client()
            return
    
    # Default: Educational demo
    explain_udp()
    create_udp_packet()
    demonstrate_udp_properties()
    compare_udp_tcp()
    show_common_udp_ports()
    
    print_section("Running the Demo")
    print("""
To see UDP in action:

Terminal 1 (Server):
    python3 01_udp_basics.py server

Terminal 2 (Client):
    python3 01_udp_basics.py client

Watch messages being exchanged!
    """)
    
    print_section("Experiments to Try")
    print("""
1. Capture UDP traffic:
   sudo tcpdump -i lo udp port 9999 -vv

2. Send UDP with netcat:
   echo "Hello" | nc -u localhost 9999

3. Test packet loss:
   - Use tc (traffic control) to simulate loss
   - See how application handles it

4. Monitor DNS (UDP):
   sudo tcpdump -i any udp port 53 -vv
   (Run while browsing websites)

5. Compare sizes:
   - Send same data via UDP and TCP
   - Use Wireshark to compare packet sizes
   - Notice UDP's lower overhead

6. Test large packets:
   - Send 2KB message via UDP
   - May fragment at IP layer
   - Observe in tcpdump
    """)
    
    print("\n✅ Demo complete! Continue to 02_tcp_handshake.py\n")

if __name__ == "__main__":
    main()
