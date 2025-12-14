#!/usr/bin/env python3
"""
Layer 4 Demo: TCP 3-Way Handshake
==================================

This script visualizes the TCP 3-way handshake.
You'll learn:
- How TCP connections are established
- SYN, SYN-ACK, ACK sequence
- TCP flags and their meanings

Run with: sudo python3 02_tcp_handshake.py

EXPERIMENT IDEAS:
1. Connect to different servers
2. Observe sequence numbers
3. Analyze failed handshakes
"""

from scapy.all import IP, TCP, sr1, send, sniff
import random

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_tcp_handshake():
    """Explain the 3-way handshake"""
    print_section("TCP 3-Way Handshake")
    print("""
Before data transfer, TCP establishes a connection:

Step 1: SYN (Synchronize)
    Client → Server: "I want to connect"
    - SYN flag set
    - Initial sequence number (ISN) chosen randomly
    
Step 2: SYN-ACK (Synchronize-Acknowledge)
    Server → Client: "OK, I'm ready too"
    - SYN flag set
    - ACK flag set
    - Server's ISN chosen
    - ACK = Client's ISN + 1
    
Step 3: ACK (Acknowledge)
    Client → Server: "Connection established"
    - ACK flag set
    - ACK = Server's ISN + 1

After this, both sides can send data!

Packet Flow:
    Client                          Server
      |                               |
      |---> SYN (seq=x) ------------->|  Step 1
      |                               |
      |<--- SYN-ACK (seq=y,ack=x+1) <-|  Step 2
      |                               |
      |---> ACK (ack=y+1) ----------->|  Step 3
      |                               |
      |<==== DATA TRANSFER ==========>|
      |                               |

Why 3 steps?
- Synchronize sequence numbers (both directions)
- Confirm both sides are ready
- Establish initial parameters (window size, MSS, etc.)
    """)

def show_tcp_flags():
    """Explain TCP flags"""
    print_section("TCP Flags")
    
    print("""
TCP Header Flags (Control Bits):

URG (Urgent):         Urgent data present
ACK (Acknowledge):    Acknowledgment field valid
PSH (Push):           Push data to application immediately
RST (Reset):          Reset/abort connection
SYN (Synchronize):    Initiate connection
FIN (Finish):         Close connection gracefully

Common Flag Combinations:
- SYN:           Connection request
- SYN-ACK:       Connection response
- ACK:           Normal data acknowledgment
- PSH-ACK:       Data + force delivery
- FIN-ACK:       Graceful close
- RST:           Abrupt close/reject
- RST-ACK:       Abrupt close with ack
    """)

def create_syn_packet(dst_ip, dst_port):
    """Create SYN packet (Step 1)"""
    print_section("Step 1: Creating SYN Packet")
    
    # Random source port and sequence number
    src_port = random.randint(1024, 65535)
    seq_num = random.randint(0, 2**32 - 1)
    
    # Create SYN packet
    syn = IP(dst=dst_ip)/TCP(sport=src_port, dport=dst_port, 
                              flags='S', seq=seq_num)
    
    print(f"\nSYN Packet to {dst_ip}:{dst_port}")
    print(syn.show(dump=True))
    
    print("\n\nKey Fields:")
    print(f"Source Port: {syn[TCP].sport}")
    print(f"Destination Port: {syn[TCP].dport}")
    print(f"Sequence Number: {syn[TCP].seq}")
    print(f"Acknowledgment: {syn[TCP].ack} (not used yet)")
    print(f"Flags: {syn[TCP].flags} (S = SYN)")
    print(f"Window Size: {syn[TCP].window} bytes")
    
    return syn, seq_num

def perform_handshake(dst_ip, dst_port):
    """Perform complete 3-way handshake"""
    print_section(f"Performing 3-Way Handshake to {dst_ip}:{dst_port}")
    
    # Generate random source port and ISN
    src_port = random.randint(1024, 65535)
    client_isn = random.randint(0, 2**32 - 1)
    
    print(f"\n🔹 Client ISN: {client_isn}")
    print(f"🔹 Source Port: {src_port}\n")
    
    # Step 1: Send SYN
    print("Step 1: Sending SYN")
    print("-" * 40)
    syn = IP(dst=dst_ip)/TCP(sport=src_port, dport=dst_port, 
                             flags='S', seq=client_isn)
    print(f"→ SYN: seq={client_isn}, ack=0, flags=S")
    
    # Send and wait for SYN-ACK
    syn_ack = sr1(syn, timeout=5, verbose=0)
    
    if syn_ack is None:
        print("✗ No SYN-ACK received (timeout)")
        print("  Possible reasons:")
        print("  - Port is closed")
        print("  - Firewall blocking")
        print("  - Host unreachable")
        return False
    
    if not syn_ack.haslayer(TCP):
        print("✗ Unexpected response (not TCP)")
        return False
    
    # Step 2: Received SYN-ACK
    print("\nStep 2: Received SYN-ACK")
    print("-" * 40)
    server_isn = syn_ack[TCP].seq
    ack_num = syn_ack[TCP].ack
    flags = syn_ack[TCP].flags
    
    print(f"← SYN-ACK: seq={server_isn}, ack={ack_num}, flags={flags}")
    print(f"🔹 Server ISN: {server_isn}")
    
    # Verify SYN-ACK
    if 'S' in str(flags) and 'A' in str(flags):
        if ack_num == client_isn + 1:
            print("✓ SYN-ACK is valid!")
            print(f"✓ Server acknowledged our seq+1: {client_isn} + 1 = {ack_num}")
        else:
            print("✗ Invalid ACK number")
            return False
    elif 'R' in str(flags):
        print("✗ Connection refused (RST received)")
        return False
    else:
        print(f"✗ Unexpected flags: {flags}")
        return False
    
    # Step 3: Send ACK
    print("\nStep 3: Sending ACK")
    print("-" * 40)
    ack = IP(dst=dst_ip)/TCP(sport=src_port, dport=dst_port,
                             flags='A', seq=client_isn+1, 
                             ack=server_isn+1)
    print(f"→ ACK: seq={client_isn+1}, ack={server_isn+1}, flags=A")
    send(ack, verbose=0)
    
    print("\n✅ TCP Connection Established!")
    print("\nSequence Number Summary:")
    print(f"  Client ISN: {client_isn}")
    print(f"  Server ISN: {server_isn}")
    print(f"  Next client seq: {client_isn + 1}")
    print(f"  Next server seq: {server_isn + 1}")
    
    return True

def analyze_handshake_variations():
    """Show different handshake scenarios"""
    print_section("Handshake Variations")
    
    print("""
1. Successful Connection:
   Client: SYN →
   Server: ← SYN-ACK
   Client: ACK →
   Status: ESTABLISHED

2. Port Closed:
   Client: SYN →
   Server: ← RST-ACK
   Status: Connection refused

3. Filtered/No Response:
   Client: SYN →
   (timeout)
   Status: No response (firewall?)

4. SYN Flood Attack (educational):
   Attacker: SYN → (many, spoofed IPs)
   Server: ← SYN-ACK (waits...)
   Attacker: (never sends ACK)
   Server: Half-open connections accumulate
   Status: DoS condition

5. Simultaneous Open (rare):
   A: SYN →     ← SYN :B
   A: ← SYN-ACK   SYN-ACK →:B
   A: ACK →     ← ACK :B
   Status: Both connect
    """)

def demonstrate_tcp_states():
    """Show TCP connection states"""
    print_section("TCP Connection States")
    
    print("""
During handshake, both sides transition through states:

Client States:
  CLOSED → SYN-SENT → ESTABLISHED

Server States:
  CLOSED → LISTEN → SYN-RECEIVED → ESTABLISHED

Full State Diagram:
  CLOSED
    ↓
  LISTEN (server only)
    ↓
  SYN-SENT (client) / SYN-RECEIVED (server)
    ↓
  ESTABLISHED ← Data transfer happens here
    ↓
  FIN-WAIT-1, FIN-WAIT-2, CLOSING, TIME-WAIT...
    ↓
  CLOSED

Check your system's connections:
  ss -tan         (Linux)
  netstat -tan    (cross-platform)
    """)

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 4: TCP 3-WAY HANDSHAKE DEMO")
    print("="*60)
    print("\nThis demo visualizes TCP connection establishment.")
    print("See how connections are born!")
    
    # Part 1: Explain
    explain_tcp_handshake()
    
    # Part 2: TCP flags
    show_tcp_flags()
    
    # Part 3: Create SYN packet
    create_syn_packet("8.8.8.8", 80)
    
    # Part 4: Show variations
    analyze_handshake_variations()
    
    # Part 5: States
    demonstrate_tcp_states()
    
    # Part 6: Real handshake
    try:
        print("\n" + "="*60)
        print("Attempting real handshake to google.com:80")
        perform_handshake("142.250.185.46", 80)  # Google IP
        
    except PermissionError:
        print_section("Live Handshake Demo")
        print("\n⚠️  Sending raw TCP requires root privileges")
        print("Run with: sudo python3 02_tcp_handshake.py")
    
    print_section("Experiments to Try")
    print("""
1. Capture handshake in Wireshark:
   - Filter: tcp.flags.syn==1
   - Observe 3-way handshake
   - Check sequence numbers

2. Use tcpdump:
   sudo tcpdump -i any 'tcp[tcpflags] & (tcp-syn) != 0' -nn

3. Try different ports:
   - Port 80 (HTTP): Usually open
   - Port 22 (SSH): May be open
   - Port 9999: Likely closed (see RST)

4. Check connection states:
   ss -tan | grep ESTABLISHED
   ss -tan | grep SYN

5. SYN scan (educational):
   nmap -sS 192.168.1.1
   (Sends SYN, doesn't complete handshake)

6. Monitor your own connections:
   watch -n 1 'ss -tan | head -20'
   (Open browser, watch connections form)
    """)
    
    print("\n✅ Demo complete! Continue to 03_tcp_connection.py\n")

if __name__ == "__main__":
    main()
