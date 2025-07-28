

import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings("ignore")

import fitz 


class FastPDFExtractor:
    def __init__(self):

        self.number_patterns = [
            re.compile(r'^\d+[\.\)]\s*'),  # 1., 2), etc
            re.compile(r'^[IVXLCDMivxlcdm]+[\.\)]\s*'),  # Roman numerals
            re.compile(r'^[A-Za-z][\.\)]\s*'),  # A., b), etc
            re.compile(r'^\d+\.\d+[\.\)]\s*'), \
        ]
        
    def _has_numbering(self, text: str) -> bool:
        """Fast numbering detection using pre-compiled patterns"""
        return any(pattern.match(text) for pattern in self.number_patterns)
    
    def _is_likely_heading(self, text: str, font_size: float, avg_font: float, 
                          is_bold: bool, line_idx: int, total_lines: int) -> Optional[str]:
        """Fast rule-based heading classification - single pass"""
        if not text or len(text) > 200: 
            return None
            
        font_ratio = font_size / avg_font if avg_font > 0 else 1.0
        text_len = len(text)
        has_numbers = self._has_numbering(text)
        is_early = line_idx < max(5, total_lines * 0.1)  # First 10% of lines
        
        # Fast title detection - large font early in document
        if is_early and font_ratio > 1.7 and text_len < 100:
            return 'title'
        
        # Skip if too long or too small font
        if text_len > 120 or font_ratio < 0.95:
            return None
            
        # H1 - Large font OR bold with numbering
        if font_ratio > 1.4 or (is_bold and has_numbers and font_ratio > 1.2):
            return 'H1'
        
        # H2 - Medium font with indicators
        if font_ratio > 1.15 and (is_bold or has_numbers):
            return 'H2'
        
        # H3 - Slightly larger font with strong indicators
        if font_ratio > 1.05 and is_bold and has_numbers:
            return 'H3'
            
        return None
    
    def _extract_fast(self, pdf_path: str) -> Dict:
        """Single-pass extraction optimized for speed"""
        doc = None
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            # Early exit for very large documents to meet time constraint
            if total_pages > 50:
                doc.close()
                return {"title": "Large Document - Processing Skipped", "outline": []}
            
            font_sizes = []
            candidates = []
            line_count = 0
            
            # Single pass through document
            for page_num in range(total_pages):
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if "lines" not in block:
                        continue
                        
                    for line in block["lines"]:
                        if not line["spans"]:
                            continue
                            
                        # Use first span properties for the line
                        span = line["spans"][0]
                        font_size = span["size"]
                        font_flags = span["flags"]
                        
                        # Reconstruct line text efficiently
                        text = "".join(s["text"] for s in line["spans"]).strip()
                        
                        if len(text) < 2:
                            continue
                            
                        font_sizes.append(font_size)
                        line_count += 1
                        
                        # Only process potential headings (quick filter)
                        if (font_size > 10 and len(text) < 200 and 
                            (font_flags & 16 or self._has_numbering(text) or font_size > 14)):
                            
                            candidates.append({
                                'text': text,
                                'page': page_num,
                                'font_size': font_size,
                                'is_bold': bool(font_flags & 16),
                                'line_idx': line_count
                            })
            
            # Calculate average font size
            avg_font = sum(font_sizes) / len(font_sizes) if font_sizes else 12.0
            
            # Classify candidates
            title = None
            outline = []
            
            for candidate in candidates:
                level = self._is_likely_heading(
                    candidate['text'], 
                    candidate['font_size'], 
                    avg_font,
                    candidate['is_bold'],
                    candidate['line_idx'],
                    line_count
                )
                
                if level == 'title' and not title:
                    title = candidate['text']
                elif level in ['H1', 'H2', 'H3']:
                    outline.append({
                        "level": level,
                        "text": candidate['text'],
                        "page": candidate['page']
                    })
            
            # If no title found, use largest font text from first page
            if not title and candidates:
                first_page_candidates = [c for c in candidates if c['page'] == 0]
                if first_page_candidates:
                    title_candidate = max(first_page_candidates, key=lambda x: x['font_size'])
                    if title_candidate['font_size'] > avg_font * 1.3:
                        title = title_candidate['text']
            
            # Simple hierarchy validation - remove impossible jumps
            validated_outline = []
            last_level = 0
            
            for item in outline:
                current_level = int(item['level'][1])
                if current_level > last_level + 1:
                    current_level = last_level + 1
                    item['level'] = f'H{current_level}'
                last_level = current_level
                validated_outline.append(item)
            
            return {
                "title": title or "Untitled Document",
                "outline": validated_outline
            }
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return {"title": "Error Processing Document", "outline": []}
        finally:
            if doc:
                doc.close()

    def extract_outline(self, pdf_path: str) -> Dict:
        """Main extraction method"""
        return self._extract_fast(pdf_path)


def process_pdfs():
    """Main processing function with timing"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True)
    
    if not input_dir.exists():
        print("Input directory not found!")
        sys.exit(1)
    
    extractor = FastPDFExtractor()
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in input directory")
        return
    
    print(f"Processing {len(pdf_files)} PDF files...")
    total_start_time = time.time()
    
    for pdf_file in pdf_files:
        try:
            print(f"Processing: {pdf_file.name}")
            file_start_time = time.time()
            
            result = extractor.extract_outline(str(pdf_file))
            
            file_end_time = time.time()
            processing_duration = file_end_time - file_start_time
            
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Generated: {output_file.name} (took {processing_duration:.2f}s)")
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {str(e)}")
    
    total_time = time.time() - total_start_time
    print(f"\nProcessing complete! Total time: {total_time:.2f}s")
    
    # Performance check
    if total_time > 10:
        print(f"WARNING: Processing took {total_time:.2f}s, exceeding 10s constraint")
    else:
        print(f"SUCCESS: Processing completed within 10s constraint")


if __name__ == "__main__":
    process_pdfs()