import pdfplumber
import logging

class DocumentProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF file"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            self.logger.info(f"Extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            self.logger.error(f"Error extracting PDF: {e}")
            return ""
    
    def extract_tables_from_pdf(self, file_path):
        """Extract tables from PDF"""
        try:
            tables = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
            
            self.logger.info(f"Extracted {len(tables)} tables from PDF")
            return tables
        except Exception as e:
            self.logger.error(f"Error extracting tables: {e}")
            return []