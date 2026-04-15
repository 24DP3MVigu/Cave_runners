import sys
sys.path.insert(0, r'C:\Users\A242491MV\Documents\Cave_runners\Cave_run_jekabs')

print("1. Testing direct imports...")
print("  - Importing iestatijumi...")
import iestatijumi
print("    OK")

print("  - Importing monstri...")
import monstri
print("    OK")

print("2. Testing imports in a chain like main...")
import importlib
import tempfile
import os

test_code = '''
from iestatijumi import BASE_DIR
from monstri import load_monster
from prieksmeti import show_items_catalog
'''

print("  - Executing test code...")
exec(test_code)
print("    OK")

print("\nAll imports successful!")
