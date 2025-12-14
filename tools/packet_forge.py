#!/usr/bin/env python3
"""
Packet Forge Tool
=================

A tool for crafting custom network packets.
You'll learn:
- How to create packets from scratch
- Customize all header fields
- Test network behavior

Run with: sudo python3 packet_forge.py

EXPERIMENT IDEAS:
1. Craft packets with unusual values
2. Test firewall rules
3. Understand packet structure deeply
"""

from scapy.all import (Ether, IP, TCP, UDP, ICMP, ARP, Raw, 
                       send, sendp, sr1, fragment)
import argparse
import sys

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def forge_ethernet():
    """Forge Ethernet frame"""
    print_section("Forging Ethernet Frame")
    
    src = input("Source MAC (or Enter for auto): ").strip() or None
    dst = input("Destination MAC (or Enter for broadcast): ").strip() or "ff:ff:ff:ff:ff:ff"
    
    frame = Ether(src=src, dst=dst)
    print("\nCreated Ethernet frame:")
    frame.show()
    
    return frame

def forge_ip():
    """Forge IP packet"""
    print_section("Forging IP Packet")
    
    dst = input("Destination IP: ").strip()
    src = input("Source IP (or Enter for auto): ").strip() or None
    ttl = input("TTL (or Enter for 64): ").strip() or "64"
    
    packet = IP(dst=dst, src=src, ttl=int(ttl))
    print("\nCreated IP packet:")
    packet.show()
    
    return packet

def forge_tcp():
    """Forge TCP packet"""
    print_section("Forging TCP Packet")
    
    dport = int(input("Destination port: ").strip())
    sport = input("Source port (or Enter for random): ").strip()
    sport = int(sport) if sport else None
    
    flags = input("Flags (S/A/F/R/P or combination like SA): ").strip() or "S"
    seq = input("Sequence number (or Enter for random): ").strip()
    seq = int(seq) if seq else None
    
    packet = TCP(dport=dport, sport=sport, flags=flags, seq=seq)
    print("\nCreated TCP packet:")
    packet.show()
    
    return packet

def forge_udp():
    """Forge UDP packet"""
    print_section("Forging UDP Packet")
    
    dport = int(input("Destination port: ").strip())
    sport = input("Source port (or Enter for random): ").strip()
    sport = int(sport) if sport else None
    
    packet = UDP(dport=dport, sport=sport)
    print("\nCreated UDP packet:")
    packet.show()
    
    return packet

def forge_icmp():
    """Forge ICMP packet"""
    print_section("Forging ICMP Packet")
    
    print("\nCommon ICMP types:")
    print("  0 - Echo Reply (ping response)")
    print("  3 - Destination Unreachable")
    print("  8 - Echo Request (ping)")
    print("  11 - Time Exceeded")
    
    icmp_type = int(input("\nICMP type: ").strip() or "8")
    icmp_code = int(input("ICMP code (usually 0): ").strip() or "0")
    
    packet = ICMP(type=icmp_type, code=icmp_code)
    print("\nCreated ICMP packet:")
    packet.show()
    
    return packet

def forge_arp():
    """Forge ARP packet"""
    print_section("Forging ARP Packet")
    
    print("\nARP operations:")
    print("  1 - Request (who-has)")
    print("  2 - Reply (is-at)")
    
    op = int(input("\nOperation: ").strip() or "1")
    pdst = input("Target IP: ").strip()
    psrc = input("Source IP (or Enter for auto): ").strip() or None
    
    packet = ARP(op=op, pdst=pdst, psrc=psrc)
    print("\nCreated ARP packet:")
    packet.show()
    
    return packet

def interactive_forge():
    """Interactive packet forging"""
    print_section("Interactive Packet Forge")
    
    print("\nSelect protocol to forge:")
    print("  1. Ethernet")
    print("  2. IP")
    print("  3. TCP")
    print("  4. UDP")
    print("  5. ICMP")
    print("  6. ARP")
    print("  7. IP/TCP (complete)")
    print("  8. IP/UDP (complete)")
    print("  9. IP/ICMP (complete)")
    
    choice = input("\nChoice: ").strip()
    
    packet = None
    
    if choice == "1":
        packet = forge_ethernet()
    elif choice == "2":
        packet = forge_ip()
    elif choice == "3":
        packet = forge_tcp()
    elif choice == "4":
        packet = forge_udp()
    elif choice == "5":
        packet = forge_icmp()
    elif choice == "6":
        packet = forge_arp()
    elif choice == "7":
        packet = forge_ip() / forge_tcp()
    elif choice == "8":
        packet = forge_ip() / forge_udp()
    elif choice == "9":
        packet = forge_ip() / forge_icmp()
    else:
        print("Invalid choice")
        return None
    
    # Add payload
    payload = input("\nAdd payload? (Enter text or leave blank): ").strip()
    if payload:
        packet = packet / Raw(load=payload)
    
    print_section("Complete Packet")
    packet.show()
    
    # Send option
    send_it = input("\nSend this packet? (yes/no): ").strip().lower()
    if send_it == "yes":
        try:
            if packet.haslayer(Ether):
                sendp(packet, verbose=1)
            else:
                send(packet, verbose=1)
            print("✓ Packet sent!")
        except PermissionError:
            print("✗ Need root privileges to send packets")
    
    return packet

def quick_examples():
    """Show quick packet examples"""
    print_section("Quick Examples")
    
    print("\n1. SYN Packet (Port Scan):")
    syn = IP(dst="192.168.1.1")/TCP(dport=80, flags="S")
    syn.show()
    
    print("\n2. ICMP Ping:")
    ping = IP(dst="8.8.8.8")/ICMP()
    ping.show()
    
    print("\n3. UDP DNS Query:")
    dns_packet = IP(dst="8.8.8.8")/UDP(dport=53)
    dns_packet.show()
    
    print("\n4. ARP Request:")
    arp = ARP(pdst="192.168.1.1")
    arp.show()
    
    print("\n5. Custom TTL Packet:")
    ttl_packet = IP(dst="8.8.8.8", ttl=1)/ICMP()
    ttl_packet.show()
    
    print("\n6. Fragmented Packet:")
    large = IP(dst="8.8.8.8")/ICMP()/Raw(b"X"*2000)
    frags = fragment(large, fragsize=500)
    print(f"   Original size: {len(large)} bytes")
    print(f"   Fragments: {len(frags)}")
    
    print("\n7. TCP with Payload:")
    data = IP(dst="192.168.1.1")/TCP(dport=80, flags="PA")/"GET / HTTP/1.1\r\n\r\n"
    data.show()

def preset_packets():
    """Preset packet templates"""
    print_section("Preset Packet Templates")
    
    templates = {
        "1": ("SYN Scan", lambda: IP(dst="TARGET")/TCP(dport=80, flags="S")),
        "2": ("Ping", lambda: IP(dst="TARGET")/ICMP()),
        "3": ("Traceroute", lambda: IP(dst="TARGET", ttl=1)/ICMP()),
        "4": ("ARP Request", lambda: ARP(pdst="TARGET")),
        "5": ("UDP Probe", lambda: IP(dst="TARGET")/UDP(dport=53)),
        "6": ("FIN Scan", lambda: IP(dst="TARGET")/TCP(dport=80, flags="F")),
        "7": ("NULL Scan", lambda: IP(dst="TARGET")/TCP(dport=80, flags="")),
        "8": ("XMAS Scan", lambda: IP(dst="TARGET")/TCP(dport=80, flags="FPU")),
    }
    
    print("\nAvailable templates:")
    for key, (name, _) in templates.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect template: ").strip()
    
    if choice in templates:
        name, func = templates[choice]
        target = input(f"\nEnter target (IP/hostname): ").strip()
        
        packet = func()
        # Replace TARGET with actual target
        if packet.haslayer(IP):
            packet[IP].dst = target
        elif packet.haslayer(ARP):
            packet[ARP].pdst = target
        
        print(f"\n{name} packet:")
        packet.show()
        
        send_it = input("\nSend? (yes/no): ").strip().lower()
        if send_it == "yes":
            try:
                if packet.haslayer(Ether):
                    sendp(packet, verbose=1)
                else:
                    send(packet, verbose=1)
                print("✓ Sent!")
            except PermissionError:
                print("✗ Need root privileges")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Packet Forge - Craft custom network packets",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Interactive packet forging')
    parser.add_argument('--examples', '-e', action='store_true',
                       help='Show packet examples')
    parser.add_argument('--presets', '-p', action='store_true',
                       help='Use preset templates')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("  PACKET FORGE TOOL")
    print("="*60)
    print("\n⚠️  Use responsibly! Only on networks you own.")
    
    if args.interactive:
        interactive_forge()
    elif args.examples:
        quick_examples()
    elif args.presets:
        preset_packets()
    else:
        print("\nUsage:")
        print("  --interactive, -i    Interactive packet forging")
        print("  --examples, -e       Show packet examples")
        print("  --presets, -p        Use preset templates")
        print("\nExample: sudo python3 packet_forge.py -i")
        
        print_section("What You Can Do")
        print("""
With Packet Forge you can:
✓ Craft packets with custom headers
✓ Test network devices and firewalls
✓ Learn packet structure hands-on
✓ Experiment with protocol behavior
✓ Debug network issues
✓ Educational security testing

Common uses:
- Port scanning (TCP SYN)
- Traceroute (TTL manipulation)
- Ping variations (ICMP)
- Protocol testing
- Firewall rule testing
        """)
        
        print_section("Quick Start")
        print("""
1. Interactive mode:
   sudo python3 packet_forge.py -i
   
2. See examples:
   python3 packet_forge.py -e
   
3. Use presets:
   sudo python3 packet_forge.py -p

Remember: Requires root/sudo to send packets!
        """)

if __name__ == "__main__":
    main()
