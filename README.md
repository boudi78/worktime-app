# Zeiterfassungs-App Dokumentation

## Übersicht

Diese Zeiterfassungs-App ist eine umfassende Lösung für die Verwaltung von Arbeitszeiten, Projekten und Homeoffice-Tagen. Die App bietet folgende Hauptfunktionen:

- Benutzerregistrierung und -anmeldung mit Administratorrechten
- Persistente Datenspeicherung (Daten bleiben nach Neustart erhalten)
- Einfache Check-in/Check-out-Funktionalität
- Präzise Zeiterfassung mit Stoppuhr-Funktion
- Projektzuordnung für Zeiteinträge
- Homeoffice-Dokumentation und -Bescheinigungen
- Umfangreiche Auswertungsmöglichkeiten
- Administratorfunktionen zur Mitarbeiterverwaltung (inkl. Löschen von Mitarbeitern)

## Installation und Start

1. Stellen Sie sicher, dass Python 3.6+ und Streamlit installiert sind:
   ```
   pip install streamlit pandas
   ```

2. Starten Sie die App mit:
   ```
   streamlit run app_with_enhanced_features.py
   ```

## Dateien und Struktur

- `app_with_enhanced_features.py`: Hauptanwendung mit allen integrierten Funktionen
- `data_persistence.py`: Funktionen für persistente Datenspeicherung
- `admin_employee_management.py`: Funktionen für die Mitarbeiterverwaltung
- `enhanced_time_tracking.py`: Verbesserte Zeiterfassungsfunktionen

## Benutzerhandbuch

### Registrierung und Login

1. Beim ersten Start der App können Sie sich registrieren.
2. Der erste registrierte Benutzer erhält automatisch Administratorrechte.
3. Nach der Registrierung können Sie sich mit Ihren Zugangsdaten anmelden.

### Dashboard

Das Dashboard zeigt Ihren aktuellen Status (anwesend/abwesend) und ermöglicht einfaches Check-in/Check-out.

### Zeiterfassung

Die Zeiterfassung bietet folgende Funktionen:

- **Stoppuhr**: Starten und Stoppen der Zeiterfassung für präzise Aufzeichnung
- **Projektzuordnung**: Zuordnung von Zeiteinträgen zu Projekten
- **Homeoffice-Kennzeichnung**: Markierung von Zeiteinträgen als im Homeoffice gearbeitet

### Projektverwaltung

Die Projektverwaltung ermöglicht:

- Übersicht über alle Projekte
- Anzeige der verbrauchten Stunden pro Projekt
- Budgetverwaltung mit Warnungen bei Überschreitung
- Anlegen neuer Projekte (nur für Administratoren)

### Homeoffice-Dokumentation

Die Homeoffice-Dokumentation bietet:

- Übersicht über alle Homeoffice-Tage
- Monatsweise Aufschlüsselung
- Erstellung von Homeoffice-Bescheinigungen

### Auswertungen

Die Auswertungsfunktionen umfassen:

- Zeitauswertung mit Diagrammen
- Projektauswertung
- Export von Daten als CSV oder JSON

### Mitarbeiterverwaltung (nur für Administratoren)

Administratoren können:

- Alle Mitarbeiter einsehen
- Mitarbeiter löschen (mit Bestätigungsabfrage)
- Mitarbeiterrollen ändern

### Profil

Im Profilbereich können Sie:

- Ihre persönlichen Daten einsehen
- Ihr Passwort ändern

## Datenspeicherung

Alle Daten werden in JSON-Dateien im Verzeichnis `data/` gespeichert:

- `employees.json`: Mitarbeiterdaten
- `time_entries.json`: Zeiterfassungseinträge
- `projects.json`: Projektdaten
- `homeoffice_data.json`: Homeoffice-Daten

## Inspiriert von führenden Zeiterfassungssystemen

Die Funktionen dieser App wurden inspiriert von den besten Praktiken folgender Zeiterfassungssysteme:

- Clockin
- ZEP
- Crewmeister
- TimeTac
- MOCO
- Personizer
- ZMI
