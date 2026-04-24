# Enzym-Simulator v3

Ein interaktiver, webbasierter Simulator für die Enzymkinetik. Dieses Projekt demonstriert anschaulich die Michaelis-Menten-Kinetik, den Einfluss der Temperatur (RGT-Regel), Enzymdenaturierung sowie die Effekte von thermostabilen Enzymen.

## Features

- **Interaktive Simulation:** Visualisierung von Enzymen, Substraten und Produkten in Echtzeit auf einem HTML5-Canvas.
- **Echtzeit-Graph:** Ein live aktualisiertes Diagramm, das die Reaktionsgeschwindigkeit in Abhängigkeit von der Substratkonzentration darstellt.
- **Temperatur-Kontrolle (RGT-Regel):** Die Temperatur kann stufenlos geregelt werden. Die Reaktionsgeschwindigkeit passt sich entsprechend an.
- **Denaturierung:** Ab einer bestimmten Temperatur denaturieren Enzyme (mit Option für thermostabile Enzyme, die höhere Temperaturen aushalten).
- **Steuerbare Parameter:** Anzahl der Enzyme und Substrate können flexibel angepasst werden.
- **Anpassbare Geschwindigkeit & Zoom:** Simulationsgeschwindigkeit und Ansichtsgröße können für bessere Übersicht eingestellt werden.

## Technologie-Stack

- **Frontend:** Vanilla JavaScript, HTML5, CSS3.
- **Darstellung:** HTML5 `<canvas>` für performante Echtzeit-Grafiken und Diagramme.

## Installation & Ausführung

Da es sich um eine reine Webanwendung (Frontend) handelt, ist keine serverseitige Installation erforderlich.

1. Repository klonen oder herunterladen:
   ```bash
   git clone https://github.com/dein-username/enzym-simulator.git
   ```
2. Den Ordner `webapp` öffnen.
3. Die Datei `index.html` in einem beliebigen modernen Webbrowser öffnen.

## Nutzung

1. Stelle die **Temperatur** ein (Standard ist 20 °C).
2. Wähle die gewünschte Anzahl an **Enzymen** und **Substraten**.
3. (Optional) Aktiviere **thermostabile Enzyme**, um eine Denaturierung bei Standardtemperaturen zu verhindern.
4. Klicke auf **▶ START**, um die Simulation zu beginnen.
5. Beobachte die Partikel-Interaktionen im linken Fenster und den Graphen im rechten Fenster.

## Lizenz

Dieses Projekt steht unter der [MIT Lizenz](LICENSE).
