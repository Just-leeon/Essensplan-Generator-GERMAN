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
<img width="902" height="832" alt="image" src="https://github.com/user-attachments/assets/430d5d2f-058c-4963-8205-edf2f74d8988" />
<img width="502" height="632" alt="image" src="https://github.com/user-attachments/assets/081b0ca6-979b-4a59-89ba-f50ea1820308" />

<br> 3. **Einstellungen:** Konfiguriere deinen Wochenplan
- Wähle Start- und Enddatum der Woche
- Bestimme die Anzahl der Gerichte pro Mahlzeit
- Konfiguriere Anzeige-Optionen und Datei-Operationen
<img width="902" height="832" alt="image" src="https://github.com/user-attachments/assets/ed6ca3a0-3fc6-4601-83ea-8bc647552040" />
<img width="1402" height="832" alt="image" src="https://github.com/user-attachments/assets/db6180f3-ac72-443b-b868-17fae3d2de0e" />

<br> 4. **Zuordnung:** Weise jedem Tag und jeder Mahlzeit Gerichte zu
- Nutze die Suchfunktion für Gerichte aus der Bibliothek
- Oder lade neue Fotos/PDFs direkt hoch
- Benenne Gerichte individuell
<img width="902" height="832" alt="image" src="https://github.com/user-attachments/assets/7845e269-40d0-4085-8ffc-808288f362bc" />
<img width="602" height="532" alt="image" src="https://github.com/user-attachments/assets/468cfe8e-c830-4ad0-8f44-414610f5a5ed" />

<br> 5. **Fertigstellung:** Generiere deine Website
- Das Tool erstellt automatisch eine HTML-Website
- Alle Dateien werden organisiert und verlinkt
- Optional: ZIP-Export für einfaches Teilen

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
