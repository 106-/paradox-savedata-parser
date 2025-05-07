"""
Python implementation of Paradox save data parser
"""

import io
import os
import re
from typing import Dict, List, Union, Any, Optional, Tuple, TextIO


class SaveData:
    """
    Represents parsed Paradox save data with attribute-like access
    
    Allows both dictionary-style and attribute-style access:
    - save_data["country"]["ruler"]["name"]
    - save_data.country.ruler.name
    """
    
    def __init__(self, data):
        self._data = data
        
        # Convert nested dictionaries to SaveDataNode
        for key, value in self._data.items():
            if isinstance(value, dict):
                self._data[key] = SaveDataNode(value)
            elif isinstance(value, list):
                self._data[key] = [
                    SaveDataNode(item) if isinstance(item, dict) else item
                    for item in value
                ]
    
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'SaveData' object has no attribute '{name}'")
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __contains__(self, key):
        return key in self._data
    
    def __repr__(self):
        return f"SaveData({repr(self._data)})"
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Legacy method to get data using a dot-notation path
        
        Example: save_data.get("country.ruler.name")
        """
        parts = path.split('.')
        current = self._data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            elif isinstance(current, SaveDataNode) and part in current:
                current = current[part]
            else:
                return default
                
        return current
    
    @property
    def data(self):
        """Return the raw data dictionary"""
        return self._convert_to_raw(self._data)
    
    def _convert_to_raw(self, obj):
        """Convert SaveDataNode objects back to raw dictionaries for serialization"""
        if isinstance(obj, SaveDataNode):
            return {k: self._convert_to_raw(v) for k, v in obj._data.items()}
        elif isinstance(obj, dict):
            return {k: self._convert_to_raw(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_raw(item) for item in obj]
        else:
            return obj
    
    def save(self, file_path: str):
        """
        Save the data back to a Paradox save file format
        
        Args:
            file_path: Path where to save the file
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            self._write_data(f, self._data)
    
    def _write_data(self, file: TextIO, data, indent: int = 0):
        """Write data in Paradox format"""
        if isinstance(data, SaveDataNode):
            data = data._data
            
        if isinstance(data, dict):
            for key, value in data.items():
                self._write_key_value(file, key, value, indent)
    
    def _write_key_value(self, file: TextIO, key: str, value: Any, indent: int = 0):
        """Write a key-value pair in Paradox format"""
        indentation = '\t' * indent
        
        if isinstance(value, SaveDataNode):
            value = value._data
            
        if isinstance(value, dict):
            file.write(f"{indentation}{key}={{\n")
            self._write_data(file, value, indent + 1)
            file.write(f"{indentation}}}\n")
        elif isinstance(value, list):
            file.write(f"{indentation}{key}={{\n")
            for i, item in enumerate(value):
                if isinstance(item, dict) or isinstance(item, SaveDataNode):
                    file.write(f"{indentation}\t{i}={{\n")
                    self._write_data(file, item, indent + 2)
                    file.write(f"{indentation}\t}}\n")
                else:
                    file.write(f"{indentation}\t{i}={self._format_value(item)}\n")
            file.write(f"{indentation}}}\n")
        else:
            file.write(f"{indentation}{key}={self._format_value(value)}\n")
    
    def _format_value(self, value: Any) -> str:
        """Format a value for Paradox save format"""
        if isinstance(value, bool):
            return "yes" if value else "no"
        elif isinstance(value, str):
            # Quote strings if they contain spaces or special characters
            if re.search(r'[\s{}=]', value) or not value:
                return f'"{value}"'
            return value
        else:
            return str(value)


class SaveDataNode:
    """
    Node in the SaveData tree
    
    Provides attribute-like access to dictionary keys
    """
    
    def __init__(self, data):
        self._data = data
        
        # Recursively convert nested dictionaries to SaveDataNode
        for key, value in self._data.items():
            if isinstance(value, dict):
                self._data[key] = SaveDataNode(value)
            elif isinstance(value, list):
                self._data[key] = [
                    SaveDataNode(item) if isinstance(item, dict) else item
                    for item in value
                ]
    
    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"'SaveDataNode' object has no attribute '{name}'")
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        """Allow modifying the data using dictionary access"""
        if isinstance(value, dict) and not isinstance(value, SaveDataNode):
            self._data[key] = SaveDataNode(value)
        else:
            self._data[key] = value
    
    def __setattr__(self, name, value):
        """Allow modifying the data using attribute access"""
        if name == "_data":
            super().__setattr__(name, value)
        else:
            if isinstance(value, dict) and not isinstance(value, SaveDataNode):
                self._data[name] = SaveDataNode(value)
            else:
                self._data[name] = value
    
    def __contains__(self, key):
        return key in self._data
    
    def __repr__(self):
        return f"SaveDataNode({repr(self._data)})"


def _parse_value(value_str: str) -> Union[str, int, float, bool]:
    """Parse a value string into the appropriate type"""
    value_str = value_str.strip('"')
    
    # Try to parse as number
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        # Check for boolean
        if value_str.lower() == "yes":
            return True
        elif value_str.lower() == "no":
            return False
        
        # Return as string
        return value_str


def _parse_block(lines: List[str], start_idx: int) -> Tuple[Dict[str, Any], int]:
    """Parse a block of save data"""
    result = {}
    i = start_idx
    brace_count = 0
    in_block = False
    current_key = None
    value_buffer = []
    
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
            
        # Count braces to track nested blocks
        brace_count += line.count('{') - line.count('}')
        
        # Check for end of block
        if brace_count < 0:
            break
            
        # Check for key-value pair
        if '=' in line and not in_block:
            # Split on first equals sign
            parts = line.split('=', 1)
            key = parts[0].strip()
            value = parts[1].strip()
            
            # Check if value is a block
            if value.endswith('{'):
                current_key = key
                in_block = True
                brace_count = 1  # We're in a block now
                value_buffer = []
            else:
                # Handle simple key-value
                result[key] = _parse_value(value)
                
        elif in_block:
            value_buffer.append(line)
            
            # Check if block ended
            if brace_count == 0:
                # Parse the block contents
                block_str = ' '.join(value_buffer)
                
                # Check if it's a list or dictionary
                if re.match(r'^\s*\d+\s*=', block_str):
                    # Looks like a list in disguise (keys are numeric indices)
                    list_items = re.findall(r'\d+\s*=\s*([^={}]+|\{[^}]*\})', block_str)
                    result[current_key] = [_parse_value(item.strip()) for item in list_items]
                else:
                    # Regular nested block
                    sub_block, _ = _parse_block(value_buffer, 0)
                    result[current_key] = sub_block
                    
                in_block = False
                current_key = None
                value_buffer = []
                
    return result, i


def parse_save_file(file_path: str) -> SaveData:
    """
    Parse a Paradox game save file
    
    This is a pure Python implementation that should work but will be slow
    for large files. For better performance, use the Rust implementation when available.
    
    Args:
        file_path: Path to the save file
        
    Returns:
        SaveData object with parsed data
    """
    try:
        # Check if Rust implementation is available
        from . import rust_parser
        return rust_parser.parse_save_file(file_path)
    except ImportError:
        # Fall back to Python implementation
        print("Warning: Using slower Python parser. Install Rust implementation for better performance.")
        
    # Read file content
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    
    # Parse root block
    data, _ = _parse_block(lines, 0)
    
    return SaveData(data)


def save_to_file(save_data: SaveData, file_path: str) -> None:
    """
    Save data to a Paradox save file format
    
    Args:
        save_data: SaveData object to save
        file_path: Path where to save the file
    """
    save_data.save(file_path)