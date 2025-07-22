# Essensplan Generator (Meal Plan Generator)

## Beschreibung
Ein Python-Tool zur einfachen Erstellung von Essensplänen für eine Woche mit automatischer HTML-Website-Generierung.  
Dieses Tool ermöglicht es, strukturierte Wochenpläne mit Fotos, Rezepten und Zutatenlisten zu erstellen und als übersichtliche Website zu exportieren.

## Beispiel
<img width="1642" height="672" alt="image" src="https://github.com/user-attachments/assets/19cd89ad-cfa8-41a3-925d-2cf983a864bf" />

## Features
### Gerichte-Bibliothek
- Eigene Gerichte-Datenbank mit Fotos, PDFs und zusätzlichen Informationen
- Einfaches Hinzufügen neuer Gerichte mit Namen, Bild, Rezept-PDF und Notizen
- Automatische Speicherung in strukturiertem `meals_data` Ordner
- Intelligente Suchfunktion beim Zuordnen von Gerichten

### Wochenplanung
- Konfigurierbare Mahlzeiten: Frühstück, Mittagessen, Snacks, Dessert
- Flexible Anzahl von Gerichten pro Mahlzeit
- Datum-basierte Planung (Montag bis Sonntag)
- Leere Zellen individuell konfigurierbar

### Website-Generierung
- Automatische HTML-Website mit Wochenübersicht
- Eingebettete Fotos und verlinkbare PDF-Rezepte
- Responsive Design für verschiedene Bildschirmgrößen
- Optionale Zutatenlisten-Integration

### Dateiverwaltung
- Kopieren oder Ausschneiden von Dateien
- Automatische Ordnerstruktur-Erstellung
- ZIP-Export der kompletten Website
- Temporäre Dateien aus Zwischenablage

## Anforderungen
- Python 3.10+
- Tkinter (normalerweise in Python enthalten)

### Python-Pakete
Installiere die folgenden Python-Pakete mit `pip`:
```bash
pip install Pillow
```

### Standard-Bibliotheken
Die folgenden Python-Standard-Bibliotheken werden verwendet und müssen nicht separat installiert werden:
- tkinter
- os
- shutil
- webbrowser
- subprocess
- platform
- datetime
- zipfile
- io
- json
- uuid

## Verwendung
1. Starte das Python-Script

2. **Gerichte-Bibliothek:** Füge deine Lieblingsgerichte zur Datenbank hinzu:
- Klicke auf das "+" um neue Gerichte hinzuzufügen
- Lade Fotos und PDF-Rezepte hoch oder füge sie aus der Zwischenablage ein
- Konfiguriere den Speicherort der `meals_data` Datenbank
*(Hier wäre ein Screenshot der Gerichte-Bibliothek hilfreich)*

3. **Einstellungen:** Konfiguriere deinen Wochenplan
- Wähle Start- und Enddatum der Woche
- Bestimme die Anzahl der Gerichte pro Mahlzeit
- Konfiguriere Anzeige-Optionen und Datei-Operationen
*(Hier wäre ein Screenshot der Konfigurationsseite hilfreich)*

4. **Zuordnung:** Weise jedem Tag und jeder Mahlzeit Gerichte zu
- Nutze die Suchfunktion für Gerichte aus der Bibliothek
- Oder lade neue Fotos/PDFs direkt hoch
- Benenne Gerichte individuell
*(Hier wäre ein Screenshot der Zuordnungsseite hilfreich)*

5. **Fertigstellung:** Generiere deine Website
- Das Tool erstellt automatisch eine HTML-Website
- Alle Dateien werden organisiert und verlinkt
- Optional: ZIP-Export für einfaches Teilen
*(Hier wäre ein Screenshot der finalen Website hilfreich)*

## Ordnerstruktur
Das Tool erstellt automatisch folgende Struktur:

Essensplan [Datum]/<br>
├── index.html (Hauptwebsite)<br>
├── fotos/ (Alle Essensfotos)<br>
├── rezepte/ (PDF-Rezepte)<br>
└── quellen/ (Zutatenlisten)<br>

meals_data/<br>
├── meals.json (Gerichte-Datenbank)<br>
└── [meal_id]/<br>
_____├── photo.[ext]<br>
_____├── recipe.pdf<br>
_____└── info.txt<br>

## Besondere Features
- **Intelligente Dateiverwaltung:** Unterscheidet zwischen Kopieren und Ausschneiden
- **Zwischenablage-Integration:** Füge Bilder direkt aus der Zwischenablage ein
- **Notizen-Modus:** Praktische Notizfunktion während der Planung
- **Discord-Integration:** Kopiere Wochennamen in Discord-kompatiblem Format
- **Schutz vor Datenverlust:** Warnungen bei ungespeicherten Änderungen

## Tipps zur Nutzung
- Erstelle einmal eine umfangreiche Gerichte-Bibliothek für schnellere zukünftige Planungen
- Nutze aussagekräftige Namen für deine Gerichte
- Die Suchfunktion erkennt auch Teilübereinstimmungen
- Bei Gerichten aus der Bibliothek ist "Ausschneiden" deaktiviert zum Schutz der Datenbank

## Zukünftige Verbesserungen
Lass mich wissen, wenn du Funktionen vermisst oder Ideen für Verbesserungen hast!<br>
Feedback und Vorschläge sind sehr willkommen.
