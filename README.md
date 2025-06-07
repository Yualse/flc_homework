# Bulanık Mantık ile Oda Sıcaklığı Denetleyicisi

Bu proje, **Soru 1 - Mamdani Tipi Oda Sıcaklığı Denetleyicisi** ödevi kapsamında geliştirilmiştir. Amaç, Python ve `scikit-fuzzy` kütüphanesi kullanılarak, değişken dış ortam koşulları altında bir odanın sıcaklığını istenen hedef değerde tutan bir bulanık mantık denetleyicisi tasarlamak, simüle etmek ve performansını analiz etmektir.

## Projenin Amacı

25 m²'lik bir odanın sıcaklığını, 2 kW'lık bir elektrikli ısıtıcı kullanarak 22°C'de sabit tutmak. Sistem, dış ortam sıcaklığındaki ani değişimlere (bozucu etki) karşı sağlam (robust) olmalı ve hedefe minimum aşım (overshoot) ve hızlı bir yerleşme süresi (settling time) ile ulaşmalıdır.

**Metodoloji:** Proje, aşağıdaki adımları izleyerek geliştirilmiştir:

1.  **Sistem Modelleme:** Verilen diferansiyel denklemin analizi.

2.  **Fiziksel Sınırlılıkların Tespiti:** Sistemin hedefe ulaşıp ulaşamayacağının matematiksel olarak incelenmesi ve minimum sistem kazancının (`K_min`) hesaplanması.

3.  **Bulanık Mantık Tasarımı:**

    -   Giriş/çıkış değişkenlerinin ve üyelik fonksiyonlarının tanımlanması.

    -   Çıkış üyelik fonksiyonlarının, sistemin fiziksel gereksinimlerine (denge gücü) göre özel olarak tasarlanması.

    -   Kararlılık ve performansı dengeleyen 5x5'lik bir Mamdani kural tabanının iteratif olarak geliştirilmesi.
    
4.  **Simülasyon ve Analiz:** Farklı sistem parametreleri (`K=1`, `K=8.5`, `K=10`) altında denetleyici performansının test edilmesi ve sonuçların nicel metriklerle (Aşım, Yerleşme Süresi, IAE, RMSE) değerlendirilmesi.

## 1. Sistem Modeli

Odanın termal davranışı, Newton'un Soğuma Yasası'nı temel alan aşağıdaki birinci dereceden diferansiyel denklem ile modellenmiştir:

$$
\frac{dT_{oda}}{dt} = -\frac{1}{\tau} \cdot [T_{oda}(t) - T_{dış}(t)] + \frac{K}{\tau} \cdot u(t)
$$

Burada;
- $T_{oda}(t)$: Odanın anlık sıcaklığı (°C)

- $T_{dış}(t)$: Dış ortamın anlık sıcaklığı (°C)

- $u(t)$: Isıtıcının kontrol gücü (kW)

- $\tau$: Sistemin zaman sabiti (s), odanın termal tembelliğini temsil eder.

- $K$: Sistemin kazancı (°C/kW), ısıtıcı gücünün sıcaklık üzerindeki etkinliğini temsil eder.

## 2. Fiziksel Sınırlılıkların Tespiti ve (`K_min`) Değerinin Tayini


Bir kontrol sisteminin başarısı, sadece denetleyicinin zekasına değil, aynı zamanda kontrol edilecek sistemin (plant) fiziksel limitlerine de bağlıdır. Bu nedenle, tasarıma başlamadan önce sistemin hedefe ulaşıp ulaşamayacağı analitik olarak incelenmiştir.

### 2.1. Denge Durumu Analizi

Sistemin kararlı bir sıcaklığa ulaştığı denge durumunda, sıcaklığın zamanla değişimi sıfır olur ($\frac{dT_{oda}}{dt} = 0$). Bu koşulu ana denklemde yerine koyarsak:

$$
0 = -\frac{1}{\tau} \cdot [T_{denge} - T_{dış}] + \frac{K}{\tau} \cdot u_{denge}
$$

Denklemi $u_{denge}$ için düzenlediğimizde, belirli bir sıcaklığı korumak için gereken denge gücünü buluruz:

$$
\frac{K}{\tau} \cdot u_{denge} = \frac{1}{\tau} \cdot [T_{denge} - T_{dış}]
$$

$$
\implies u_{denge} = \frac{T_{denge} - T_{dış}}{K}
$$

Bu denklem, projenin geri kalanındaki tüm tasarım kararlarının temelini oluşturur.

### 2.2. Minimum Sistem Kazancının (`K_min`) Tayini

Sistemin 22°C hedefine ulaşabilmesi için, en zorlu koşulda bile ısıtıcının gücünün bu hedefi korumaya yetmesi gerekir.

- **En Zorlu Koşul:** $T_{dış} = 5°C$ iken $T_{hedef} = 22°C$'yi korumak.
- **Sistem Limiti:** Isıtıcının maksimum gücü $u_{max} = 2.0 kW$.

Bu değerleri denge denklemine yerleştirerek, gereken minimum `K` kazancını hesaplayabiliriz:

$$
K_{min} = \frac{T_{hedef} - T_{dış,min}}{u_{max}} = \frac{22 - 5}{2.0} = \frac{17}{2.0} = 8.50
$$

**Analitik Sonuç:** Bu sistemi 22°C hedefine ulaştırabilmek için gereken minimum `K` değeri **8.50**'dir.

Bu sonuç, ödevde başlangıçta verilen `K=1` değeriyle hedefe ulaşmanın **fiziksel olarak imkansız** olduğunu matematiksel olarak kanıtlamıştır. Ayrıca, `K=8.50` ile yapılan testler, sistemin bozucu etki altında kararlılığını yitirdiğini göstermiştir. Bu nedenle, bir **güvenlik payı (safety margin)** bırakılarak nihai ve başarılı tasarımda **`K=10.0`** değeri kullanılmıştır.

### Model Parametreleri
- **Hedef Sıcaklık (`Thedef`):** 22 °C
- **Zaman Sabiti (`τ`):** 300 s
- **Sistem Kazancı (`K`):** 10.0
  - *Not: Kod modüler bir yapıyla tasarlanmış olduğu için istenildiği takdirde değiştirilebilir fakat hem iteratif yöntemlerle hem de matematiksel yöntemlerle K=1 değeriyle sistemin başarılı olmayacağı farkedildiği için K=10 değerine göre sistem optimize edilmiştir.*
- **Isıtıcı Gücü (`u`):** [0, 2] kW aralığında denetleyici tarafından belirlenen değer.
- **Dış Sıcaklık (`Tdış`):**
  - 0-30 dakika: 10 °C
  - 30-60 dakika: 5 °C

## Denetleyici Tasarımı

Denetleyici, Mamdani tipi bir bulanık çıkarım sistemi olarak tasarlanmıştır.

### 1. Linguistik Değişkenler
- **Giriş 1: Hata (`e`)**
  - `e = Thedef - Toda`
  - Evren: [-15, 15] °C
- **Giriş 2: Hata Türevi (`e'`)**
  - Hatanın değişim hızı.
  - Evren: [-1, 1] °C/s
- **Çıkış: Isıtıcı Gücü (`u`)**
  - Isıtıcının çalışma gücü.
  - Evren: [0, 2] kW

### 2. Üyelik Fonksiyonları ve Dilsel Terimler
Tüm değişkenler için 5 adet üçgensel üyelik fonksiyonu ve `NB, NS, Z, PS, PB` dilsel terimleri kullanılmıştır. Çıkış değişkeni olan `isitici_gucu`'nun `Z` (Orta) etiketi, en zorlu koşuldaki denge gücü olan `1.7 kW`'ı merkez alacak şekilde tasarlanmıştır. Bu, denetleyicinin hedefe kilitlenmesini önleyen en kritik tasarım kararıdır.

### 3. Kural Tabanı
5x5'lik kural tabanı, k = 10 durumunda, en zorlu koşulda sistemin dengeye ulaşmasına yönelik tasarlanmıştır. Bu strateji, hedefe ulaşma kararlılığı ile hedefe yakınken yapılan hassas ayar arasında bir denge kurar.

| Hata(`e`)\`e'`| NB | NS | Z  | PS | PB |
|:-------------:|:--:|:--:|:--:|:--:|:--:|
|     **PB**    | PB | PB | PB | PS | Z  |
|     **PS**    | PB | PS | PS | Z  | NS |
|     **Z**     | PS | PS | Z  | Z  | NS |
|     **NS**    | NS | NS | NB | NB | NB |
|     **NB**    | NS | NB | NB | NB | NB |

## Kurulum ve Çalıştırma

1.  **Gerekli Kütüphaneler:**
    Projenin çalışması için aşağıdaki Python kütüphanelerinin yüklü olması gerekmektedir:
    ```bash
    pip install numpy
    pip install scikit-fuzzy
    pip install matplotlib
    ```

2.  **Çalıştırma:**
    Proje ana dizinindeyken, terminal üzerinden aşağıdaki komutu çalıştırın:
    ```bash
    python <dosya_adi>.py
    ```
    Script çalıştığında, önce konsola simülasyon adımlarını ve performans metriklerini yazdıracak, ardından simülasyon grafiğini bir pencerede gösterecektir.

2.  **Senaryoları Test Etme:**
    Script dosyasındaki `K` değişkeninin değerini değiştirerek üç ana senaryoyu test edebilirsiniz:
    ```python
    # K = 1.0   # Fiziksel olarak imkansız senaryo
    # K = 8.5   # Teorik minimum, kırılgan senaryo
    K = 10.0  # Güvenlik payı içeren, başarılı senaryo
    ```
    Scripti çalıştırdığınızda, konsolda detaylı bir analiz ve ham metrik değerleri basılacak, ardından sonuç grafiği gösterilecektir.

## Sonuçların Karşılaştırılması ve Nihai Performans

| Metrik                      | K = 1.0 (İmkansız) | K = 8.5 (Kırılgan) | K = 10.0 (Başarılı) |
| --------------------------- | ------------------ | ------------------ | ------------------- |
| **Aşım Yüzdesi (%)**        | 0.00               | 0.28               | **0.53**            |
| **Yerleşme Süresi (dk)**    | Yerleşemedi        | Yerleşemedi        | **4.42**            |
| **IAE (∫\|e\|dt)**          | 37456.88           | 4555.84            | **1705.76**         |
| **RMSE (√Σe²/N)**           | 10.74              | 2.20               | **1.76**            |

## Örnek Çıktı
--- Minimum Sistem Kazancı (K) Analizi ---

Hedef Sıcaklık: 22.0°C

En Zorlu Dış Ortam Sıcaklığı: 5.0°C

Maksimum Isıtıcı Gücü: 2.0 kW

Bu sistemi 22.0°C hedefine ulaştırabilmek için gereken minimum K değeri: 8.50

----------------------------------------

--- Simülasyon Başlatılıyor (Fiziğe Dayalı Nihai Tasarım, K=10) ---

Zaman:  0 dk | Oda Sıcaklığı: 10.00°C | Hata (e): 12.00 | Güç (u): 1.98 kW

Zaman:  5 dk | Oda Sıcaklığı: 21.65°C | Hata (e):  0.35 | Güç (u): 1.75 kW

Zaman: 10 dk | Oda Sıcaklığı: 22.12°C | Hata (e): -0.12 | Güç (u): 1.21 kW

Zaman: 15 dk | Oda Sıcaklığı: 22.12°C | Hata (e): -0.12 | Güç (u): 1.21 kW

Zaman: 20 dk | Oda Sıcaklığı: 22.12°C | Hata (e): -0.12 | Güç (u): 1.21 kW

Zaman: 25 dk | Oda Sıcaklığı: 22.12°C | Hata (e): -0.12 | Güç (u): 1.21 kW

Zaman: 30 dk | Oda Sıcaklığı: 22.12°C | Hata (e): -0.12 | Güç (u): 1.21 kW

Zaman: 35 dk | Oda Sıcaklığı: 22.00°C | Hata (e): -0.00 | Güç (u): 1.70 kW

Zaman: 40 dk | Oda Sıcaklığı: 22.00°C | Hata (e): -0.00 | Güç (u): 1.70 kW

Zaman: 45 dk | Oda Sıcaklığı: 22.00°C | Hata (e): -0.00 | Güç (u): 1.70 kW

Zaman: 50 dk | Oda Sıcaklığı: 22.00°C | Hata (e): -0.00 | Güç (u): 1.70 kW

Zaman: 55 dk | Oda Sıcaklığı: 22.00°C | Hata (e): -0.00 | Güç (u): 1.70 kW

Zaman: 60 dk | Oda Sıcaklığı: 22.00°C

--- Simülasyon Tamamlandı ---



--- Performans Metrikleri Analizi ---

1. Aşım (Overshoot):

   - En Yüksek Sıcaklık: 22.12 °C

   - Aşım Miktarı: 0.12 °C

   - Aşım Yüzdesi: %0.53

3. Yerleşme Süresi (Settling Time):

   - Tanım: Sıcaklığın [±%5] yani [20.90°C, 23.10°C] bandına kalıcı olarak girdiği an.

   - Sonuç: Sistem 4.42. dakikada kalıcı olarak banda girmiştir.

5. Genel Hata Ölçütleri:

   - IAE (Integral of Absolute Error): 1705.76 °C·s

   - RMSE (Root Mean Square Error): 1.76 °C

--- HAM DEĞERLER (RAW VALUES) ---

en_yuksek_sicaklik: 22.1163

asim_yuzdesi: 0.5285

yerlesme_suresi_dakika: 4.4167

iae: 1705.7552

rmse: 1.7605

--- Analiz Tamamlandı ---
### Tartışma
Tablo, `K` değerinin sistem performansı üzerindeki kritik etkisini net bir şekilde göstermektedir.
- `K=1` senaryosu, devasa bir kalıcı durum hatasıyla sonuçlanmıştır.
- `K=8.5` senaryosu, aşımı neredeyse sıfırlasa da bozucu etki altında kararlılığını koruyamamış ve hedeften sapmıştır. Yüksek IAE değeri, hedeften uzakta geçirilen sürenin fazlalığını gösterir.
- **`K=10` senaryosu**, diğerlerine göre biraz daha fazla aşım yapma pahasına, **her koşulda hedefe yerleşmeyi başaran tek tasarımdır.** En düşük IAE ve RMSE değerlerine sahip olması, genel hata performansının en iyi olduğunu kanıtlar.
