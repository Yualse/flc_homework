# =============================================================================
# BULANIK MANTIK KONTROL - ODA SICAKLIĞI DENETLEYİCİSİ
#
# İsim: Alperen Burak Temiz
# No: 22406601004
# Tarih: 6 Haziran 2025
#
# Açıklama: Bu betik, bir odanın sıcaklığını hedef değerde tutmak için
# Mamdani tipi bir bulanık mantık denetleyicisi tasarlar, simüle eder
# ve performansını analiz eder.
# =============================================================================

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# 1. LINGUISTIC DEĞİŞKENLER VE ÜYELİK FONKSİYONLARI
# -----------------------------------------------------------------------------

# --- Değişkenlerin ve Evren Sınırlarının Tanımlanması ---
# Girişler (Antecedents)
e = ctrl.Antecedent(np.arange(-10, 16, 1), 'error')         # Hata (e)
edot = ctrl.Antecedent(np.arange(-1, 1.1, 0.1), 'error_dot') # Hata Türevi (edot)

# Çıkış (Consequent)
u = ctrl.Consequent(np.arange(0, 2.1, 0.1), 'control_output') # Kontrol Çıkışı (u)

# --- Üyelik Fonksiyonları (MF) Tanımları ---
# Dilsel terimler: nb, ns, z, ps, pb

# Hata (e) için MF'ler
e['nb'] = fuzz.trimf(e.universe, [-10, -10, -5])
e['ns'] = fuzz.trimf(e.universe, [-7.5, -3.5, 0])
e['z']  = fuzz.trimf(e.universe, [-2.5, 0, 2.5])
e['ps'] = fuzz.trimf(e.universe, [0, 5, 10])
e['pb'] = fuzz.trimf(e.universe, [7.5, 15, 15])

# Hata Türevi (edot) için MF'ler
edot['nb'] = fuzz.trimf(edot.universe, [-1, -1, -0.5])
edot['ns'] = fuzz.trimf(edot.universe, [-0.75, -0.25, 0])
edot['z']  = fuzz.trimf(edot.universe, [-0.2, 0, 0.2])
edot['ps'] = fuzz.trimf(edot.universe, [0, 0.25, 0.75])
edot['pb'] = fuzz.trimf(edot.universe, [0.5, 1, 1])

# Isıtıcı Gücü (u) için FİZİĞE DAYALI MF'ler
# 'z' (orta) gücün merkezi, Tdış=5°C için denge gücü olan 1.7 kW'ı referans alır.
u['nb'] = fuzz.trimf(u.universe, [0, 0, 1.2])           # Kapalı/Çok Düşük
u['ns'] = fuzz.trimf(u.universe, [1.0, 1.3725, 1.75])   # Düşük (Ama yine de güçlü)
u['z']  = fuzz.trimf(u.universe, [1.65, 1.7, 1.75])     # Denge Gücü
u['ps'] = fuzz.trimf(u.universe, [1.7, 1.85, 2.0])      # Yüksek
u['pb'] = fuzz.trimf(u.universe, [1.9, 2.0, 2.0])       # Tam Güç

# -----------------------------------------------------------------------------
# 2. KURAL TABANI (RULE BASE)
# -----------------------------------------------------------------------------
# "Altın Oran" kural tabanı: Hız ve stabilite arasında denge kurar.
kural_listesi = [
    # Hata\Ė |   NB    |    NS   |    Z    |    PS   |    PB
    #----------------------------------------------------------
    # PB     |   PB    |    PB   |    PB   |    PS   |    Z
    ctrl.Rule(e['pb'] & edot['nb'], u['pb']),
    ctrl.Rule(e['pb'] & edot['ns'], u['pb']),
    ctrl.Rule(e['pb'] & edot['z'],  u['pb']),
    ctrl.Rule(e['pb'] & edot['ps'], u['ps']),
    ctrl.Rule(e['pb'] & edot['pb'], u['z']),

    # PS     |   PB    |    PS   |    PS   |    Z    |    NS
    ctrl.Rule(e['ps'] & edot['nb'], u['pb']),
    ctrl.Rule(e['ps'] & edot['ns'], u['ps']),
    ctrl.Rule(e['ps'] & edot['z'],  u['ps']),
    ctrl.Rule(e['ps'] & edot['ps'], u['z']),
    ctrl.Rule(e['ps'] & edot['pb'], u['ns']),

    # Z      |   PS    |    PS   |    Z    |    Z    |    NS
    ctrl.Rule(e['z'] & edot['nb'], u['ps']),
    ctrl.Rule(e['z'] & edot['ns'], u['ps']),
    ctrl.Rule(e['z'] & edot['z'],  u['z']),
    ctrl.Rule(e['z'] & edot['ps'], u['z']),
    ctrl.Rule(e['z'] & edot['pb'], u['ns']),

    # NS     |   NS    |    NS   |    NB   |    NB   |    NB
    ctrl.Rule(e['ns'] & edot['nb'], u['ns']),
    ctrl.Rule(e['ns'] & edot['ns'], u['ns']),
    ctrl.Rule(e['ns'] & edot['z'],  u['nb']),
    ctrl.Rule(e['ns'] & edot['ps'], u['nb']),
    ctrl.Rule(e['ns'] & edot['pb'], u['nb']),

    # NB     |   NS    |    NB   |    NB   |    NB   |    NB
    ctrl.Rule(e['nb'] & edot['nb'], u['ns']),
    ctrl.Rule(e['nb'] & edot['ns'], u['nb']),
    ctrl.Rule(e['nb'] & edot['z'],  u['nb']),
    ctrl.Rule(e['nb'] & edot['ps'], u['nb']),
    ctrl.Rule(e['nb'] & edot['pb'], u['nb']),
]

# -----------------------------------------------------------------------------
# 3. KONTROL SİSTEMİ (CONTROL SYSTEM)
# -----------------------------------------------------------------------------
# Min-max kompozisyon ve centroid durulaştırma varsayılan olarak kullanılır.
denetleyici_sistemi = ctrl.ControlSystem(rules=kural_listesi)
denetleyici = ctrl.ControlSystemSimulation(denetleyici_sistemi)

print("--- Tasarlanan Üyelik Fonksiyonları Gösteriliyor ---")

# Tek bir pencere (fig) ve içinde 3 adet alt-grafik alanı (axes) oluştur.
fig_mf, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(10, 12))

# Fonksiyon 1: Hata (e)
ax0.set_title('Hata (e) Değişkeni Üyelik Fonksiyonları', fontsize=12)
for etiket, mf in e.terms.items():
    y_degerleri = fuzz.interp_membership(e.universe, mf.mf, e.universe)
    ax0.plot(e.universe, y_degerleri, label=etiket.upper())
ax0.legend()

# Fonksiyon 2: Hata Türevi (edot)
ax1.set_title('Hata Türevi (edot) Değişkeni Üyelik Fonksiyonları', fontsize=12)
for etiket, mf in edot.terms.items():
    y_degerleri = fuzz.interp_membership(edot.universe, mf.mf, edot.universe)
    ax1.plot(edot.universe, y_degerleri, label=etiket.upper())
ax1.legend()

# Fonksiyon 3: Isıtıcı Gücü (u)
ax2.set_title('Isıtıcı Gücü (u) Çıkış Değişkeni Üyelik Fonksiyonları', fontsize=12)
for etiket, mf in u.terms.items():
    y_degerleri = fuzz.interp_membership(u.universe, mf.mf, u.universe)
    ax2.plot(u.universe, y_degerleri, label=etiket.upper())
ax2.legend()
    
# Tüm grafikler için ortak etiketler ve stil
for ax in [ax0, ax1, ax2]:
    ax.set_xlabel("Değer", fontsize=10)
    ax.set_ylabel("Üyelik Derecesi", fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()
    ax.grid(True)

# Başlıkların ve etiketlerin üst üste binmesini engellemek için.
plt.tight_layout()

# Hazırlanan tek figürü göster. Bu pencere kapatıldıktan sonra simülasyon başlar.
plt.show()

# -----------------------------------------------------------------------------
# 4. SİMÜLASYON
# -----------------------------------------------------------------------------

# --- Sistem Parametreleri ---
T_hedef = 22.0
tau = 300.0
K = 1.0 # Başarılı senaryo için sistem kazancı

# --- Simülasyon Ayarları ---
sim_suresi = 3601
dt = 1
zaman_vektoru = np.arange(0, sim_suresi, dt)

# --- Kayıt Listeleri ve Başlangıç Koşulları ---
Toda_kaydi = []
u_kaydi = []
T_oda = 10.0
e_eski = T_hedef - T_oda

print(f"--- Simülasyon Başlatılıyor (K={K}) ---")

# --- Simülasyon Döngüsü ---
for t in zaman_vektoru:
    # Dış Koşul Değişimi (Bozucu Etki)
    if t < 1800:
        T_dis = 10.0
    else:
        T_dis = 5.0

    # Denetleyici Adımları
    hata = T_hedef - T_oda
    hata_dot = (hata - e_eski) / dt
    denetleyici.input['error'] = hata
    denetleyici.input['error_dot'] = hata_dot
    denetleyici.compute()
    guc = denetleyici.output['control_output']

    # Debug Çıktısı
    if t % 300 == 0:
        print(f"Zaman: {t/60:2.0f} dk | T_oda: {T_oda:5.2f}°C | Hata: {hata:5.2f} | Güç: {guc:4.2f} kW")

    # Değerleri Kaydet ve Güncelle
    e_eski = hata
    Toda_kaydi.append(T_oda)
    u_kaydi.append(guc)

    # Fiziksel Modelin Güncellenmesi
    dToda_dt = (-1/tau) * (T_oda - T_dis) + (K/tau) * guc
    T_oda = T_oda + dToda_dt * dt

print("--- Simülasyon Tamamlandı ---")

# -----------------------------------------------------------------------------
# 5. PERFORMANS ANALİZİ
# -----------------------------------------------------------------------------
print("\n--- Performans Metrikleri Analizi ---")
Toda_np = np.array(Toda_kaydi)
hatalar = T_hedef - Toda_np

# Aşım Yüzdesi
en_yuksek_sicaklik = np.max(Toda_np)
if en_yuksek_sicaklik > T_hedef:
    asim_yuzdesi = ((en_yuksek_sicaklik - T_hedef) / T_hedef) * 100
    print(f"Aşım Yüzdesi (Overshoot): %{asim_yuzdesi:.2f}")
else:
    print("Sistemde aşım gözlemlenmedi.")

# Yerleşme Süresi (±%5)
ust_sinir = T_hedef * 1.05
alt_sinir = T_hedef * 0.95
tolerans_disi_indeksler = np.where((Toda_np > ust_sinir) | (Toda_np < alt_sinir))[0]
if len(tolerans_disi_indeksler) > 0 and tolerans_disi_indeksler[-1] < len(zaman_vektoru) - 2:
    yerlesme_suresi = zaman_vektoru[tolerans_disi_indeksler[-1] + 1] / 60
    print(f"Yerleşme Süresi (±%5): {yerlesme_suresi:.2f} dakika")
else:
    print("Sistem simülasyon süresi boyunca hedefe yerleşemedi.")

# IAE ve RMSE
iae = np.sum(np.abs(hatalar)) * dt
rmse = np.sqrt(np.mean(hatalar**2))
print(f"IAE (Integral of Absolute Error): {iae:.2f} °C·s")
print(f"RMSE (Root Mean Square Error): {rmse:.2f} °C")

# -----------------------------------------------------------------------------
# 6. GÖRSELLEŞTİRME
# -----------------------------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(14, 7))
ax1.set_title(f'Oda Sıcaklığı Kontrolü Simülasyonu (K={K})', fontsize=16)
ax1.set_xlabel('Zaman (dakika)', fontsize=12)
ax1.grid(True)

# Sıcaklık Ekseni
ax1.set_ylabel('Sıcaklık (°C)', color='blue', fontsize=12)
ax1.plot(zaman_vektoru/60, Toda_kaydi, 'b-', linewidth=2, label='Oda Sıcaklığı')
ax1.axhline(y=T_hedef, color='gray', linestyle='--', linewidth=2, label='Hedef Sıcaklık')
ax1.tick_params(axis='y', labelcolor='blue')

# Isıtıcı Gücü Ekseni
ax2 = ax1.twinx()
ax2.set_ylabel('Isıtıcı Gücü (kW)', color='red', fontsize=12)
ax2.plot(zaman_vektoru/60, u_kaydi, 'r-', alpha=0.7, linewidth=2, label='Isıtıcı Gücü')
ax2.tick_params(axis='y', labelcolor='red')
ax2.set_ylim(0, 2.2)

# Lejantları birleştir
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines1 + lines2, labels1 + labels2, loc='best')

fig.tight_layout()
plt.show()