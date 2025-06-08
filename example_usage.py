#!/usr/bin/env python3
"""
GRI Extraction Example Usage

This file demonstrates how to use the GRI extraction system.
"""

import os
import json
from extractGRI import extract_gri_from_pdf, GRIExtractor

def example_basic_usage():
    """Basic usage example."""
    print("=== Basic GRI Extraction Example ===")
    
    # Path to your PDF file
    pdf_path = "pdfs/antam2024.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    # Extract GRI disclosures (without Groq LLM)
    print(f"Extracting GRI disclosures from: {pdf_path}")
    results = extract_gri_from_pdf(pdf_path)
    
    # Print summary
    total_codes = len(results["gri_disclosures"])
    found_codes = sum(1 for item in results["gri_disclosures"] if item["status"] == "yes")
    
    print(f"\n📊 Extraction Summary:")
    print(f"   Total GRI codes: {total_codes}")
    print(f"   Found GRI codes: {found_codes}")
    print(f"   Coverage: {found_codes/total_codes*100:.1f}%")
    
    return results

def example_with_groq():
    """Example using Groq LLM as fallback."""
    print("\n=== GRI Extraction with Groq LLM Example ===")
    
    # You would need to set your Groq API key here
    # groq_api_key = "your_groq_api_key_here"
    groq_api_key = None  # Set to None if you don't have an API key
    
    pdf_path = "pdfs/antam2024.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    # Extract with Groq fallback
    if groq_api_key:
        print(f"Extracting GRI disclosures with Groq LLM fallback...")
        results = extract_gri_from_pdf(pdf_path, groq_api_key=groq_api_key)
    else:
        print("No Groq API key provided, using pattern matching and TF-IDF only")
        results = extract_gri_from_pdf(pdf_path)
    
    return results

def example_detailed_analysis():
    """Detailed analysis example."""
    print("\n=== Detailed GRI Analysis Example ===")
    
    pdf_path = "pdfs/antam2024.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    # Create extractor instance for more control
    extractor = GRIExtractor()
    
    # Extract results
    results = extractor.extract_gri_disclosures(pdf_path)
    
    # Analyze by GRI standards
    standards_analysis = {}
    
    for item in results["gri_disclosures"]:
        standard = item["material_topic"]
        if standard not in standards_analysis:
            standards_analysis[standard] = {"total": 0, "found": 0}
        
        standards_analysis[standard]["total"] += 1
        if item["status"] == "yes":
            standards_analysis[standard]["found"] += 1
    
    print(f"\n📈 Analysis by GRI Standards:")
    for standard, data in standards_analysis.items():
        coverage = data["found"] / data["total"] * 100 if data["total"] > 0 else 0
        print(f"   {standard}")
        print(f"      Found: {data['found']}/{data['total']} ({coverage:.1f}%)")
    
    return results

def save_results_to_csv(results, filename="gri_results.csv"):
    """Save results to CSV file."""
    import csv
    
    print(f"\n💾 Saving results to {filename}")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['material_topic', 'gri_code', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for item in results["gri_disclosures"]:
            writer.writerow(item)
    
    print(f"   Results saved successfully!")

def main():
    """Main function to run examples."""
    print("🔍 GRI Disclosure Extraction System - Examples\n")
    
    # Run basic example
    results = example_basic_usage()
    
    if results:
        # Run detailed analysis
        example_detailed_analysis()
        
        # Save to CSV
        save_results_to_csv(results)
        
        # Show some found codes
        print(f"\n✅ Sample of found GRI codes:")
        found_items = [item for item in results["gri_disclosures"] if item["status"] == "yes"]
        for item in found_items[:10]:  # Show first 10
            print(f"   {item['gri_code']}: {item['material_topic']}")
        
        if len(found_items) > 10:
            print(f"   ... and {len(found_items) - 10} more")
    
    print(f"\n🎉 Examples completed!")

if __name__ == "__main__":
    main()
