"""
FAST Agricultural Translation Tests - Optimized for Speed & Accuracy
"""
import pytest
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from language_processing.translator import agricultural_translator

class TestOptimizedTranslation:
    
    @pytest.fixture
    def translator(self):
        return agricultural_translator

    def test_language_detection_speed(self, translator):
        """Test language detection speed and accuracy"""
        test_cases = [
            ("मुझे गेहूं की खेती के बारे में जानना है", "hi"),
            ("ਮੈਨੂੰ ਧਾਨ ਦੀ ਖੇਤੀ ਬਾਰੇ ਦੱਸੋ", "pa"),
            ("What is the best fertilizer for wheat?", "en"),
        ]
        
        start_time = time.time()
        
        for text, expected_lang in test_cases:
            detected = translator.detect_language(text)
            print(f"✅ '{text[:30]}...' → {detected}")
            assert detected == expected_lang or expected_lang == 'en'
        
        elapsed = time.time() - start_time
        print(f"⚡ Language detection: {elapsed:.2f}s for {len(test_cases)} queries")
        assert elapsed < 1.0  # Should be very fast with caching

    def test_agricultural_translation_quality(self, translator):
        """Test agricultural query translation quality"""
        test_queries = [
            # Hindi agricultural queries
            ("मुझे धान की खेती के लिए कौन सा उर्वरक इस्तेमाल करना चाहिए?", ["fertilizer", "rice"]),
            ("खरीफ सीजन में कपास का भाव क्या है?", ["price", "cotton", "kharif"]),
            ("सिंचाई के लिए सरकारी योजना क्या है?", ["irrigation", "scheme", "government"]),
            
            # Code-switched queries
            ("मुझे cotton farming के बारे में बताइए", ["cotton", "farming"]),
            ("Rice का price kya hai?", ["rice", "price"]),
            
            # English (unchanged)
            ("What is the best fertilizer for wheat?", ["fertilizer", "wheat"]),
        ]
        
        start_time = time.time()
        
        for query, expected_terms in test_queries:
            english_query, detected_lang = translator.query_to_english(query)
            
            print(f"\n📝 Original: {query}")
            print(f"🌐 Language: {detected_lang}")
            print(f"🇬🇧 English: {english_query}")
            
            # Quality checks
            assert len(english_query) > 0
            assert english_query != query or detected_lang == 'en'
            
            # Agricultural term preservation
            english_lower = english_query.lower()
            found_terms = [term for term in expected_terms if term in english_lower]
            assert len(found_terms) > 0, f"Expected terms {expected_terms} not found in: {english_query}"
        
        elapsed = time.time() - start_time
        print(f"\n⚡ Translation speed: {elapsed:.2f}s for {len(test_queries)} queries")
        assert elapsed < 30.0  # Should be much faster than 130s!

    def test_response_translation_back(self, translator):
        """Test response translation back to original language"""
        responses = [
            "For wheat farming in Punjab, use 120 kg nitrogen per hectare during sowing season.",
            "Current cotton prices are Rs 6,200 per quintal in Gujarat markets.",
            "Government irrigation schemes include PMKSY with 55% subsidy for drip systems."
        ]
        
        target_languages = ['hi', 'pa']
        
        start_time = time.time()
        
        for response in responses:
            for lang in target_languages:
                translated = translator.response_to_original_language(response, lang)
                
                print(f"\n🇬🇧 English: {response[:50]}...")
                print(f"🌐 {lang.upper()}: {translated[:50]}...")
                
                assert len(translated) > 0
                assert translated != response  # Should be different from English
        
        elapsed = time.time() - start_time
        print(f"\n⚡ Response translation: {elapsed:.2f}s")

    def test_caching_performance(self, translator):
        """Test that caching improves performance"""
        repeated_query = "मुझे गेहूं की खेती के बारे में बताइए"
        
        # First call (cache miss)
        start_time = time.time()
        result1, lang1 = translator.query_to_english(repeated_query)
        first_call_time = time.time() - start_time
        
        # Second call (cache hit)
        start_time = time.time()
        result2, lang2 = translator.query_to_english(repeated_query)
        second_call_time = time.time() - start_time
        
        print(f"🔥 First call: {first_call_time:.3f}s")
        print(f"⚡ Cached call: {second_call_time:.3f}s")
        print(f"🚀 Speed improvement: {first_call_time/second_call_time:.1f}x faster")
        
        # Results should be identical
        assert result1 == result2
        assert lang1 == lang2
        
        # Cached call should be much faster
        assert second_call_time < first_call_time * 0.5

    def test_agricultural_term_preservation(self, translator):
        """Test agricultural terminology is correctly handled"""
        agricultural_queries = [
            ("गेहूं का भाव क्या है?", "price"),  # भाव should become price
            ("धान की फसल में उर्वरक", "fertilizer"),  # उर्वरक should become fertilizer
            ("सिंचाई की व्यवस्था", "irrigation"),  # सिंचाई should become irrigation
            ("खरीफ सीजन", "kharif"),  # खरीफ should remain kharif
        ]
        
        for hindi_query, expected_term in agricultural_queries:
            english_query, _ = translator.query_to_english(hindi_query)
            
            print(f"🌾 {hindi_query} → {english_query}")
            
            assert expected_term.lower() in english_query.lower(), \
                f"Expected '{expected_term}' in translation: {english_query}"

def run_performance_benchmark():
    """Benchmark the optimized translator"""
    translator = agricultural_translator
    
    print("🚀 Agricultural Translation Performance Benchmark")
    print("=" * 60)
    
    # Benchmark queries
    queries = [
        "मुझे धान की खेती के बारे में बताइए",
        "ਕਣਕ ਦੀ ਖੇਤੀ ਕਿਵੇਂ ਕਰੀਏ?",
        "કપાસની ખેતી કેવી રીતે કરવી?",
        "Rice farming के लिए best method क्या है?",
        "What is the MSP for wheat this year?"
    ]
    
    # Warm up caches
    for query in queries[:2]:
        translator.query_to_english(query)
    
    # Benchmark translation speed
    start_time = time.time()
    
    for i, query in enumerate(queries * 3):  # 15 total queries
        english_query, lang = translator.query_to_english(query)
        print(f"{i+1:2d}. {lang} → EN: {english_query[:60]}...")
    
    total_time = time.time() - start_time
    avg_time = total_time / (len(queries) * 3)
    
    print(f"\n📊 Performance Results:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Average per query: {avg_time:.3f}s")
    print(f"   Queries per second: {1/avg_time:.1f}")
    
    # Show cache stats
    stats = translator.get_translation_stats()
    print(f"\n🎯 Cache Performance:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    run_performance_benchmark()
