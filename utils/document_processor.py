import os
import logging
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles extraction of text from various document formats"""
    
    def __init__(self):
        self.supported_formats = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required dependencies are available"""
        try:
            # Test PyMuPDF
            fitz.open()
            logger.info("PyMuPDF (PDF processing) is available")
        except Exception as e:
            logger.warning(f"PyMuPDF may have issues: {str(e)}")
        
        try:
            # Test Tesseract
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
        except Exception as e:
            logger.warning(f"Tesseract OCR not available: {str(e)}")
    
    def extract_text(self, file_path: str) -> Optional[str]:
        """Extract text from document based on file extension"""
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext not in self.supported_formats:
            logger.error(f"Unsupported file format: {file_ext}")
            return None
        
        try:
            if file_ext == '.pdf':
                return self._extract_from_pdf(file_path)
            else:
                return self._extract_from_image(file_path)
                
        except Exception as e:
            logger.error(f"Text extraction failed for {file_path}: {str(e)}")
            return None
    
    def _extract_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract text from PDF file"""
        try:
            text_content = []
            
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                
                # Try to extract text directly
                page_text = page.get_text()
                
                if page_text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                else:
                    # If no text found, try OCR on page image
                    logger.info(f"No text found on page {page_num + 1}, attempting OCR...")
                    page_image = self._pdf_page_to_image(page)
                    if page_image:
                        ocr_text = self._ocr_image(page_image)
                        if ocr_text.strip():
                            text_content.append(f"--- Page {page_num + 1} (OCR) ---\n{ocr_text}")
            
            doc.close()
            
            extracted_text = '\n\n'.join(text_content)
            
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
            return extracted_text if extracted_text.strip() else None
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {str(e)}")
            return None
    
    def _pdf_page_to_image(self, page) -> Optional[np.ndarray]:
        """Convert PDF page to image for OCR"""
        try:
            # Render page as image
            mat = fitz.Matrix(2, 2)  # 2x zoom for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.pil_tobytes(format="PNG")
            
            # Convert to PIL Image then to numpy array
            pil_image = Image.open(io.BytesIO(img_data))
            return np.array(pil_image)
            
        except Exception as e:
            logger.error(f"Failed to convert PDF page to image: {str(e)}")
            return None
    
    def _extract_from_image(self, image_path: str) -> Optional[str]:
        """Extract text from image file using OCR"""
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not load image: {image_path}")
                return None
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image(image)
            
            # Perform OCR
            extracted_text = self._ocr_image(processed_image)
            
            logger.info(f"Extracted {len(extracted_text)} characters from image")
            return extracted_text if extracted_text.strip() else None
            
        except Exception as e:
            logger.error(f"Image text extraction failed: {str(e)}")
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image to improve OCR accuracy"""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Resize image if too small
            height, width = gray.shape
            if height < 300 or width < 300:
                scale_factor = max(300/height, 300/width)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Noise removal
            kernel = np.ones((1, 1), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            binary = cv2.medianBlur(binary, 3)
            
            return binary
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            return image
    
    def _ocr_image(self, image: np.ndarray) -> str:
        """Perform OCR on preprocessed image"""
        try:
            # Configure Tesseract
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:!?"\'()[]{}/-_+*=<>@#$%&\|^~` \n\t'
            
            # Perform OCR
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Clean up text
            text = self._clean_extracted_text(text)
            
            return text
            
        except Exception as e:
            logger.error(f"OCR failed: {str(e)}")
            return ""
    
    def _clean_extracted_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Replace multiple whitespaces with single space
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive line breaks
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def get_document_info(self, file_path: str) -> dict:
        """Get basic information about the document"""
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        file_ext = os.path.splitext(file_path)[1].lower()
        file_size = os.path.getsize(file_path)
        
        info = {
            "filename": os.path.basename(file_path),
            "extension": file_ext,
            "size_bytes": file_size,
            "size_mb": round(file_size / (1024 * 1024), 2),
            "supported": file_ext in self.supported_formats
        }
        
        try:
            if file_ext == '.pdf':
                doc = fitz.open(file_path)
                info["page_count"] = doc.page_count
                info["metadata"] = doc.metadata
                doc.close()
            elif file_ext in {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}:
                image = Image.open(file_path)
                info["dimensions"] = image.size
                info["mode"] = image.mode
                image.close()
                
        except Exception as e:
            info["error"] = str(e)
        
        return info