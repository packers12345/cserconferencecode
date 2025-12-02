#!/usr/bin/env python3

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Systems_Engineering_Chatbot'))

from src.system_component_extractor import SystemComponentExtractor
from src.morphism_detector import MorphismDetector
from src.isomorphism_graph_renderer import IsomorphismGraphRenderer
from src.morphism_cache import MorphismCache
from src.api_integration import GeminiClient
from src.morphism_detector import Morphism

def test_spring_circuit_visual_rendering():
    """Test the exact prompt: 'Create a visual graph for the isomorphisms across a mechanical spring system and an electric circuit model'"""
    prompt = "Create a visual graph for the isomorphisms across a mechanical spring system and an electric circuit model"
    
    print(f"Testing prompt: {prompt}\n")
    print("="*80)
    
    try:
        start_total = time.time()
        
        client = GeminiClient()
        cache = MorphismCache()
        extractor = SystemComponentExtractor(client)
        detector = MorphismDetector(client)
        renderer = IsomorphismGraphRenderer()
        
        system1_name = "mechanical spring system"
        system2_name = "electric circuit model"
        
        print(f"\n[TEST] Checking cache...")
        cached_morphisms = cache.get_cached_morphisms(system1_name, system2_name)
        
        if not cached_morphisms:
            print(f"[TEST] Cache MISS - will need to extract specifications")
            
            print(f"\n[TEST] Extracting {system1_name}...")
            start = time.time()
            system1_spec = extractor.extract_system_specification(system1_name)
            t1 = time.time() - start
            print(f"✓ System 1 extracted in {t1:.2f}s")
            
            print(f"\n[TEST] Extracting {system2_name}...")
            start = time.time()
            system2_spec = extractor.extract_system_specification(system2_name)
            t2 = time.time() - start
            print(f"✓ System 2 extracted in {t2:.2f}s")
            
            print(f"\n[TEST] Detecting morphisms...")
            start = time.time()
            morphisms = detector.detect_morphisms(system1_spec, system2_spec)
            t3 = time.time() - start
            print(f"✓ Morphisms detected in {t3:.2f}s ({len(morphisms)} morphisms found)")
            
        else:
            print(f"[TEST] Cache HIT - using cached morphisms ({len(cached_morphisms)} items)")
            from src.morphism_detector import Morphism
            morphisms = [Morphism(**m) for m in cached_morphisms]
            system1_spec = cache.get_cached_system(system1_name)
            system2_spec = cache.get_cached_system(system2_name)
        
        print(f"\n[TEST] Rendering visualization...")
        start = time.time()
        svg = renderer.render_full_visualization(system1_spec, system2_spec, morphisms)
        t_render = time.time() - start
        print(f"✓ SVG rendered in {t_render:.2f}s ({len(svg)} bytes)")
        
        total_time = time.time() - start_total
        print(f"\n[TEST] TOTAL TIME: {total_time:.2f}s")
        print(f"\nVisualization SUCCESS: Generated {len(svg)} byte SVG with {len(morphisms)} morphisms")
        
        if len(svg) == 0:
            print("❌ ERROR: SVG is empty!")
            return False
        
        if len(morphisms) == 0:
            print("⚠️  WARNING: No morphisms detected!")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_spring_circuit_visual_rendering()
    sys.exit(0 if success else 1)
