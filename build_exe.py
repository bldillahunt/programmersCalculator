import subprocess
import sys

# This forces Python to install the compiler internally, bypassing your broken terminal PATH
subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# This tells Python to compile your actual project file
import PyInstaller.__main__
PyInstaller.__main__.run([
    'programmersCalculator.py', # <-- Change this to your main script's filename
    '--onefile',
    '--noconsole'            # Delete this line if your app is a command-line/text-only tool
])
