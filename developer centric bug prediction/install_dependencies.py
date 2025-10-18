import subprocess
import sys

def install_requirements():
    """Install required dependencies"""
    requirements = [
        'semgrep>=1.45.0',
        'matplotlib>=3.5.0',
        'pandas>=1.3.0',
        'seaborn>=0.11.0'
    ]
    
    for requirement in requirements:
        try:
            print(f"Installing {requirement}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', requirement])
            print(f"✓ {requirement} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {requirement}: {e}")
    
    print("\nInstallation complete! You can now run the application with: python main.py")

if __name__ == "__main__":
    install_requirements()
