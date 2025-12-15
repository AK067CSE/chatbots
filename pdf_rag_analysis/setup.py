#!/usr/bin/env python3
"""
Setup script for PDF Analysis system
Handles dependency installation and configuration
"""

import os
import sys
from pathlib import Path
import subprocess


def setup_environment():
    """Setup project environment"""
    print("\n" + "="*60)
    print("PDF ANALYSIS SYSTEM - SETUP")
    print("="*60 + "\n")
    
    project_root = Path(__file__).parent
    
    print("[1/5] Creating directories...")
    directories = ['data', 'reports', 'chroma_db', 'src']
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        print(f"  ✓ {directory}/")
    
    print("\n[2/5] Checking Python version...")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info >= (3, 8):
        print(f"  ✓ Python {python_version} (OK)")
    else:
        print(f"  ✗ Python {python_version} (requires 3.8+)")
        return False
    
    print("\n[3/5] Installing dependencies...")
    requirements_file = project_root / 'requirements.txt'
    
    try:
        subprocess.check_call(
            [sys.executable, '-m', 'pip', 'install', '-q', '-r', str(requirements_file)]
        )
        print("  ✓ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to install dependencies: {e}")
        return False
    
    print("\n[4/5] Setting up environment configuration...")
    env_file = project_root / '.env'
    env_example = project_root / '.env.example'
    
    if not env_file.exists() and env_example.exists():
        env_file.write_text(env_example.read_text())
        print("  ✓ .env file created from template")
        print("  ⚠ Please update .env with your API keys!")
    else:
        print("  ✓ .env already configured")
    
    print("\n[5/5] Verifying setup...")
    
    checks = [
        ('src/config.py', 'Configuration module'),
        ('data/', 'Data directory'),
        ('reports/', 'Reports directory'),
    ]
    
    all_good = True
    for check_path, description in checks:
        full_path = project_root / check_path
        if full_path.exists():
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_good = False
    
    if all_good:
        print("\n" + "="*60)
        print("SETUP COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nNext steps:")
        print("1. Update .env with your OpenAI API key")
        print("2. Place PDF files in the 'data/' directory")
        print("3. Run: python main.py --mode pipeline")
        print("="*60 + "\n")
        return True
    else:
        print("\n" + "="*60)
        print("SETUP INCOMPLETE - Some checks failed")
        print("="*60 + "\n")
        return False


def verify_installation():
    """Verify all dependencies are installed correctly"""
    print("\nVerifying installation...")
    
    required_packages = [
        'pypdf',
        'chromadb',
        'langchain',
        'langchain_openai',
        'sentence_transformers',
        'openai',
        'pandas',
        'openpyxl',
        'pydantic',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('_', '-').replace('-', '_'))
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        return False
    
    print("\n✓ All dependencies verified!")
    return True


def main():
    """Main setup entry point"""
    try:
        success = setup_environment()
        
        if success:
            if verify_installation():
                print("\n✓ Setup verification passed!")
                return 0
            else:
                print("\n✗ Some dependencies are missing")
                print("Run: pip install -r requirements.txt")
                return 1
        else:
            print("\n✗ Setup failed")
            return 1
            
    except Exception as e:
        print(f"\n✗ Setup error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
