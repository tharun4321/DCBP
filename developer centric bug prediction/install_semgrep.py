import subprocess
import sys

def install_semgrep():
    """Install Semgrep using pip"""
    try:
        print("Installing Semgrep...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "semgrep"])
        print("✅ Semgrep installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Semgrep: {e}")
        return False

def check_semgrep():
    """Check if Semgrep is working"""
    try:
        result = subprocess.run(['semgrep', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Semgrep is working: {result.stdout.strip()}")
            return True
        else:
            print("❌ Semgrep is not working properly")
            return False
    except FileNotFoundError:
        print("❌ Semgrep not found")
        return False

if __name__ == "__main__":
    print("🔧 Setting up Semgrep for Bug Prediction Model...")
    
    if not check_semgrep():
        if install_semgrep():
            check_semgrep()
    
    print("\n📋 Next steps:")
    print("1. Run: python main.py")
    print("2. Load sample_vulnerable_code.py to test the analysis")
    print("3. Check the detected vulnerabilities in the results panel")
