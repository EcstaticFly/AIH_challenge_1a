
"""
Entry point for Production PDF Outline Extractor
"""
import sys
import os


sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pdf_extractor import process_pdfs

if __name__ == "__main__":
    process_pdfs()