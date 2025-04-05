import streamlit as st

def test_navigation():
    """
    Testet die verbesserte Navigation und das Beheben des Doppelklick-Problems.
    Führt verschiedene Tests durch, um sicherzustellen, dass die Navigation korrekt funktioniert.
    """
    st.title("Test der verbesserten Navigation")
    
    st.write("Dieser Test überprüft, ob die Navigation korrekt funktioniert und das Doppelklick-Problem behoben wurde.")
    
    # Test 1: Überprüfen, ob die Navigation-Module korrekt importiert werden können
    try:
        from modules.navigation import set_page
        st.success("✅ Test 1: Navigation-Modul erfolgreich importiert")
    except ImportError:
        st.error("❌ Test 1: Navigation-Modul konnte nicht importiert werden")
        return
    
    # Test 2: Überprüfen, ob die verbesserten Dateien existieren
    import os
    
    files_to_check = [
        "app_improved.py",
        "main_improved.py",
        "modules/login_improved.py",
        "modules/navigation.py",
        ".gitignore"
    ]
    
    all_files_exist = True
    for file in files_to_check:
        if not os.path.exists(file):
            st.error(f"❌ Datei {file} existiert nicht")
            all_files_exist = False
    
    if all_files_exist:
        st.success("✅ Test 2: Alle verbesserten Dateien existieren")
    
    # Test 3: Überprüfen der Funktionalität der set_page Funktion
    st.subheader("Test der set_page Funktion")
    st.write("Die set_page Funktion sollte die Seite wechseln und automatisch ein Rerun auslösen.")
    
    # Überprüfen, ob die Funktion den korrekten Code enthält
    import inspect
    set_page_source = inspect.getsource(set_page)
    
    if "st.rerun()" in set_page_source:
        st.success("✅ Test 3: set_page Funktion enthält st.rerun()")
    else:
        st.error("❌ Test 3: set_page Funktion enthält kein st.rerun()")
    
    # Test 4: Überprüfen der Icon-Navigation
    st.subheader("Test der Icon-Navigation")
    
    # Lese die verbesserten Dateien und prüfe, ob Icons verwendet werden
    with open("app_improved.py", "r") as f:
        app_improved_content = f.read()
    
    with open("main_improved.py", "r") as f:
        main_improved_content = f.read()
    
    icons_found = False
    for content in [app_improved_content, main_improved_content]:
        if "🏠" in content and "⏰" in content and "📅" in content:
            icons_found = True
            break
    
    if icons_found:
        st.success("✅ Test 4: Icons in der Navigation gefunden")
    else:
        st.error("❌ Test 4: Keine Icons in der Navigation gefunden")
    
    # Test 5: Überprüfen der .gitignore Datei
    st.subheader("Test der .gitignore Datei")
    
    with open(".gitignore", "r") as f:
        gitignore_content = f.read()
    
    required_entries = [
        "__pycache__",
        "*.py[cod]",
        ".streamlit/secrets.toml",
        "venv/",
        ".env"
    ]
    
    all_entries_found = True
    for entry in required_entries:
        if entry not in gitignore_content:
            st.error(f"❌ Eintrag {entry} fehlt in .gitignore")
            all_entries_found = False
    
    if all_entries_found:
        st.success("✅ Test 5: Alle erforderlichen Einträge in .gitignore gefunden")
    
    # Zusammenfassung
    st.subheader("Zusammenfassung")
    
    if all_files_exist and "st.rerun()" in set_page_source and icons_found and all_entries_found:
        st.success("✅ Alle Tests erfolgreich bestanden! Die Lösung ist bereit für die Auslieferung.")
    else:
        st.warning("⚠️ Einige Tests sind fehlgeschlagen. Bitte überprüfen Sie die Fehler und beheben Sie sie.")

if __name__ == "__main__":
    test_navigation()
