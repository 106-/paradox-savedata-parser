#!/usr/bin/env python3
"""
Script to test the SaveData functionality with both Python and Rust implementations
"""

import sys
from pathlib import Path

# Sample file path
SAMPLE_FILE = "examples/sample_saves/sample.hoi4"

def test_python_implementation():
    """Test the Python implementation's SaveData functionality"""
    print("\n1. Testing Python implementation...")
    
    # Temporarily modify sys.modules to remove rust_parser if it's loaded
    rust_parser = sys.modules.pop('paradox_savedata.parser.rust_parser', None)
    
    # Import the parser module (which will now use the Python implementation)
    from paradox_savedata.parser import parse_save_file
    
    print("  Using Python implementation")
    
    # Parse the sample file
    save_data = parse_save_file(SAMPLE_FILE)
    
    # Test attribute access
    print("\n  Testing attribute access:")
    try:
        player_tag = save_data.player
        print(f"  ✓ Attribute access works: save_data.player = {player_tag}")
    except Exception as e:
        print(f"  ❌ Attribute access failed: {e}")
    
    # Test nested attribute access
    print("\n  Testing nested attribute access:")
    try:
        country_name = save_data.countries.IRQ.name
        print(f"  ✓ Nested attribute access works: save_data.countries.IRQ.name = {country_name}")
    except Exception as e:
        print(f"  ❌ Nested attribute access failed: {e}")
    
    # Test dictionary access
    print("\n  Testing dictionary access:")
    try:
        country_name = save_data["countries"]["IRQ"]["name"]
        print(f"  ✓ Dictionary access works: save_data[\"countries\"][\"IRQ\"][\"name\"] = {country_name}")
    except Exception as e:
        print(f"  ❌ Dictionary access failed: {e}")
    
    # Test mixed access
    print("\n  Testing mixed access:")
    try:
        country_name = save_data.countries["IRQ"].name
        print(f"  ✓ Mixed access works: save_data.countries[\"IRQ\"].name = {country_name}")
    except Exception as e:
        print(f"  ❌ Mixed access failed: {e}")
    
    # Test data modification
    print("\n  Testing data modification:")
    try:
        original_treasury = save_data.countries.IRQ.treasury
        save_data.countries.IRQ.treasury = 1000.0
        new_treasury = save_data.countries.IRQ.treasury
        print(f"  ✓ Data modification works: Changed treasury from {original_treasury} to {new_treasury}")
    except Exception as e:
        print(f"  ❌ Data modification failed: {e}")
    
    # Restore the rust_parser module if it was loaded
    if rust_parser:
        sys.modules['paradox_savedata.parser.rust_parser'] = rust_parser

def test_rust_implementation():
    """Test the Rust implementation's SaveData functionality"""
    print("\n2. Testing Rust implementation...")
    
    # First, ensure the rust_parser is available
    try:
        # Try to import the rust_parser directly
        from paradox_savedata.parser import rust_parser
        print("  Rust module imported successfully")
    except ImportError:
        print("  Rust implementation is not available. Skipping Rust test.")
        return
    
    # Import the parser module
    from paradox_savedata.parser import parse_save_file
    
    print("  Using Rust implementation")
    
    # Parse the sample file
    save_data = parse_save_file(SAMPLE_FILE)
    
    # Test attribute access
    print("\n  Testing attribute access:")
    try:
        player_tag = save_data.player
        print(f"  ✓ Attribute access works: save_data.player = {player_tag}")
    except Exception as e:
        print(f"  ❌ Attribute access failed: {e}")
    
    # Test nested attribute access
    print("\n  Testing nested attribute access:")
    try:
        country_name = save_data.countries.IRQ.name
        print(f"  ✓ Nested attribute access works: save_data.countries.IRQ.name = {country_name}")
    except Exception as e:
        print(f"  ❌ Nested attribute access failed: {e}")
    
    # Test dictionary access
    print("\n  Testing dictionary access:")
    try:
        country_name = save_data["countries"]["IRQ"]["name"]
        print(f"  ✓ Dictionary access works: save_data[\"countries\"][\"IRQ\"][\"name\"] = {country_name}")
    except Exception as e:
        print(f"  ❌ Dictionary access failed: {e}")
    
    # Test mixed access
    print("\n  Testing mixed access:")
    try:
        country_name = save_data.countries["IRQ"].name
        print(f"  ✓ Mixed access works: save_data.countries[\"IRQ\"].name = {country_name}")
    except Exception as e:
        print(f"  ❌ Mixed access failed: {e}")
    
    # Test data modification
    print("\n  Testing data modification:")
    try:
        original_treasury = save_data.countries.IRQ.treasury
        save_data.countries.IRQ.treasury = 1000.0
        new_treasury = save_data.countries.IRQ.treasury
        print(f"  ✓ Data modification works: Changed treasury from {original_treasury} to {new_treasury}")
    except Exception as e:
        print(f"  ❌ Data modification failed: {e}")

def main():
    print("Testing SaveData functionality with sample file:", SAMPLE_FILE)
    
    # Test Python implementation
    test_python_implementation()
    
    # Test Rust implementation
    test_rust_implementation()
    
    print("\nTests completed.")

if __name__ == "__main__":
    main()
