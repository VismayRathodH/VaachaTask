import json
import gemma_client

def run_test_suite():
    # Load test cases
    try:
        with open("examples.json", "r", encoding="utf-8") as f:
            test_cases = json.load(f)
    except Exception as e:
        print(f"Error loading examples.json: {e}")
        return

    print("=" * 60)
    print("VAACHATASK TEST RUNNER")
    print("=" * 60)

    for tc in test_cases:
        print(f"\n[Test Case {tc['id']}] {tc['name']}")
        print(f"Input: \"{tc['input']}\"")
        
        # 1. Extraction
        extracted = gemma_client.extract_fields(tc['input'])
        print("\nExtracted Fields:")
        print(json.dumps(extracted, ensure_ascii=False, indent=2))
        
        # 2. Generation
        message = gemma_client.generate_confirmation(extracted)
        print("\nGenerated WhatsApp Message:")
        print(message)
        print("-" * 60)

if __name__ == "__main__":
    import sys
    # Force UTF-8 stdout for Windows consoles
    sys.stdout.reconfigure(encoding='utf-8')
    run_test_suite()
