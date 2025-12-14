#!/usr/bin/env python3
"""
Layer 3 Demo: ICMP Ping Implementation
=======================================

This script demonstrates ICMP and builds a custom ping utility.
You'll learn:
- How ICMP works
- Ping implementation details
- Echo request/reply structure

Run with: sudo python3 02_icmp_ping.py

EXPERIMENT IDEAS:
1. Ping different hosts and observe RTT
2. Modify packet size and see fragmentation
3. Change TTL to test reachability
"""

from scapy.all import IP, ICMP, sr1, send
import time
import statistics

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_icmp():
    """Explain ICMP protocol"""
    print_section("ICMP (Internet Control Message Protocol)")
    print("""
ICMP is used for:
✓ Network diagnostics (ping, traceroute)
✓ Error reporting (destination unreachable, time exceeded)
✓ Network management

ICMP is Layer 3 (sits on top of IP, but considered part of IP suite)

Common ICMP Types:
- Type 0: Echo Reply (ping response)
- Type 3: Destination Unreachable
- Type 8: Echo Request (ping)
- Type 11: Time Exceeded (TTL=0)

ICMP Echo structure:
- Type: 8 (request) or 0 (reply)
- Code: 0
- Checksum: Error detection
- Identifier: Match requests to replies
- Sequence: Track individual pings
- Data: Optional payload
    """)

def create_icmp_packet():
    """Create and display ICMP packet"""
    print_section("Creating ICMP Echo Request")
    
    # Create ICMP echo request
    ip = IP(dst="8.8.8.8")
    icmp = ICMP(type=8, code=0, id=12345, seq=1)
    packet = ip/icmp/"Hello, Network!"
    
    print("\nComplete ICMP Packet:")
    print(packet.show(dump=True))
    
    print("\n\nICMP Header Fields:")
    print(f"Type: {icmp.type} (8 = Echo Request)")
    print(f"Code: {icmp.code} (0 = No code)")
    print(f"Checksum: {icmp.chksum} (calculated automatically)")
    print(f"Identifier: {icmp.id} (matches request to reply)")
    print(f"Sequence: {icmp.seq} (counts ping attempts)")
    print(f"Payload: {packet[ICMP].load if hasattr(packet[ICMP], 'load') else 'None'}")
    
    return packet

def send_single_ping(destination, timeout=2, ttl=64):
    """Send a single ping and get response"""
    print(f"\nPinging {destination}...")
    
    # Create packet
    packet = IP(dst=destination, ttl=ttl)/ICMP()
    
    # Record time and send
    start_time = time.time()
    reply = sr1(packet, timeout=timeout, verbose=0)
    rtt = (time.time() - start_time) * 1000  # Convert to ms
    
    if reply:
        print(f"✅ Reply from {reply.src}")
        print(f"   TTL: {reply.ttl}")
        print(f"   Time: {rtt:.2f} ms")
        print(f"   ICMP Type: {reply[ICMP].type} (0 = Echo Reply)")
        print(f"   Sequence: {reply[ICMP].seq}")
        return rtt
    else:
        print(f"❌ No reply (timeout after {timeout}s)")
        return None

def ping_host(destination, count=4, interval=1, size=56):
    """Implement a full ping utility"""
    print_section(f"PING {destination}")
    
    print(f"Sending {count} ICMP echo requests with {size} bytes of data\n")
    
    sent = 0
    received = 0
    rtts = []
    
    for i in range(count):
        # Create packet with sequence number
        packet = IP(dst=destination)/ICMP(seq=i)/("X" * size)
        
        # Send and time
        start_time = time.time()
        reply = sr1(packet, timeout=2, verbose=0)
        rtt = (time.time() - start_time) * 1000
        
        sent += 1
        
        if reply:
            received += 1
            rtts.append(rtt)
            print(f"{len(packet)} bytes from {reply.src}: icmp_seq={i} ttl={reply.ttl} time={rtt:.2f} ms")
        else:
            print(f"Request timeout for icmp_seq {i}")
        
        # Wait before next ping (except for last one)
        if i < count - 1:
            time.sleep(interval)
    
    # Statistics
    print(f"\n--- {destination} ping statistics ---")
    print(f"{sent} packets transmitted, {received} received, {(sent-received)/sent*100:.1f}% packet loss")
    
    if rtts:
        print(f"rtt min/avg/max/stddev = {min(rtts):.2f}/{statistics.mean(rtts):.2f}/{max(rtts):.2f}/{statistics.stdev(rtts) if len(rtts) > 1 else 0:.2f} ms")

def demonstrate_icmp_types():
    """Show different ICMP message types"""
    print_section("ICMP Message Types")
    
    icmp_types = [
        (ICMP(type=8, code=0), "Echo Request (Ping)"),
        (ICMP(type=0, code=0), "Echo Reply (Ping response)"),
        (ICMP(type=3, code=0), "Dest Unreachable: Network"),
        (ICMP(type=3, code=1), "Dest Unreachable: Host"),
        (ICMP(type=3, code=3), "Dest Unreachable: Port"),
        (ICMP(type=11, code=0), "Time Exceeded (TTL=0)"),
        (ICMP(type=5, code=0), "Redirect"),
    ]
    
    for icmp, desc in icmp_types:
        print(f"\n{desc}:")
        print(f"  Type: {icmp.type}, Code: {icmp.code}")

def test_different_ttls(destination):
    """Test ping with different TTL values"""
    print_section("Testing Different TTL Values")
    
    print(f"\nPinging {destination} with varying TTL values:")
    print("(Lower TTL values may cause 'Time Exceeded' errors)\n")
    
    for ttl in [1, 5, 10, 64]:
        packet = IP(dst=destination, ttl=ttl)/ICMP()
        start_time = time.time()
        reply = sr1(packet, timeout=2, verbose=0)
        rtt = (time.time() - start_time) * 1000
        
        if reply:
            if reply.haslayer(ICMP):
                icmp_type = reply[ICMP].type
                if icmp_type == 0:
                    print(f"TTL {ttl:3d}: ✅ Success! Reply from {reply.src} ({rtt:.2f} ms)")
                elif icmp_type == 11:
                    print(f"TTL {ttl:3d}: ⏱️  Time Exceeded from {reply.src} (hop {ttl})")
                else:
                    print(f"TTL {ttl:3d}: ⚠️  ICMP Type {icmp_type} from {reply.src}")
        else:
            print(f"TTL {ttl:3d}: ❌ No reply")

def analyze_ping_sizes(destination):
    """Test different ping payload sizes"""
    print_section("Testing Different Payload Sizes")
    
    print(f"\nPinging {destination} with different payload sizes:")
    print("(Large sizes may cause fragmentation)\n")
    
    sizes = [0, 56, 500, 1472, 2000]
    
    for size in sizes:
        packet = IP(dst=destination)/ICMP()/"X" * size
        total_size = len(packet)
        
        reply = sr1(packet, timeout=2, verbose=0)
        
        if reply:
            print(f"Size {size:4d} bytes (total {total_size:4d}): ✅ Success")
            if total_size > 1500:
                print(f"         ⚠️  Larger than typical MTU, likely fragmented")
        else:
            print(f"Size {size:4d} bytes (total {total_size:4d}): ❌ Failed")

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 3: ICMP PING DEMO")
    print("="*60)
    print("\nThis demo implements ping using ICMP.")
    print("See how network diagnostics work under the hood!")
    
    # Part 1: Explain ICMP
    explain_icmp()
    
    # Part 2: Create ICMP packet
    create_icmp_packet()
    
    # Part 3: Show ICMP types
    demonstrate_icmp_types()
    
    # Part 4-7: Live demos (require sudo)
    try:
        # Test single ping
        send_single_ping("8.8.8.8")
        
        # Full ping implementation
        ping_host("8.8.8.8", count=4)
        
        # Test different TTLs
        test_different_ttls("8.8.8.8")
        
        # Test different sizes
        analyze_ping_sizes("8.8.8.8")
        
    except PermissionError:
        print_section("Live ICMP Demo")
        print("\n⚠️  Sending ICMP requires root privileges")
        print("Run with: sudo python3 02_icmp_ping.py")
    
    print_section("Experiments to Try")
    print("""
1. Compare with system ping:
   ping -c 4 8.8.8.8
   (Compare results with our implementation)

2. Capture ICMP traffic:
   sudo tcpdump -i any icmp -vv

3. Ping unreachable host:
   - Try pinging 192.0.2.1 (reserved, unreachable)
   - Observe ICMP Destination Unreachable

4. Test MTU discovery:
   ping -M do -s 1472 8.8.8.8  (should work)
   ping -M do -s 1473 8.8.8.8  (may fail with DF flag)

5. Monitor ping in Wireshark:
   - Filter: icmp
   - Observe request/reply pairs
   - Check sequence numbers

6. Implement ping statistics:
   - Modify script to calculate jitter
   - Add packet loss percentage
   - Graph RTT over time
    """)
    
    print("\n✅ Demo complete! Continue to 03_traceroute.py\n")

if __name__ == "__main__":
    main()
