# ⚗️ Enzym-Simulator (Michaelis-Menten-Kinetik)

Ein interaktiver Simulator zur Visualisierung der Enzymaktivität und Abhängigkeit von der Substratkonzentration. Dieses Projekt demonstriert anschaulich die Prinzipien der **Michaelis-Menten-Kinetik** sowie den Einfluss von Temperatur und Sättigung auf die Reaktionsgeschwindigkeit.

Das Projekt ist in **zwei Versionen** verfügbar:
1. **Python Desktop App** (mit `tkinter`)
2. **Web App** (mit Vanilla HTML/CSS/JavaScript)

---

## ✨ Features

- **Live-Simulation**: Visualisiert thermische Bewegung und die Interaktion (Schlüssel-Schloss-Prinzip) von Enzymen und Substraten in Echtzeit.
- **Michaelis-Menten-Graph**: Ein Live-Plot zeigt die gemessene Reaktionsgeschwindigkeit ($v_0$) über der anfänglichen Substratkonzentration ($[S]$). Referenzlinien für $V_{max}$ und $K_m$ werden dynamisch berechnet und eingezeichnet.
- **Temperaturkontrolle (0-100 °C)**: 
  - Die Bewegung der Teilchen skaliert realistisch nach der RGT-Regel.
  - Simulation von **Denaturierung** bei zu starker Erhitzung (Enzyme verlieren dauerhaft ihre Form und Funktion).
  - Option für **thermostabile Enzyme**, deren Denaturierung erst bei höheren Temperaturen (ab 80 °C) einsetzt.
- **Benutzerdefinierte Parameter**: Anzahl der Enzyme und initiale Substratkonzentration frei wählbar.
- **Theme-Unterstützung**: Nahtloser Wechsel zwischen zwei optischen Aufmachungen:
  - 🌙 **Dunkel**: Ein präzises "Labor-/Matrix-Neon"-Design.
  - 📄 **Hell**: Ein organischer "Papier & Skizzen"-Stil für einen handgezeichneten Look.
- **Zoom & Sim-Speed**: Simulation kann beschleunigt, verlangsamt und für bessere Sichtbarkeit herangezoomt werden.

---

## 🚀 Installation & Nutzung

### 🐍 Python-Version (Desktop-App)
Die Desktop-Anwendung benötigt lediglich eine Standard-Python-Installation (keine weiteren `pip`-Pakete erforderlich).

1. Python 3.9+ wird empfohlen.
2. Wechsle in das Verzeichnis.
3. Führe das Skript aus:
   ```bash
   python3 enzym_simulation.py
   ```

### 🌐 Web-Version (Im Browser)
Die Web-Version läuft vollständig lokal im Browser und benötigt keinen Backend-Server.

1. Navigiere in den Ordner `webapp/`.
2. Öffne die `index.html`-Datei einfach in einem beliebigen modernen Browser (Chrome, Firefox, Safari, Edge).

---

## 🧬 Physikalische & Biologische Hintergründe

- **RGT-Regel (Reaktionsgeschwindigkeit-Temperatur-Regel)**: Angepasst an die klassische Lehrmeinung verdoppelt/halbiert sich die Reaktionsrate für jede 10°C Temperaturveränderung (bezogen auf Start-Temperatur 25°C).
- **Enzym-Denaturierung**: Ab 50°C (bzw. 80°C bei thermostabilen Enzymen) beginnt eine strukturelle Verformung der Enzyme. Dies ist visuell durch eine Deformation des Graphen und rote Kreuze im Canvas deutlich maskiert. Solche Enzyme können keine Substrate mehr andocken ("Denaturierung").
- **Substrathemmung**: Das Kinetik-Modell berücksichtigt subtil Substratübersättigung bei extrem hohen Konzentrationen, bei der sich Substrate gegenseitig beim Binden behindern können.

---

## 🛠 Technologien & Libraries

- **Python-App**: `tkinter`, `math`, `random`, `time` (alles Teil der Python Standard Library).
- **Web-App**: Vanilla JavaScript (ES6+), Canvas API für hardwarebeschleunigtes 2D-Rendering, CSS Variablen zur dynamischen Theme-Steuerung.

---

## 📝 Lizenz
Dieses Projekt dient Bildungs- und Visualisierungszwecken. (Füge hier deine Lizenz ein, standardmäßig MIT).
