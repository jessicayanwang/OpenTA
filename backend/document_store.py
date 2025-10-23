"""
Document ingestion and chunking pipeline
"""
import re
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    """Represents a chunk of a document with metadata"""
    text: str
    source: str  # e.g., "syllabus.txt", "assignment1.txt"
    section: str  # e.g., "Late Policy", "Assignment 1 - Question 2"
    chunk_id: str
    
class DocumentStore:
    """Manages course documents and chunking"""
    
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        
    def ingest_document(self, text: str, source: str):
        """
        Ingest a document and chunk it by sections.
        Simple chunking: split by double newlines and headers.
        """
        # Split by sections (headers marked with ## or all caps lines)
        sections = self._split_into_sections(text, source)
        
        for section_name, section_text in sections:
            # Create chunks (max 500 chars for simplicity)
            section_chunks = self._chunk_text(section_text, max_length=500)
            
            for i, chunk_text in enumerate(section_chunks):
                chunk_id = f"{source}::{section_name}::{i}"
                chunk = DocumentChunk(
                    text=chunk_text,
                    source=source,
                    section=section_name,
                    chunk_id=chunk_id
                )
                self.chunks.append(chunk)
    
    def _split_into_sections(self, text: str, source: str) -> List[tuple]:
        """Split document into sections based on headers"""
        sections = []
        lines = text.split('\n')
        current_section = "Introduction"
        current_text = []
        
        for line in lines:
            # Check if line is a header (starts with ## or is all caps)
            if line.startswith('##') or (line.strip() and line.strip().isupper() and len(line.strip()) > 3):
                # Save previous section
                if current_text:
                    sections.append((current_section, '\n'.join(current_text)))
                
                # Start new section
                current_section = line.replace('##', '').strip()
                current_text = []
            else:
                current_text.append(line)
        
        # Add last section
        if current_text:
            sections.append((current_section, '\n'.join(current_text)))
        
        return sections
    
    def _chunk_text(self, text: str, max_length: int = 500) -> List[str]:
        """Split text into chunks of max_length"""
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = re.split(r'[.!?]\s+', text)
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_all_chunks(self) -> List[DocumentChunk]:
        """Return all document chunks"""
        return self.chunks
