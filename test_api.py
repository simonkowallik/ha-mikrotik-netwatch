#!/usr/bin/env python3
"""Test script for MikroTik Netwatch API."""

import asyncio
import sys

import aiohttp

from custom_components.mikrotik_netwatch.api import MikroTikNetwatchAPI


async def test_api(host: str, username: str, password: str, ignore_ssl: bool = False) -> bool:
    """Test the MikroTik Netwatch API."""
    print(f"Testing connection to {host}...")
    
    async with aiohttp.ClientSession() as session:
        api = MikroTikNetwatchAPI(
            host=host,
            username=username,
            password=password,
            verify_ssl=not ignore_ssl,
            session=session,
        )
        
        try:
            data = await api.async_get_netwatch_data()
            print(f"✅ Successfully retrieved {len(data)} netwatch entries:")
            
            for i, entry in enumerate(data, 1):
                print(f"\n--- Entry {i} ---")
                print(f"ID: {entry.get('.id', 'N/A')}")
                print(f"Comment: {entry.get('comment', 'N/A')}")
                print(f"Host: {entry.get('host', 'N/A')}")
                print(f"Status: {entry.get('status', 'N/A')}")
                print(f"RTT Avg: {entry.get('rtt-avg', 'N/A')} ms")
                print(f"Loss %: {entry.get('loss-percent', 'N/A')}%")
                
        except Exception as err:
            print(f"❌ Error: {err}")
            return False
    
    return True


def main():
    """Main function."""
    if len(sys.argv) < 4:
        print("Usage: python test_api.py <host> <username> <password> [ignore_ssl]")
        print("Example: python test_api.py 192.168.1.1 admin mypassword true")
        sys.exit(1)
    
    host = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    ignore_ssl = len(sys.argv) > 4 and sys.argv[4].lower() in ('true', '1', 'yes')
    
    asyncio.run(test_api(host, username, password, ignore_ssl))


if __name__ == "__main__":
    main()
