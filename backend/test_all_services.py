"""
Master Test Script - Tests all AWS services
Run this to verify all services are working
"""
import sys
import subprocess

def run_test(test_name, script_path):
    """Run a test script and return result"""
    print("\n" + "=" * 70)
    print(f"RUNNING: {test_name}")
    print("=" * 70)
    
    result = subprocess.run(
        ['python', script_path],
        capture_output=False
    )
    
    return result.returncode == 0


def main():
    """Run all service tests"""
    print("\n" + "=" * 70)
    print("AWS SERVICES MASTER TEST SUITE")
    print("=" * 70)
    print("Testing: Polly, Transcribe, and Bedrock")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Polly (Text-to-Speech)
    results['Polly'] = run_test(
        "Amazon Polly (Text-to-Speech)",
        "backend/test_polly_simple.py"
    )
    
    # Test 2: Transcribe (Speech-to-Text)
    results['Transcribe'] = run_test(
        "Amazon Transcribe (Speech-to-Text)",
        "backend/test_transcribe_simple.py"
    )
    
    # Test 3: Bedrock (LLM)
    results['Bedrock'] = run_test(
        "Amazon Bedrock (LLM)",
        "backend/test_bedrock_simple.py"
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for service, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{service:20s}: {status}")
    
    print("=" * 70)
    
    all_passed = all(results.values())
    if all_passed:
        print("\n✓ ALL SERVICES ARE READY!")
        print("You can now proceed with Task 3: Intent Classification")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        print("Please check the error messages above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
