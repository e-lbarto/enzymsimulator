# ⚗️ Enzym-Simulator (Michaelis-Menten-Kinetik)

Ein interaktiver Simulator zur Visualisierung der Enzymaktivität und Abhängigkeit von der Substratkonzentration. Dieses Projekt demonstriert anschaulich die Prinzipien der **Michaelis-Menten-Kinetik** sowie den Einfluss von Temperatur, Hemmstoffen und Sättigung auf die Reaktionsgeschwindigkeit.

Die Simulation läuft auch vollständig als **Single-File Web App** im Browser.

---

## ✨ Features

- **Live-Simulation**: Visualisiert thermische Bewegung und die Interaktion (Schlüssel-Schloss-Prinzip) von Enzymen und Substraten in Echtzeit.
- **Michaelis-Menten-Graph**: Ein Live-Plot zeigt die gemessene Reaktionsgeschwindigkeit ($v_0$) über der anfänglichen Substratkonzentration ($[S]$). Referenzlinien für $V_{max}$ und $K_m$ werden dynamisch berechnet und eingezeichnet.
- **Hemmstoffe (Inhibitoren)**: Simulation von kompetitiver und allosterischer Hemmung inklusive Auswirkungen auf $K_m$ und $V_{max}$.
- **Temperaturkontrolle (0-100 °C)**: 
  - Die Bewegung der Teilchen skaliert realistisch nach der RGT-Regel.
  - Simulation von **Denaturierung** bei zu starker Erhitzung (Enzyme verlieren dauerhaft ihre Form und Funktion).
  - Option für **thermostabile Enzyme**, deren Denaturierung erst bei höheren Temperaturen (ab 80 °C) einsetzt.
- **Benutzerdefinierte Parameter**: Anzahl der Enzyme und initiale Substratkonzentration frei wählbar.
- **Theme-Unterstützung**: Nahtloser Wechsel zwischen zwei optischen Aufmachungen:
  - 🌙 **Dunkel**: Ein präzises "Labor-/Matrix-Neon"-Design.
  - 📄 **Hell**: Ein organischer "Papier & Skizzen"-Stil für einen handgezeichneten Look.
- **Zoom & Sim-Speed**: Simulation kann beschleunigt, verlangsamt und für bessere Sichtbarkeit herangezoomt werden (Diagramm-Zoom per Klick).

---

## 🚀 Nutzung

Die Simulation benötigt keinen Webserver und keine Installation.

1. Öffne die Datei `Enzym-Simulator.html` einfach in einem beliebigen modernen Browser (Chrome, Firefox, Safari, Edge).
2. Alle Logiken (JS) und Designs (CSS) sind direkt in der Datei enthalten, sodass sie auch offline und ohne Internetverbindung funktioniert.

---

## 🧬 Physikalische & Biologische Hintergründe

- **RGT-Regel (Reaktionsgeschwindigkeit-Temperatur-Regel)**: Angepasst an die klassische Lehrmeinung verdoppelt/halbiert sich die Reaktionsrate für jede 10°C Temperaturveränderung (bezogen auf Start-Temperatur 25°C).
- **Enzym-Denaturierung**: Ab 50°C (bzw. 80°C bei thermostabilen Enzymen) beginnt eine strukturelle Verformung der Enzyme. Dies ist visuell durch eine Deformation der Enzyme und rote Kreuze im Simulator deutlich markiert. Denaturierte Enzyme können keine Substrate mehr binden.
- **Inhibition**:
  - **Kompetitiv**: Hemmstoffe konkurrieren mit dem Substrat um das aktive Zentrum ($K_m$ erhöht sich).
  - **Allosterisch**: Hemmstoffe binden an ein anderes Zentrum und verändern die Enzymstruktur ($V_{max}$ sinkt).

---

## 🛠 Technologien

- **Web-App**: Vanilla JavaScript (ES6+), Canvas API für hardwarebeschleunigtes 2D-Rendering, CSS Variablen zur dynamischen Theme-Steuerung. Keine externen Libraries notwendig.

---

## 📝 Lizenz
Dieses Projekt dient Bildungs- und Visualisierungszwecken. (Lizenz: MIT). 2026 von m.poehlmann mit Antigravity
