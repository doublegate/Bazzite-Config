#!/usr/bin/env python3
"""
Test script to validate kernel parameter deduplication fix
"""
import re
import sys

def clean_kernel_params(current_cmdline: str, new_params: list) -> str:
    """Clean and deduplicate kernel parameters properly"""
    # Parse existing parameters using proper regex to handle quoted values
    existing_params = re.findall(r'(?:[^\s"]|"(?:\\.|[^"])*")+', current_cmdline.strip())
    param_dict = {}
    
    # Build parameter dictionary from existing parameters
    for param in existing_params:
        if '=' in param:
            key, value = param.split('=', 1)
            # Remove surrounding quotes from values if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            param_dict[key] = value
        else:
            param_dict[param] = None
    
    # Update/add new parameters (this replaces duplicates)
    for param in new_params:
        param = param.strip()
        if not param:
            continue
            
        if '=' in param:
            key, value = param.split('=', 1)
            param_dict[key] = value
        else:
            param_dict[param] = None
    
    # Rebuild clean parameter string
    clean_params = []
    for key, value in param_dict.items():
        if value is not None:
            clean_params.append(f"{key}={value}")
        else:
            clean_params.append(key)
    
    return ' '.join(clean_params)

def test_kernel_param_deduplication():
    """Test cases to validate the fix"""
    print("Testing kernel parameter deduplication fix...")
    
    # Test Case 1: Boot log scenario - mitigations duplicated
    current = "quiet splash mitigations=auto mitigations=off mitigations=off processor.max_cstate=3 processor.max_cstate=3"
    new_params = ["mitigations=off", "processor.max_cstate=3"]
    result = clean_kernel_params(current, new_params)
    expected = "quiet splash mitigations=off processor.max_cstate=3"
    
    print(f"\nTest 1 - Boot log duplication scenario:")
    print(f"Input:    {current}")
    print(f"Adding:   {new_params}")
    print(f"Result:   {result}")
    print(f"Expected: {expected}")
    print(f"✓ PASS" if result == expected else f"✗ FAIL")
    
    # Test Case 2: New parameter addition
    current = "quiet splash"
    new_params = ["mitigations=off", "processor.max_cstate=1"]
    result = clean_kernel_params(current, new_params)
    expected = "quiet splash mitigations=off processor.max_cstate=1"
    
    print(f"\nTest 2 - New parameter addition:")
    print(f"Input:    {current}")
    print(f"Adding:   {new_params}")
    print(f"Result:   {result}")
    print(f"Expected: {expected}")
    print(f"✓ PASS" if result == expected else f"✗ FAIL")
    
    # Test Case 3: Parameter value replacement
    current = "quiet splash mitigations=auto processor.max_cstate=3"
    new_params = ["mitigations=off", "processor.max_cstate=1"]
    result = clean_kernel_params(current, new_params)
    expected = "quiet splash mitigations=off processor.max_cstate=1"
    
    print(f"\nTest 3 - Parameter value replacement:")
    print(f"Input:    {current}")
    print(f"Adding:   {new_params}")
    print(f"Result:   {result}")
    print(f"Expected: {expected}")
    print(f"✓ PASS" if result == expected else f"✗ FAIL")
    
    # Test Case 4: Complex quoted parameters
    current = 'quiet splash root="UUID=12345" mitigations=auto'
    new_params = ["mitigations=off", "intel_idle.max_cstate=1"]
    result = clean_kernel_params(current, new_params)
    expected = 'quiet splash root=UUID=12345 mitigations=off intel_idle.max_cstate=1'
    
    print(f"\nTest 4 - Complex parameters with quotes:")
    print(f"Input:    {current}")
    print(f"Adding:   {new_params}")
    print(f"Result:   {result}")
    print(f"Expected: {expected}")
    print(f"✓ PASS" if result == expected else f"✗ FAIL")
    
    print("\n" + "="*60)
    print("Kernel parameter deduplication fix validation complete!")
    print("All test cases simulate the exact boot log scenarios.")
    print("="*60)

if __name__ == "__main__":
    test_kernel_param_deduplication()