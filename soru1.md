# 📡 Mamdani Tipi Oda Sıcaklığı Denetleyicisi

Bu proje, **Bulanık Mantık Kontrolü – Ödev 3 / Soru 1** kapsamında geliştirilmiştir. Amaç, Python ve `scikit-fuzzy` kütüphanesi kullanarak bir odanın sıcaklığını değişken dış ortam koşullarında istenen hedef değerde tutan bir **Mamdani tipi bulanık denetleyici** tasarlamak, simüle etmek ve analiz etmektir.

## 🎯 Projenin Amacı

- **Hedef:** 25 m²'lik bir odayı, 2 kW elektrikli ısıtıcı ile 22°C sıcaklıkta sabit tutmak.
- **Zorluk:** Dış ortam sıcaklığı zamanla değişmektedir (ilk 30 dk 10°C, sonra 5°C).
- **Performans Kriterleri:** Minimum aşım (overshoot), kısa yerleşme süresi (settling time) ve düşük hata değerleri (IAE, RMSE).

---

## 🔬 Sistem Modeli

Termal sistem şu diferansiyel denklem ile modellenmiştir:

$$
\frac{dT_{oda}}{dt} = -\frac{1}{\tau} \cdot [T_{oda}(t) - T_{dış}(t)] + \frac{K}{\tau} \cdot u(t)
$$

**Model Parametreleri:**

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| `τ`       | 300 s | Zaman sabiti |
| `K`       | 10.0  | Sistem kazancı (°C/kW) |
| `Thedef`  | 22 °C | Hedef sıcaklık |
| `u(t)`    | [0, 2.0] kW | Isıtıcı gücü |
| `T_dış`   | 10°C (0–30dk), 5°C (30–60dk) | Dış sıcaklık profili |

---

## 📐 Fiziksel Sınırlamalar ve `K_min` Hesabı

Sistemin hedef sıcaklığa ulaşabilmesi için minimum sistem kazancı:

$$
K_{min} = \frac{T_{hedef} - T_{dış,min}}{u_{max}} = \frac{22 - 5}{2} = 8.50
$$

Bu nedenle **`K=10.0`** güvenlik payı ile kullanılmıştır.

---

## 🤖 Denetleyici Tasarımı

### 🎛️ Linguistik Değişkenler

- **Giriş 1:** Hata `e = Thedef - Toda` ∈ [-10, 15]
- **Giriş 2:** Hata türevi `ė` ∈ [-1, 1]
- **Çıkış:** Isıtıcı gücü `u` ∈ [0, 2]

### 📊 Üyelik Fonksiyonları

Her değişken için 5 üçgensel üyelik fonksiyonu tanımlanmıştır: `NB`, `NS`, `Z`, `PS`, `PB`.

- Çıkışın “Z” etiketi 1.7 kW merkezlidir (denge gücü).
- Isıtıcı gücü fiziksel sistem gereksinimlerine göre asimetrik tanımlanmıştır.

### 📋 Kural Tabanı (5x5)

| Hata (`e`) \ ė | NB | NS | Z | PS | PB |
|----------------|----|----|---|----|----|
| **PB**         | PB | PB | PB | PS | Z  |
| **PS**         | PB | PS | PS | Z  | NS |
| **Z**          | PS | PS | Z  | Z  | NS |
| **NS**         | NS | NS | NB | NB | NB |
| **NB**         | NS | NB | NB | NB | NB |

---

## 🧪 Simülasyon

- Süre: 60 dakika
- Zaman adımı: 1 saniye
- Simülasyon boyunca `Toda(t)` ve `u(t)` izlenmiştir.

---

## 📈 Performans Analizi

### Hesaplanan Metrikler:

| Metrik | Açıklama |
|--------|----------|
| **Overshoot (%)** | Hedefin ne kadar aşıldığı |
| **Settling Time (dk)** | Hedef ±%5 bandına kalıcı giriş süresi |
| **IAE (°C·s)** | Toplam mutlak hata |
| **RMSE (°C)** | Hataların kare ortalaması |

### Örnek Sonuç (`K=10`):

```
Overshoot: %0.53
Settling Time: 4.42 dk
IAE: 1705.76 °C·s
RMSE: 1.76 °C
```

---

## 💻 Kurulum ve Çalıştırma

### 🔧 Gerekli Kütüphaneler

```bash
pip install numpy matplotlib scikit-fuzzy
```

### 🚀 Çalıştırmak için:

```bash
python soru_1_1.py
```

---

## 📊 Farklı `K` Senaryoları

| K Değeri | Durum | Overshoot (%) | Settling Time | IAE | RMSE |
|----------|-------|----------------|----------------|-----|------|
| 1.0      | Yetersiz (imkansız) | 0.00 | Yerleşemedi | 37456.88 | 10.74 |
| 8.5      | Kırılgan | 0.28 | Yerleşemedi | 4555.84 | 2.20 |
| **10.0** | ✅ Başarılı | **0.53** | **4.42 dk** | **1705.76** | **1.76** |

---

## 📚 Kaynakça

- Ödev Belgesi: `FLC_hw3.pdf`
- Eğitmen: Dr. Öğr. Üyesi İlhan Tunç – Bahar 2025
- Kullanılan araç: `scikit-fuzzy`, `matplotlib`, `numpy`

---

## 🧠 Sonuç ve Değerlendirme

Bu çalışma, bulanık mantık denetleyicisinin fiziksel sistemle uyumlu bir şekilde tasarlanmasının ne kadar önemli olduğunu göstermektedir. Uygun üyelik fonksiyonları ve mantıklı bir kural tabanı ile, sistem:

- Hedef sıcaklığa hızla ve kararlı biçimde ulaşmış,
- Dış sıcaklık değişimlerine rağmen dengeyi korumuş,
- Hataları minimumda tutarak verimli bir kontrol gerçekleştirmiştir.

**En yüksek başarı**, `K=10.0` değeri ile elde edilmiştir.
