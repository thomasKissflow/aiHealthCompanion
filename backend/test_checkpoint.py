"""
Checkpoint Test - Run all non-interactive tests
"""
import subprocess
import sys

def run_test(test_name, script_path):
    """Run a test script and return result"""
    print("\n" + "=" * 70)
    print(f"RUNNING: {test_name}")
    print("=" * 70)
    
    result = subprocess.run(
        ['python', script_path],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def main():
    """Run all checkpoint tests"""
    print("\n" + "=" * 70)
    print("CHECKPOINT TEST SUITE")
    print("=" * 70)
    print("Running all non-interactive tests...")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Intent Classifier
    results['Intent Classifier'] = run_test(
        "Intent Classifier",
        "backend/test_intent_classifier.py"
    )
    
    # Test 2: Template Engine
    results['Template Engine'] = run_test(
        "Template Response Engine",
        "backend/test_template_engine.py"
    )
    
    # Test 3: Response Cache
    results['Response Cache'] = run_test(
        "Response Cache",
        "backend/test_response_cache.py"
    )
    
    # Test 4: Polly (non-interactive)
    results['Polly'] = run_test(
        "Amazon Polly (Text-to-Speech)",
        "backend/test_polly_simple.py"
    )
    
    # Test 5: Bedrock
    results['Bedrock'] = run_test(
        "Amazon Bedrock (LLM)",
        "backend/test_bedrock_simple.py"
    )
    
    # Summary
    print("\n" + "=" * 70)
    print("CHECKPOINT TEST RESULTS")
    print("=" * 70)
    
    for component, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{component:30s}: {status}")
    
    print("=" * 70)
    
    all_passed = all(results.values())
    if all_passed:
        print("\n✓ ALL CHECKPOINT TESTS PASSED!")
        print("Ready to proceed with Task 6: Risk Escalation Agent")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        print("Please review the errors above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
