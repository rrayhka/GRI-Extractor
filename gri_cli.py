#!/usr/bin/env python3
"""
GRI Extraction Command Line Interface

Simple command-line interface for the GRI extraction system.
Usage: python gri_cli.py <pdf_path> [options]
"""

import argparse
import os
import sys
import json
import time
from extractGRI import extract_gri_from_pdf

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract GRI disclosures from sustainability report PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gri_cli.py report.pdf
  python gri_cli.py report.pdf --output results.json
  python gri_cli.py report.pdf --groq-key YOUR_API_KEY
  python gri_cli.py report.pdf --summary-only
        """
    )
    
    parser.add_argument(
        "pdf_path",
        help="Path to the sustainability report PDF file"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="gri_results.json",
        help="Output JSON file path (default: gri_results.json)"
    )
    
    parser.add_argument(
        "--groq-key",
        help="Groq API key for LLM fallback (optional)"
    )
    
    parser.add_argument(
        "--summary-only", "-s",
        action="store_true",
        help="Print only summary statistics, don't save full results"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--list-found",
        action="store_true",
        help="List all found GRI codes"
    )
    
    return parser.parse_args()

def format_duration(seconds):
    """Format duration in a human-readable way."""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutes"
    else:
        return f"{seconds/3600:.1f} hours"

def print_summary(results, duration):
    """Print extraction summary."""
    total_codes = len(results["gri_disclosures"])
    found_codes = sum(1 for item in results["gri_disclosures"] if item["status"] == "yes")
    coverage = found_codes / total_codes * 100 if total_codes > 0 else 0
    
    print(f"\n📊 GRI Extraction Summary")
    print("=" * 40)
    print(f"📄 Processing time: {format_duration(duration)}")
    print(f"🎯 Total GRI codes: {total_codes}")
    print(f"✅ Found GRI codes: {found_codes}")
    print(f"📈 Coverage rate: {coverage:.1f}%")
    
    # Status indicator
    if coverage >= 90:
        status = "🟢 EXCELLENT"
    elif coverage >= 70:
        status = "🟡 GOOD"
    elif coverage >= 50:
        status = "🟠 FAIR"
    else:
        status = "🔴 POOR"
    
    print(f"🏆 Extraction quality: {status}")

def print_found_codes(results):
    """Print list of found GRI codes."""
    found_items = [item for item in results["gri_disclosures"] if item["status"] == "yes"]
    
    if not found_items:
        print("\n❌ No GRI codes found")
        return
    
    print(f"\n✅ Found GRI Codes ({len(found_items)} total)")
    print("-" * 50)
    
    # Group by standard
    by_standard = {}
    for item in found_items:
        standard = item["material_topic"]
        if standard not in by_standard:
            by_standard[standard] = []
        by_standard[standard].append(item["gri_code"])
    
    # Print grouped results
    for standard, codes in sorted(by_standard.items()):
        print(f"\n📋 {standard}")
        codes_str = ", ".join(sorted(codes))
        print(f"   {codes_str}")

def main():
    """Main CLI function."""
    args = parse_arguments()
    
    # Check if PDF file exists
    if not os.path.exists(args.pdf_path):
        print(f"❌ Error: PDF file not found: {args.pdf_path}")
        sys.exit(1)
    
    # Configure logging if verbose
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print(f"🔍 GRI Extraction Tool")
    print(f"📄 Processing: {args.pdf_path}")
    
    # Start extraction
    start_time = time.time()
    
    try:
        # Extract GRI disclosures
        if args.groq_key:
            print(f"🤖 Using Groq LLM fallback")
            results = extract_gri_from_pdf(args.pdf_path, groq_api_key=args.groq_key)
        else:
            results = extract_gri_from_pdf(args.pdf_path)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Print summary
        print_summary(results, duration)
        
        # Print found codes if requested
        if args.list_found:
            print_found_codes(results)
        
        # Save results if not summary-only
        if not args.summary_only:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {args.output}")
        
        print(f"\n🎉 Extraction completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Extraction failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
