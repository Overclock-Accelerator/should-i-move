"""
Test script for the Should I Move? API.
Run this to test the API locally or on Railway.
"""

import requests
import time
import sys

# Configure the base URL
BASE_URL = "http://localhost:8000"  # Change to your Railway URL when deployed

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        response.raise_for_status()
        print("✅ Health check passed")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def submit_analysis():
    """Submit a test analysis request"""
    print("\nSubmitting analysis request...")
    
    payload = {
        "current_city": "New York City",
        "desired_city": "Austin",
        "annual_income": 85000,
        "monthly_expenses": 3500,
        "city_preferences": ["good weather", "tech industry", "arts scene"],
        "current_city_likes": ["great public transit", "diverse food options"],
        "current_city_dislikes": ["high cost of living", "harsh winters"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analyze", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Analysis request submitted")
        print(f"   Analysis ID: {data['analysis_id']}")
        print(f"   Status: {data['status']}")
        print(f"   Estimated time: {data['estimated_completion_time']}")
        
        return data['analysis_id']
    except Exception as e:
        print(f"❌ Failed to submit analysis: {e}")
        return None

def poll_analysis(analysis_id, max_attempts=60, interval=10):
    """Poll for analysis results"""
    print(f"\nPolling for results (checking every {interval} seconds)...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/analysis/{analysis_id}")
            response.raise_for_status()
            data = response.json()
            
            status = data['status']
            print(f"   Attempt {attempt + 1}/{max_attempts}: Status = {status}")
            
            if status == "completed":
                print("\n✅ Analysis completed successfully!")
                print("\n" + "="*80)
                print("RESULTS:")
                print("="*80)
                
                result = data['result']
                print(f"\n🎯 RECOMMENDATION: {result['recommendation']}")
                print(f"📊 CONFIDENCE: {result['confidence_level']}")
                
                print(f"\n✅ Key Supporting Factors:")
                for factor in result['key_supporting_factors']:
                    print(f"   • {factor}")
                
                print(f"\n⚠️  Key Concerns:")
                for concern in result['key_concerns']:
                    print(f"   • {concern}")
                
                print(f"\n📈 Next Steps:")
                for step in result['next_steps']:
                    print(f"   • {step}")
                
                return True
                
            elif status == "failed":
                print(f"\n❌ Analysis failed: {data.get('error', 'Unknown error')}")
                return False
            
            # Still processing, wait before next poll
            time.sleep(interval)
            
        except Exception as e:
            print(f"   ❌ Error checking status: {e}")
            time.sleep(interval)
    
    print(f"\n⏱️  Timeout: Analysis did not complete within {max_attempts * interval} seconds")
    return False

def main():
    """Run the test suite"""
    print("="*80)
    print("Should I Move? API Test Script")
    print("="*80)
    
    # Allow custom base URL
    if len(sys.argv) > 1:
        global BASE_URL
        BASE_URL = sys.argv[1]
        print(f"Using custom base URL: {BASE_URL}")
    else:
        print(f"Using default base URL: {BASE_URL}")
        print("(Provide URL as argument to test a different endpoint)")
    
    print("\n" + "-"*80)
    
    # Test health check
    if not test_health_check():
        print("\n⚠️  Server may not be running. Start with: python api.py")
        return
    
    # Submit analysis
    analysis_id = submit_analysis()
    if not analysis_id:
        return
    
    # Poll for results
    success = poll_analysis(analysis_id)
    
    print("\n" + "="*80)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
