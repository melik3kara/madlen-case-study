"""
Rate Limiting Middleware Test Suite

Bu test dosyası rate limiting middleware'inin doğru çalıştığını doğrular.
Test türleri:
1. Unit Tests - RateLimiter class'ını direkt test eder
2. Integration Tests - FastAPI app üzerinden middleware'i test eder
"""

import pytest
import time
from unittest.mock import MagicMock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

# Import rate limiting components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.middleware.rate_limit import (
    RateLimiter,
    RateLimitConfig,
    RateLimitMiddleware,
    _rate_limiter
)


class TestRateLimiterUnit:
    """Unit tests for RateLimiter class."""
    
    def setup_method(self):
        """Her test öncesi yeni bir RateLimiter oluştur."""
        self.limiter = RateLimiter()
        self.config = RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=100,
            chat_requests_per_minute=2,
            chat_requests_per_hour=50,
            max_burst=3
        )
    
    def test_first_request_allowed(self):
        """İlk istek her zaman kabul edilmeli."""
        allowed, reason, headers = self.limiter.check_rate_limit(
            "192.168.1.1", 
            is_chat=False, 
            config=self.config
        )
        
        assert allowed is True
        assert reason == ""
        assert headers["X-RateLimit-Limit-Minute"] == 5
        print(f"✅ İlk istek kabul edildi. Remaining: {headers['X-RateLimit-Remaining-Minute']}")
    
    def test_minute_limit_enforced(self):
        """Dakikalık limit aşıldığında istek reddedilmeli."""
        client_ip = "192.168.1.2"
        
        # Burst'u devre dışı bırakacak config
        config_no_burst = RateLimitConfig(
            requests_per_minute=5,
            requests_per_hour=100,
            chat_requests_per_minute=2,
            chat_requests_per_hour=50,
            max_burst=100  # Burst'u fiilen devre dışı bırak
        )
        
        # 5 istek yap (limit)
        for i in range(5):
            allowed, reason, headers = self.limiter.check_rate_limit(
                client_ip,
                is_chat=False,
                config=config_no_burst
            )
            print(f"  Request {i+1}: allowed={allowed}, remaining={headers['X-RateLimit-Remaining-Minute']}")
            assert allowed is True, f"Request {i+1} should be allowed"
        
        # 6. istek reddedilmeli
        allowed, reason, headers = self.limiter.check_rate_limit(
            client_ip, 
            is_chat=False, 
            config=config_no_burst
        )
        
        assert allowed is False, "6th request should be denied"
        assert "rate limit exceeded" in reason.lower()
        print(f"✅ 6. istek reddedildi: {reason}")
    
    def test_chat_has_stricter_limits(self):
        """Chat endpoint'leri daha sıkı limitler uygulamalı."""
        client_ip = "192.168.1.3"
        
        # Chat için limit 2
        for i in range(2):
            allowed, _, _ = self.limiter.check_rate_limit(
                client_ip, 
                is_chat=True, 
                config=self.config
            )
            assert allowed is True
        
        # 3. chat isteği reddedilmeli
        allowed, reason, _ = self.limiter.check_rate_limit(
            client_ip, 
            is_chat=True, 
            config=self.config
        )
        
        assert allowed is False
        assert "2" in reason  # Limit değeri mesajda olmalı
        print(f"✅ Chat limiti çalışıyor: {reason}")
    
    def test_burst_protection(self):
        """Burst protection 1 saniye içinde çok fazla isteği engellemeli."""
        client_ip = "192.168.1.4"
        
        # Burst limit 3
        for i in range(3):
            allowed, _, _ = self.limiter.check_rate_limit(
                client_ip, 
                is_chat=False, 
                config=self.config
            )
            assert allowed is True
        
        # 4. istek aynı saniye içinde reddedilmeli
        allowed, reason, _ = self.limiter.check_rate_limit(
            client_ip, 
            is_chat=False, 
            config=self.config
        )
        
        assert allowed is False
        assert "burst" in reason.lower()
        print(f"✅ Burst protection çalışıyor: {reason}")
    
    def test_different_ips_have_separate_limits(self):
        """Farklı IP'ler ayrı limitler kullanmalı."""
        # IP 1 için limit doldur
        for i in range(5):
            self.limiter.check_rate_limit("10.0.0.1", is_chat=False, config=self.config)
        
        # IP 1 reddedilmeli
        allowed1, _, _ = self.limiter.check_rate_limit("10.0.0.1", is_chat=False, config=self.config)
        assert allowed1 is False
        
        # IP 2 hala kabul edilmeli
        allowed2, _, _ = self.limiter.check_rate_limit("10.0.0.2", is_chat=False, config=self.config)
        assert allowed2 is True
        
        print("✅ Farklı IP'ler ayrı limitler kullanıyor")
    
    def test_rate_limit_headers(self):
        """Response header'ları doğru değerler içermeli."""
        client_ip = "192.168.1.5"
        
        allowed, _, headers = self.limiter.check_rate_limit(
            client_ip, 
            is_chat=False, 
            config=self.config
        )
        
        assert "X-RateLimit-Limit-Minute" in headers
        assert "X-RateLimit-Remaining-Minute" in headers
        assert "X-RateLimit-Limit-Hour" in headers
        assert "X-RateLimit-Remaining-Hour" in headers
        
        assert headers["X-RateLimit-Limit-Minute"] == 5
        assert headers["X-RateLimit-Remaining-Minute"] == 4  # 5 - 1
        
        print(f"✅ Headers doğru: {headers}")


class TestRateLimitMiddlewareIntegration:
    """Integration tests using FastAPI TestClient."""
    
    def setup_method(self):
        """Her test için yeni bir FastAPI app ve TestClient oluştur."""
        # Yeni config ile yeni limiter
        self.config = RateLimitConfig(
            requests_per_minute=3,
            requests_per_hour=100,
            chat_requests_per_minute=2,
            chat_requests_per_hour=50,
            max_burst=10,
            exempt_paths=("/health", "/metrics")
        )
        
        # Yeni FastAPI app
        self.app = FastAPI()
        
        # Test endpoint'leri
        @self.app.get("/test")
        async def test_endpoint():
            return {"message": "ok"}
        
        @self.app.post("/chat/send")
        async def chat_endpoint():
            return {"message": "chat response"}
        
        @self.app.get("/health")
        async def health_endpoint():
            return {"status": "healthy"}
        
        # Middleware ekle - YENİ limiter ile
        self.limiter = RateLimiter()
        
        # Middleware'i monkey-patch ile yeni limiter kullanacak şekilde ayarla
        original_init = RateLimitMiddleware.__init__
        test_limiter = self.limiter
        test_config = self.config
        
        def patched_init(self_mw, app, config=None):
            original_init(self_mw, app, test_config)
        
        with patch.object(RateLimitMiddleware, '__init__', patched_init):
            self.app.add_middleware(RateLimitMiddleware, config=self.config)
        
        # Global limiter'ı da sıfırla
        global _rate_limiter
        import app.middleware.rate_limit as rl_module
        rl_module._rate_limiter = self.limiter
        
        self.client = TestClient(self.app)
    
    def test_normal_request_passes(self):
        """Normal istek başarıyla geçmeli."""
        response = self.client.get("/test")
        
        assert response.status_code == 200
        assert response.json()["message"] == "ok"
        print(f"✅ Normal istek geçti: {response.status_code}")
    
    def test_rate_limit_headers_in_response(self):
        """Response'ta rate limit header'ları olmalı."""
        response = self.client.get("/test")
        
        # Header'lar var mı kontrol et
        assert "x-ratelimit-limit-minute" in response.headers or "X-RateLimit-Limit-Minute" in response.headers
        print(f"✅ Rate limit headers mevcut: {dict(response.headers)}")
    
    def test_exempt_paths_not_rate_limited(self):
        """Exempt path'ler rate limit'e tabi olmamalı."""
        # Health endpoint 100 kez çağır
        for i in range(100):
            response = self.client.get("/health")
            assert response.status_code == 200, f"Health check failed at request {i+1}"
        
        print("✅ Exempt path (/health) rate limit'e tabi değil")
    
    def test_rate_limit_returns_429(self):
        """Limit aşıldığında 429 dönmeli."""
        # Limiti aş (3 istek/dakika)
        for i in range(3):
            response = self.client.get("/test")
            print(f"  Request {i+1}: status={response.status_code}")
            assert response.status_code == 200
        
        # 4. istek 429 dönmeli
        response = self.client.get("/test")
        print(f"  Request 4: status={response.status_code}, body={response.json()}")
        
        assert response.status_code == 429
        assert response.json()["error"] == "rate_limit_exceeded"
        print("✅ Rate limit aşıldığında 429 dönüyor")
    
    def test_429_response_has_retry_after(self):
        """429 response'unda Retry-After header olmalı."""
        # Limiti aş
        for i in range(3):
            self.client.get("/test")
        
        response = self.client.get("/test")
        
        assert response.status_code == 429
        assert "retry-after" in response.headers or "Retry-After" in response.headers
        print(f"✅ Retry-After header mevcut: {response.headers.get('retry-after', response.headers.get('Retry-After'))}")


class TestRateLimitEdgeCases:
    """Edge case ve stress testleri."""
    
    def setup_method(self):
        self.limiter = RateLimiter()
        self.config = RateLimitConfig(
            requests_per_minute=10,
            max_burst=5
        )
    
    def test_concurrent_requests_same_ip(self):
        """Aynı anda gelen istekler doğru sayılmalı."""
        client_ip = "10.0.0.100"
        
        results = []
        for i in range(15):
            allowed, reason, _ = self.limiter.check_rate_limit(
                client_ip, 
                is_chat=False, 
                config=self.config
            )
            results.append(allowed)
        
        allowed_count = sum(results)
        denied_count = len(results) - allowed_count
        
        # Burst limit 5, yani ilk 5'ten sonra burst'a takılmalı
        print(f"Allowed: {allowed_count}, Denied: {denied_count}")
        assert denied_count > 0, "Some requests should be denied"
        print(f"✅ Concurrent requests doğru işlendi: {allowed_count} allowed, {denied_count} denied")
    
    def test_empty_ip_handled(self):
        """Boş veya unknown IP gracefully handle edilmeli."""
        allowed, _, _ = self.limiter.check_rate_limit(
            "unknown", 
            is_chat=False, 
            config=self.config
        )
        
        # İlk istek kabul edilmeli
        assert allowed is True
        print("✅ 'unknown' IP handle edildi")
    
    def test_ipv6_address(self):
        """IPv6 adresleri desteklenmeli."""
        ipv6 = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        
        allowed, _, _ = self.limiter.check_rate_limit(
            ipv6, 
            is_chat=False, 
            config=self.config
        )
        
        assert allowed is True
        print(f"✅ IPv6 adresi destekleniyor: {ipv6}")


class TestSimpleLimitEnforcement:
    """En basit senaryo: 1 istek limiti."""
    
    def test_limit_of_one(self):
        """Limit 1 olduğunda 2. istek reddedilmeli."""
        limiter = RateLimiter()
        config = RateLimitConfig(
            requests_per_minute=1,
            requests_per_hour=100,
            max_burst=100  # Burst'u devre dışı bırak
        )
        
        client_ip = "test.client.1"
        
        # 1. istek
        allowed1, reason1, headers1 = limiter.check_rate_limit(client_ip, is_chat=False, config=config)
        print(f"Request 1: allowed={allowed1}, reason='{reason1}', remaining={headers1['X-RateLimit-Remaining-Minute']}")
        
        assert allowed1 is True, "First request must be allowed"
        
        # 2. istek - MUTLAKA REDDEDİLMELİ
        allowed2, reason2, headers2 = limiter.check_rate_limit(client_ip, is_chat=False, config=config)
        print(f"Request 2: allowed={allowed2}, reason='{reason2}', remaining={headers2['X-RateLimit-Remaining-Minute']}")
        
        assert allowed2 is False, "Second request MUST be denied when limit is 1"
        assert "rate limit exceeded" in reason2.lower()
        
        print("✅ Limit=1 doğru çalışıyor!")
    
    def test_limit_of_one_integration(self):
        """FastAPI üzerinden limit=1 testi."""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # Yeni app
        app = FastAPI()
        
        @app.get("/api/test")
        async def test_route():
            return {"status": "ok"}
        
        # Özel config
        test_config = RateLimitConfig(
            requests_per_minute=1,
            requests_per_hour=100,
            max_burst=100,
            exempt_paths=("/health",)
        )
        
        # Yeni limiter instance
        test_limiter = RateLimiter()
        
        # Middleware'i ekle ve global limiter'ı override et
        import app.middleware.rate_limit as rl_module
        original_limiter = rl_module._rate_limiter
        rl_module._rate_limiter = test_limiter
        
        try:
            app.add_middleware(RateLimitMiddleware, config=test_config)
            client = TestClient(app)
            
            # 1. istek
            resp1 = client.get("/api/test")
            print(f"Response 1: status={resp1.status_code}, body={resp1.json()}")
            assert resp1.status_code == 200
            
            # 2. istek - 429 olmalı
            resp2 = client.get("/api/test")
            print(f"Response 2: status={resp2.status_code}, body={resp2.json()}")
            assert resp2.status_code == 429, f"Expected 429 but got {resp2.status_code}"
            
            print("✅ Integration test: Limit=1 FastAPI üzerinde çalışıyor!")
            
        finally:
            # Original limiter'ı geri yükle
            rl_module._rate_limiter = original_limiter


def run_quick_test():
    """Hızlı manuel test - pytest olmadan çalıştırılabilir."""
    print("=" * 60)
    print("RATE LIMIT QUICK TEST")
    print("=" * 60)
    
    limiter = RateLimiter()
    config = RateLimitConfig(
        requests_per_minute=3,
        requests_per_hour=100,
        max_burst=10
    )
    
    client_ip = "test.ip.address"
    
    print("\n📋 Test: 3 request/minute limit\n")
    
    for i in range(5):
        allowed, reason, headers = limiter.check_rate_limit(client_ip, config=config)
        status = "✅ ALLOWED" if allowed else "❌ DENIED"
        remaining = headers.get('X-RateLimit-Remaining-Minute', '?')
        
        print(f"  Request {i+1}: {status}")
        print(f"    - Remaining: {remaining}")
        if reason:
            print(f"    - Reason: {reason}")
        print()
    
    print("=" * 60)
    print("Test tamamlandı!")
    print("=" * 60)


if __name__ == "__main__":
    # Pytest olmadan hızlı test
    run_quick_test()
    
    print("\n\n📌 Tüm testleri çalıştırmak için:")
    print("   pytest tests/test_rate_limit.py -v")
