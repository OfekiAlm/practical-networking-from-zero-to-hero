#!/usr/bin/env python3
"""
Layer 3 Demo: IP Packet Anatomy
================================

This script demonstrates the structure of IP packets.
You'll learn:
- IP header fields and their purposes
- IPv4 packet structure
- How to craft and inspect IP packets

Run with: sudo python3 01_ip_packet_anatomy.py

EXPERIMENT IDEAS:
1. Change TTL values and observe effects
2. Modify TOS/DSCP for QoS
3. Create packets with different flags
"""

from scapy.all import IP, ICMP, Raw, fragment, send, sr1
import struct

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_ip_basics():
    """Explain IP fundamentals"""
    print_section("IP (Internet Protocol) Basics")
    print("""
IP provides:
✓ Addressing: Unique identifier for each host (e.g., 192.168.1.1)
✓ Routing: Moving packets across networks
✓ Best-effort delivery: No guarantees (unlike TCP)

IPv4 Packet Header: 20 bytes minimum (without options)

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |Type of Service|          Total Length         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|      Fragment Offset    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Time to Live |    Protocol   |         Header Checksum       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source Address                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination Address                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    """)

def create_basic_ip_packet():
    """Create and display a basic IP packet"""
    print_section("Creating a Basic IP Packet")
    
    # Create IP packet
    packet = IP(dst="8.8.8.8", src="192.168.1.100")
    
    print("\nIP Packet:")
    print(packet.show(dump=True))
    
    print("\n\nField-by-Field Breakdown:")
    print(f"Version: {packet.version} (4 = IPv4, 6 = IPv6)")
    print(f"IHL (Header Length): {packet.ihl} (in 32-bit words, {packet.ihl * 4} bytes)")
    print(f"TOS (Type of Service): {packet.tos:#04x}")
    print(f"Total Length: {packet.len} bytes")
    print(f"Identification: {packet.id} (for fragment reassembly)")
    print(f"Flags: {packet.flags}")
    print(f"  - DF (Don't Fragment): {bool(packet.flags & 2)}")
    print(f"  - MF (More Fragments): {bool(packet.flags & 1)}")
    print(f"Fragment Offset: {packet.frag}")
    print(f"TTL (Time To Live): {packet.ttl} hops")
    print(f"Protocol: {packet.proto} (1=ICMP, 6=TCP, 17=UDP)")
    print(f"Checksum: {packet.chksum:#06x}")
    print(f"Source IP: {packet.src}")
    print(f"Destination IP: {packet.dst}")
    
    return packet

def demonstrate_ttl():
    """Show how TTL works"""
    print_section("TTL (Time To Live)")
    
    print("""
TTL prevents packets from looping forever:
- Each router decrements TTL by 1
- When TTL reaches 0, packet is dropped
- Router sends ICMP "Time Exceeded" back to source

Common TTL values:
- Linux: 64
- Windows: 128
- Cisco: 255
    """)
    
    print("\nPackets with different TTLs:")
    for ttl in [1, 10, 64, 255]:
        packet = IP(dst="8.8.8.8", ttl=ttl)
        print(f"\nTTL={ttl:3d}: {packet.summary()}")
    
    print("\n💡 Traceroute uses TTL to discover route!")
    print("   Sends packets with TTL=1, 2, 3... to find each hop")

def demonstrate_tos_dscp():
    """Show TOS/DSCP field for QoS"""
    print_section("TOS/DSCP (Quality of Service)")
    
    print("""
TOS (Type of Service) / DSCP (Differentiated Services):
- Used for Quality of Service (QoS)
- Routers can prioritize based on this field
- 8 bits total (6 bits DSCP + 2 bits ECN)

Common DSCP values:
- 0x00 (BE): Best Effort (default)
- 0x2E (EF): Expedited Forwarding (VoIP)
- 0x0A (AF11): Assured Forwarding (important data)
    """)
    
    print("\nPackets with different TOS/DSCP:")
    configs = [
        (0x00, "Best Effort"),
        (0x2E, "Expedited (VoIP)"),
        (0x0A, "Assured Forwarding"),
    ]
    
    for tos, desc in configs:
        packet = IP(dst="8.8.8.8", tos=tos)
        print(f"\nTOS={tos:#04x} ({desc}):")
        print(f"  {packet.summary()}")

def demonstrate_fragmentation():
    """Show IP fragmentation"""
    print_section("IP Fragmentation")
    
    print("""
IP Fragmentation occurs when:
- Packet is larger than MTU (Maximum Transmission Unit)
- MTU is typically 1500 bytes for Ethernet
- Router breaks packet into smaller fragments
- Destination reassembles using Identification field

Flags:
- DF (Don't Fragment): Disallow fragmentation (send ICMP if too big)
- MF (More Fragments): More fragments follow this one
    """)
    
    # Create a large packet
    large_packet = IP(dst="8.8.8.8")/ICMP()/Raw(b"X"*2000)
    print(f"\nOriginal packet size: {len(large_packet)} bytes")
    print(f"Payload size: 2000 bytes")
    
    # Fragment it
    fragments = fragment(large_packet, fragsize=500)
    
    print(f"\nFragmented into {len(fragments)} pieces:")
    for i, frag in enumerate(fragments):
        print(f"\nFragment {i+1}:")
        print(f"  ID: {frag[IP].id}")
        print(f"  MF flag: {bool(frag[IP].flags & 1)}")
        print(f"  Fragment offset: {frag[IP].frag}")
        print(f"  Size: {len(frag)} bytes")

def demonstrate_protocols():
    """Show different protocol numbers"""
    print_section("Protocol Field")
    
    print("""
Protocol field identifies the next-layer protocol:
    """)
    
    protocols = [
        (IP(dst="8.8.8.8")/ICMP(), "ICMP (1)"),
        (IP(dst="8.8.8.8", proto=6), "TCP (6)"),
        (IP(dst="8.8.8.8", proto=17), "UDP (17)"),
        (IP(dst="8.8.8.8", proto=41), "IPv6 encapsulation (41)"),
        (IP(dst="8.8.8.8", proto=50), "ESP (IPsec, 50)"),
    ]
    
    for packet, desc in protocols:
        print(f"\n{desc}:")
        print(f"  Protocol number: {packet[IP].proto}")
        print(f"  Summary: {packet.summary()}")

def compare_ipv4_ipv6():
    """Compare IPv4 and IPv6"""
    print_section("IPv4 vs IPv6")
    
    print("""
IPv4:
- 32-bit addresses (4.3 billion)
- Dotted decimal: 192.168.1.1
- Header: 20-60 bytes (variable with options)
- NAT commonly used
- Fragmentation by routers

IPv6:
- 128-bit addresses (340 undecillion)
- Hex notation: 2001:db8::1
- Header: 40 bytes (fixed, simpler)
- No NAT needed (huge address space)
- No router fragmentation
- Built-in IPsec support
    """)

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 3: IP PACKET ANATOMY")
    print("="*60)
    print("\nThis demo explores IP packet structure.")
    print("See what's inside every IP packet!")
    
    # Part 1: Explain basics
    explain_ip_basics()
    
    # Part 2: Create and inspect packet
    create_basic_ip_packet()
    
    # Part 3: TTL demonstration
    demonstrate_ttl()
    
    # Part 4: TOS/DSCP
    demonstrate_tos_dscp()
    
    # Part 5: Fragmentation
    demonstrate_fragmentation()
    
    # Part 6: Protocol field
    demonstrate_protocols()
    
    # Part 7: IPv4 vs IPv6
    compare_ipv4_ipv6()
    
    print_section("Experiments to Try")
    print("""
1. Capture and inspect real IP packets:
   sudo tcpdump -i eth0 -vv -n ip

2. See IP headers in Wireshark:
   - Capture traffic
   - Expand "Internet Protocol Version 4" section
   - Observe field values

3. Test fragmentation:
   ping -M dont -s 2000 8.8.8.8
   (May fail if MTU < 2000)

4. Check your system's default TTL:
   sysctl net.ipv4.ip_default_ttl

5. Monitor TTL in responses:
   ping 8.8.8.8
   (Look at ttl= in output)

6. Create custom packets:
   - Modify script to send packets
   - Try different TTL, TOS values
   - Observe with tcpdump
    """)
    
    print("\n✅ Demo complete! Continue to 02_icmp_ping.py\n")

if __name__ == "__main__":
    main()
