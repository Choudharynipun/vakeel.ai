import os
import logging
from typing import List, Dict, Any
import json
import PyPDF2
import fitz  # PyMuPDF - better PDF extraction
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class LegalKnowledgeBase:
    """Manages legal reference documents and knowledge base"""
    
    def __init__(self, data_dir: str = "legal_data"):
        self.data_dir = data_dir
        self.documents = []
        self.document_index = {}
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def load_legal_documents(self):
        """Load all legal documents from the data directory (both PDF and text files)"""
        try:
            logger.info("Loading legal knowledge base documents...")
            
            # First load PDF files
            self._load_pdf_files()
            
            # Then load any existing text files (for backward compatibility)
            self._load_text_files()
            
            logger.info(f"Legal knowledge base loaded with {len(self.documents)} documents")
            
        except Exception as e:
            logger.error(f"Failed to load legal documents: {str(e)}")
            raise
    
    def _load_pdf_files(self):
        """Load and process all PDF files from the legal_data directory"""
        try:
            pdf_files = [f for f in os.listdir(self.data_dir) if f.lower().endswith('.pdf')]
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            for pdf_file in pdf_files:
                file_path = os.path.join(self.data_dir, pdf_file)
                logger.info(f"Processing PDF: {pdf_file}")
                
                # Extract text from PDF
                content = self._extract_text_from_pdf(file_path)
                
                if content and len(content.strip()) > 100:  # Minimum content check
                    # Create document metadata
                    doc_info = self._get_pdf_metadata(pdf_file)
                    
                    document = {
                        "id": f"pdf_{pdf_file.replace('.pdf', '').replace('-', '_').replace(' ', '_').lower()}",
                        "title": doc_info["title"],
                        "content": content,
                        "category": doc_info["category"],
                        "source": doc_info["source"],
                        "filename": pdf_file,
                        "file_type": "pdf",
                        "content_length": len(content)
                    }
                    
                    self.documents.append(document)
                    self.document_index[document["id"]] = document
                    
                    logger.info(f"Successfully loaded: {doc_info['title']} ({len(content)} characters)")
                else:
                    logger.warning(f"Failed to extract sufficient content from: {pdf_file}")
                    
        except Exception as e:
            logger.error(f"Failed to load PDF files: {str(e)}")
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using multiple methods for best results"""
        content = ""
        
        try:
            # Method 1: Try PyMuPDF (fitz) first - usually better for complex PDFs
            try:
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    page_text = page.get_text()
                    if page_text.strip():
                        content += f"\n--- Page {page_num + 1} ---\n{page_text}"
                doc.close()
                
                if content.strip():
                    logger.info(f"Extracted text using PyMuPDF from {os.path.basename(file_path)}")
                    return self._clean_extracted_text(content)
            except Exception as e:
                logger.warning(f"PyMuPDF extraction failed for {file_path}: {str(e)}")
            
            # Method 2: Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    content = ""
                    
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text.strip():
                            content += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                if content.strip():
                    logger.info(f"Extracted text using PyPDF2 from {os.path.basename(file_path)}")
                    return self._clean_extracted_text(content)
            except Exception as e:
                logger.warning(f"PyPDF2 extraction failed for {file_path}: {str(e)}")
                
        except Exception as e:
            logger.error(f"All PDF extraction methods failed for {file_path}: {str(e)}")
        
        return content.strip()
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted PDF text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PDF extraction issues
        text = text.replace('', '')  # Remove null bytes
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)  # Fix hyphenated words across lines
        
        # Normalize line breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove page headers/footers patterns (customize as needed)
        text = re.sub(r'Page \d+.*?\n', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _get_pdf_metadata(self, filename: str) -> Dict[str, str]:
        """Get metadata for PDF files based on filename"""
        filename_lower = filename.lower()
        
        # Define metadata mappings based on your uploaded files
        metadata_map = {
            "muslim-women-protection-of-rights-on-divorce-act-1986": {
                "title": "The Muslim Women (Protection of Rights on Divorce) Act, 1986",
                "category": "family_law",
                "source": "Government of India"
            },
            "muslim-marriages-registration-act-1981": {
                "title": "Jammu and Kashmir Muslim Marriages Registration Act, 1981",
                "category": "family_law",
                "source": "Government of J&K"
            },
            "hindu-adoption-and-maintenance-act": {
                "title": "The Hindu Adoptions and Maintenance Act, 1956",
                "category": "family_law",
                "source": "Government of India"
            },
            "sale-of-goods-act": {
                "title": "The Sale of Goods Act, 1930",
                "category": "commercial_law",
                "source": "Government of India"
            },
            "the-hindu-succession-act1956": {
                "title": "The Hindu Succession Act, 1956",
                "category": "family_law",
                "source": "Government of India"
            },
            "limitation-act": {
                "title": "The Limitation Act, 1963",
                "category": "procedural_law",
                "source": "Government of India"
            },
            "tpa": {
                "title": "The Transfer of Property Act, 1882",
                "category": "property_law",
                "source": "Government of India"
            },
            "dissolution-of-muslim-marriage-act": {
                "title": "The Dissolution of Muslim Marriages Act, 1939",
                "category": "family_law",
                "source": "Government of India"
            },
            "evidence-act": {
                "title": "The Indian Evidence Act, 1872",
                "category": "evidence_law",
                "source": "Government of India"
            },
            "hindu-marriage-act": {
                "title": "The Hindu Marriage Act, 1955",
                "category": "family_law",
                "source": "Government of India"
            },
            "negotiable-instruments-act-1881": {
                "title": "The Negotiable Instruments Act, 1881",
                "category": "commercial_law",
                "source": "Government of India"
            },
            "contract-act": {
                "title": "The Indian Contract Act, 1872",
                "category": "contract_law",
                "source": "Government of India"
            },
            "the-bharatiya-sakshya-adhiniyam-2023": {
                "title": "The Bharatiya Sakshya Adhiniyam, 2023",
                "category": "evidence_law",
                "source": "Government of India"
            },
            "ipc-bare-act": {
                "title": "The Indian Penal Code, 1860",
                "category": "criminal_law",
                "source": "Government of India"
            },
            "the-bharatiya-nyaya-sanhita-2023": {
                "title": "The Bharatiya Nyaya Sanhita, 2023",
                "category": "criminal_law",
                "source": "Government of India"
            },
            "crpc-bare-act-1973": {
                "title": "The Code of Criminal Procedure, 1973",
                "category": "procedural_law",
                "source": "Government of India"
            },
            "bharatiya-nagarik-suraksha-sanhita-2023": {
                "title": "The Bharatiya Nagarik Suraksha Sanhita, 2023",
                "category": "procedural_law",
                "source": "Government of India"
            },
            "cpc-bare-act": {
                "title": "The Code of Civil Procedure, 1908",
                "category": "civil_law",
                "source": "Government of India"
            }
        }
        
        # Try to match filename with metadata
        for key, metadata in metadata_map.items():
            if key in filename_lower:
                return metadata
        
        # Default metadata if no match found
        clean_name = filename.replace('.pdf', '').replace('-', ' ').replace('_', ' ').title()
        return {
            "title": clean_name,
            "category": "general_law",
            "source": "Legal Document"
        }
    
    def _load_text_files(self):
        """Load existing text files for backward compatibility"""
        try:
            text_files = [f for f in os.listdir(self.data_dir) if f.lower().endswith('.txt')]
            
            for txt_file in text_files:
                file_path = os.path.join(self.data_dir, txt_file)
                content = self._load_text_file(file_path)
                
                if content:
                    # Avoid duplicates - check if we already have this content from PDF
                    doc_id = f"txt_{txt_file.replace('.txt', '').replace('-', '_').replace(' ', '_').lower()}"
                    
                    if doc_id not in self.document_index:
                        document = {
                            "id": doc_id,
                            "title": txt_file.replace('_', ' ').replace('.txt', '').title(),
                            "content": content,
                            "category": "additional_text",
                            "source": "Local Text File",
                            "filename": txt_file,
                            "file_type": "text",
                            "content_length": len(content)
                        }
                        
                        self.documents.append(document)
                        self.document_index[document["id"]] = document
                        logger.info(f"Loaded text file: {txt_file}")
                        
        except Exception as e:
            logger.error(f"Failed to load text files: {str(e)}")
    
    def _load_text_file(self, file_path: str) -> str:
        """Load content from a text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Basic content validation
            if len(content) < 100:  # Minimum content length
                logger.warning(f"File {file_path} has very little content")
                return None
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to load file {file_path}: {str(e)}")
            return None
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all loaded documents"""
        return self.documents
    
    def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """Get a specific document by ID"""
        return self.document_index.get(doc_id)
    
    def search_documents(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Search documents by content or title"""
        results = []
        query_lower = query.lower()
        
        for doc in self.documents:
            if category and doc["category"] != category:
                continue
            
            # Search in title and content
            if (query_lower in doc["title"].lower() or 
                query_lower in doc["content"].lower()):
                results.append(doc)
        
        return results
    
    def get_categories(self) -> List[str]:
        """Get all available document categories"""
        categories = set()
        for doc in self.documents:
            categories.add(doc["category"])
        return sorted(list(categories))
    
    def get_document_count(self) -> Dict[str, int]:
        """Get count of documents by category"""
        counts = {}
        for doc in self.documents:
            category = doc["category"]
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def get_documents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all documents in a specific category"""
        return [doc for doc in self.documents if doc["category"] == category]
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about the loaded documents"""
        total_docs = len(self.documents)
        total_content_length = sum(doc["content_length"] for doc in self.documents)
        
        # File type breakdown
        file_types = {}
        for doc in self.documents:
            file_type = doc.get("file_type", "unknown")
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            "total_documents": total_docs,
            "total_content_length": total_content_length,
            "average_content_length": total_content_length // total_docs if total_docs > 0 else 0,
            "categories": self.get_document_count(),
            "file_types": file_types,
            "category_list": self.get_categories()
        }
    
    def export_knowledge_base(self, output_file: str):
        """Export knowledge base to JSON file"""
        try:
            export_data = {
                "documents": self.documents,
                "metadata": {
                    "total_documents": len(self.documents),
                    "categories": self.get_categories(),
                    "document_counts": self.get_document_count(),
                    "statistics": self.get_document_stats()
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Knowledge base exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export knowledge base: {str(e)}")
            raise
    
    def create_document_summary(self) -> str:
        """Create a summary of all loaded documents"""
        stats = self.get_document_stats()
        summary = f"""
Legal Knowledge Base Summary:
============================

Total Documents: {stats['total_documents']}
Total Content: {stats['total_content_length']:,} characters
Average Document Length: {stats['average_content_length']:,} characters

Categories:
-----------
"""
        for category, count in sorted(stats['categories'].items()):
            summary += f"• {category.replace('_', ' ').title()}: {count} documents\n"
        
        summary += f"\nFile Types:\n-----------\n"
        for file_type, count in sorted(stats['file_types'].items()):
            summary += f"• {file_type.upper()}: {count} files\n"
        
        summary += f"\nDocument List:\n--------------\n"
        for doc in sorted(self.documents, key=lambda x: x['category']):
            summary += f"• {doc['title']} ({doc['category']})\n"
        
        return summary
