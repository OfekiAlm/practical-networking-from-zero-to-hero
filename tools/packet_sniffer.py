#!/usr/bin/env python3
"""
Packet Sniffer Tool
===================

A customizable packet sniffer for learning and network analysis.
You'll learn:
- How to capture live packets
- Filtering traffic
- Analyzing protocols in real-time

Run with: sudo python3 packet_sniffer.py

EXPERIMENT IDEAS:
1. Filter by protocol (TCP, UDP, ICMP)
2. Filter by port or IP
3. Capture to file for later analysis
"""

from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, Raw
import argparse
import sys

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def packet_callback(packet):
    """Process each captured packet"""
    timestamp = packet.time
    
    # Layer 2 - Ethernet
    if packet.haslayer(ARP):
        arp = packet[ARP]
        print(f"\n[ARP] {arp.psrc} → {arp.pdst}")
        if arp.op == 1:
            print(f"  Who has {arp.pdst}? Tell {arp.psrc}")
        elif arp.op == 2:
            print(f"  {arp.psrc} is at {arp.hwsrc}")
    
    # Layer 3 - IP
    if packet.haslayer(IP):
        ip = packet[IP]
        protocol = "Unknown"
        
        # Layer 4 - TCP
        if packet.haslayer(TCP):
            tcp = packet[TCP]
            flags = tcp.sprintf("%TCP.flags%")
            protocol = "TCP"
            print(f"\n[TCP] {ip.src}:{tcp.sport} → {ip.dst}:{tcp.dport}")
            print(f"  Flags: {flags}, Seq: {tcp.seq}, Ack: {tcp.ack}")
            print(f"  Window: {tcp.window}, Len: {len(tcp.payload)}")
            
            # Application layer hints
            if tcp.dport == 80 or tcp.sport == 80:
                print(f"  [HTTP traffic]")
            elif tcp.dport == 443 or tcp.sport == 443:
                print(f"  [HTTPS traffic]")
            elif tcp.dport == 22 or tcp.sport == 22:
                print(f"  [SSH traffic]")
            
            # Show payload if present
            if packet.haslayer(Raw):
                payload = packet[Raw].load[:50]  # First 50 bytes
                try:
                    print(f"  Payload: {payload.decode('utf-8', errors='ignore')}")
                except:
                    print(f"  Payload: {payload.hex()[:100]}")
        
        # Layer 4 - UDP
        elif packet.haslayer(UDP):
            udp = packet[UDP]
            protocol = "UDP"
            print(f"\n[UDP] {ip.src}:{udp.sport} → {ip.dst}:{udp.dport}")
            print(f"  Len: {udp.len}")
            
            # Application layer hints
            if udp.dport == 53 or udp.sport == 53:
                print(f"  [DNS traffic]")
            elif udp.dport == 67 or udp.dport == 68:
                print(f"  [DHCP traffic]")
            elif udp.dport == 123:
                print(f"  [NTP traffic]")
        
        # Layer 3 - ICMP
        elif packet.haslayer(ICMP):
            icmp = packet[ICMP]
            protocol = "ICMP"
            icmp_types = {0: "Echo Reply", 3: "Dest Unreachable", 
                         8: "Echo Request", 11: "Time Exceeded"}
            icmp_type_name = icmp_types.get(icmp.type, f"Type {icmp.type}")
            print(f"\n[ICMP] {ip.src} → {ip.dst}")
            print(f"  Type: {icmp.type} ({icmp_type_name}), Code: {icmp.code}")

def detailed_packet_callback(packet):
    """Detailed packet analysis"""
    print(f"\n{'='*60}")
    print(packet.summary())
    print("-" * 60)
    packet.show()

def simple_packet_callback(packet):
    """Simple one-line summary"""
    print(packet.summary())

def start_sniffing(interface=None, count=0, filter_str=None, mode="normal", output_file=None):
    """Start packet capture"""
    
    # Choose callback based on mode
    if mode == "detailed":
        callback = detailed_packet_callback
    elif mode == "simple":
        callback = simple_packet_callback
    else:
        callback = packet_callback
    
    print_section("Packet Sniffer Started")
    print(f"Interface: {interface or 'default'}")
    print(f"Count: {count if count > 0 else 'unlimited'}")
    print(f"Filter: {filter_str or 'none (all packets)'}")
    print(f"Mode: {mode}")
    if output_file:
        print(f"Output file: {output_file}")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        packets = sniff(
            iface=interface,
            count=count,
            filter=filter_str,
            prn=callback,
            store=True if output_file else False
        )
        
        if output_file:
            from scapy.all import wrpcap
            wrpcap(output_file, packets)
            print(f"\n✓ Saved {len(packets)} packets to {output_file}")
            
    except KeyboardInterrupt:
        print("\n\nCapture stopped by user")
    except PermissionError:
        print("\n⚠️  Packet capture requires root privileges")
        print("Run with: sudo python3 packet_sniffer.py")

def show_examples():
    """Show usage examples"""
    print_section("Usage Examples")
    print("""
1. Capture all traffic (default):
   sudo python3 packet_sniffer.py

2. Capture only TCP traffic:
   sudo python3 packet_sniffer.py -f "tcp"

3. Capture HTTP traffic:
   sudo python3 packet_sniffer.py -f "tcp port 80"

4. Capture from specific host:
   sudo python3 packet_sniffer.py -f "host 192.168.1.1"

5. Capture 100 packets:
   sudo python3 packet_sniffer.py -c 100

6. Detailed mode:
   sudo python3 packet_sniffer.py -m detailed

7. Save to file:
   sudo python3 packet_sniffer.py -o capture.pcap

8. Capture ICMP (ping):
   sudo python3 packet_sniffer.py -f "icmp"

9. Capture DNS:
   sudo python3 packet_sniffer.py -f "udp port 53"

10. Capture specific interface:
    sudo python3 packet_sniffer.py -i eth0

BPF Filter Syntax:
- Protocol: tcp, udp, icmp, arp
- Port: port 80, src port 80, dst port 443
- Host: host 8.8.8.8, src host 192.168.1.1
- Network: net 192.168.1.0/24
- Combine: tcp and port 80, tcp or udp
    """)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Packet Sniffer - Capture and analyze network traffic",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-i', '--interface', 
                       help='Network interface to capture on')
    parser.add_argument('-c', '--count', type=int, default=0,
                       help='Number of packets to capture (0 = unlimited)')
    parser.add_argument('-f', '--filter',
                       help='BPF filter (e.g., "tcp port 80")')
    parser.add_argument('-m', '--mode', 
                       choices=['normal', 'detailed', 'simple'],
                       default='normal',
                       help='Display mode')
    parser.add_argument('-o', '--output',
                       help='Save packets to pcap file')
    parser.add_argument('--examples', action='store_true',
                       help='Show usage examples')
    
    args = parser.parse_args()
    
    if args.examples:
        show_examples()
        return
    
    if len(sys.argv) == 1:
        print("\n" + "="*60)
        print("  PACKET SNIFFER TOOL")
        print("="*60)
        print("\nCapture and analyze network packets in real-time.\n")
        parser.print_help()
        print("\nRun with --examples to see usage examples")
        return
    
    start_sniffing(
        interface=args.interface,
        count=args.count,
        filter_str=args.filter,
        mode=args.mode,
        output_file=args.output
    )

if __name__ == "__main__":
    main()
