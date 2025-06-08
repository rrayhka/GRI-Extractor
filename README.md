# GRI Disclosure Extraction System

A robust Python system for extracting GRI (Global Reporting Initiative) disclosures from Sustainability Report PDFs using multiple detection strategies.

## 🎯 Features

- **Multi-Strategy Detection**: Uses pattern matching, TF-IDF similarity search, and optional Groq LLM fallback
- **Comprehensive GRI Coverage**: Supports all major GRI standards (Economic, Environmental, Social)
- **Language Support**: Handles English and Indonesian documents
- **Robust Text Processing**: Deals with noisy PDF text extraction and format variations
- **Modular Design**: Clean, well-commented code for easy customization

## 📋 Requirements

- Python 3.8+
- Required packages (see `requirements.txt`):
  - pypdf>=3.0.0
  - scikit-learn>=1.3.0
  - numpy>=1.24.0
  - fuzzywuzzy>=0.18.0
  - python-levenshtein>=0.21.0
  - groq>=0.4.0 (optional, for LLM fallback)

## 🚀 Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Basic Usage

```python
from extractGRI import extract_gri_from_pdf

# Extract GRI disclosures from a PDF
results = extract_gri_from_pdf("path/to/sustainability_report.pdf")

# Print summary
total_codes = len(results["gri_disclosures"])
found_codes = sum(1 for item in results["gri_disclosures"] if item["status"] == "yes")
print(f"Found {found_codes} out of {total_codes} GRI codes")
```

### Advanced Usage with Groq LLM

```python
from extractGRI import extract_gri_from_pdf

# Extract with Groq LLM fallback (requires API key)
results = extract_gri_from_pdf(
    "path/to/sustainability_report.pdf",
    groq_api_key="your_groq_api_key"
)
```

### Using the GRIExtractor Class

```python
from extractGRI import GRIExtractor

# Create extractor instance
extractor = GRIExtractor(groq_api_key="optional_groq_key")

# Extract disclosures
results = extractor.extract_gri_disclosures("path/to/pdf")
```

## 📊 Output Format

The system returns a dictionary with the following structure:

```json
{
  "gri_disclosures": [
    {
      "material_topic": "GRI 417: Marketing and Labeling 2016",
      "gri_code": "417-2",
      "status": "yes"
    },
    {
      "material_topic": "GRI 201: Economic Performance 2016",
      "gri_code": "201-1",
      "status": "none"
    }
  ]
}
```

Where:

- `material_topic`: The GRI standard name
- `gri_code`: The specific GRI disclosure code
- `status`: "yes" if found in the document, "none" if not found

## 🔧 How It Works

### 1. Multi-Strategy GRI Section Detection

The system uses three strategies to locate the GRI section in sustainability reports:

**Strategy 1: Pattern Matching**

- Searches for common GRI section headers like "GRI Content Index", "GRI Standards Index"
- Uses regex patterns for English and Indonesian documents
- Focuses on the last 30-40% of pages where GRI sections typically appear

**Strategy 2: TF-IDF Similarity Search**

- Falls back to semantic similarity if pattern matching fails
- Compares document pages against GRI-related query terms
- Uses cosine similarity to find the most relevant pages

**Strategy 3: Groq LLM Heuristic**

- Optional fallback using large language model
- Analyzes sample pages to detect GRI content
- Requires Groq API key

### 2. GRI Code Extraction

Once the GRI section is identified:

- Scans the section for specific GRI codes (e.g., "2-1", "417-2")
- Uses exact pattern matching with the comprehensive `GRI_Dicts` dictionary
- Handles format variations and noisy text extraction
- Applies fuzzy matching on descriptions as fallback

### 3. Supported GRI Standards

The system includes comprehensive coverage of GRI standards:

- **GRI 2**: General Disclosures 2021 (30 indicators)
- **GRI 3**: Material Topics 2021 (3 indicators)
- **Economic Standards**: 201-207 (Economic Performance, Market Presence, etc.)
- **Environmental Standards**: 101, 301-308 (Energy, Water, Emissions, Biodiversity, etc.)
- **Social Standards**: 401-418 (Employment, Health & Safety, Human Rights, etc.)

## 📁 Project Structure

```
├── extractGRI.py          # Main extraction system
├── example_usage.py       # Usage examples
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── pdfs/                 # Directory for PDF files
│   └── antam2024.pdf     # Sample sustainability report
└── gri_extraction_results.json  # Output from extraction
```

## 🧪 Testing

Run the system with the sample PDF:

```bash
python extractGRI.py
```

Run usage examples:

```bash
python example_usage.py
```

## 🎛️ Configuration

### Groq API Key (Optional)

To use the LLM fallback feature:

1. Get a Groq API key from [https://console.groq.com](https://console.groq.com)
2. Pass it to the extraction function:
   ```python
   results = extract_gri_from_pdf(pdf_path, groq_api_key="your_key_here")
   ```

### Customizing GRI Standards

Modify the `GRI_Dicts` dictionary in `extractGRI.py` to add new standards or update existing ones:

```python
GRI_Dicts = {
    "GRI 999: New Standard 2024": {
        "999-1": "New disclosure requirement",
        "999-2": "Another requirement"
    }
}
```

## 🚨 Limitations

- **PDF Quality**: Results depend on PDF text extraction quality
- **Format Variations**: Some non-standard formats may require manual adjustment
- **Language Support**: Optimized for English and Indonesian, may need adaptation for other languages
- **Large Documents**: Memory usage scales with document size

## 🔍 Troubleshooting

### Common Issues

1. **No GRI Section Detected**

   - Check if the PDF contains a GRI content index
   - Try adjusting the search range in the code
   - Enable Groq LLM fallback

2. **Low Coverage**

   - Verify the GRI section is properly identified
   - Check for non-standard GRI code formats in the document
   - Review the extraction logs for insights

3. **Memory Issues**
   - Use smaller PDF files or split large documents
   - Reduce the TF-IDF feature count in the code

### Logging

The system provides detailed logging. To see debug information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source. Please ensure compliance with the licenses of all dependencies.

## 🙏 Acknowledgments

- Global Reporting Initiative (GRI) for the sustainability reporting standards
- The open source community for the excellent Python libraries used
- pypdf for PDF text extraction capabilities
