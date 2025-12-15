"""TCP 3-way handshake demo as a pure function.

This module provides a refactored version of the TCP handshake demo
that returns structured JSON output instead of printing to console.
"""
import time
import random
from typing import Dict, Any, Optional
from scapy.all import IP, TCP, sr1, send

from backend.schemas.demos import TCPHandshakeParams


def execute_tcp_handshake(params: TCPHandshakeParams) -> Dict[str, Any]:
    """
    Execute TCP 3-way handshake demonstration.
    
    This function performs a complete TCP 3-way handshake with a target
    server and returns structured information about the process.
    
    Args:
        params: Validated parameters including target IP, port, and timeout
        
    Returns:
        Dictionary containing:
        - success: bool indicating if handshake completed
        - data: Dictionary with handshake details
        - error: Error message if failed
        - metadata: Execution metadata
    """
    start_time = time.time()
    
    try:
        result = _perform_handshake(
            target_ip=params.target_ip,
            target_port=params.target_port,
            timeout=params.timeout,
            source_port=params.source_port
        )
        
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            "success": result["success"],
            "data": result,
            "error": result.get("error"),
            "metadata": {
                "execution_time_ms": execution_time,
                "demo_id": "tcp-handshake",
                "demo_version": "1.0.0"
            }
        }
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return {
            "success": False,
            "data": None,
            "error": f"Unexpected error: {str(e)}",
            "metadata": {
                "execution_time_ms": execution_time,
                "demo_id": "tcp-handshake",
                "demo_version": "1.0.0"
            }
        }


def _perform_handshake(
    target_ip: str,
    target_port: int,
    timeout: int,
    source_port: Optional[int] = None
) -> Dict[str, Any]:
    """
    Perform the actual TCP 3-way handshake.
    
    Returns structured data about each step of the handshake.
    """
    # Generate random source port and ISN if not provided
    src_port = source_port or random.randint(1024, 65535)
    client_isn = random.randint(0, 2**32 - 1)
    
    handshake_data = {
        "success": False,
        "target_ip": target_ip,
        "target_port": target_port,
        "source_port": src_port,
        "client_isn": client_isn,
        "server_isn": None,
        "steps": []
    }
    
    # Step 1: Send SYN
    step1_start = time.time()
    syn = IP(dst=target_ip) / TCP(
        sport=src_port,
        dport=target_port,
        flags='S',
        seq=client_isn
    )
    
    handshake_data["steps"].append({
        "step": 1,
        "name": "SYN",
        "direction": "client_to_server",
        "packet": {
            "seq": client_isn,
            "ack": 0,
            "flags": "S",
            "source_port": src_port,
            "dest_port": target_port
        },
        "timestamp_ms": step1_start * 1000
    })
    
    # Send and wait for SYN-ACK
    try:
        syn_ack = sr1(syn, timeout=timeout, verbose=0)
    except Exception as e:
        handshake_data["error"] = f"Failed to send SYN: {str(e)}"
        return handshake_data
    
    if syn_ack is None:
        handshake_data["error"] = "No SYN-ACK received (timeout)"
        handshake_data["reason"] = "Port may be closed, filtered, or host unreachable"
        return handshake_data
    
    if not syn_ack.haslayer(TCP):
        handshake_data["error"] = "Unexpected response (not TCP)"
        return handshake_data
    
    # Step 2: Received SYN-ACK
    step2_time = time.time()
    server_isn = syn_ack[TCP].seq
    ack_num = syn_ack[TCP].ack
    flags = str(syn_ack[TCP].flags)
    
    handshake_data["server_isn"] = server_isn
    handshake_data["steps"].append({
        "step": 2,
        "name": "SYN-ACK",
        "direction": "server_to_client",
        "packet": {
            "seq": server_isn,
            "ack": ack_num,
            "flags": flags,
            "source_port": target_port,
            "dest_port": src_port,
            "ttl": syn_ack.ttl if hasattr(syn_ack, 'ttl') else None,
            "window_size": syn_ack[TCP].window
        },
        "timestamp_ms": step2_time * 1000,
        "rtt_ms": (step2_time - step1_start) * 1000
    })
    
    # Verify SYN-ACK
    if 'S' in flags and 'A' in flags:
        if ack_num == client_isn + 1:
            handshake_data["syn_ack_valid"] = True
        else:
            handshake_data["error"] = f"Invalid ACK number: expected {client_isn + 1}, got {ack_num}"
            handshake_data["syn_ack_valid"] = False
            return handshake_data
    elif 'R' in flags:
        handshake_data["error"] = "Connection refused (RST received)"
        handshake_data["reason"] = "Port is closed or server rejected connection"
        return handshake_data
    else:
        handshake_data["error"] = f"Unexpected flags: {flags}"
        return handshake_data
    
    # Step 3: Send ACK
    step3_time = time.time()
    ack = IP(dst=target_ip) / TCP(
        sport=src_port,
        dport=target_port,
        flags='A',
        seq=client_isn + 1,
        ack=server_isn + 1
    )
    
    try:
        send(ack, verbose=0)
    except Exception as e:
        handshake_data["error"] = f"Failed to send ACK: {str(e)}"
        return handshake_data
    
    handshake_data["steps"].append({
        "step": 3,
        "name": "ACK",
        "direction": "client_to_server",
        "packet": {
            "seq": client_isn + 1,
            "ack": server_isn + 1,
            "flags": "A",
            "source_port": src_port,
            "dest_port": target_port
        },
        "timestamp_ms": step3_time * 1000
    })
    
    # Connection established successfully
    handshake_data["success"] = True
    handshake_data["connection_established"] = True
    handshake_data["next_client_seq"] = client_isn + 1
    handshake_data["next_server_seq"] = server_isn + 1
    handshake_data["total_time_ms"] = (step3_time - step1_start) * 1000
    
    return handshake_data


def execute_tcp_handshake_cli(params: TCPHandshakeParams) -> None:
    """
    CLI wrapper that prints human-readable output.
    
    This maintains backward compatibility with the original script's
    behavior while using the same core logic.
    """
    print(f"\n{'='*60}")
    print(f"  TCP 3-Way Handshake: {params.target_ip}:{params.target_port}")
    print('='*60)
    
    result = execute_tcp_handshake(params)
    
    if result["success"]:
        data = result["data"]
        print(f"\n✅ Connection established successfully!\n")
        print(f"Client ISN: {data['client_isn']}")
        print(f"Server ISN: {data['server_isn']}")
        print(f"Source Port: {data['source_port']}")
        print(f"\nHandshake Steps:")
        for step in data["steps"]:
            print(f"  Step {step['step']}: {step['name']} ({step['direction']})")
            print(f"    Seq={step['packet']['seq']}, Ack={step['packet']['ack']}, Flags={step['packet']['flags']}")
            if 'rtt_ms' in step:
                print(f"    RTT: {step['rtt_ms']:.2f} ms")
        print(f"\nTotal Time: {data['total_time_ms']:.2f} ms")
    else:
        print(f"\n❌ Handshake failed: {result['error']}")
        if 'reason' in result.get('data', {}):
            print(f"   Reason: {result['data']['reason']}")
    
    print(f"\nExecution time: {result['metadata']['execution_time_ms']:.2f} ms\n")


if __name__ == "__main__":
    """Allow running this module standalone for testing."""
    import sys
    
    # Example usage
    params = TCPHandshakeParams(
        target_ip="142.250.185.46",  # Google
        target_port=80,
        timeout=5
    )
    
    try:
        execute_tcp_handshake_cli(params)
    except PermissionError:
        print("\n⚠️  This demo requires root/sudo privileges to send raw packets")
        print("Run with: sudo python3 -m backend.demos.layer4.tcp_handshake")
        sys.exit(1)
