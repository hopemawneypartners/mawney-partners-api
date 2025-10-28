"""
Test CV Formatting API
"""

import requests
import json

def test_cv_formatting():
    """Test the CV formatting endpoint"""
    
    # Sample CV text
    sample_cv = """
John Smith
john.smith@email.com | +44 20 1234 5678

PROFESSIONAL SUMMARY
Experienced credit analyst with 5+ years in corporate credit markets.

WORK EXPERIENCE

Senior Credit Analyst | ABC Bank | 2020-2023
• Managed credit portfolio
• Conducted analysis
• Presented to committee

EDUCATION
BSc Finance, London Business School, 2018
"""
    
    print("Testing CV formatting API...")
    print("=" * 60)
    
    # Create a test request (simulating file upload)
    url = "http://localhost:5001/api/ai-assistant"
    
    # Test with multipart form data
    files = {
        'attachments': ('test_cv.txt', sample_cv.encode(), 'text/plain')
    }
    
    data = {
        'query': 'Format this CV in Mawney Partners style',
        'chat_id': 'test_user'
    }
    
    try:
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS!")
            print()
            print(f"Response Type: {result.get('type')}")
            print(f"Has HTML Content: {'html_content' in result}")
            print(f"Has Download URL: {'download_url' in result}")
            print(f"Has Download Filename: {'download_filename' in result}")
            print()
            
            if 'download_url' in result:
                print(f"Download URL: {result['download_url']}")
                print(f"Filename: {result.get('download_filename')}")
            
            if 'html_content' in result:
                html_length = len(result['html_content'])
                print(f"HTML Content Length: {html_length} characters")
                print()
                print("HTML Preview (first 500 chars):")
                print(result['html_content'][:500])
            
            print()
            print("Response Text Preview:")
            print(result.get('text', '')[:300])
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cv_formatting()




