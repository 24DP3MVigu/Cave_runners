import sys
import traceback

sys.path.insert(0, r'C:\Users\A242491MV\Documents\Cave_runners\Cave_run_jekabs')

try:
    import main
    print("Main imported successfully!")
except Exception as e:
    print(f"Error importing main: {e}")
    traceback.print_exc()
