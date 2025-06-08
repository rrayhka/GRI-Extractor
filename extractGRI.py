"""
GRI Disclosure Extraction System

This module extracts GRI (Global Reporting Initiative) disclosures from 
Sustainability Report PDFs using multiple detection strategies:
1. Pattern matching for GRI section headers
2. TF-IDF similarity search as fallback
3. Optional Groq LLM heuristic as last resort

Author: Mohammad Habibul Akhyar
Date: 8 June 2025
"""

import re
import os
import logging
from typing import Dict, List, Tuple, Optional, Any
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from fuzzywuzzy import fuzz, process
from groq import Groq
import json
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# GRI Dicts
GRI_Dicts = {
    "GRI 2: General Disclosures 2021": {
        "2-1": "Organizational details",
        "2-2": "Entities included in the organization’s sustainability reporting",
        "2-3": "Reporting period, frequency and contact point",
        "2-4": "Restatements of information",
        "2-5": "External assurance",
        "2-6": "Activities, value chain and other business relationships",
        "2-7": "Employees",
        "2-8": "Workers who are not employees",
        "2-9": "Governance structure and composition",
        "2-10": "Nomination and selection of the highest governance body",
        "2-11": "Chair of the highest governance body",
        "2-12": "Role of the highest governance body in overseeing the management of impacts",
        "2-13": "Delegating authority for managing impacts",
        "2-14": "Role of the highest governance body in sustainability reporting",
        "2-15": "Conflicts of interest",
        "2-16": "Communication of critical concerns",
        "2-17": "Collective knowledge of the highest governance body",
        "2-18": "Evaluation of the performance of the highest governance body",
        "2-19": "Remuneration policies",
        "2-20": "Process to determine remuneration",
        "2-21": "Annual total compensation ratio",
        "2-22": "Statement on sustainable development strategy",
        "2-23": "Policy commitments",
        "2-24": "Embedding policy commitments",
        "2-25": "Processes to remediate negative impacts",
        "2-26": "Mechanisms for seeking advice and raising concerns",
        "2-27": "Compliance with laws and regulations",
        "2-28": "Membership associations",
        "2-29": "Approach to stakeholder engagement",
        "2-30": "Collective bargaining agreements"
    },
    "GRI 3: Material Topics 2021": {
        "3-1": "Process to determine material topics",
        "3-2": "List of material topics",
        "3-3": "Management of material topics"
    },
    "GRI 101: Biodiversity 2024": {
        "101-1": "Policies to halt and reverse biodiversity loss",
        "101-2": "Management of biodiversity impacts",
        "101-3": "Access and benefit-sharing",
        "101-4": "Identification of biodiversity impacts",
        "101-5": "Locations with biodiversity impacts",
        "101-6": "Direct drivers of biodiversity loss",
        "101-7": "Changes to the state of biodiversity",
        "101-8": "Ecosystem services"
    },
    "GRI 201: Economic Performance 2016": {
        "201-1": "Direct economic value generated and distributed",
        "201-2": "Financial implications and other risks and opportunities due to climate change",
        "201-3": "Defined benefit plan obligations and other retirement plans",
        "201-4": "Financial assistance received from government"
    },
    "GRI 202: Market Presence 2016": {
        "202-1": "Ratios of standard entry level wage by gender compared to local minimum wage",
        "202-2": "Proportion of senior management hired from the local community"
    },
    "GRI 203: Indirect Economic Impacts 2016": {
        "203-1": "Infrastructure investments and services supported",
        "203-2": "Significant indirect economic impacts"
    }, 
    "GRI 204: Procurement Practices 2016": {
        "204-1": "Proportion of spending on local suppliers"
    },
    "GRI 205: Anti-Corruption 2016": {
        "205-1": "Operations assessed for risks related to corruption",
        "205-2": "Communication and training about anti-corruption policies and procedures",
        "205-3": "Confirmed incidents of corruption and actions taken"
    },
    "GRI 206: Anti-Competitive Behavior 2016": {
        "206-1": "Legal actions for anti-competitive behavior, anti-trust, and monopoly practices"
    },
    "GRI 207: Tax 2019": {
        "207-1": "Approach to tax",
        "207-2": "Tax governance, control, and risk management",
        "207-3": "Stakeholder engagement and management of concerns related to tax",
        "207-4": "Country-by-country reporting"
    },
    "GRI 301: Materials 2016": {
        "301-1": "Materials used by weight or volume",
        "301-2": "Recycled input materials used",
        "301-3": "Reclaimed products and their packaging materials"
    },
    "GRI 302: Energy 2016": {
        "302-1": "Energy consumption within the organization",
        "302-2": "Energy consumption outside of the organization",
        "302-3": "Energy intensity",
        "302-4": "Reduction of energy consumption",
        "302-5": "Reduction in energy requirements of products and services"
    },
    "GRI 303: Water and Effluents 2018": {
        "303-1": "Interactions with water as a shared resource",
        "303-2": "Management of water discharge-related impacts",
        "303-3": "Water withdrawal",
        "303-4": "Water discharge",
        "303-5": "Water consumption"
    },
    "GRI 304: Biodiversity 2016": {
        "304-1": "Operational sites owned, leased, managed in, or adjacent to, protected areas and areas of high biodiversity value outside protected areas",
        "304-2": "Significant impacts of activities, products, and services on biodiversity",
        "304-3": "Habitat protection and restoration",
        "304-4": "IUCN Red List species and national conservation list species with habitats in areas affected by operations"
    },
    "GRI 305: Emissions 2016": {
        "305-1": "Direct (Scope 1) GHG emissions",
        "305-2": "Energy indirect (Scope 2) GHG emissions",
        "305-3": "Other indirect (Scope 3) GHG emissions",
        "305-4": "GHG emissions intensity",
        "305-5": "Reduction of GHG emissions",
        "305-6": "Emissions of ozone-depleting substances (ODS)",
        "305-7": "Nitrogen oxides (NOX), sulfur oxides (SOX), and other significant air emissions"  
    },
    "GRI 306: Effluents and Waste 2016": {
        # "306-1": "Water discharge by quality and destination",
        # "306-2": "Waste by type and disposal method",
        "306-3": "Significant spills",
        # "306-4": "Transport of hazardous waste",
        # "306-5": "Water bodies affected by water discharges and/or runoff"
    },
    "GRI 306: Waste 2020": {
        "306-1": "Waste generation and significant waste-related impacts",
        "306-2": "Management of significant waste-related impacts",
        "306-3": "Waste generated",
        "306-4": "Waste diverted from disposal",
        "306-5": "Waste directed to disposal"
    },
    "GRI 308: Supplier Environmental Assessment 2016": {
        "308-1": "New suppliers that were screened using environmental criteria",
        "308-2": "Negative environmental impacts in the supply chain and actions taken"
    },
    "GRI 401: Employment 2016": {
        "401-1": "New employee hires and employee turnover",
        "401-2": "Benefits provided to full-time employees that are not provided to temporary or part-time employees",
        "401-3": "Parental leave"
    },
    "GRI 402: Labor/Management Relations 2016": {
        "402-1": "Minimum notice periods regarding operational changes"
    },
    "GRI 403: Occupational Health and Safety 2018": {
        "403-1": "Occupational health and safety management system",
        "403-2": "Hazard identification, risk assessment, and incident investigation",
        "403-3": "Occupational health services",
        "403-4": "Worker participation, consultation, and communication",
        "403-5": "Worker training on occupational health and safety",
        "403-6": "Promotion of worker health",
        "403-7": "Prevention and mitigation of occupational health and safety impacts directly linked by business relationships",
        "403-8": "Workers covered by an occupational health and safety management system",
        "403-9": "Work-related injuries",
        "403-10": "Work-related ill health",
    },
    "GRI 404: Training and Education 2016": {
        "404-1": "Average hours of training per year per employee",
        "404-2": "Programs for upgrading employee skills and transition assistance programs",
        "404-3": "Percentage of employees receiving regular performance and career development reviews"
    },
    "GRI 405: Diversity and Equal Opportunity 2016": {
        "405-1": "Diversity of governance bodies and employees",
        "405-2": "Ratio of basic salary and remuneration of women to men",
        "405-3": "Parental leave"
    },
    "GRI 406: Non-discrimination 2016": {
        "406-1": "Incidents of discrimination and corrective actions taken"
    },
    "GRI 407: Freedom of Association and Collective Bargaining 2016": {
        "407-1": "Operations and suppliers in which the right to freedom of association and collective bargaining may be at risk"
    },
    "GRI 408: Child Labor 2016"	: {
        "408-1": "Operations and suppliers at significant risk for incidents of child labor"
    },
    "GRI 409: Forced or Compulsory Labor 2016": {
        "409-1": "Operations and suppliers at significant risk for incidents of forced or compulsory labor"
    },			
    "GRI 410: Security Practices 2016": {
        "410-1": "Security personnel trained in human rights policies or procedures"
    },
    "GRI 411: Rights of Indigenous Peoples 2016": {
        "411-1": "Operations and suppliers in which the rights of indigenous peoples may be at risk"
    },
    "GRI 412: Human Rights Assessment 2016": {
        "412-1": "Operations that have been subject to human rights reviews or impact assessments",
        "412-2": "Employee training on human rights policies or procedures",
        "412-3": "Significant investment agreements and contracts that include human rights clauses or that underwent human rights screening"
    },
    "GRI 413: Local Communities 2016": {
        "413-1": "Operations with local community engagement, impact assessments, and development programs",
        "413-2": "Operations with significant actual and potential negative impacts on local communities"
    },
    "GRI 414: Supplier Social Assessment 2016": {
        "414-1": "New suppliers that were screened using social criteria",
        "414-2": "Negative social impacts in the supply chain and actions taken"
    },
    "GRI 415: Public Policy 2016": {
        "415-1": "Political contributions"
    },
    "GRI 416: Customer Health and Safety 2016": {
        "416-1": "Assessment of the health and safety impacts of product and service categories",
        "416-2": "Incidents of non-compliance concerning the health and safety impacts of products and services"
    },
    "GRI 417: Marketing and Labeling 2016": {
        "417-1": "Requirements for product and service information and labeling",
        "417-2": "Incidents of non-compliance concerning product and service information and labeling",
        "417-3": "Incidents of non-compliance concerning marketing communications"
    },
    "GRI 418: Customer Privacy 2016": {
        "418-1": "Substantiated complaints concerning breaches of customer privacy and losses of customer data"
    },
}

class GRIExtractor:
    """
    Main class for extracting GRI disclosures from sustainability report PDFs.
    
    Uses a multi-strategy approach:
    1. Pattern matching for GRI section detection
    2. TF-IDF similarity search as fallback
    3. Optional Groq LLM for edge cases
    """
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Initialize the GRI extractor.
        
        Args:
            groq_api_key: Optional API key for Groq LLM fallback
        """
        self.gri_dicts = GRI_Dicts
        self.groq_client = None
        api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        if api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Groq client: {e}")
        else:
            logger.warning("No Groq API key provided, LLM detection will be disabled")
        
        # GRI section detection patterns (English and Indonesian)
        self.gri_patterns = [
            r"GRI\s+(?:Content\s+)?Index",
            r"GRI\s+\d+:\s+[A-Za-z\s]+\d{4}",
            r"Global\s+Reporting\s+Initiative",
            r"GRI\s+Standards?\s+Index",
            r"Sustainability\s+Reporting\s+Standards?",
            r"Indeks\s+GRI",  # Indonesian
            r"Standar\s+Pelaporan\s+Berkelanjutan",  # Indonesian
            r"GRI\s+Disclosure",
            r"GRI\s+Reference"
        ]
        
        # Compile patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.gri_patterns]
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from PDF pages.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing page number and text
        """
        try:
            reader = PdfReader(pdf_path)
            pages_data = []
            
            logger.info(f"Processing PDF with {len(reader.pages)} pages")
            
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    # Clean and normalize text
                    text = self._clean_text(text)
                    pages_data.append({
                        'page_num': page_num + 1,
                        'text': text,
                        'char_count': len(text)
                    })
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    pages_data.append({
                        'page_num': page_num + 1,
                        'text': "",
                        'char_count': 0
                    })
            
            return pages_data
            
        except Exception as e:
            logger.error(f"Failed to read PDF {pdf_path}: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted PDF text.
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()
        
        # Fix common PDF extraction issues
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)  # Fix broken words
        text = re.sub(r'([a-z])\s+([A-Z])', r'\1\n\2', text)  # Add line breaks before capitals
        
        return text
    
    def detect_gri_section_pattern_matching(self, pages_data: List[Dict[str, Any]]) -> Optional[int]:
        """
        Detect GRI section start using pattern matching.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            Page number where GRI section starts (1-indexed), or None if not found
        """
        # Focus on last 30-40% of pages
        total_pages = len(pages_data)
        start_search_page = max(0, int(total_pages * 0.6))
        
        logger.info(f"Searching for GRI patterns in pages {start_search_page + 1} to {total_pages}")
        
        for page_data in pages_data[start_search_page:]:
            text = page_data['text']
            page_num = page_data['page_num']
            
            # Check each pattern
            for pattern in self.compiled_patterns:
                matches = pattern.findall(text)
                if matches:
                    logger.info(f"Found GRI pattern '{matches[0]}' on page {page_num}")
                    return page_num
            
            # Also check for specific GRI standard mentions
            for gri_standard in self.gri_dicts.keys():
                if gri_standard.lower() in text.lower():
                    logger.info(f"Found GRI standard '{gri_standard}' on page {page_num}")
                    return page_num
        
        logger.warning("No GRI patterns found using pattern matching")
        return None
    
    def detect_gri_section_tfidf(self, pages_data: List[Dict[str, Any]]) -> Optional[int]:
        """
        Detect GRI section start using TF-IDF similarity search.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            Page number where GRI section starts (1-indexed), or None if not found
        """
        # Focus on last 30-40% of pages
        total_pages = len(pages_data)
        start_search_page = max(0, int(total_pages * 0.6))
        search_pages = pages_data[start_search_page:]
        
        if not search_pages:
            return None
        
        logger.info(f"Using TF-IDF search on pages {start_search_page + 1} to {total_pages}")
        
        # Prepare texts for TF-IDF
        page_texts = [page['text'] for page in search_pages if page['text'].strip()]
        if not page_texts:
            return None
        
        # Create GRI-related query terms
        gri_query_terms = [
            "GRI content index global reporting initiative sustainability standards disclosure",
            "GRI standards disclosure table",
            "GRI 2: General Disclosures 2021",
            "GRI 2 general disclosures organizational details governance",
            "GRI 3 material topics process management",
            "environmental social economic performance emissions water energy",
            "biodiversity waste health safety human rights labor practices"
        ]
        
        try:
            # Use TF-IDF with n-grams to capture phrases
            vectorizer = TfidfVectorizer(
                ngram_range=(1, 3),
                max_features=1000,
                stop_words='english',
                lowercase=True
            )
            
            # Fit on page texts and query terms
            all_texts = page_texts + gri_query_terms
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            # Convert sparse matrix to dense array for slicing
            tfidf_dense = tfidf_matrix.toarray()  
            logger.info(f"TF-IDF matrix shape: {tfidf_dense.shape}")
            
            # Calculate similarity between pages and query terms
            num_pages = len(page_texts)
            page_vectors = tfidf_dense[:num_pages]
            query_vectors = tfidf_dense[num_pages:]
            
            
            # Average similarity across all query terms
            similarities = cosine_similarity(page_vectors, query_vectors).mean(axis=1)
            
            # Find page with highest similarity above threshold
            threshold = 0.1
            best_page_idx = np.argmax(similarities)
            best_similarity = similarities[best_page_idx]
            
            if best_similarity > threshold:
                gri_page_num = search_pages[best_page_idx]['page_num']
                logger.info(f"TF-IDF found potential GRI section on page {gri_page_num} (similarity: {best_similarity:.3f})")
                return gri_page_num
            else:
                logger.warning(f"TF-IDF similarity too low (max: {best_similarity:.3f})")
                return None
                
        except Exception as e:
            logger.error(f"TF-IDF search failed: {e}")
            return None
    
    def detect_gri_section_llm(self, pages_data: List[Dict[str, Any]]) -> Optional[int]:
        """
        Detect GRI section start using Groq LLM heuristic.
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            Page number where GRI section starts (1-indexed), or None if not found
        """
        if not self.groq_client:
            logger.warning("Groq client not available for LLM detection")
            return None
        
        # Focus on last 30-40% of pages
        total_pages = len(pages_data)
        start_search_page = max(0, int(total_pages * 0.6))
        search_pages = pages_data[start_search_page:]
        
        # Sample a few pages for LLM analysis to avoid token limits
        sample_pages = search_pages[::max(1, len(search_pages) // 5)][:5]
        
        logger.info(f"Using LLM analysis on {len(sample_pages)} sample pages")
        
        for page_data in sample_pages:
            text = page_data['text'][:2000]  # Limit text length
            page_num = page_data['page_num']
            
            prompt = f"""
            Analyze this text from page {page_num} of a sustainability report. 
            Does this page contain a GRI (Global Reporting Initiative) content index, GRI standards disclosure section, or GRI reference table?
            
            Look for:
            - GRI Content Index
            - GRI Standards references
            - Systematic listing of GRI disclosures
            - Table of GRI codes (like 2-1, 3-2, 401-1, etc.)
            
            Text:
            {text}
            
            Answer only: YES or NO
            """
            
            try:
                response = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    temperature=0.1,
                    max_tokens=10
                )
                
                content = response.choices[0].message.content
                if content is not None:
                    answer = content.strip().upper()
                    if answer == "YES":
                        logger.info(f"LLM detected GRI section on page {page_num}")
                        return page_num
                    
            except Exception as e:
                logger.warning(f"LLM analysis failed for page {page_num}: {e}")
                continue
        
        logger.warning("LLM did not detect GRI section")
        return None
    
    def extract_gri_codes_from_section(self, pages_data: List[Dict[str, Any]], start_page: int) -> Dict[str, str]:
        """
        Extract GRI codes from the identified GRI section.
        
        Args:
            pages_data: List of page data dictionaries
            start_page: Page number where GRI section starts (1-indexed)
            
        Returns:
            Dictionary mapping GRI codes to their status ("yes" or "none")
        """
        # Extract text from GRI section (start_page to end, or next 20 pages max)
        end_page = min(len(pages_data), start_page + 20)
        section_text = ""
        
        for page_data in pages_data[start_page-1:end_page]:
            section_text += " " + page_data['text']
        
        logger.info(f"Analyzing GRI section from page {start_page} to {end_page}")
        
        # Initialize results with all GRI codes as "none"
        results = {}
        for material_topic, codes in self.gri_dicts.items():
            for gri_code in codes.keys():
                results[gri_code] = None
        
        # Search for each GRI code in the section text
        section_text_lower = section_text.lower()
        
        for material_topic, codes in self.gri_dicts.items():
            for gri_code, description in codes.items():
                # Multiple search strategies for each code
                found = self._search_gri_code_in_text(gri_code, description, section_text_lower)
                if found:
                    results[gri_code] = "YES"
                    logger.debug(f"Found GRI code {gri_code}")
        
        found_count = sum(1 for status in results.values() if status == "YES")
        logger.info(f"Found {found_count} out of {len(results)} GRI codes")
        
        return results
    
    def _search_gri_code_in_text(self, gri_code: str, description: str, text: str) -> bool:
        """
        Search for a specific GRI code in text using multiple strategies.
        
        Args:
            gri_code: GRI code (e.g., "2-1", "417-2")
            description: GRI code description
            text: Text to search in (lowercase)
            
        Returns:
            True if GRI code is found, False otherwise
        """
        # Strategy 1: Exact GRI code match
        code_patterns = [
            rf"\b{re.escape(gri_code)}\b",
            rf"GRI\s*{re.escape(gri_code)}\b",
            rf"{re.escape(gri_code)}[\s:.-]",
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Strategy 2: Fuzzy matching on description (for cases where code is missing but description is present)
        description_words = description.lower().split()
        if len(description_words) >= 3:  # Only for descriptions with enough words
            description_key_words = [word for word in description_words if len(word) > 4]
            if len(description_key_words) >= 2:
                # Check if most key words from description appear in text
                found_words = sum(1 for word in description_key_words if word in text)
                if found_words >= len(description_key_words) * 0.7:  # 70% of key words found
                    return True
        
        return False
    
    def extract_gri_disclosures(self, pdf_path: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Main method to extract GRI disclosures from a PDF.
        
        Args:
            pdf_path: Path to the sustainability report PDF
            
        Returns:
            Dictionary with extraction results in the specified format
        """
        logger.info(f"Starting GRI extraction for {pdf_path}")
        
        # Step 1: Extract text from PDF
        pages_data = self.extract_text_from_pdf(pdf_path)
        if not pages_data:
            logger.error("No pages extracted from PDF")
            return self._create_empty_result()
        
        # Step 2: Detect GRI section using multiple strategies
        gri_start_page = None
        
        # Strategy 1: Pattern matching
        # gri_start_page = self.detect_gri_section_pattern_matching(pages_data)
        
        # Strategy 2: TF-IDF (fallback)
        if gri_start_page is None:
            logger.info("Pattern matching failed, trying TF-IDF")
            gri_start_page = self.detect_gri_section_tfidf(pages_data)
        
        # Strategy 3: LLM (last resort)
        if gri_start_page is None and self.groq_client:
            logger.info("TF-IDF failed, trying LLM")
            gri_start_page = self.detect_gri_section_llm(pages_data)
        
        if gri_start_page is None:
            logger.warning("Could not detect GRI section using any method")
            return self._create_empty_result()
        
        # Step 3: Extract GRI codes from the identified section
        gri_status = self.extract_gri_codes_from_section(pages_data, gri_start_page)
        
        # Step 4: Format results according to requirements
        return self._format_results(gri_status)
    
    def _create_empty_result(self) -> Dict[str, List[Dict[str, str]]]:
        """Create result dictionary with all GRI codes marked as 'none'."""
        results = []
        for material_topic, codes in self.gri_dicts.items():
            for gri_code, description in codes.items():
                results.append({
                    "material_topic": material_topic,
                    "gri_code": gri_code,
                    "status": "none",
                    "description": description
                })
        return {"gri_disclosures": results}
    
    def _format_results(self, gri_status: Dict[str, str]) -> Dict[str, List[Dict[str, str]]]:
        """
        Format extraction results according to requirements.
        
        Args:
            gri_status: Dictionary mapping GRI codes to their status
            
        Returns:
            Formatted results dictionary
        """
        results = []
        
        for material_topic, codes in self.gri_dicts.items():
            for gri_code, description in codes.items():
                status = gri_status.get(gri_code, "none")
                results.append({
                    "material_topic": material_topic,
                    "gri_code": gri_code,
                    "status": status,
                    "description": description
                })
        
        return {"gri_disclosures": results}


def extract_gri_from_pdf(pdf_path: str, groq_api_key: Optional[str] = None) -> Dict[str, List[Dict[str, str]]]:
    """
    Convenience function to extract GRI disclosures from a PDF.
    
    Args:
        pdf_path: Path to the sustainability report PDF
        groq_api_key: Optional Groq API key for LLM fallback
        
    Returns:
        Dictionary with GRI extraction results
    """
    extractor = GRIExtractor(groq_api_key=groq_api_key)
    return extractor.extract_gri_disclosures(pdf_path)


if __name__ == "__main__":
    # Example usage
    pdf_file = "../antam2024.pdf"
    
    if os.path.exists(pdf_file):
        print("Extracting GRI disclosures...")
        results = extract_gri_from_pdf(pdf_file)
        
        # Print summary
        total_codes = len(results["gri_disclosures"])
        found_codes = sum(1 for item in results["gri_disclosures"] if item["status"] == "yes")
        
        print(f"\nExtraction Summary:")
        print(f"Total GRI codes: {total_codes}")
        print(f"Found GRI codes: {found_codes}")
        print(f"Coverage: {found_codes/total_codes*100:.1f}%")
        
        # Show found codes
        print(f"\nFound GRI codes:")
        for item in results["gri_disclosures"]:
            if item["status"] == "yes":
                print(f"- {item['gri_code']}: {item['material_topic']}")
        
        # Save results to JSON
        with open("gri_extraction_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nResults saved to 'gri_extraction_results.json'")
        
    else:
        print(f"PDF file '{pdf_file}' not found!")