#!/usr/bin/env python3
"""
Layer 2 Demo: Ethernet Basics
==============================

This script demonstrates Ethernet frame structure and MAC addresses.
You'll learn:
- What's in an Ethernet frame
- How MAC addresses work
- How to inspect Ethernet headers

Run with: sudo python3 01_ethernet_basics.py

EXPERIMENT IDEAS:
1. Change the destination MAC address
2. Modify the payload and see how it affects the frame
3. Try different Ethernet types
"""

from scapy.all import Ether, ARP, srp, get_if_hwaddr, conf
import netifaces

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

def display_mac_address_info():
    """Display information about MAC addresses"""
    print_section("MAC Address Fundamentals")
    
    iface = get_default_interface()
    mac = get_if_hwaddr(iface)
    
    print(f"Your interface: {iface}")
    print(f"Your MAC address: {mac}")
    print(f"\nMAC Address Format: XX:XX:XX:XX:XX:XX (48 bits)")
    print(f"First 3 bytes (OUI): Manufacturer identifier")
    print(f"Last 3 bytes: Device-specific identifier")
    print(f"\nBroadcast MAC: ff:ff:ff:ff:ff:ff")
    print(f"Multicast MACs: Start with 01:00:5e (IPv4 multicast)")

def create_ethernet_frame():
    """Create and display an Ethernet frame"""
    print_section("Creating an Ethernet Frame")
    
    # Create a basic Ethernet frame with ARP payload
    frame = Ether(dst="ff:ff:ff:ff:ff:ff", src=get_if_hwaddr(get_default_interface()))
    
    print("\nEthernet Frame Structure:")
    print(frame.show(dump=True))
    
    print("\n\nField Breakdown:")
    print(f"Destination MAC: {frame.dst}")
    print(f"Source MAC: {frame.src}")
    print(f"EtherType: {hex(frame.type)} (0x{frame.type:04x})")
    print(f"  - 0x0800: IPv4")
    print(f"  - 0x0806: ARP")
    print(f"  - 0x86DD: IPv6")
    
    return frame

def scan_local_network():
    """Scan local network to see MAC addresses in action"""
    print_section("Live MAC Address Discovery (ARP Scan)")
    
    iface = get_default_interface()
    
    # Get local IP range
    try:
        addrs = netifaces.ifaddresses(iface)
        ip_info = addrs[netifaces.AF_INET][0]
        ip = ip_info['addr']
        netmask = ip_info['netmask']
        
        # Simple /24 network assumption
        network = '.'.join(ip.split('.')[:-1]) + '.0/24'
        
        print(f"\nScanning network: {network}")
        print(f"Interface: {iface}")
        print("\nThis may take a few seconds...\n")
        
        # Create ARP request
        arp = ARP(pdst=network)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp
        
        # Send and receive responses
        result = srp(packet, timeout=3, iface=iface, verbose=0)[0]
        
        print(f"Found {len(result)} devices:\n")
        print(f"{'IP Address':<20} {'MAC Address':<20} {'Description'}")
        print("-" * 60)
        
        for sent, received in result:
            print(f"{received.psrc:<20} {received.hwsrc:<20} {'Live device'}")
            
        print("\n💡 Observation: Each device has a unique MAC address!")
        print("💡 ARP (Address Resolution Protocol) maps IP → MAC addresses")
        
    except Exception as e:
        print(f"Scan error: {e}")
        print("You may need to run with sudo or adjust network interface")

def demonstrate_frame_analysis():
    """Show how to analyze Ethernet frames"""
    print_section("Ethernet Frame Analysis")
    
    # Create a sample frame with payload
    frame = Ether(dst="ff:ff:ff:ff:ff:ff", src="aa:bb:cc:dd:ee:ff")
    frame = frame / ARP(pdst="192.168.1.1")
    
    print("\nComplete Frame with ARP Payload:")
    print(frame.show(dump=True))
    
    print("\n\nLayer Breakdown:")
    print(f"Layer 2 (Ethernet): {frame[Ether].summary()}")
    if frame.haslayer(ARP):
        print(f"Layer 2.5 (ARP): {frame[ARP].summary()}")
    
    print(f"\nFrame size: {len(frame)} bytes")
    print(f"Minimum Ethernet frame: 64 bytes (with padding)")
    print(f"Maximum Ethernet frame: 1518 bytes (standard MTU)")

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 2: ETHERNET BASICS DEMO")
    print("="*60)
    print("\nThis demo explores Ethernet frames and MAC addresses.")
    print("Watch how data is packaged at Layer 2!")
    
    # Part 1: MAC Address basics
    display_mac_address_info()
    
    # Part 2: Create and inspect a frame
    create_ethernet_frame()
    
    # Part 3: Demonstrate frame analysis
    demonstrate_frame_analysis()
    
    # Part 4: Live network scan
    try:
        scan_local_network()
    except PermissionError:
        print_section("Network Scan")
        print("\n⚠️  Network scan requires root privileges")
        print("Run with: sudo python3 01_ethernet_basics.py")
    
    print_section("Experiments to Try")
    print("""
1. Modify the destination MAC address in create_ethernet_frame()
   - Try unicast (specific device) vs broadcast (ff:ff:ff:ff:ff:ff)

2. Look up your MAC address vendor:
   - Visit https://maclookup.app/
   - Enter the first 3 bytes of your MAC

3. Create frames with different payload types:
   - Add IP() layer instead of ARP()
   - Add custom Raw() data

4. Capture real traffic:
   - Run: sudo tcpdump -i eth0 -e -n
   - Observe MAC addresses in live traffic
    """)
    
    print("\n✅ Demo complete! Continue to 02_arp_demo.py\n")

if __name__ == "__main__":
    main()
