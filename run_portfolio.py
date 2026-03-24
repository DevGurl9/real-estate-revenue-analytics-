from pathlib import Path
import subprocess
import sys

BASE_DIR = Path(__file__).resolve().parent

def run_script(script_path):
    print(f"\nRunning: {script_path}")
    result = subprocess.run([sys.executable, str(script_path)])
    if result.returncode != 0:
        raise RuntimeError(f"Failed: {script_path}")

def main():
    run_script(BASE_DIR / "scripts" / "generate_synthetic_data.py")
    run_script(BASE_DIR / "etl" / "load_data.py")

    print("\nPipeline completed successfully.")

if __name__ == "__main__":
    main()
