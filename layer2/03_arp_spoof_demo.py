#!/usr/bin/env python3
"""
Layer 2 Demo: ARP Spoofing (Educational)
=========================================

⚠️  WARNING: This demo shows ARP spoofing for EDUCATIONAL purposes only!
   - Use ONLY on networks you own
   - Illegal on networks you don't control
   - Can disrupt network communication

This script demonstrates:
- How ARP cache poisoning works
- Why ARP is insecure by design
- Network security implications

Run with: sudo python3 03_arp_spoof_demo.py

This demo does NOT actually perform the attack - it only shows how it would work.
"""

from scapy.all import ARP, Ether, send, sniff
import time

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_arp_vulnerability():
    """Explain the ARP security issue"""
    print_section("Why ARP is Vulnerable")
    print("""
ARP has NO built-in security:
❌ No authentication - anyone can send ARP packets
❌ No verification - hosts trust all ARP replies
❌ Stateless - accepts unrequested replies

The Attack (ARP Spoofing/Poisoning):
1. Attacker sends fake ARP reply to Victim
2. Fake reply says: "I am the Gateway, my MAC is [Attacker's MAC]"
3. Victim updates ARP cache with false information
4. Victim now sends all gateway traffic to Attacker
5. Attacker can intercept, modify, or drop packets

Real-world impact:
- Man-in-the-middle attacks
- Session hijacking
- Credential theft
- Network DOS
    """)

def show_normal_arp_flow():
    """Show legitimate ARP communication"""
    print_section("Normal ARP Flow")
    
    print("\nLegitimate scenario:")
    print("=" * 60)
    print("Host 192.168.1.10 wants to reach Gateway 192.168.1.1")
    print()
    
    print("Step 1: Host sends ARP request")
    arp_req = ARP(op=1, pdst="192.168.1.1", psrc="192.168.1.10")
    print(arp_req.show(dump=True))
    
    print("\nStep 2: Gateway sends legitimate ARP reply")
    arp_reply = ARP(op=2, 
                    hwsrc="aa:bb:cc:dd:ee:01",  # Gateway's real MAC
                    psrc="192.168.1.1",
                    hwdst="aa:bb:cc:dd:ee:10",  # Host's MAC
                    pdst="192.168.1.10")
    print(arp_reply.show(dump=True))
    
    print("\n✅ Host now knows: 192.168.1.1 → aa:bb:cc:dd:ee:01")

def show_arp_spoof_attack():
    """Demonstrate ARP spoofing packet structure"""
    print_section("ARP Spoofing Attack (Demonstration Only)")
    
    print("\nAttack scenario:")
    print("=" * 60)
    print("Attacker: 192.168.1.99 (MAC: 11:22:33:44:55:99)")
    print("Victim: 192.168.1.10 (MAC: aa:bb:cc:dd:ee:10)")
    print("Gateway: 192.168.1.1 (MAC: aa:bb:cc:dd:ee:01)")
    print()
    
    print("Attacker sends FAKE ARP reply to Victim:")
    fake_arp = ARP(op=2,  # ARP reply
                   hwsrc="11:22:33:44:55:99",  # Attacker's MAC (lying!)
                   psrc="192.168.1.1",          # Claiming to be gateway
                   hwdst="aa:bb:cc:dd:ee:10",  # Victim's MAC
                   pdst="192.168.1.10")         # Victim's IP
    
    print(fake_arp.show(dump=True))
    
    print("\n❌ Victim now INCORRECTLY believes:")
    print("   192.168.1.1 (Gateway) → 11:22:33:44:55:99 (Attacker's MAC!)")
    print()
    print("Result: All victim's traffic to gateway goes to attacker first!")

def show_mitigation_techniques():
    """Explain how to defend against ARP spoofing"""
    print_section("Defense Against ARP Spoofing")
    print("""
Protection methods:

1. Static ARP Entries:
   sudo arp -s 192.168.1.1 aa:bb:cc:dd:ee:01
   - Pro: Prevents cache poisoning
   - Con: Hard to manage, doesn't scale

2. ARP Inspection (DAI) on Switches:
   - Switch validates ARP packets
   - Drops invalid ARP replies
   - Requires managed switch

3. Network Monitoring:
   - Detect multiple IPs claiming same MAC
   - Detect MAC address changes
   - Tools: arpwatch, XArp

4. Network Segmentation:
   - VLANs limit ARP broadcast domain
   - Reduces attack surface

5. Encrypted Protocols:
   - Use HTTPS, SSH, VPN
   - Even if ARP is poisoned, data is encrypted

6. Port Security:
   - Limit MAC addresses per switch port
   - Prevents MAC spoofing
    """)

def demonstrate_detection():
    """Show how to detect ARP spoofing"""
    print_section("Detecting ARP Spoofing")
    
    print("""
Detection techniques:

1. Monitor ARP cache changes:
   watch -n 1 arp -n
   Look for: frequent changes, duplicate IPs

2. Capture and analyze ARP traffic:
   sudo tcpdump -i eth0 arp -vv
   Look for: unsolicited ARP replies, gratuitous ARPs

3. Check for IP/MAC conflicts:
   sudo arping -D 192.168.1.1
   
4. Use detection tools:
   sudo arpwatch -i eth0
   - Logs all IP-MAC pairings
   - Alerts on changes

5. Wireshark filters:
   arp.opcode == 2  (Show only ARP replies)
   arp.duplicate-address-detected
    """)

def build_safe_demo_packets():
    """Build example packets without sending them"""
    print_section("Packet Construction (Not Sent)")
    
    print("\nExample 1: Legitimate ARP reply")
    legit = ARP(op=2, hwsrc="aa:bb:cc:dd:ee:01", psrc="192.168.1.1")
    print(legit.show(dump=True))
    
    print("\nExample 2: Gratuitous ARP (can be legitimate)")
    grat = ARP(op=2, psrc="192.168.1.10", pdst="192.168.1.10")
    print(grat.show(dump=True))
    
    print("\nExample 3: Spoofed packet structure (DEMO ONLY)")
    spoofed = ARP(op=2, hwsrc="11:22:33:44:55:99", psrc="192.168.1.1", 
                  pdst="192.168.1.10")
    print(spoofed.show(dump=True))
    
    print("\n⚠️  These packets are NOT being sent!")
    print("This is purely educational to understand the structure.")

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 2: ARP SPOOFING (EDUCATIONAL DEMO)")
    print("="*60)
    print("""
⚠️  IMPORTANT DISCLAIMER ⚠️
This script demonstrates ARP spoofing for educational purposes ONLY.
No actual attack is performed. This helps you understand:
- How ARP vulnerabilities work
- Why network security matters
- How to detect and prevent attacks

NEVER use this knowledge to attack networks you don't own!
    """)
    
    input("Press Enter to continue with educational demo...")
    
    # Part 1: Explain vulnerability
    explain_arp_vulnerability()
    
    # Part 2: Show normal flow
    show_normal_arp_flow()
    
    # Part 3: Show attack structure
    show_arp_spoof_attack()
    
    # Part 4: Show detection
    demonstrate_detection()
    
    # Part 5: Show mitigation
    show_mitigation_techniques()
    
    # Part 6: Build demo packets
    build_safe_demo_packets()
    
    print_section("Learning Outcomes")
    print("""
✅ You now understand:
1. ARP has no built-in security
2. ARP cache poisoning works by sending fake replies
3. This enables man-in-the-middle attacks
4. Detection requires monitoring ARP traffic
5. Defense requires multiple layers (static ARP, DAI, encryption)

Key takeaway: Layer 2 protocols often lack security because they were
designed for trusted local networks. Modern networks need additional
protections!
    """)
    
    print_section("Experiments to Try (Safe)")
    print("""
1. Monitor your ARP cache:
   watch -n 2 arp -n
   
2. Capture ARP traffic:
   sudo tcpdump -i eth0 arp -vv -e
   
3. Test arpwatch:
   sudo arpwatch -i eth0 -d
   
4. Learn Wireshark ARP analysis:
   - Capture on your interface
   - Filter: arp
   - Analyze legitimate vs suspicious patterns

5. Lab environment:
   - Set up VMs on isolated network
   - Practice detection techniques safely
   - Use tools like Ettercap (in lab only!)
    """)
    
    print("\n✅ Demo complete! Continue to Layer 3 demos\n")

if __name__ == "__main__":
    main()
