#!/usr/bin/env python3
"""Run server and test in subprocess to capture errors"""

import subprocess
import time
import asyncio
import signal
import sys

async def run_test():
    """Start server and run test"""
    
    # Start the server
    print("Starting server...")
    server_proc = subprocess.Popen(
        [sys.executable, "main.py"],
        env={"LISTEN_ADDRESS": ":8081", "PATH": sys.path[0]},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(2)
    
    # Run the test
    print("\nRunning test...")
    test_proc = subprocess.Popen(
        [sys.executable, "test_mcp_tools.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for test to complete or timeout
    try:
        stdout, stderr = test_proc.communicate(timeout=10)
        print("\nTest output:")
        print(stdout)
        if stderr:
            print("\nTest errors:")
            print(stderr)
    except subprocess.TimeoutExpired:
        print("\nTest timed out!")
        test_proc.kill()
    
    # Stop the server
    print("\nStopping server...")
    server_proc.send_signal(signal.SIGINT)
    
    # Get server output
    try:
        stdout, stderr = server_proc.communicate(timeout=5)
        print("\nServer output:")
        print(stdout)
        if stderr:
            print("\nServer errors:")
            print(stderr)
    except subprocess.TimeoutExpired:
        print("\nServer didn't stop cleanly, killing...")
        server_proc.kill()
        stdout, stderr = server_proc.communicate()
        print("\nServer output after kill:")
        print(stdout)
        if stderr:
            print("\nServer errors:")
            print(stderr)

if __name__ == "__main__":
    asyncio.run(run_test())