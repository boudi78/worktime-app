import streamlit as st
import json
import os
from datetime import datetime

def implement_management_roles():
    """
    Implementiert erweiterte Management-Rollen für Mitarbeiter
    """
    def save_roles_data(roles_data):
        """Speichert Rollendaten in einer JSON-Datei"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        file_path = os.path.join(data_dir, "roles.json")
        
        with open(file_path, "w") as f:
            json.dump(roles_data, f)
    
    def load_roles_data():
        """Lädt Rollendaten aus einer JSON-Datei"""
        data_dir = "data"
        file_path = os.path.join(data_dir, "roles.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            # Standard-Rollen
            default_roles = {
                "roles": [
                    {
                        "id": 1,
                        "name": "Administrator",
                        "description": "Vollständiger Zugriff auf alle Funktionen",
                        "permissions": [
                            "admin_panel",
                            "manage_employees",
                            "manage_projects",
                            "view_statistics",
                            "approve_leave",
                            "export_data",
                            "manage_roles"
                        ]
                    },
                    {
                        "id": 2,
                        "name": "Manager",
                        "description": "Zugriff auf Mitarbeiter- und Projektverwaltung",
                        "permissions": [
                            "manage_employees",
                            "manage_projects",
                            "view_statistics",
                            "approve_leave",
                            "export_data"
                        ]
                    },
                    {
                        "id": 3,
                        "name": "Teamleiter",
                        "description": "Zugriff auf Teammitglieder und Projekte",
                        "permissions": [
                            "manage_projects",
                            "view_statistics",
                            "approve_leave"
                        ]
                    },
                    {
                        "id": 4,
                        "name": "Mitarbeiter",
                        "description": "Standardzugriff für Mitarbeiter",
                        "permissions": [
                            "track_time",
                            "view_own_statistics"
                        ]
                    }
                ],
                "permissions": [
                    {
                        "id": "admin_panel",
                        "name": "Admin-Panel",
                        "description": "Zugriff auf das Admin-Panel"
                    },
                    {
                        "id": "manage_employees",
                        "name": "Mitarbeiterverwaltung",
                        "description": "Mitarbeiter hinzufügen, bearbeiten und löschen"
                    },
                    {
                        "id": "manage_projects",
                        "name": "Projektverwaltung",
                        "description": "Projekte erstellen, bearbeiten und löschen"
                    },
                    {
                        "id": "view_statistics",
                        "name": "Statistiken einsehen",
                        "description": "Zugriff auf alle Statistiken und Berichte"
                    },
                    {
                        "id": "approve_leave",
                        "name": "Urlaub genehmigen",
                        "description": "Urlaubsanträge genehmigen oder ablehnen"
                    },
                    {
                        "id": "export_data",
                        "name": "Daten exportieren",
                        "description": "Daten in verschiedenen Formaten exportieren"
                    },
                    {
                        "id": "manage_roles",
                        "name": "Rollenverwaltung",
                        "description": "Rollen und Berechtigungen verwalten"
                    },
                    {
                        "id": "track_time",
                        "name": "Zeiterfassung",
                        "description": "Arbeitszeit erfassen"
                    },
                    {
                        "id": "view_own_statistics",
                        "name": "Eigene Statistiken",
                        "description": "Eigene Statistiken und Berichte einsehen"
                    }
                ],
                "employee_roles": {}
            }
            save_roles_data(default_roles)
            return default_roles
    
    def load_employees():
        """Lädt Mitarbeiterdaten aus einer JSON-Datei"""
        data_dir = "data"
        file_path = os.path.join(data_dir, "employees.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            return []
    
    def save_employees(employees):
        """Speichert Mitarbeiterdaten in einer JSON-Datei"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        file_path = os.path.join(data_dir, "employees.json")
        
        with open(file_path, "w") as f:
            json.dump(employees, f)
    
    def has_permission(user_id, permission_id):
        """Prüft, ob ein Benutzer eine bestimmte Berechtigung hat"""
        # Rollendaten laden
        roles_data = load_roles_data()
        
        # Mitarbeiterdaten laden
        employees = load_employees()
        
        # Mitarbeiter finden
        employee = next((emp for emp in employees if emp["id"] == user_id), None)
        
        if not employee:
            return False
        
        # Prüfen, ob der Mitarbeiter Admin ist (Legacy-Unterstützung)
        if employee.get("is_admin", False):
            return True
        
        # Zugewiesene Rolle des Mitarbeiters finden
        employee_role_id = roles_data.get("employee_roles", {}).get(str(user_id), 4)  # Standard: Mitarbeiter
        
        # Rolle finden
        role = next((r for r in roles_data["roles"] if r["id"] == employee_role_id), None)
        
        if not role:
            return False
        
        # Prüfen, ob die Rolle die Berechtigung enthält
        return permission_id in role["permissions"]
    
    def show_role_management_ui():
        st.title("Rollenverwaltung")
        
        # Prüfen, ob der Benutzer Admin ist
        if not st.session_state.get("is_admin", False):
            st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
            return
        
        # Rollendaten laden
        roles_data = load_roles_data()
        
        # Mitarbeiterdaten laden
        employees = load_employees()
        
        # Tabs für Rollenverwaltung
        tab1, tab2 = st.tabs(["Mitarbeiterrollen", "Rollendefinitionen"])
        
        with tab1:
            st.subheader("Mitarbeiterrollen zuweisen")
            
            # Mitarbeiterliste
            for employee in employees:
                with st.expander(f"{employee['name']} ({employee['username']})"):
                    # Aktuelle Rolle anzeigen
                    current_role_id = roles_data.get("employee_roles", {}).get(str(employee["id"]), 4)  # Standard: Mitarbeiter
                    current_role = next((r for r in roles_data["roles"] if r["id"] == current_role_id), None)
                    
                    st.write(f"Aktuelle Rolle: **{current_role['name'] if current_role else 'Keine Rolle'}**")
                    
                    # Rollenliste für Auswahl
                    role_names = [r["name"] for r in roles_data["roles"]]
                    role_ids = [r["id"] for r in roles_data["roles"]]
                    
                    # Aktuellen Index finden
                    current_index = role_ids.index(current_role_id) if current_role_id in role_ids else 0
                    
                    # Neue Rolle auswählen
                    selected_index = st.selectbox(
                        "Rolle auswählen", 
                        range(len(role_names)), 
                        format_func=lambda x: role_names[x],
                        key=f"role_{employee['id']}",
                        index=current_index
                    )
                    selected_role_id = role_ids[selected_index]
                    
                    # Rolle speichern
                    if st.button("Rolle speichern", key=f"save_role_{employee['id']}"):
                        # Rollenzuweisung aktualisieren
                        if "employee_roles" not in roles_data:
                            roles_data["employee_roles"] = {}
                        
                        roles_data["employee_roles"][str(employee["id"])] = selected_role_id
                        
                        # Legacy-Unterstützung: is_admin-Flag aktualisieren
                        is_admin = selected_role_id == 1  # Administrator-Rolle
                        
                        for emp in employees:
                            if emp["id"] == employee["id"]:
                                emp["is_admin"] = is_admin
                                break
                        
                        # Daten speichern
                        save_roles_data(roles_data)
                        save_employees(employees)
                        
                        st.success(f"Rolle für {employee['name']} aktualisiert!")
                        st.rerun()
        
        with tab2:
            st.subheader("Rollendefinitionen")
            
            # Rollen anzeigen
            for role in roles_data["roles"]:
                with st.expander(f"{role['name']} - {role['description']}"):
                    st.write("**Berechtigungen:**")
                    
                    # Berechtigungen anzeigen
                    for permission_id in role["permissions"]:
                        # Berechtigungsbeschreibung finden
                        permission = next((p for p in roles_data["permissions"] if p["id"] == permission_id), None)
                        if permission:
                            st.write(f"- {permission['name']}: {permission['description']}")
                    
                    # Neue Rolle erstellen (nur für benutzerdefinierte Rollen)
                    if role["id"] > 4:
                        if st.button("Rolle löschen", key=f"delete_role_{role['id']}"):
                            # Prüfen, ob die Rolle verwendet wird
                            is_used = any(r == role["id"] for r in roles_data.get("employee_roles", {}).values())
                            
                            if is_used:
                                st.error("Diese Rolle kann nicht gelöscht werden, da sie noch Mitarbeitern zugewiesen ist.")
                            else:
                                # Rolle löschen
                                roles_data["roles"] = [r for r in roles_data["roles"] if r["id"] != role["id"]]
                                
                                # Daten speichern
                                save_roles_data(roles_data)
                                
                                st.success(f"Rolle {role['name']} gelöscht!")
                                st.rerun()
            
            # Neue Rolle erstellen
            st.subheader("Neue Rolle erstellen")
            
            new_role_name = st.text_input("Rollenname")
            new_role_description = st.text_area("Beschreibung")
            
            # Berechtigungen auswählen
            st.write("**Berechtigungen auswählen:**")
            
            selected_permissions = []
            for permission in roles_data["permissions"]:
                if st.checkbox(f"{permission['name']}: {permission['description']}", key=f"perm_{permission['id']}"):
                    selected_permissions.append(permission["id"])
            
            if st.button("Rolle erstellen"):
                if not new_role_name:
                    st.error("Bitte geben Sie einen Rollennamen ein.")
                elif not selected_permissions:
                    st.error("Bitte wählen Sie mindestens eine Berechtigung aus.")
                else:
                    # Neue Rollen-ID generieren
                    new_role_id = max(r["id"] for r in roles_data["roles"]) + 1
                    
                    # Neue Rolle erstellen
                    new_role = {
                        "id": new_role_id,
                        "name": new_role_name,
                        "description": new_role_description,
                        "permissions": selected_permissions
                    }
                    
                    # Rolle hinzufügen
                    roles_data["roles"].append(new_role)
                    
                    # Daten speichern
                    save_roles_data(roles_data)
                    
                    st.success(f"Rolle {new_role_name} erstellt!")
                    st.rerun()
    
    # Rückgabe der UI-Funktion und Hilfsfunktion
    return show_role_management_ui, has_permission

# Exportiere die Funktionen
__all__ = ['implement_management_roles']
