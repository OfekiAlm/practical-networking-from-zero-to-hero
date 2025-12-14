#!/usr/bin/env python3
"""
Layer 4 Demo: TCP State Machine
================================

This script demonstrates TCP connection states.
You'll learn:
- TCP state transitions
- State diagram walkthrough
- How to monitor connection states

Run with: python3 04_tcp_states.py

EXPERIMENT IDEAS:
1. Monitor states during connection
2. Observe TIME_WAIT state
3. Test different close scenarios
"""

import socket
import subprocess
import time
import sys

def print_section(title):
    """Pretty print section headers"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def explain_tcp_states():
    """Explain TCP state machine"""
    print_section("TCP State Machine")
    print("""
TCP connections transition through various states:

Connection States:
==================

CLOSED
  ↓ (server: listen)
LISTEN          - Server waiting for connections
  ↓ (client: connect)
SYN-SENT        - Client sent SYN, waiting for SYN-ACK
  ↓
SYN-RECEIVED    - Server received SYN, sent SYN-ACK
  ↓
ESTABLISHED     - Connection established, data transfer
  ↓
[Close sequence begins]

Active Close (who initiates FIN):
ESTABLISHED
  → FIN-WAIT-1    - Sent FIN, waiting for ACK
  → FIN-WAIT-2    - Got ACK, waiting for other FIN
  → TIME-WAIT     - Got FIN, sent ACK, wait 2*MSL
  → CLOSED

Passive Close (receives FIN first):
ESTABLISHED
  → CLOSE-WAIT    - Received FIN, sent ACK
  → LAST-ACK      - Sent FIN, waiting for ACK
  → CLOSED

Simultaneous Close:
ESTABLISHED
  → FIN-WAIT-1    - Both sent FIN simultaneously
  → CLOSING       - Received FIN while in FIN-WAIT-1
  → TIME-WAIT
  → CLOSED

Special States:
- TIME-WAIT: Ensures proper close (duration: 2*MSL ≈ 60-120s)
- CLOSE-WAIT: Application hasn't closed yet
    """)

def show_state_diagram():
    """Display ASCII state diagram"""
    print_section("Complete TCP State Diagram")
    print("""
                           ┌─────────┐
                           │ CLOSED  │
                           └────┬────┘
                     passive│    │active
                      open  │    │open
                   ┌────────┘    └────────┐
                   │                      │
                   ↓                      ↓
            ┌──────────┐           ┌────────────┐
            │  LISTEN  │           │  SYN-SENT  │
            └─────┬────┘           └─────┬──────┘
           recv SYN│                     │recv SYN-ACK
          send SYN-ACK                   │send ACK
                   │                     │
                   ↓                     │
          ┌────────────────┐            │
          │  SYN-RECEIVED  │            │
          └────────┬───────┘            │
                   │recv ACK            │
                   │                    │
                   └────────┬───────────┘
                            │
                            ↓
                   ┌─────────────────┐
                   │  ESTABLISHED    │
                   └────────┬────────┘
                           │
               ┌───────────┴───────────┐
            close│                   │recv FIN
          send FIN│                   │send ACK
               │                       │
               ↓                       ↓
        ┌────────────┐          ┌────────────┐
        │ FIN-WAIT-1 │          │ CLOSE-WAIT │
        └─────┬──────┘          └─────┬──────┘
              │recv ACK               │close
              │                       │send FIN
              ↓                       ↓
        ┌────────────┐          ┌────────────┐
        │ FIN-WAIT-2 │          │  LAST-ACK  │
        └─────┬──────┘          └─────┬──────┘
              │recv FIN               │recv ACK
              │send ACK               │
              ↓                       ↓
        ┌────────────┐          ┌────────────┐
        │ TIME-WAIT  │          │   CLOSED   │
        └─────┬──────┘          └────────────┘
              │timeout
              │(2*MSL)
              ↓
        ┌────────────┐
        │   CLOSED   │
        └────────────┘
    """)

def monitor_tcp_states():
    """Show how to monitor TCP states"""
    print_section("Monitoring TCP States")
    print("""
Tools to monitor TCP connection states:

1. ss (socket statistics) - Modern Linux tool:
   ss -tan                    # All TCP connections
   ss -tan state established  # Only ESTABLISHED
   ss -tan state time-wait    # Only TIME-WAIT
   ss -tan | grep 8080        # Specific port

2. netstat - Classic tool:
   netstat -tan               # All TCP connections
   netstat -tan | grep EST    # ESTABLISHED
   netstat -tan | grep TIME   # TIME-WAIT

3. lsof - List open files:
   lsof -i tcp                # All TCP
   lsof -i tcp:8080           # Specific port

Output columns:
- State: Current TCP state
- Recv-Q: Bytes in receive queue (should be 0)
- Send-Q: Bytes in send queue (should be 0)
- Local Address: Your IP:port
- Peer Address: Remote IP:port
    """)

def demonstrate_time_wait():
    """Explain TIME-WAIT state"""
    print_section("Understanding TIME-WAIT")
    print("""
TIME-WAIT is crucial but often misunderstood:

Why TIME-WAIT exists:
1. Ensure last ACK is received
   - If lost, remote will retransmit FIN
   - We need to be around to re-ACK
   
2. Prevent old packets from confusing new connection
   - Old packets might arrive late
   - Wait 2*MSL (Maximum Segment Lifetime)
   - Ensures old packets expire

Duration:
- Linux: 60 seconds (default)
- Can be tuned: net.ipv4.tcp_fin_timeout

Who enters TIME-WAIT?
- The side that sends FIN first (active close)
- Server or client, whoever closes first

Problems with TIME-WAIT:
- Socket can't be reused immediately
- Many connections = many TIME-WAIT sockets
- Can exhaust ephemeral ports

Solutions:
1. SO_REUSEADDR socket option
2. Increase ephemeral port range
3. Connection pooling (reuse connections)
4. Tune tcp_fin_timeout (carefully!)

Check TIME-WAIT count:
  ss -tan state time-wait | wc -l
    """)

def show_state_examples():
    """Show state examples"""
    print_section("State Examples")
    
    print("\nExample 1: Normal Client Connection")
    print("-" * 60)
    print("Time  Client State       Server State       Event")
    print("-" * 60)
    print("t0    CLOSED            LISTEN             Initial")
    print("t1    SYN-SENT          LISTEN             Client → SYN")
    print("t2    SYN-SENT          SYN-RECEIVED       Server → SYN-ACK")
    print("t3    ESTABLISHED       SYN-RECEIVED       Client → ACK")
    print("t4    ESTABLISHED       ESTABLISHED        Connection ready")
    print("t5    ESTABLISHED       ESTABLISHED        Data transfer")
    print("t6    FIN-WAIT-1        ESTABLISHED        Client → FIN")
    print("t7    FIN-WAIT-2        CLOSE-WAIT         Server → ACK")
    print("t8    FIN-WAIT-2        LAST-ACK           Server → FIN")
    print("t9    TIME-WAIT         LAST-ACK           Client → ACK")
    print("t10   TIME-WAIT         CLOSED             Server closes")
    print("t11   CLOSED            CLOSED             After 2*MSL")
    
    print("\n\nExample 2: Connection Refused")
    print("-" * 60)
    print("Time  Client State       Server State       Event")
    print("-" * 60)
    print("t0    CLOSED            CLOSED             No listener")
    print("t1    SYN-SENT          CLOSED             Client → SYN")
    print("t2    CLOSED            CLOSED             Server → RST-ACK")
    print("      (Connection refused)")

def monitor_live_connections():
    """Monitor connections in real-time"""
    print_section("Live Connection Monitoring")
    
    print("\nDemonstrating connection states...")
    print("(Run 'watch -n 1 ss -tan' in another terminal to see real-time)")
    
    try:
        print("\n1. Creating a connection...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        
        print(f"   Bound to localhost:{port}")
        print(f"   State: CLOSED → (bound)")
        
        sock.listen(1)
        print(f"   State: LISTEN")
        print(f"\n   Check with: ss -tan | grep {port}")
        
        input("\n   Press Enter to close socket...")
        
        sock.close()
        print(f"   State: CLOSED")
        
    except Exception as e:
        print(f"   Error: {e}")

def main():
    """Main demonstration function"""
    print("\n" + "="*60)
    print("  LAYER 4: TCP STATE MACHINE DEMO")
    print("="*60)
    print("\nThis demo explains TCP connection states.")
    print("Understand the lifecycle of every TCP connection!")
    
    # Part 1: Explain states
    explain_tcp_states()
    
    # Part 2: State diagram
    show_state_diagram()
    
    # Part 3: Monitoring
    monitor_tcp_states()
    
    # Part 4: TIME-WAIT
    demonstrate_time_wait()
    
    # Part 5: Examples
    show_state_examples()
    
    # Part 6: Live demo
    monitor_live_connections()
    
    print_section("Experiments to Try")
    print("""
1. Monitor states during HTTP request:
   Terminal 1: watch -n 0.5 'ss -tan | grep :80'
   Terminal 2: curl http://example.com
   (Watch states change rapidly)

2. Count TIME-WAIT connections:
   ss -tan state time-wait | wc -l
   
3. Stress test:
   ab -n 1000 -c 10 http://localhost/
   (Apache Bench creates many connections)
   Watch TIME-WAIT sockets accumulate

4. Check state distribution:
   ss -tan | awk '{print $1}' | sort | uniq -c

5. Find long-lived connections:
   ss -tanp | grep ESTABLISHED

6. Monitor CLOSE-WAIT (app not closing):
   ss -tan state close-wait
   (Indicates application leak)

7. Tune TIME-WAIT (careful!):
   sysctl net.ipv4.tcp_fin_timeout
   (View current setting)

8. Watch in Wireshark:
   - Right-click packet → Follow TCP Stream
   - Analyze → Expert Info → Errors
   - See state transitions in time
    """)
    
    print("\n✅ Demo complete! Continue to 05_tcp_retransmission.py\n")

if __name__ == "__main__":
    main()
