#!/usr/bin/env python3

import sys
import os
import requests
import time
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Systems_Engineering_Chatbot'))

def test_visualization_endpoint():
    """Test the visualization endpoint with timing information."""
    
    print("Testing /isomorphism_visualization endpoint...")
    print("=" * 70)
    
    base_url = "http://127.0.0.1:5001"
    prompt = "create a visual graph for the isomorphisms across a mechanical spring system and an electric circuit model"
    
    print(f"\nEndpoint: {base_url}/isomorphism_visualization")
    print(f"Prompt: {prompt}")
    print("\nNote: This will take 60-150 seconds on first run (cache miss)")
    print("      Subsequent runs will be 10-30 seconds (cache hit)")
    print("\n" + "=" * 70)
    print("Starting request...")
    print()
    
    try:
        start_total = time.time()
        
        response = requests.post(
            f"{base_url}/isomorphism_visualization",
            data={"prompt": prompt},
            timeout=300
        )
        
        elapsed_total = time.time() - start_total
        
        print("\n" + "=" * 70)
        print(f"Response received in {elapsed_total:.2f} seconds")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\nResponse contents:")
            print(f"  - response_text: {len(data.get('response_text', ''))} chars")
            print(f"  - visualization_svg: {len(data.get('visualization_svg', ''))} chars")
            print(f"  - morphisms: {len(data.get('morphisms', []))} items")
            
            if data.get('statistics'):
                stats = data['statistics']
                print(f"  - Statistics:")
                print(f"      Total morphisms: {stats.get('total_morphisms')}")
                print(f"      Isomorphic: {stats.get('isomorphic_count')}")
                print(f"      Homomorphic: {stats.get('homomorphic_count')}")
                print(f"      Avg Strength: {stats.get('average_strength', 0):.2%}")
            
            print(f"\n  - system1_name: {data.get('system1_name')}")
            print(f"  - system2_name: {data.get('system2_name')}")
            
            svg = data.get('visualization_svg', '')
            if svg and '<svg' in svg:
                print(f"\n[SUCCESS] SVG visualization generated successfully")
                print(f"  - SVG size: {len(svg)} chars")
                print(f"  - Contains systems: {'Mechanical Spring System' in svg and 'Electric Circuit Model' in svg}")
                print(f"  - Contains morphisms: {'ISOMORPHIC' in svg or 'HOMOMORPHIC' in svg}")
            else:
                print(f"\n[FAIL] No valid SVG in response")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        print("\n" + "=" * 70)
        print("Check the Flask server logs for detailed timing information:")
        print("  [VISUALIZATION] System 1 extracted in X.XXs")
        print("  [VISUALIZATION] System 2 extracted in X.XXs")
        print("  [VISUALIZATION] Morphisms detected in X.XXs")
        print("  [VISUALIZATION] Visualization rendered in X.XXs")
        print("  [VISUALIZATION] Justification generated in X.XXs")
        print("=" * 70)
        
        return response.status_code == 200
        
    except requests.exceptions.Timeout:
        print("\n[FAIL] Request timeout after 5 minutes")
        print("This likely means:")
        print("  1. The Flask server is not running")
        print("  2. The LLM API calls are hanging")
        print("  3. Network issues")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n[FAIL] Could not connect to {base_url}")
        print("Make sure Flask server is running: python run.py")
        return False
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = test_visualization_endpoint()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
