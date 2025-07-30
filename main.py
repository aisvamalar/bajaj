#!/usr/bin/env python3
"""
Simple launcher for PDF processing and Q&A system.
Just place doc1.pdf in the data/ directory and run this script.
"""

import os
import sys

def main():
    # Check if doc1.pdf exists
    pdf_path = "data/doc1.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found!")
        print("\n Instructions:")
        print("1. Place your PDF file in the data/ directory")
        print("2. Rename it to 'doc1.pdf'")
        print("3. Run this script again")
        print(f"\nExample: cp your_document.pdf data/doc1.pdf")
        return
    
    # Import and run the main processing script
    try:
        from document_processor import main as process_and_qa
        process_and_qa()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 