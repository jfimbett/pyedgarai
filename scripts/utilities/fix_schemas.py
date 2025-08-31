#!/usr/bin/env python3
"""
Fix Field definitions in schemas.py by removing extra spaces
"""

import re

def fix_schemas():
    with open('src/pyedgarai/api/schemas.py', 'r') as f:
        content = f.read()
    
    # Fix Field definitions with extra spaces
    content = re.sub(r'Field\(\s+description=', 'Field(description=', content)
    content = re.sub(r'api_token\s*:\s*str\s*=\s*Field\(\s*description=', 'api_token: str = Field(description=', content)
    content = re.sub(r':\s*str\s*=\s*Field\(\s+description=', ': str = Field(description=', content)
    content = re.sub(r':\s*int\s*=\s*Field\(\s+description=', ': int = Field(description=', content)
    content = re.sub(r':\s*float\s*=\s*Field\(\s+description=', ': float = Field(description=', content)
    content = re.sub(r':\s*List\[.*?\]\s*=\s*Field\(\s+description=', lambda m: m.group(0).replace('Field( description=', 'Field(description='), content)
    content = re.sub(r':\s*Dict\[.*?\]\s*=\s*Field\(\s+description=', lambda m: m.group(0).replace('Field( description=', 'Field(description='), content)
    content = re.sub(r':\s*Optional\[.*?\]\s*=\s*Field\(\s+description=', lambda m: m.group(0).replace('Field( description=', 'Field(description='), content)
    
    # Fix spacing around Field parameters  
    content = re.sub(r',\s+example\s*=', ', example=', content)
    content = re.sub(r',\s+default\s*=', ', default=', content)
    
    with open('src/pyedgarai/api/schemas.py', 'w') as f:
        f.write(content)
    
    print("Fixed Field definitions in schemas.py")

if __name__ == "__main__":
    fix_schemas()
