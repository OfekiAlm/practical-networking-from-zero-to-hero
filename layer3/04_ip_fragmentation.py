#!/usr/bin/env python3
"""
Layer 3 Demo: IP Fragmentation
===============================

This script demonstrates IP packet fragmentation.
You'll learn:
- When and why fragmentation occurs
- How fragments are reassembled
- MTU (Maximum Transmission Unit)

Run with: sudo python3 04_ip_fragmentation.py

EXPERIMENT IDEAS:
1. Send packets of different sizes
2. Test with DF (Don't Fragment) flag
3. Observe MTU path discovery
"""

from scapy.all import IP, ICMP, Raw, fragment, send, sr1
import sys

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_fragmentation():
    """Explain IP fragmentation"""
    print_section("IP Fragmentation")
    print("""
Why Fragmentation?
- Each network has a Maximum Transmission Unit (MTU)
- Ethernet MTU: 1500 bytes
- If packet > MTU, it must be fragmented

When does it happen?
- Router receives packet larger than outgoing link's MTU
- Sender doesn't set "Don't Fragment" (DF) flag
- Router splits packet into smaller fragments

Fragmentation Fields in IP Header:
- Identification: Same for all fragments of one packet
- Flags:
  • DF (Don't Fragment): If set, drop packet and send ICMP error
  • MF (More Fragments): Set except on last fragment
- Fragment Offset: Position of this fragment in original packet

Reassembly:
- Happens at destination only (not at routers)
- Destination collects all fragments
- Uses Identification field to group them
- Uses Fragment Offset to order them
- Waits for fragment with MF=0 (last one)

Problems with Fragmentation:
- Performance overhead
- All fragments must arrive (lose one = lose all)
- Firewall/NAT issues
- Better to avoid via Path MTU Discovery
    """)

def demonstrate_fragmentation():
    """Show fragmentation in action"""
    print_section("Creating and Fragmenting a Packet")
    
    # Create a large packet
    large_data = "X" * 2000
    packet = IP(dst="8.8.8.8")/ICMP()/Raw(load=large_data)
    
    print(f"\nOriginal Packet:")
    print(f"  Total size: {len(packet)} bytes")
    print(f"  IP header: 20 bytes")
    print(f"  ICMP header: 8 bytes")
    print(f"  Payload: {len(large_data)} bytes")
    print(f"  Exceeds typical MTU (1500 bytes): {len(packet) > 1500}")
    
    # Fragment the packet
    print(f"\nFragmenting to 500-byte chunks...")
    fragments = fragment(packet, fragsize=500)
    
    print(f"\nResult: {len(fragments)} fragments")
    
    for i, frag in enumerate(fragments, 1):
        ip = frag[IP]
        print(f"\nFragment {i}:")
        print(f"  ID: {ip.id}")
        print(f"  Size: {len(frag)} bytes")
        print(f"  Flags: {ip.flags} (MF={'Yes' if ip.flags & 1 else 'No'})")
        print(f"  Fragment Offset: {ip.frag} (byte position: {ip.frag * 8})")
        print(f"  More Fragments: {'Yes' if ip.flags & 1 else 'No (Last)'}")

def test_mtu_discovery():
    """Demonstrate Path MTU Discovery"""
    print_section("Path MTU Discovery")
    print("""
Modern systems use Path MTU Discovery (PMTUD):

1. Sender sets DF (Don't Fragment) flag
2. Sends packet
3. If too large for router's MTU:
   - Router drops packet
   - Router sends ICMP "Fragmentation Needed" (Type 3, Code 4)
   - ICMP includes the required MTU
4. Sender reduces packet size and retries
5. Eventually finds the path MTU

Benefits:
- No fragmentation (better performance)
- Optimal packet size for path
- Works around fragmentation problems

IPv6:
- Routers CANNOT fragment
- Sender must do PMTUD
- Minimum MTU: 1280 bytes
    """)

def compare_fragment_sizes():
    """Compare different packet sizes"""
    print_section("Testing Different Packet Sizes")
    
    sizes = [500, 1000, 1472, 1500, 2000, 3000]
    mtu = 1500
    
    print(f"Assuming MTU = {mtu} bytes\n")
    print(f"{'Payload Size':<15} {'Total Size':<15} {'Fragments':<15} {'Status'}")
    print("-" * 70)
    
    for size in sizes:
        # IP header (20) + ICMP header (8) + payload
        total = 20 + 8 + size
        
        if total <= mtu:
            fragments = 1
            status = "No fragmentation"
        else:
            # Simplified fragment calculation
            fragments = (total + mtu - 1) // mtu
            status = "Fragmented"
        
        print(f"{size:<15} {total:<15} {fragments:<15} {status}")

def demonstrate_df_flag():
    """Show Don't Fragment flag behavior"""
    print_section("Don't Fragment (DF) Flag")
    
    print("\nCreating packets with DF flag:")
    
    # Small packet with DF
    small = IP(dst="8.8.8.8", flags="DF")/ICMP()/"Small"
    print(f"\n1. Small packet with DF:")
    print(f"   Size: {len(small)} bytes")
    print(f"   DF flag: {bool(small.flags & 2)}")
    print(f"   Result: Will be sent normally")
    
    # Large packet with DF
    large = IP(dst="8.8.8.8", flags="DF")/ICMP()/Raw("X"*2000)
    print(f"\n2. Large packet with DF:")
    print(f"   Size: {len(large)} bytes")
    print(f"   DF flag: {bool(large.flags & 2)}")
    print(f"   Result: Router will drop and send ICMP error")
    print(f"   ICMP: Type 3, Code 4 (Fragmentation Needed)")
    
    # Large packet without DF
    large_no_df = IP(dst="8.8.8.8")/ICMP()/Raw("X"*2000)
    print(f"\n3. Large packet without DF:")
    print(f"   Size: {len(large_no_df)} bytes")
    print(f"   DF flag: {bool(large_no_df.flags & 2)}")
    print(f"   Result: Router will fragment")

def show_fragmentation_example():
    """Show a complete fragmentation example"""
    print_section("Complete Fragmentation Example")
    
    print("""
Original packet: 2000 bytes total
MTU: 1500 bytes
IP header: 20 bytes
Maximum data per fragment: 1500 - 20 = 1480 bytes

Fragment 1:
  - IP ID: 12345
  - MF: 1 (more fragments)
  - Offset: 0
  - Data: bytes 0-1479 (1480 bytes)
  - Total size: 1500 bytes

Fragment 2:
  - IP ID: 12345 (same)
  - MF: 0 (last fragment)
  - Offset: 185 (1480/8 = 185)
  - Data: bytes 1480-1979 (500 bytes)
  - Total size: 520 bytes

Destination receives:
  1. Sees ID=12345, collects fragments
  2. Orders by offset
  3. Waits for MF=0
  4. Reassembles: bytes[0:1480] + bytes[1480:1980]
  5. Delivers to upper layer
    """)

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 3: IP FRAGMENTATION DEMO")
    print("="*60)
    print("\nThis demo explores IP packet fragmentation.")
    print("Learn how large packets are split and reassembled!")
    
    # Part 1: Explain
    explain_fragmentation()
    
    # Part 2: Demonstrate fragmentation
    demonstrate_fragmentation()
    
    # Part 3: Compare sizes
    compare_fragment_sizes()
    
    # Part 4: DF flag
    demonstrate_df_flag()
    
    # Part 5: PMTUD
    test_mtu_discovery()
    
    # Part 6: Example
    show_fragmentation_example()
    
    print_section("Experiments to Try")
    print("""
1. Test your interface MTU:
   ip link show
   (Look for 'mtu' value)

2. Ping with different sizes:
   ping -M do -s 1472 8.8.8.8  (should work)
   ping -M do -s 1473 8.8.8.8  (may fail - needs fragment but DF set)
   
3. Capture fragmented packets:
   sudo tcpdump -i any 'ip[6:2] & 0x3fff != 0' -nn
   (Shows only fragmented packets)

4. Fragment in Wireshark:
   - Filter: ip.flags.mf == 1 || ip.frag_offset > 0
   - Right-click packet → Follow → UDP/TCP Stream
   - See reassembly

5. Send large ICMP:
   ping -s 3000 8.8.8.8
   (Will fragment, watch with tcpdump)

6. Path MTU:
   tracepath 8.8.8.8
   (Shows MTU along path)

7. IPv6 (no fragmentation at routers):
   ping6 -s 2000 ::1
   (Must fragment before sending)
    """)
    
    print("\n✅ Demo complete! Layer 3 demos finished!\n")

if __name__ == "__main__":
    main()
