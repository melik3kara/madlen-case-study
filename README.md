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
- [Mimari](#-mimari)
- [Teknik Seçimler ve Nedenleri](#-teknik-seçimler-ve-nedenleri)
- [Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
- [API Dokümantasyonu](#-api-dokümantasyonu)
- [OpenTelemetry ve Jaeger](#-opentelemetry-ve-jaeger)
- [Proje Yapısı](#-proje-yapısı)

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

### Frontend Özellikleri
- 🎨 **Modern UI** - Sıcak renk paleti (sarı/turuncu/kırmızı)
- 🌓 **Dark/Light Mode** - Tema tercihi localStorage'da saklanır
- 📱 **Responsive Tasarım** - Mobil uyumlu arayüz
- 📚 **Sohbet Geçmişi Sidebar'ı** - Katlanabilir oturum listesi
- 🖼️ **Görsel Yükleme** - Sürükle & bırak + otomatik sıkıştırma
- ⏳ **Loading States** - Yazma göstergesi ve hata mesajları

---

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
3. **Nginx** → İsteği backend'e proxy'ler
4. **Backend** → OpenRouter API'ye istek gönderir
5. **OpenRouter** → AI modelinden yanıt alır
6. **Backend** → Yanıtı cache'ler, trace'i Jaeger'a gönderir
7. **Frontend** → Yanıtı kullanıcıya gösterir

---

## 🛠️ Teknik Seçimler ve Nedenleri

### Backend Teknolojileri

| Teknoloji | Seçim Nedeni |
|-----------|--------------|
| **Python 3.11** | Modern async özellikler, geniş kütüphane desteği, hızlı geliştirme |
| **FastAPI** | Yüksek performans, otomatik OpenAPI dokümantasyonu, native async desteği, Pydantic entegrasyonu |
| **httpx** | Async HTTP istemci, HTTP/2 desteği, modern API |
| **Pydantic** | Type-safe veri validasyonu, otomatik JSON serialization |
| **OpenTelemetry** | Endüstri standardı dağıtık izleme, vendor-agnostic |
| **prometheus-client** | Standart metrik formatı, Grafana uyumluluğu |

### Frontend Teknolojileri

| Teknoloji | Seçim Nedeni |
|-----------|--------------|
| **React 18** | Component tabanlı mimari, büyük ekosistem, hooks API |
| **TypeScript** | Compile-time hata yakalama, daha iyi IDE desteği, refactoring kolaylığı |
| **Vite** | Anında HMR, hızlı build, modern ESM desteği |
| **TailwindCSS** | Utility-first yaklaşım, hızlı prototipleme, dark mode desteği |
| **Lucide React** | Temiz, tutarlı ikon seti, tree-shaking desteği |

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
# .env dosyası oluşturun (zaten mevcutsa bu adımı atlayın)
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
| `DELETE` | `/api/chat/sessions/{id}` | Oturum sil |
| `POST` | `/api/chat/clear` | Geçmişi temizle |

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

### Örnek İstek

```bash
# Mesaj gönder
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Merhaba! Nasılsın?",
    "model": "meta-llama/llama-3.3-70b-instruct:free"
  }'

# Modelleri listele
curl http://localhost:8000/api/models
```

---

## 🔍 OpenTelemetry ve Jaeger

### Jaeger UI'a Erişim

1. Tarayıcınızda **http://localhost:16686** adresini açın
2. **Service** dropdown'undan `chat-backend` seçin
3. **Find Traces** butonuna tıklayın

### Trace Yapısı

Her chat isteği aşağıdaki span hiyerarşisini oluşturur:

```
POST /api/chat (toplam süre)
├── api.chat.send_message
│   ├── model.id: meta-llama/llama-3.3-70b-instruct:free
│   ├── model.provider: meta-llama
│   ├── message.length: 25
│   ├── message.word_count: 4
│   ├── response.length: 150
│   ├── response.word_count: 25
│   ├── tokens.prompt: 38
│   ├── tokens.completion: 45
│   ├── tokens.total: 83
│   └── duration_seconds: 2.5
│
├── openrouter.send_message
│   ├── api.endpoint: https://openrouter.ai/api/v1/chat/completions
│   ├── http.status_code: 200
│   └── response.finish_reason: stop
│
├── chat_history.add_message (user)
│   ├── session_id: abc-123
│   └── message_role: user
│
└── chat_history.add_message (assistant)
    ├── session_id: abc-123
    └── message_role: assistant
```

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
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py          # Chat endpoint'leri
│   │   │   └── models.py        # Model endpoint'leri
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── chat.py          # Pydantic şemaları
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── openrouter.py    # OpenRouter API servisi
│   │   │   └── chat_history.py  # Sohbet geçmişi yönetimi
│   │   └── telemetry/
│   │       ├── __init__.py
│   │       ├── setup.py         # OpenTelemetry yapılandırması
│   │       └── metrics.py       # Prometheus metrikleri
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.tsx       # Üst menü ve model seçici
│   │   │   ├── Sidebar.tsx      # Sohbet geçmişi sidebar'ı
│   │   │   ├── ChatInput.tsx    # Mesaj giriş alanı
│   │   │   ├── ChatMessage.tsx  # Mesaj baloncuğu
│   │   │   ├── MessageList.tsx  # Mesaj listesi
│   │   │   ├── ModelSelector.tsx# Model seçim dropdown'u
│   │   │   ├── ImageUpload.tsx  # Görsel yükleme
│   │   │   ├── ThemeToggle.tsx  # Dark/Light mode geçişi
│   │   │   └── ...
│   │   ├── services/
│   │   │   └── api.ts           # API istemci fonksiyonları
│   │   ├── types/
│   │   │   └── index.ts         # TypeScript tip tanımları
│   │   ├── App.tsx              # Ana uygulama bileşeni
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
