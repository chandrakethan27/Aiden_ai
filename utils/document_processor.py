"""
Document processing utilities for chunking and preprocessing
"""
import tiktoken
from typing import List, Dict, Any, Union
import re
import io
import PyPDF2
import docx


class DocumentProcessor:
    """Handles document preprocessing and chunking for long documents"""
    
    def __init__(self, chunk_size: int = 3000, chunk_overlap: int = 200):
        """
        Initialize document processor
        
        Args:
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Number of tokens to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
    
    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text"""
        return len(self.encoding.encode(text))
    
    def read_pdf(self, file_obj) -> str:
        """Extract text from PDF file object"""
        try:
            pdf_reader = PyPDF2.PdfReader(file_obj)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    def read_docx(self, file_obj) -> str:
        """Extract text from DOCX file object"""
        try:
            doc = docx.Document(file_obj)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might cause issues
        text = text.strip()
        return text
    
    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """Extract basic metadata from document"""
        lines = text.split('\n')
        words = text.split()
        
        return {
            "total_characters": len(text),
            "total_words": len(words),
            "total_lines": len(lines),
            "total_tokens": self.count_tokens(text),
        }
    
    def chunk_by_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitter
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """
        Split document into overlapping chunks
        
        Args:
            text: Input document text
            
        Returns:
            List of chunks with metadata
        """
        # Clean the text first
        text = self.clean_text(text)
        
        # Check if chunking is needed
        total_tokens = self.count_tokens(text)
        if total_tokens <= self.chunk_size:
            return [{
                "chunk_id": 0,
                "text": text,
                "tokens": total_tokens,
                "is_complete_document": True
            }]
        
        # Split into sentences for better chunk boundaries
        sentences = self.chunk_by_sentences(text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_tokens = self.count_tokens(sentence)
            
            # If adding this sentence exceeds chunk size, save current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "tokens": current_tokens,
                    "is_complete_document": False
                })
                
                # Create overlap by keeping last few sentences
                overlap_text = chunk_text
                overlap_tokens = current_tokens
                overlap_sentences = []
                
                # Build overlap from end of current chunk
                for s in reversed(current_chunk):
                    s_tokens = self.count_tokens(s)
                    if overlap_tokens - s_tokens >= self.chunk_overlap:
                        break
                    overlap_sentences.insert(0, s)
                    overlap_tokens -= s_tokens
                
                # Start new chunk with overlap
                current_chunk = overlap_sentences
                current_tokens = self.count_tokens(' '.join(current_chunk))
                chunk_id += 1
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Add the last chunk
        if current_chunk:
            chunks.append({
                "chunk_id": chunk_id,
                "text": ' '.join(current_chunk),
                "tokens": current_tokens,
                "is_complete_document": False
            })
        
        return chunks
    
    def process_document(self, text: str) -> Dict[str, Any]:
        """
        Process a document: clean, extract metadata, and create chunks
        
        Args:
            text: Input document text
            
        Returns:
            Dictionary with metadata and chunks
        """
        cleaned_text = self.clean_text(text)
        metadata = self.extract_metadata(cleaned_text)
        chunks = self.create_chunks(cleaned_text)
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "metadata": metadata,
            "chunks": chunks,
            "num_chunks": len(chunks),
            "requires_chunking": len(chunks) > 1
        }
