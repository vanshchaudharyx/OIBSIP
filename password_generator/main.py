#!/usr/bin/env python3
"""
Password Generator — Main entry point.
 
Run with:
  python main.py         → launches GUI
  python main.py --cli   → launches CLI (interactive)
  python main.py --cli --length 20 --count 3  → CLI with flags
"""
import sys
import os
 
# Ensure imports resolve from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
 
 
def launch_gui():
    try:
        from gui.app import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"[GUI] tkinter not available: {e}")
        print("Falling back to CLI mode.\n")
        launch_cli()
 
 
def launch_cli():
    from cli import main as cli_main
    cli_main()
 
 
if __name__ == "__main__":
    if "--cli" in sys.argv:
        sys.argv.remove("--cli")
        launch_cli()
    else:
        launch_gui()