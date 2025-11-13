def test_methods_fix():
    """Test that all methods are properly inside the class"""
    try:
        from services.news_retrieval_service import get_news_retrieval_service
        
        service = get_news_retrieval_service()
        print("✅ Service created successfully")
        
        # Check for the missing methods
        required_methods = [
            '_validate_url_exists',
            '_filter_real_articles', 
            '_get_real_nepal_news_sources',
            '_get_fallback_real_sources',
            'get_real_news_only'
        ]
        
        for method_name in required_methods:
            if hasattr(service, method_name):
                print(f"✅ {method_name} - Found")
            else:
                print(f"❌ {method_name} - Missing")
        
        # Test the homepage news method
        news_data = service.get_all_news_categories()
        print(f"✅ Homepage news: {len(news_data.get('recent', []))} articles")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_methods_fix()