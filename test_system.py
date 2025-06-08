#!/usr/bin/env python3
"""
Simple test script for GRI extraction system.
"""

import os
import json
from extractGRI import extract_gri_from_pdf, GRIExtractor

def test_basic_extraction():
    """Test basic GRI extraction functionality."""
    print("🔍 Testing GRI Extraction System")
    print("=" * 50)
    
    pdf_path = "pdfs/antam2024.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    print(f"📄 Processing: {pdf_path}")
    
    try:
        # Extract GRI disclosures
        results = extract_gri_from_pdf(pdf_path)
        
        # Analyze results
        total_codes = len(results["gri_disclosures"])
        found_codes = sum(1 for item in results["gri_disclosures"] if item["status"] == "yes")
        coverage = found_codes / total_codes * 100
        
        print(f"\n📊 Results Summary:")
        print(f"   Total GRI codes: {total_codes}")
        print(f"   Found GRI codes: {found_codes}")
        print(f"   Coverage: {coverage:.1f}%")
        
        # Show sample of found codes
        found_items = [item for item in results["gri_disclosures"] if item["status"] == "yes"]
        print(f"\n✅ Sample found codes:")
        for item in found_items[:5]:
            print(f"   • {item['gri_code']}: {item['material_topic']}")
        
        if len(found_items) > 5:
            print(f"   ... and {len(found_items) - 5} more")
        
        # Save results
        output_file = "test_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to: {output_file}")
        
        # Test success criteria
        if coverage > 80:
            print(f"\n🎉 Test PASSED! Excellent coverage: {coverage:.1f}%")
            return True
        elif coverage > 50:
            print(f"\n✅ Test PASSED! Good coverage: {coverage:.1f}%")
            return True
        else:
            print(f"\n⚠️  Test WARNING! Low coverage: {coverage:.1f}%")
            return False
            
    except Exception as e:
        print(f"\n❌ Test FAILED! Error: {e}")
        return False

def test_gri_standards_coverage():
    """Test coverage by GRI standards."""
    print(f"\n📈 Testing GRI Standards Coverage")
    print("-" * 30)
    
    # Load test results
    if not os.path.exists("test_results.json"):
        print("❌ No test results found. Run basic extraction first.")
        return
    
    with open("test_results.json", 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Analyze by standards
    standards_stats = {}
    
    for item in results["gri_disclosures"]:
        standard = item["material_topic"]
        if standard not in standards_stats:
            standards_stats[standard] = {"total": 0, "found": 0}
        
        standards_stats[standard]["total"] += 1
        if item["status"] == "yes":
            standards_stats[standard]["found"] += 1
    
    # Print coverage by standard
    for standard, stats in sorted(standards_stats.items()):
        coverage = stats["found"] / stats["total"] * 100 if stats["total"] > 0 else 0
        status_icon = "🟢" if coverage > 80 else "🟡" if coverage > 50 else "🔴"
        print(f"{status_icon} {standard}")
        print(f"     Coverage: {stats['found']}/{stats['total']} ({coverage:.0f}%)")

def main():
    """Run all tests."""
    print("🧪 GRI Extraction System - Test Suite")
    print("=" * 60)
    
    # Test 1: Basic extraction
    success = test_basic_extraction()
    
    if success:
        # Test 2: Standards coverage
        test_gri_standards_coverage()
        
        print(f"\n🎯 System Status: OPERATIONAL")
        print(f"✨ The GRI extraction system is working correctly!")
    else:
        print(f"\n⚠️  System Status: NEEDS ATTENTION")
        print(f"🔧 Please check the logs for issues.")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()
