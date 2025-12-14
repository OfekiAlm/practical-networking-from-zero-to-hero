#!/usr/bin/env python3
"""
Layer 4 Demo: TCP Retransmission
=================================

This script demonstrates TCP reliability mechanisms.
You'll learn:
- How TCP ensures delivery
- Retransmission timers
- Fast retransmit
- Flow and congestion control

Run with: python3 05_tcp_retransmission.py

EXPERIMENT IDEAS:
1. Simulate packet loss
2. Observe retransmission timers
3. Test congestion control
"""

import time

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_tcp_reliability():
    """Explain TCP reliability mechanisms"""
    print_section("TCP Reliability Mechanisms")
    print("""
TCP ensures reliable delivery through:

1. ACKNOWLEDGMENTS (ACKs)
   - Receiver acknowledges received data
   - ACK number = next expected sequence number
   - "I received all bytes up to N-1, send N next"

2. SEQUENCE NUMBERS
   - Every byte has a sequence number
   - Sender tracks what's sent
   - Receiver orders packets correctly

3. RETRANSMISSION
   - If ACK not received → retransmit
   - Uses Retransmission Timeout (RTO)
   - Exponential backoff on repeated loss

4. CHECKSUMS
   - Detect corruption
   - Drop corrupted packets
   - Trigger retransmission

5. FLOW CONTROL
   - Window size advertised by receiver
   - Prevents sender from overwhelming receiver
   - Dynamic adjustment

6. CONGESTION CONTROL
   - Prevents network congestion
   - Slow start, congestion avoidance
   - Reduces rate when loss detected
    """)

def explain_retransmission():
    """Explain retransmission in detail"""
    print_section("TCP Retransmission")
    print("""
How Retransmission Works:
=========================

Normal Case (No Loss):
  Client: Send seq=1000, len=100
  Server: ACK=1100 (received bytes 1000-1099)
  ✓ Success!

Packet Loss:
  Client: Send seq=1000, len=100
  (packet lost in network)
  Server: (never receives)
  Client: (no ACK after RTO) → RETRANSMIT seq=1000
  Server: ACK=1100
  ✓ Recovered!

ACK Loss:
  Client: Send seq=1000, len=100
  Server: ACK=1100
  (ACK lost in network)
  Client: (no ACK after RTO) → RETRANSMIT seq=1000
  Server: ACK=1100 (duplicate, but harmless)
  ✓ Works due to sequence numbers!

Retransmission Timeout (RTO):
- Calculated dynamically based on RTT
- Too short: unnecessary retransmits
- Too long: poor performance
- Formula: RTO = SRTT + 4*RTTVAR
  • SRTT: Smoothed Round Trip Time
  • RTTVAR: RTT variance
- Starts ~1 second, adjusts with measurements
- Doubles on each timeout (exponential backoff)

Fast Retransmit:
- Don't wait for RTO
- If 3 duplicate ACKs received → retransmit immediately
- Much faster recovery
- Part of TCP Fast Recovery algorithm
    """)

def demonstrate_retransmission_example():
    """Show retransmission example"""
    print_section("Retransmission Example")
    
    print("\nScenario: Packet loss during file transfer")
    print("=" * 60)
    
    print("\nTime  Event                              State")
    print("-" * 60)
    print("t0    Send: seq=1000, len=1000          Waiting for ACK")
    print("t1    Send: seq=2000, len=1000          Waiting for ACK")
    print("t2    Send: seq=3000, len=1000          Waiting for ACK")
    print("      (seq=2000 packet lost)")
    print("t3    Recv: ACK=2000                    Partial success")
    print("      (ACK for seq=1000)")
    print("t4    Recv: ACK=2000 (duplicate)        Loss detected!")
    print("      (Receiver got seq=3000 but wants 2000)")
    print("t5    Recv: ACK=2000 (duplicate)")
    print("t6    Recv: ACK=2000 (3rd duplicate)    Fast Retransmit!")
    print("      RETRANSMIT: seq=2000, len=1000")
    print("t7    Recv: ACK=4000                    Recovered!")
    print("      (Receiver had 3000 buffered, now has 2000-4000)")
    
    print("\n💡 Fast Retransmit triggered after 3 duplicate ACKs")
    print("💡 Much faster than waiting for RTO timeout")

def explain_flow_control():
    """Explain flow control"""
    print_section("Flow Control (Receiver Window)")
    print("""
Flow Control prevents sender from overwhelming receiver:

Window Advertisement:
- Receiver tells sender: "I can buffer N bytes"
- Sent in every ACK
- Sender respects this limit

Example:
  Receiver: window=2000 bytes, ACK=1000
  Sender: Can send bytes 1000-2999 (2000 bytes)
  
  Sender transmits 2000 bytes (seq 1000-2999)
  Receiver: window=0 (buffer full!)
  Sender: STOPS sending (window closed)
  
  Receiver: processes data, frees buffer
  Receiver: window=2000, ACK=3000
  Sender: Resumes sending

Zero Window Probe:
- If window=0, sender waits
- Periodically sends 1-byte probe
- Ensures window updates aren't lost

Silly Window Syndrome:
- Problem: many tiny window updates
- Solution: delay ACK until reasonable window
- Nagle's algorithm helps
    """)

def explain_congestion_control():
    """Explain congestion control"""
    print_section("Congestion Control (Network Capacity)")
    print("""
Congestion Control prevents overwhelming the network:

Two Windows:
1. Receiver Window (rwnd): receiver's capacity
2. Congestion Window (cwnd): network's capacity
   Effective window = min(rwnd, cwnd)

Congestion Control Phases:
===========================

1. SLOW START
   - Start conservatively
   - cwnd starts at 1-4 segments (MSS)
   - Double cwnd each RTT
   - Exponential growth
   - Ends when reaches ssthresh or loss

2. CONGESTION AVOIDANCE
   - Slower growth
   - Increase cwnd by 1 MSS per RTT
   - Linear growth
   - More cautious

3. FAST RECOVERY
   - After fast retransmit
   - Set ssthresh = cwnd / 2
   - Set cwnd = ssthresh + 3
   - Resume with linear growth

Loss Detection:
- Timeout: severe, reduce cwnd to 1 MSS
- 3 duplicate ACKs: mild, halve cwnd

Example:
  Initial: cwnd=1 MSS (1460 bytes)
  RTT 1: cwnd=2 MSS
  RTT 2: cwnd=4 MSS
  RTT 3: cwnd=8 MSS (slow start)
  ...
  RTT 5: cwnd=32 MSS, reaches ssthresh
  Switch to congestion avoidance
  RTT 6: cwnd=33 MSS (+1)
  RTT 7: cwnd=34 MSS (+1)
  ...
  Loss detected (3 dup ACKs)
  ssthresh = 17 MSS
  cwnd = 20 MSS (fast recovery)

Algorithms:
- Reno: classic algorithm (above)
- Cubic: modern Linux default
- BBR: Google's bottleneck bandwidth algorithm
    """)

def show_performance_factors():
    """Show factors affecting TCP performance"""
    print_section("TCP Performance Factors")
    print("""
Factors affecting TCP throughput:

1. Bandwidth-Delay Product (BDP)
   BDP = Bandwidth × RTT
   - Maximum data "in flight"
   - Window must be >= BDP for full utilization
   
   Example:
   - 100 Mbps link, 50ms RTT
   - BDP = 100 Mbps × 0.05s = 5 Mb = 625 KB
   - Need window >= 625 KB
   
2. Packet Loss
   - Triggers retransmission
   - Reduces cwnd
   - Major performance killer
   - Example: 1% loss can reduce throughput by ~50% (varies by RTT, algorithm)

3. Round Trip Time (RTT)
   - Higher RTT → slower growth
   - ACKs arrive slower
   - Reduces effective throughput
   
4. Window Scaling
   - Default max window: 64 KB
   - Window scaling option: up to 1 GB
   - Essential for high-speed networks
   
5. Selective ACK (SACK)
   - Acknowledge non-contiguous blocks
   - Better recovery from multiple losses
   - Enabled by default on modern systems

Calculating Maximum Throughput:
  Without loss: Throughput = Window / RTT
  With loss: Throughput ≈ MSS / (RTT × sqrt(loss_rate))
    """)

def show_monitoring_commands():
    """Show how to monitor TCP behavior"""
    print_section("Monitoring TCP Behavior")
    print("""
Tools to observe TCP reliability:

1. tcpdump - Capture packets:
   sudo tcpdump -i any -nn 'tcp[tcpflags] & tcp-ack != 0'
   (Show packets with ACK flag)
   
   sudo tcpdump -i any -nn 'tcp[20:4]'
   (May show retransmissions)

2. Wireshark - Deep analysis:
   Filter: tcp.analysis.retransmission
   Filter: tcp.analysis.duplicate_ack
   Filter: tcp.analysis.window_full
   Statistics → TCP Stream Graphs

3. ss - Socket statistics:
   ss -ti
   (Shows detailed TCP info including retransmits)
   
   Look for:
   - rto: Retransmission timeout
   - rtt: Round trip time
   - cwnd: Congestion window
   - ssthresh: Slow start threshold

4. netstat - Network statistics:
   netstat -s | grep retrans
   (System-wide retransmission stats)

5. nstat - Network statistics:
   nstat -az | grep -i retrans
   (Detailed counters)

Example ss output:
  ESTAB  0  0  192.168.1.100:52341  93.184.216.34:80
         rto:204 rtt:3.5/1.5 ato:40 cwnd:10 ssthresh:7
         bytes_acked:1234 bytes_received:5678
         segs_out:15 segs_in:12 data_segs_out:8
         send 22.9Mbps lastsnd:100 lastrcv:100 
         lastack:100 pacing_rate 45.7Mbps
         retrans:0/2 rcv_space:29200
    """)

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 4: TCP RETRANSMISSION & RELIABILITY")
    print("="*60)
    print("\nThis demo explains how TCP ensures reliable delivery.")
    print("See the mechanisms that make TCP work!")
    
    # Part 1: Reliability overview
    explain_tcp_reliability()
    
    # Part 2: Retransmission
    explain_retransmission()
    
    # Part 3: Example
    demonstrate_retransmission_example()
    
    # Part 4: Flow control
    explain_flow_control()
    
    # Part 5: Congestion control
    explain_congestion_control()
    
    # Part 6: Performance
    show_performance_factors()
    
    # Part 7: Monitoring
    show_monitoring_commands()
    
    print_section("Experiments to Try")
    print("""
1. Observe retransmissions:
   sudo tcpdump -i any port 80 -vv
   curl http://example.com
   (Look for retransmissions in output)

2. Monitor TCP stats:
   ss -ti dst example.com
   (Shows RTO, RTT, cwnd)

3. Simulate packet loss:
   sudo tc qdisc add dev eth0 root netem loss 5%
   (Add 5% packet loss)
   curl http://example.com
   sudo tc qdisc del dev eth0 root
   (Remove)

4. Analyze in Wireshark:
   - Capture traffic
   - Statistics → TCP Stream Graphs → Time-Sequence (Stevens)
   - See retransmissions, window updates
   
5. Test high-latency:
   sudo tc qdisc add dev eth0 root netem delay 100ms
   (Add 100ms delay)
   time curl http://example.com
   (Notice slower)
   sudo tc qdisc del dev eth0 root

6. Check system retransmits:
   netstat -s | grep -i retrans
   (Before and after transfers)

7. Long transfer:
   curl -O http://example.com/largefile
   In parallel: watch -n 1 'ss -ti | grep example'
   (Watch cwnd grow)

8. iperf3 testing:
   Server: iperf3 -s
   Client: iperf3 -c server_ip
   (Shows throughput, retransmits)
    """)
    
    print("\n✅ Demo complete! All Layer 4 demos finished!\n")

if __name__ == "__main__":
    main()
