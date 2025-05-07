#!/usr/bin/env python3
"""
Script to compare the output of Python and Rust implementations of the paradox-savedata parser
"""

import json
import sys
import importlib
from pathlib import Path

# Sample file path
SAMPLE_FILE = "examples/sample_saves/sample.hoi4"

def get_python_implementation_result():
    """Force the use of Python implementation and parse the sample file"""
    # Temporarily modify sys.modules to remove rust_parser if it's loaded
    rust_parser = sys.modules.pop('paradox_savedata.parser.rust_parser', None)
    
    # Import the parser module (which will now use the Python implementation)
    from paradox_savedata.parser import parse_save_file
    
    # Print which implementation is being used
    print("  Using Python implementation")
    
    # Parse the sample file
    save_data = parse_save_file(SAMPLE_FILE)
    
    # Convert to dictionary for comparison
    result = save_data.data
    
    # Restore the rust_parser module if it was loaded
    if rust_parser:
        sys.modules['paradox_savedata.parser.rust_parser'] = rust_parser
    
    return result

def get_rust_implementation_result():
    """Force the use of Rust implementation and parse the sample file"""
    # First, ensure the rust_parser is available
    try:
        # Try to import the rust_parser directly
        from paradox_savedata.parser import rust_parser
        print("  Rust module imported successfully:", rust_parser)
    except ImportError:
        print("  Rust implementation is not available. Skipping Rust test.")
        return None
    
    # Import the parser module
    from paradox_savedata.parser import parse_save_file
    
    # Print which implementation is being used
    print("  Using Rust implementation")
    
    # Parse the sample file
    save_data = parse_save_file(SAMPLE_FILE)
    
    # Convert to dictionary for comparison
    result = save_data.data
    
    return result

def compare_results(python_result, rust_result):
    """Compare the results from both implementations"""
    if rust_result is None:
        print("Cannot compare: Rust implementation is not available")
        return
    
    # Convert to JSON strings for easier comparison
    python_json = json.dumps(python_result, sort_keys=True, indent=2)
    rust_json = json.dumps(rust_result, sort_keys=True, indent=2)
    
    # Check if the results are identical
    if python_json == rust_json:
        print("✅ Both implementations return identical results")
    else:
        print("❌ The implementations return different results")
        
        # Find differences
        print("\nDifferences:")
        
        # Check for keys in Python result but not in Rust result
        python_keys = set(python_result.keys())
        rust_keys = set(rust_result.keys())
        
        python_only_keys = python_keys - rust_keys
        if python_only_keys:
            print(f"Keys only in Python result: {python_only_keys}")
        
        rust_only_keys = rust_keys - python_keys
        if rust_only_keys:
            print(f"Keys only in Rust result: {rust_only_keys}")
        
        # Check for different values in common keys
        common_keys = python_keys.intersection(rust_keys)
        for key in common_keys:
            python_value = python_result[key]
            rust_value = rust_result[key]
            
            if python_value != rust_value:
                print(f"Different values for key '{key}':")
                print(f"  Python: {python_value}")
                print(f"  Rust:   {rust_value}")
    
    # Detailed structure analysis
    print("\nDetailed structure analysis:")
    
    # Check nested objects
    if "countries" in python_result and "countries" in rust_result:
        print("✓ Both implementations parsed the 'countries' nested object")
        
        # Check specific country data
        if "IRQ" in python_result["countries"] and "IRQ" in rust_result["countries"]:
            print("✓ Both implementations parsed the 'IRQ' country data")
            
            # Check nested country properties
            irq_py = python_result["countries"]["IRQ"]
            irq_rust = rust_result["countries"]["IRQ"]
            
            if "politics" in irq_py and "politics" in irq_rust:
                print("✓ Both implementations parsed the nested 'politics' object")
            else:
                print("❌ Difference in parsing nested 'politics' object")
            
            if "history" in irq_py and "history" in irq_rust:
                print("✓ Both implementations parsed the nested 'history' object")
                
                # Check deeply nested object
                if "set_politics" in irq_py["history"] and "set_politics" in irq_rust["history"]:
                    print("✓ Both implementations parsed the deeply nested 'set_politics' object")
                else:
                    print("❌ Difference in parsing deeply nested 'set_politics' object")
            else:
                print("❌ Difference in parsing nested 'history' object")
        else:
            print("❌ Difference in parsing 'IRQ' country data")
    else:
        print("❌ Difference in parsing 'countries' nested object")
    
    # Check data types
    if "treasury" in python_result["countries"]["IRQ"] and "treasury" in rust_result["countries"]["IRQ"]:
        py_treasury = python_result["countries"]["IRQ"]["treasury"]
        rust_treasury = rust_result["countries"]["IRQ"]["treasury"]
        
        print(f"Treasury data type - Python: {type(py_treasury).__name__}, Rust: {type(rust_treasury).__name__}")
        if isinstance(py_treasury, float) and isinstance(rust_treasury, float):
            print("✓ Both implementations correctly parsed float values")
        else:
            print("❌ Difference in parsing float values")
    
    if "HOI4txt" in python_result and "HOI4txt" in rust_result:
        py_bool = python_result["HOI4txt"]
        rust_bool = rust_result["HOI4txt"]
        
        print(f"Boolean data type - Python: {type(py_bool).__name__}, Rust: {type(rust_bool).__name__}")
        if isinstance(py_bool, bool) and isinstance(rust_bool, bool):
            print("✓ Both implementations correctly parsed boolean values")
        else:
            print("❌ Difference in parsing boolean values")

def main():
    print("Testing parser implementations with sample file:", SAMPLE_FILE)
    
    print("\n1. Running Python implementation...")
    python_result = get_python_implementation_result()
    
    print("\n2. Running Rust implementation...")
    rust_result = get_rust_implementation_result()
    
    print("\n3. Comparing results...")
    compare_results(python_result, rust_result)
    
    # Save results to files for manual inspection
    with open("python_result.json", "w") as f:
        json.dump(python_result, f, indent=2)
    print("\nPython result saved to python_result.json")
    
    if rust_result:
        with open("rust_result.json", "w") as f:
            json.dump(rust_result, f, indent=2)
        print("Rust result saved to rust_result.json")

if __name__ == "__main__":
    main()
