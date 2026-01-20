# 🎓 MADLEN AI Chat Application

**Madlen - Great Teachers Great Futures!**

OpenRouter üzerinden çoklu AI dil modelleriyle etkileşim kurmayı sağlayan, üretim ortamına hazır bir web tabanlı sohbet uygulaması. OpenTelemetry ile tam izlenebilirlik sağlanmıştır.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-Enabled-F5A800?logo=opentelemetry&logoColor=white)

---

## 📋 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Özellikler](#-özellikler)
- [Ekstra Geliştirmeler](#-ekstra-geliştirmeler)
- [Mimari](#-mimari)
- [Teknik Seçimler ve Nedenleri](#-teknik-seçimler-ve-nedenleri)
- [Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [OpenTelemetry ve Jaeger](#-opentelemetry-ve-jaeger)
- [Proje Yapısı](#-proje-yapısı)
- [Sorun Giderme](#-sorun-giderme)

---

## 🎯 Proje Hakkında

Bu uygulama, kullanıcıların çeşitli AI modelleriyle sohbet edebileceği temiz ve kullanıcı dostu bir arayüz sunar. OpenRouter'ı birleşik bir geçit olarak kullanarak birden fazla LLM'e erişim sağlar ve Jaeger'a aktarılan OpenTelemetry izleme ile tam gözlemlenebilirlik sunar.

### Temel Yetenekler

| Özellik | Açıklama |
|---------|----------|
| **Çoklu Model Desteği** | 26+ ücretsiz AI modeli (Llama, Gemma, Qwen, DeepSeek, vb.) |
| **Oturum Bazlı Bellek** | Sohbet bağlamı oturumlar içinde korunur |
| **Görsel Yükleme** | Multimodal modeller için görsel desteği |
| **Tam İzleme** | Her istek detaylı span'larla trace edilir |
| **Prometheus Metrics** | Performans ve kullanım metrikleri |
| **Dark/Light Mode** | Kullanıcı tercihine göre tema desteği |

---

## ✨ Özellikler

### Backend Özellikleri
- ⚡ **Async API** - FastAPI ile yüksek performanslı asenkron işlemler
- 🔐 **OpenRouter Entegrasyonu** - 26+ ücretsiz AI modeline erişim
- 📊 **Prometheus Metrics** - `/metrics` endpoint'i ile metrik toplama
- 🔍 **OpenTelemetry Tracing** - Dağıtık izleme ve hata takibi
- 💾 **Oturum Yönetimi** - Sohbet geçmişi ve oturum değiştirme
- 🖼️ **Multimodal Destek** - Görsel analizi yapabilen modeller
- 🛡️ **Rate Limiting** - API koruma ve kötüye kullanım önleme
- 🔄 **Retry Logic** - Exponential backoff ile otomatik yeniden deneme

### Frontend Özellikleri
- 🎨 **Modern UI** - Sıcak renk paleti (sarı/turuncu/kırmızı)
- 🌓 **Dark/Light Mode** - Tema tercihi localStorage'da saklanır
- 📱 **Responsive Tasarım** - Mobil uyumlu arayüz
- 📚 **Sohbet Geçmişi Sidebar'ı** - Katlanabilir oturum listesi, editable başlıklar
- 🖼️ **Görsel Yükleme** - Sürükle & bırak + otomatik sıkıştırma
- ⏳ **Loading States** - Yazma göstergesi ve hata mesajları
- 📝 **Markdown Rendering** - AI yanıtlarında zengin metin formatı
- 🎨 **Syntax Highlighting** - Kod bloklarında sözdizimi renklendirme
- 📐 **LaTeX/KaTeX Desteği** - Matematiksel formüller ve denklemler
- ⏱️ **Response Time Display** - Yanıt süresi gösterimi
- 📋 **Copy to Clipboard** - Tek tıkla kod/metin kopyalama
- ✏️ **Editable Oturum Başlıkları** - Double-click ile başlık düzenle, otomatik kayıt

---

## 🚀 Ekstra Geliştirmeler

Bu proje, temel gereksinimlerin ötesinde aşağıdaki production-ready özellikleri içerir:

### 1. Rate Limiting (API Koruma)
```
├── Dakikada 60 genel istek limiti
├── Dakikada 20 chat isteği limiti
├── Burst koruma (saniyede max 10 istek)
├── IP bazlı takip
└── Rate limit header'ları (X-RateLimit-*)
```

**Neden Önemli:** Production ortamında API'yi kötüye kullanımdan ve DDoS saldırılarından korur. Her istek yanıtında kalan istek sayısı bildirilir.

### 2. Retry Logic with Exponential Backoff
```python
MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0s
MAX_BACKOFF = 10.0s
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
```

**Neden Önemli:** OpenRouter API'sinde geçici hatalar olduğunda otomatik olarak yeniden dener. Exponential backoff ile sunucuyu aşırı yüklemez.

### 3. Markdown Rendering + Syntax Highlighting
- AI yanıtlarında tam Markdown desteği
- 20+ programlama dili için syntax highlighting
- Kod bloklarında tek tıkla kopyalama
- Tablolar, listeler, blockquote desteği

**Neden Önemli:** AI asistanları genellikle Markdown formatında yanıt verir. Bu özellik yanıtları okunabilir ve kullanışlı hale getirir.

### 4. Response Time Tracking
- Her AI yanıtının süresi ölçülür
- Kullanıcıya görsel olarak gösterilir
- OpenTelemetry ile kaydedilir

**Neden Önemli:** Kullanıcı deneyimi için şeffaflık sağlar ve performans sorunlarını tespit etmeye yardımcı olur.

### 5. Comprehensive Error Handling
- Detaylı hata mesajları
- Kullanıcı dostu Türkçe hatalar
- Retry butonu ile kolay yeniden deneme
- OpenTelemetry'de hata kaydı

### 7. SQLAlchemy ORM ve Veritabanı Yönetimi

**Veritabanı Mimarisi:**
```
PostgreSQL 16
├── chat_sessions tablo
│   ├── id (UUID, Primary Key)
│   ├── title (String, indexed)
│   ├── created_at (DateTime)
│   ├── updated_at (DateTime)
│   └── messages (Foreign Key relationship)
│
└── messages tablo
    ├── id (UUID, Primary Key)
    ├── session_id (UUID, Foreign Key → chat_sessions)
    ├── role (Enum: 'user' | 'assistant')
    ├── content (Text)
    ├── model (String, nullable)
    └── created_at (DateTime)
```

**Async ORM Kullanımı:**
- SQLAlchemy 2.0.25 async engine kullanarak yüksek performanslı veritabanı işlemleri
- asyncpg driver ile native PostgreSQL async bağlantıları
- Per-request ChatHistoryDBService ile dependency injection
- Tüm sorgulamalar async/await ile yapılır

**Neden Önemli:** Production ortamında yüksek concurrency altında bile performans düşüşü olmaz. Oturumlar veritabanında persiste edilir ve uygulama yeniden başlansa da tüm geçmiş korunur.

### 8. Oturum Yönetimi ve Persistence

**İki-katmanlı Oturum Takibi:**

1. **Backend Katmanı (Veritabanı):**
   - Her oturum PostgreSQL'de kaydedilir
   - ChatHistoryDBService async metodlar ile veritabanı işlemleri yönetir
   - Her HTTP isteği için bağımsız service instance (dependency injection)

2. **Frontend Katmanı (localStorage):**
   - Aktif oturum ID'si localStorage'da saklanır
   - Sayfa yenilense bile oturum devam eder
   - `activeSessionId` state'i ile React tarafında takip edilir

**Oturum Başlığı Yönetimi:**
- 5. mesaja kadar başlık otomatik olarak mesaja dayalı oluşturulur
- Kullanıcı double-click ile başlığı manuel olarak değiştirebilir
- PATCH endpoint'i ile başlık güncellemesi gerçekleştirilir
- UI'da 20 karaktere truncate edilir (tooltip'te tam başlık gösterilir)

**Neden Önemli:** Kullanıcı deneyiminin sürekli olmasını sağlar. Oturumlar kalıcı, başlıklar kişiselleştirilebilir, ve sayfa refresh'leri tüm bağlamı koruyor.

### 9. LaTeX/KaTeX Matematiksel Formül Desteği

**Teknoloji Stack:**
- `remark-math`: Markdown'da LaTeX syntax'ını tanır
- `rehype-katex`: KaTeX'i kullanarak formülleri render eder
- `katex` CSS: Matematiksel notasyon stillendirmesi

**Format Dönüşümü:**
```
Backend yanıtı: [ \int_0^{\infty} e^{-x^2} dx ]
Frontend işlemi: processLatexContent() fonksiyonu
Sonuç: $$ \int_0^{\infty} e^{-x^2} dx $$
Render: KaTeX tarafından matematiksel gösterim
```

**Neden Önemli:** Bilim, mühendislik ve matematik konularında AI yanıtlarının profesyonel görünümü için kullanıcı deneyimi önemli ölçüde iyileşir.



## 🏗️ Mimari

```
┌─────────────────────────────────────────────────────────────────────┐
│                            Docker Compose                           │
├─────────────────┬─────────────────┬─────────────────┬───────────────┤
│                 │                 │                 │               │
│    Frontend     │    Backend      │    Jaeger       │  OpenRouter   │
│   (React/TS)    │   (FastAPI)     │  (Tracing UI)   │     API       │
│                 │                 │                 │   (Harici)    │
│   Port: 3000    │   Port: 8000    │   Port: 16686   │               │
│                 │                 │                 │               │
│   ┌─────────┐   │   ┌─────────┐   │   ┌─────────┐   │               │
│   │ Nginx   │───┼──▶│ Uvicorn │───┼──▶│ Jaeger  │   │               │
│   │ (Proxy) │   │   │ (ASGI)  │   │   │ (OTLP)  │   │               │
│   └─────────┘   │   └────┬────┘   │   └─────────┘   │               │
│                 │        │        │                 │               │
│   Vite + React  │        ▼        │                 │               │
│   TailwindCSS   │   OpenRouter ───┼─────────────────┼──────────────▶│
│                 │   Service       │                 │               │
└─────────────────┴─────────────────┴─────────────────┴───────────────┘
```

### Veri Akışı

1. **Kullanıcı** → Frontend'de mesaj yazar
2. **Frontend** → `/api/chat` endpoint'ine POST isteği
3. **Rate Limiter** → İstek limitini kontrol eder
4. **Nginx** → İsteği backend'e proxy'ler
5. **Backend** → OpenRouter API'ye istek gönderir (retry logic ile)
6. **OpenRouter** → AI modelinden yanıt alır
7. **Backend** → Yanıtı cache'ler, trace'i Jaeger'a gönderir
8. **Frontend** → Yanıtı Markdown olarak render eder

---

## 🛠️ Teknik Seçimler ve Nedenleri

### Backend Teknolojileri

| Teknoloji | Seçim Nedeni |
|-----------|--------------|
| **Python 3.11** | Modern async özellikler, geniş kütüphane desteği, hızlı geliştirme |
| **FastAPI** | Yüksek performans, otomatik OpenAPI dokümantasyonu, native async desteği, Pydantic entegrasyonu |
| **SQLAlchemy 2.0** | Modern async ORM, type hints desteği, güçlü query builder |
| **PostgreSQL 16** | Production-ready ilişkisel veritabanı, güçlü veri türü desteği |
| **asyncpg** | PostgreSQL'in native async driver'ı, yüksek performans |
| **httpx** | Async HTTP istemci, HTTP/2 desteği, modern API, retry desteği |
| **Pydantic** | Type-safe veri validasyonu, otomatik JSON serialization |
| **OpenTelemetry** | Endüstri standardı dağıtık izleme, vendor-agnostic, OTLP protokolü |
| **prometheus-client** | Standart metrik formatı, Grafana uyumluluğu |

### Frontend Teknolojileri

| Teknoloji | Seçim Nedeni |
|-----------|--------------|
| **React 18** | Component tabanlı mimari, büyük ekosistem, hooks API |
| **TypeScript** | Compile-time hata yakalama, daha iyi IDE desteği, refactoring kolaylığı |
| **Vite** | Anında HMR, hızlı build, modern ESM desteği |
| **TailwindCSS** | Utility-first yaklaşım, hızlı prototipleme, dark mode desteği |
| **Lucide React** | Temiz, tutarlı ikon seti, tree-shaking desteği |
| **react-markdown** | Güvenli Markdown rendering, özelleştirilebilir component'ler |
| **react-syntax-highlighter** | 100+ dil desteği, tema uyumluluğu |

### Altyapı Teknolojileri

| Teknoloji | Seçim Nedeni |
|-----------|--------------|
| **Docker** | Tutarlı ortam, kolay dağıtım, izolasyon |
| **Docker Compose** | Multi-container orchestration, basit yapılandırma |
| **Nginx** | Yüksek performanslı reverse proxy, statik dosya servisi |
| **Jaeger** | Açık kaynak tracing UI, OTLP desteği, kolay kurulum |

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler

- **Docker** (20.10+)
- **Docker Compose** (2.0+)
- **OpenRouter API Key** (https://openrouter.ai/keys adresinden ücretsiz alınabilir)

### Adım 1: Projeyi Klonlayın

```bash
git clone https://github.com/your-username/madlen-case-study.git
cd madlen-case-study
```

### Adım 2: Ortam Değişkenlerini Ayarlayın

```bash
# .env dosyası oluşturun
cp .env.example .env

# .env dosyasını düzenleyip API anahtarınızı ekleyin
nano .env
```

**.env dosyası içeriği:**
```env
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
DEBUG=true
```

### Adım 3: Uygulamayı Başlatın

```bash
# Tüm servisleri build edip başlatın
docker-compose up --build

# Veya arka planda çalıştırmak için
docker-compose up -d --build
```

### Adım 4: Uygulamaya Erişin

| Servis | URL | Açıklama |
|--------|-----|----------|
| **Frontend** | http://localhost:3000 | Ana uygulama arayüzü |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Jaeger UI** | http://localhost:16686 | Trace görüntüleme |
| **Metrics** | http://localhost:8000/metrics | Prometheus metrikleri |
| **Health** | http://localhost:8000/health | Sağlık kontrolü |

### Durdurma

```bash
# Servisleri durdurun
docker-compose down

# Servisleri ve volume'ları temizleyin
docker-compose down -v
```

---

## 📚 API Dokümantasyonu

### Temel Endpoint'ler

#### Chat
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/chat` | Mesaj gönder ve AI yanıtı al |
| `GET` | `/api/chat/history` | Mevcut oturum geçmişini al |
| `POST` | `/api/chat/new-session` | Yeni sohbet oturumu başlat |
| `GET` | `/api/chat/sessions` | Tüm oturumları listele |
| `POST` | `/api/chat/sessions/{id}/switch` | Oturum değiştir |
| `PATCH` | `/api/chat/sessions/{id}` | Oturum başlığını güncelle |
| `DELETE` | `/api/chat/sessions/{id}` | Oturum sil |
| `POST` | `/api/chat/clear` | Geçmişi temizle |

#### Chat (DB ile)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `POST` | `/api/chat/db` | Mesaj gönder ve veritabanına kaydet |
| `GET` | `/api/chat/db/sessions` | Veritabanından tüm oturumları al |
| `GET` | `/api/chat/db/sessions/{id}` | Belirtilen oturumun detaylarını al |
| `PATCH` | `/api/chat/db/sessions/{id}` | Oturum başlığını güncellerle |
| `DELETE` | `/api/chat/db/sessions/{id}` | Oturumu veritabanından sil |
| `GET` | `/api/chat/db/history` | Geçerli oturumun geçmişini al |

#### Models
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/api/models` | Kullanılabilir modelleri listele |

#### Sistem
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| `GET` | `/health` | Sağlık kontrolü |
| `GET` | `/metrics` | Prometheus metrikleri |
| `GET` | `/docs` | Swagger UI |

### Rate Limit Header'ları

Her API yanıtında aşağıdaki header'lar bulunur:

```
X-RateLimit-Limit-Minute: 60
X-RateLimit-Remaining-Minute: 59
X-RateLimit-Limit-Hour: 500
X-RateLimit-Remaining-Hour: 499
X-Response-Time: 0.125s
```

### Örnek İstek

```bash
# Veritabanına kaydederek mesaj gönder
curl -X POST http://localhost:8000/api/chat/db \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Merhaba! Nasılsın?",
    "model": "meta-llama/llama-3.3-70b-instruct:free",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'

# Oturum başlığını güncelle
curl -X PATCH http://localhost:8000/api/chat/db/sessions/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Python Sohbeti"
  }'

# Modelleri listele
curl http://localhost:8000/api/models

# Veritabanından tüm oturumları al
curl http://localhost:8000/api/chat/db/sessions
```

---

## 🔍 OpenTelemetry ve Jaeger

### OpenTelemetry Entegrasyonu

Uygulama, kritik işlemler için kapsamlı OpenTelemetry enstrümantasyonu içerir:

#### Enstrümante Edilen Bileşenler

| Bileşen | Açıklama |
|---------|----------|
| **FastAPI** | Otomatik HTTP istek/yanıt tracing |
| **httpx** | OpenRouter API çağrıları tracing |
| **Chat Service** | Kullanıcı etkileşimleri |
| **OpenRouter Service** | AI model çağrıları |
| **Chat History** | Oturum yönetimi işlemleri |

#### Span Hierarchy

```
🔵 HTTP POST /api/chat
├── 📊 api.chat.send_message (ana işlem)
│   ├── event: "Adding user message to history"
│   ├── event: "Sending message to OpenRouter"
│   └── event: "Adding assistant response to history"
│
├── 🌐 openrouter.send_message (API çağrısı)
│   ├── event: "Sending request to OpenRouter"
│   ├── event: "Retry attempt 1/3" (hata durumunda)
│   └── event: "Response received successfully"
│
├── 💾 chat_history.add_message (user)
│   └── session_id, message_role
│
└── 💾 chat_history.add_message (assistant)
    └── session_id, message_role, model
```

### Jaeger Kurulum ve Kullanım

Jaeger, Docker Compose ile otomatik olarak başlatılır ve `http://localhost:16686` adresinde erişilebilir.

#### Jaeger UI'a Erişim

1. Tarayıcınızda **http://localhost:16686** adresini açın
2. **Service** dropdown'undan `chat-backend` seçin
3. **Find Traces** butonuna tıklayın

#### Trace Arama

| Filtre | Örnek | Açıklama |
|--------|-------|----------|
| **Service** | `chat-backend` | Servis adına göre filtrele |
| **Operation** | `POST /api/chat` | İşlem adına göre filtrele |
| **Tags** | `model.id=meta-llama/...` | Tag'e göre filtrele |
| **Min Duration** | `1s` | Minimum süreye göre filtrele |
| **Max Duration** | `10s` | Maksimum süreye göre filtrele |

#### Trace Analizi

Jaeger UI'da bir trace seçtiğinizde:

1. **Timeline View** - Span'ların zaman çizelgesi
2. **Span Details** - Her span'ın detaylı bilgileri
3. **Tags** - Span attribute'ları
4. **Logs/Events** - Span içindeki event'ler
5. **Process** - Servis bilgileri

### Trace'lerde Kaydedilen Bilgiler

| Kategori | Attribute | Açıklama |
|----------|-----------|----------|
| **Model** | `model.id` | Kullanılan model ID'si |
| | `model.provider` | Model sağlayıcısı (meta-llama, google, vb.) |
| **Mesaj** | `message.length` | Giriş mesajı karakter sayısı |
| | `message.word_count` | Giriş mesajı kelime sayısı |
| | `response.length` | Yanıt karakter sayısı |
| | `response.word_count` | Yanıt kelime sayısı |
| **Token** | `tokens.prompt` | Prompt token sayısı |
| | `tokens.completion` | Completion token sayısı |
| | `tokens.total` | Toplam token sayısı |
| **Performans** | `duration_seconds` | İşlem süresi |
| | `http.status_code` | HTTP durum kodu |
| **Oturum** | `session.id` | Aktif oturum ID'si |
| | `context.message_count` | Bağlamdaki mesaj sayısı |
| **Görsel** | `has_image` | Görsel içerip içermediği |
| | `image.media_type` | Görsel formatı |
| | `image.size_bytes` | Görsel boyutu |
| **Retry** | `retry.attempts` | Yeniden deneme sayısı |
| | `retry.exhausted` | Tüm denemeler tükendi mi |
| **Hata** | `error.type` | Hata türü |
| | `error.message` | Hata mesajı |

### Prometheus Metrikleri

`/metrics` endpoint'inden alınabilecek metrikler:

```prometheus
# HTTP istekleri
http_requests_total{method="POST", endpoint="/api/chat", status="200"}
http_request_duration_seconds_bucket{method="POST", endpoint="/api/chat"}

# Chat metrikleri
chat_requests_total{model="meta-llama/llama-3.3-70b-instruct:free", status="success"}
chat_request_duration_seconds_bucket{model="meta-llama/llama-3.3-70b-instruct:free"}
chat_message_length_chars_bucket{role="user"}
chat_message_length_chars_bucket{role="assistant"}

# Model kullanımı
model_usage_total{model_id="meta-llama/llama-3.3-70b-instruct:free"}

# OpenRouter API
openrouter_requests_total{model="...", status="success"}
openrouter_request_duration_seconds_bucket{model="..."}

# Oturum ve hatalar
active_sessions_count
errors_total{type="ValueError", endpoint="/api/chat"}
image_uploads_total{media_type="image/jpeg", status="success"}
```

---

## 📁 Proje Yapısı

```
madlen-case-study/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI uygulama başlangıcı
│   │   ├── config.py            # Yapılandırma ve ortam değişkenleri
│   │   ├── database.py          # SQLAlchemy async engine ve session
│   │   ├── models/              # SQLAlchemy ORM modelleri
│   │   │   ├── __init__.py
│   │   │   └── chat.py          # ChatSession ve Message modelleri
│   │   ├── middleware/          # Middleware modülleri
│   │   │   ├── __init__.py
│   │   │   └── rate_limit.py    # Rate limiting middleware
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py          # Chat endpoint'leri
│   │   │   ├── chat_db.py       # Chat + veritabanı endpoint'leri
│   │   │   └── models.py        # Model endpoint'leri
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── chat.py          # Pydantic şemaları
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── openrouter.py    # OpenRouter API servisi (retry logic)
│   │   │   ├── chat_history.py  # Sohbet geçmişi yönetimi (async)
│   │   │   └── chat_db.py       # ChatHistoryDBService (SQLAlchemy async)
│   │   └── telemetry/
│   │       ├── __init__.py
│   │       ├── setup.py         # OpenTelemetry yapılandırması
│   │       └── metrics.py       # Prometheus metrikleri
│   ├── conftest.py              # pytest yapılandırması
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx       # Üst menü ve model seçici
│   │   │   ├── Sidebar.tsx      # Sohbet geçmişi sidebar'ı (editable titles)
│   │   │   ├── ChatInput.tsx    # Mesaj giriş alanı
│   │   │   ├── ChatMessage.tsx  # Markdown + LaTeX + Syntax Highlighting
│   │   │   ├── MessageList.tsx  # Mesaj listesi
│   │   │   ├── ModelSelector.tsx# Model seçim dropdown'u
│   │   │   ├── ImageUpload.tsx  # Görsel yükleme + sıkıştırma
│   │   │   ├── ThemeToggle.tsx  # Dark/Light mode geçişi
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.ts           # API istemci fonksiyonları
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript tip tanımları
│   │   ├── App.tsx              # Ana uygulama bileşeni (session state + localStorage)
│   │   └── main.tsx             # React giriş noktası
│   ├── package.json
│   ├── tailwind.config.js
│   ├── nginx.conf
│   └── Dockerfile
│
├── docker-compose.yml           # Multi-container yapılandırması
├── .env.example                 # Örnek ortam değişkenleri
└── README.md                    # Bu dosya
```

---

## 🐛 Sorun Giderme

### Docker Daemon Çalışmıyor
```bash
# Docker Desktop'ı başlatın veya
sudo systemctl start docker
```

### Port Çakışması
```bash
# 3000 veya 8000 portunu kullanan işlemi bulun
lsof -i :3000
lsof -i :8000

# İşlemi durdurun
kill -9 <PID>
```

### API Key Hatası
`.env` dosyasında `OPENROUTER_API_KEY` değişkeninin doğru ayarlandığından emin olun.

### Rate Limit Hatası (429)
```bash
# 429 Too Many Requests hatası alıyorsanız
# Retry-After header'ını kontrol edin ve bekleyin
curl -I http://localhost:8000/api/chat
```

### Jaeger'da Trace Görünmüyor
```bash
# Jaeger container'ının çalıştığını kontrol edin
docker-compose ps

# Jaeger loglarını kontrol edin
docker-compose logs jaeger

# Backend'in Jaeger'a bağlandığını kontrol edin
docker-compose logs backend | grep -i "telemetry\|jaeger\|otlp"
```

### Logları Görüntüleme
```bash
# Tüm servis logları
docker-compose logs -f

# Sadece backend logları
docker-compose logs -f backend

# Sadece frontend logları
docker-compose logs -f frontend
```

---

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.

---

**Madlen - Great Teachers Great Futures! 🎓**
