#!/usr/bin/env python3
"""
Layer 2 Demo: ARP (Address Resolution Protocol)
================================================

This script demonstrates how ARP resolves IP addresses to MAC addresses.
You'll learn:
- How ARP requests/replies work
- ARP cache behavior
- Building custom ARP packets

Run with: sudo python3 02_arp_demo.py

EXPERIMENT IDEAS:
1. Change the target IP to discover different hosts
2. Monitor your system's ARP cache before/after
3. Send gratuitous ARP packets
"""

from scapy.all import ARP, Ether, srp, send, sniff, conf
import netifaces
import subprocess
import time

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def get_default_interface():
    """Get the default network interface"""
    try:
        gateways = netifaces.gateways()
        default_iface = gateways['default'][netifaces.AF_INET][1]
        return default_iface
    except:
        return conf.iface

def display_arp_theory():
    """Explain ARP concepts"""
    print_section("What is ARP?")
    print("""
ARP (Address Resolution Protocol) solves this problem:
- You know an IP address (Layer 3): 192.168.1.1
- You need the MAC address (Layer 2): ??:??:??:??:??:??
- ARP asks: "Who has 192.168.1.1? Tell me your MAC!"

ARP Packet Flow:
1. Host A broadcasts: "Who has IP 192.168.1.1?" (ARP Request)
2. Host with that IP replies: "I have 192.168.1.1, my MAC is XX:XX:XX..." (ARP Reply)
3. Host A caches this IP→MAC mapping

Why it matters:
- Required for ANY IP communication on a local network
- Ethernet frames need destination MAC addresses
- Without ARP, IP packets can't be delivered locally
    """)

def show_system_arp_cache():
    """Display the system's ARP cache"""
    print_section("System ARP Cache")
    print("\nYour system maintains an ARP cache (IP → MAC mappings):\n")
    
    try:
        result = subprocess.run(['arp', '-n'], capture_output=True, text=True)
        print(result.stdout)
        print("\n💡 These mappings are learned via ARP and cached temporarily")
    except:
        print("Could not read ARP cache. Try: arp -n")

def build_arp_request(target_ip):
    """Build and display an ARP request packet"""
    print_section(f"Building ARP Request for {target_ip}")
    
    # Create ARP request
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    print("\nARP Request Packet Structure:")
    print(packet.show(dump=True))
    
    print("\n\nKey Fields:")
    print(f"Ethernet Destination: {ether.dst} (broadcast)")
    print(f"Ethernet Source: {ether.src}")
    print(f"ARP Operation: {arp.op} (1 = request, 2 = reply)")
    print(f"Sender MAC: {arp.hwsrc}")
    print(f"Sender IP: {arp.psrc}")
    print(f"Target MAC: {arp.hwdst} (00:00:00:00:00:00 = unknown)")
    print(f"Target IP: {arp.pdst}")
    
    return packet

def send_arp_request(target_ip):
    """Send an ARP request and capture the reply"""
    print_section(f"Sending ARP Request to {target_ip}")
    
    iface = get_default_interface()
    print(f"\nInterface: {iface}")
    print(f"Sending ARP request...")
    
    # Create and send ARP request
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send and wait for reply
    result = srp(packet, timeout=2, iface=iface, verbose=0)[0]
    
    if result:
        for sent, received in result:
            print("\n✅ ARP Reply Received!")
            print(f"\nTarget IP: {received.psrc}")
            print(f"Target MAC: {received.hwsrc}")
            print(f"\nFull reply packet:")
            print(received.show(dump=True))
            
            print("\n💡 Success! We now know the MAC address for this IP")
            return received.hwsrc
    else:
        print("\n❌ No reply received")
        print("Possible reasons:")
        print("- Host is down or unreachable")
        print("- Firewall blocking ARP")
        print("- IP not in local subnet")
        return None

def demonstrate_arp_types():
    """Show different types of ARP packets"""
    print_section("Types of ARP Packets")
    
    print("\n1. ARP REQUEST (op=1):")
    req = ARP(op=1, pdst="192.168.1.1")
    print(req.show(dump=True))
    
    print("\n2. ARP REPLY (op=2):")
    reply = ARP(op=2, hwsrc="aa:bb:cc:dd:ee:ff", psrc="192.168.1.1",
                hwdst="11:22:33:44:55:66", pdst="192.168.1.100")
    print(reply.show(dump=True))
    
    print("\n3. GRATUITOUS ARP (announce own IP):")
    print("   - Sender IP = Target IP (same)")
    print("   - Used to update other hosts' ARP caches")
    grat = ARP(op=2, psrc="192.168.1.100", pdst="192.168.1.100")
    print(grat.show(dump=True))

def scan_network_with_arp():
    """Perform a network scan using ARP"""
    print_section("ARP Network Scan")
    
    iface = get_default_interface()
    
    try:
        addrs = netifaces.ifaddresses(iface)
        ip_info = addrs[netifaces.AF_INET][0]
        ip = ip_info['addr']
        network = '.'.join(ip.split('.')[:-1]) + '.0/24'
        
        print(f"\nScanning network: {network}")
        print(f"Interface: {iface}")
        print("\nSending ARP requests to all IPs in subnet...")
        print("(This demonstrates ARP's role in network discovery)\n")
        
        arp = ARP(pdst=network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        
        result = srp(packet, timeout=3, iface=iface, verbose=0)[0]
        
        print(f"{'IP Address':<20} {'MAC Address':<20} {'Response Time'}")
        print("-" * 60)
        
        for sent, received in result:
            print(f"{received.psrc:<20} {received.hwsrc:<20} {'< 3s'}")
        
        print(f"\n✅ Found {len(result)} responding hosts")
        print("\n💡 Each response came from an ARP reply packet")
        print("💡 Only devices in the same broadcast domain respond")
        
    except Exception as e:
        print(f"Scan error: {e}")

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 2: ARP PROTOCOL DEMO")
    print("="*60)
    print("\nThis demo explores Address Resolution Protocol (ARP).")
    print("See how IP addresses are mapped to MAC addresses!")
    
    # Part 1: Theory
    display_arp_theory()
    
    # Part 2: Show system ARP cache
    show_system_arp_cache()
    
    # Part 3: Build ARP request
    build_arp_request("192.168.1.1")
    
    # Part 4: Different ARP types
    demonstrate_arp_types()
    
    # Part 5: Send real ARP request (requires sudo)
    try:
        iface = get_default_interface()
        addrs = netifaces.ifaddresses(iface)
        gateway_ip = netifaces.gateways()['default'][netifaces.AF_INET][0]
        
        print(f"\nTrying to ARP your default gateway: {gateway_ip}")
        send_arp_request(gateway_ip)
        
        # Part 6: Network scan
        scan_network_with_arp()
        
    except PermissionError:
        print_section("Live ARP Demo")
        print("\n⚠️  Sending ARP requires root privileges")
        print("Run with: sudo python3 02_arp_demo.py")
    except Exception as e:
        print(f"\n⚠️  Could not perform live demo: {e}")
    
    print_section("Experiments to Try")
    print("""
1. Monitor live ARP traffic:
   sudo tcpdump -i eth0 arp -vv

2. Manually add an ARP entry:
   sudo arp -s 192.168.1.100 aa:bb:cc:dd:ee:ff

3. Clear ARP cache:
   sudo ip -s -s neigh flush all

4. Send gratuitous ARP:
   - Modify the script to send gratuitous ARP
   - Observe how other hosts update their cache

5. ARP between two VMs:
   - Set up two VMs on same network
   - Watch ARP communication with Wireshark
    """)
    
    print("\n✅ Demo complete! Continue to 03_arp_spoof_demo.py\n")

if __name__ == "__main__":
    main()
