#!/usr/bin/env python3
"""
Layer 3 Demo: Traceroute Implementation
========================================

This script implements traceroute using TTL manipulation.
You'll learn:
- How traceroute discovers network path
- TTL-based hop discovery
- ICMP Time Exceeded messages

Run with: sudo python3 03_traceroute.py

EXPERIMENT IDEAS:
1. Trace route to different destinations
2. Compare with system traceroute
3. Use different protocols (ICMP, UDP, TCP)
"""

from scapy.all import IP, ICMP, UDP, sr1
import sys

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_traceroute():
    """Explain how traceroute works"""
    print_section("How Traceroute Works")
    print("""
Traceroute discovers the path packets take to a destination.

Principle:
1. Send packet with TTL=1
   → First router decrements TTL to 0
   → Router sends ICMP "Time Exceeded" back
   → Now we know first hop!

2. Send packet with TTL=2
   → First router decrements (TTL=1)
   → Second router decrements to 0
   → Second router sends "Time Exceeded"
   → Now we know second hop!

3. Continue increasing TTL until reaching destination

When destination reached:
- ICMP traceroute: Gets Echo Reply (type 0)
- UDP traceroute: Gets Port Unreachable (type 3)
- TCP traceroute: Gets SYN-ACK or RST

Result: We've mapped the entire path!
    """)

def traceroute(destination, max_hops=30, timeout=2, protocol="icmp"):
    """Perform traceroute to destination"""
    print_section(f"Tracerouting to {destination}")
    print(f"Using {protocol.upper()} packets, max {max_hops} hops\n")
    
    for ttl in range(1, max_hops + 1):
        # Create packet based on protocol
        if protocol.lower() == "icmp":
            packet = IP(dst=destination, ttl=ttl)/ICMP()
        elif protocol.lower() == "udp":
            packet = IP(dst=destination, ttl=ttl)/UDP(dport=33434+ttl)
        else:
            print(f"Unknown protocol: {protocol}")
            return
        
        # Send packet and wait for reply
        reply = sr1(packet, verbose=0, timeout=timeout)
        
        if reply is None:
            print(f"{ttl:2d}  *  *  * (timeout)")
        elif reply.haslayer(ICMP):
            icmp_type = reply[ICMP].type
            icmp_code = reply[ICMP].code
            
            # Time Exceeded (TTL=0 at this hop)
            if icmp_type == 11:
                print(f"{ttl:2d}  {reply.src:15s}  (intermediate hop)")
            
            # Destination Unreachable (UDP hit closed port = we're there!)
            elif icmp_type == 3 and protocol.lower() == "udp":
                print(f"{ttl:2d}  {reply.src:15s}  (destination reached)")
                break
            
            # Echo Reply (ICMP reached destination)
            elif icmp_type == 0:
                print(f"{ttl:2d}  {reply.src:15s}  (destination reached)")
                break
            
            # Other ICMP message
            else:
                print(f"{ttl:2d}  {reply.src:15s}  (ICMP type={icmp_type} code={icmp_code})")
        else:
            print(f"{ttl:2d}  {reply.src:15s}  (unexpected response)")
        
        # Check if we reached destination
        if reply and reply.src == destination:
            break
    else:
        print(f"\nMax hops ({max_hops}) reached without reaching destination")

def traceroute_with_timing(destination, max_hops=30):
    """Traceroute with RTT timing"""
    print_section(f"Traceroute with Timing: {destination}")
    
    import time
    
    print(f"{'Hop':<4} {'IP Address':<20} {'RTT (ms)':<12} {'Hostname'}")
    print("-" * 60)
    
    for ttl in range(1, max_hops + 1):
        packet = IP(dst=destination, ttl=ttl)/ICMP()
        
        # Measure RTT
        start = time.time()
        reply = sr1(packet, verbose=0, timeout=2)
        rtt = (time.time() - start) * 1000
        
        if reply is None:
            print(f"{ttl:<4} {'*':<20} {'timeout':<12}")
        else:
            ip = reply.src
            
            # Try to get hostname (may be slow)
            try:
                import socket
                hostname = socket.gethostbyaddr(ip)[0][:30]
            except:
                hostname = "-"
            
            print(f"{ttl:<4} {ip:<20} {rtt:>8.2f} ms  {hostname}")
            
            # Check if reached destination
            if reply.haslayer(ICMP):
                if reply[ICMP].type == 0 or reply.src == destination:
                    print(f"\n✅ Reached {destination} in {ttl} hops")
                    break

def demonstrate_ttl_behavior():
    """Show TTL behavior in detail"""
    print_section("TTL Behavior Demonstration")
    
    destination = "8.8.8.8"
    
    print(f"\nSending packets to {destination} with different TTL values:")
    print(f"{'TTL':<5} {'Result':<50} {'Reply From'}")
    print("-" * 70)
    
    for ttl in [1, 2, 3, 64]:
        packet = IP(dst=destination, ttl=ttl)/ICMP()
        reply = sr1(packet, verbose=0, timeout=2)
        
        if reply is None:
            print(f"{ttl:<5} {'Timeout - no response':<50}")
        elif reply.haslayer(ICMP):
            icmp_type = reply[ICMP].type
            
            if icmp_type == 11:
                result = f"Time Exceeded (TTL expired at hop {ttl})"
                print(f"{ttl:<5} {result:<50} {reply.src}")
            elif icmp_type == 0:
                result = "Echo Reply (reached destination)"
                print(f"{ttl:<5} {result:<50} {reply.src}")
            else:
                result = f"ICMP Type {icmp_type}"
                print(f"{ttl:<5} {result:<50} {reply.src}")

def compare_protocols():
    """Compare different traceroute protocols"""
    print_section("Comparing Traceroute Protocols")
    
    print("""
Different traceroute implementations use different protocols:

1. ICMP (Type 8 - Echo Request):
   - Original Unix traceroute
   - Easy to implement
   - Some firewalls block ICMP
   - Our implementation uses this

2. UDP (High ports 33434+):
   - Classic Unix traceroute
   - Uses "unlikely" destination ports
   - Expects "Port Unreachable" from destination
   - Can bypass some ICMP filters

3. TCP (Port 80 or 443):
   - Modern traceroute option
   - Uses TCP SYN packets
   - Better at bypassing firewalls
   - Can reach through strict firewalls

Each has advantages depending on network filtering!
    """)

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 3: TRACEROUTE DEMO")
    print("="*60)
    print("\nThis demo implements traceroute.")
    print("Discover the path your packets take!")
    
    # Part 1: Explain
    explain_traceroute()
    
    # Part 2: TTL behavior
    try:
        demonstrate_ttl_behavior()
    except PermissionError:
        print("\n⚠️  Requires root privileges")
    
    # Part 3: Protocol comparison
    compare_protocols()
    
    # Part 4: Actual traceroute
    if len(sys.argv) > 1:
        destination = sys.argv[1]
    else:
        destination = "8.8.8.8"
    
    try:
        print("\n" + "="*60)
        print("Performing actual traceroute...")
        traceroute(destination, max_hops=15)
        
        print("\n" + "="*60)
        print("With timing information...")
        traceroute_with_timing(destination, max_hops=15)
        
    except PermissionError:
        print_section("Live Traceroute")
        print("\n⚠️  Traceroute requires root privileges")
        print("Run with: sudo python3 03_traceroute.py [destination]")
        print("Example: sudo python3 03_traceroute.py 8.8.8.8")
    
    print_section("Experiments to Try")
    print("""
1. Compare with system traceroute:
   traceroute 8.8.8.8
   sudo python3 03_traceroute.py 8.8.8.8

2. Trace different destinations:
   - Nearby: Your gateway
   - Medium: google.com
   - Far: internationa sites

3. Watch in Wireshark:
   - Filter: icmp || (ip.ttl <= 5)
   - See TTL values and Time Exceeded messages

4. Try UDP version:
   traceroute -I 8.8.8.8  (ICMP)
   traceroute -U 8.8.8.8  (UDP)

5. Analyze routing:
   - Run multiple times
   - Do routes change?
   - Identify your ISP's routers

6. Geographic analysis:
   - Use whois to identify hop locations
   - Map the physical path
    """)
    
    print("\n✅ Demo complete! Continue to 04_ip_fragmentation.py\n")

if __name__ == "__main__":
    main()
