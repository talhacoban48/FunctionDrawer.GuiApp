# Function Drawer

Matematiksel fonksiyonları doğal notasyonla yazıp görselleştiren, türev ve integral hesapları yapabilen masaüstü uygulama.

---

## Özellikler

- **Doğal matematik notasyonu** — `2sin(4x)`, `x^2`, `sqrt(x)` gibi ifadeleri doğrudan yazın
- **Gerçek zamanlı LaTeX önizleme** — yazdıkça formül render edilir
- **Birden fazla fonksiyon** — her fonksiyon farklı renkte aynı grafikte çizilir
- **Türev** — sembolik türev hesaplar, grafikte kesikli çizgiyle gösterir
- **Belirli & belirsiz integral** — antitürev + sayısal alan hesabı, grafik üzerinde alan dolgusu
- **Ayarlanabilir aralık** — min, max, adım değerleri özelleştirilebilir

---

## Ekran Görüntüsü

```
┌─ Fonksiyonlar ──────────────┐  ┌─ Grafik ──────────────────────────────┐
│  ● f1(x) = sin(x)      [×] │  │                                       │
│  ● f2(x) = x^2/4       [×] │  │         Fonksiyon Grafiği             │
│  [+ Fonksiyon Ekle]        │  │                                       │
│                             │  │   f(x) ↑                              │
│  Önizleme:                  │  │        │   ╭───╮                      │
│  f(x) = sin(x)              │  │  ──────┼──╯   ╰──── x                │
│                             │  │        │                              │
│  Min: -10  Max: 10          │  │                                       │
│  Adım: 0.0100               │  │                                       │
│  [🔍 Çiz] [✕ Temizle]      │  └───────────────────────────────────────┘
│  ─────────────────────────  │
│  a: [-1] b: [1]             │
│  [İntegral Al] [Türev Al] ✕ │
│  Sonuçlar:                  │
│  f1'(x) = cos(x)            │
└─────────────────────────────┘
```

---

## Kurulum

**Gereksinimler:** Python 3.9+

```bash
pip install PyQt5 matplotlib numpy sympy
```

```bash
git clone <repo-url>
cd FunctionDrawer.GuiApp
python main.py
```

---

## Kullanım

### Fonksiyon Yazımı

| Yazılan         | Anlamı              |
|-----------------|---------------------|
| `2x`            | `2 · x`             |
| `x^2`           | `x²`                |
| `sin(4x)`       | `sin(4x)`           |
| `2sin(x)cos(x)` | `2 · sin(x) · cos(x)` |
| `sqrt(x)`       | `√x`                |
| `log(x)`        | `ln(x)`             |
| `log(x, 3)`     | `log₃(x)`           |
| `exp(x)`        | `eˣ`                |

### Grafik Çizimi

1. Fonksiyonu girin — önizleme anlık güncellenir
2. Gerekirse **Min / Max / Adım** değerlerini ayarlayın
3. **Çiz** butonuna tıklayın
4. Birden fazla fonksiyon için **+ Fonksiyon Ekle**'ye tıklayın

### Türev

- **Türev Al** → her fonksiyonun sembolik türevi hesaplanır
- Sonuçlar sol panelde, türev eğrisi grafik üzerinde kesikli çizgiyle gösterilir

### İntegral

- **a** ve **b** sınırlarını girin
- **İntegral Al** → belirsiz integral (antitürev) ve belirli integral değeri hesaplanır
- Grafik üzerinde `[a, b]` aralığındaki alan renkli dolgu ile gösterilir

### Temizleme

| Buton | Ne temizler |
|-------|-------------|
| **Temizle** (ana) | Tüm fonksiyonlar, grafik, sonuçlar |
| **✕** (hesaplamalar) | Yalnızca türev/integral çizimleri ve sonuçlar |
| **✕** (satır) | Yalnızca o fonksiyon satırı |

---

## Proje Yapısı

```
FunctionDrawer.GuiApp/
├── app/
│   ├── constants.py          # Sabitler, renk paleti, parse_formula()
│   ├── widgets/
│   │   ├── formula_row.py    # Fonksiyon giriş satırı bileşeni
│   │   ├── preview_canvas.py # LaTeX önizleme canvas
│   │   ├── results_canvas.py # Hesap sonuçları canvas
│   │   └── plot_canvas.py    # Ana grafik canvas
│   └── windows/
│       └── main_window.py    # Ana pencere ve uygulama mantığı
├── assets/                   # İkon dosyaları (.ico)
├── main.py                   # Uygulama giriş noktası
└── .gitignore
```

---

## Teknolojiler

| Kütüphane    | Kullanım                          |
|--------------|-----------------------------------|
| `PyQt5`      | GUI framework                     |
| `matplotlib` | Grafik çizimi (Qt backend)        |
| `sympy`      | Sembolik matematik (türev, integral, LaTeX) |
| `numpy`      | Sayısal hesaplama                 |
