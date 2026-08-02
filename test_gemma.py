import json
import gemma_client

def test_extraction_and_generation():
    print("Testing extraction offline fallback:")
    input_text = "કાલે મનોજભાઈને 25 box મોકલવાના છે, ₹12,500 payment pending છે."
    extracted = gemma_client.extract_fields(input_text)
    print("Extracted fields:", json.dumps(extracted, ensure_ascii=False, indent=2))
    
    print("\nTesting message generation offline fallback:")
    msg = gemma_client.generate_confirmation(extracted)
    print("Generated message:", msg)

if __name__ == "__main__":
    test_extraction_and_generation()
