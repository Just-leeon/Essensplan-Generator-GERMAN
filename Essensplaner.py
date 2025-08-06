import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import webbrowser
import subprocess
import platform
from datetime import datetime, timedelta
import zipfile
from PIL import Image, ImageTk
import io
import json
import uuid

class MealPlanGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Essensplan Generator")
        self.root.geometry("900x800")  # Made window taller
        
        # Variables
        self.website_path = tk.StringVar()
        self.week_start = tk.StringVar()
        self.week_end = tk.StringVar()
        self.breakfast_rows = tk.StringVar(value="1")
        self.lunch_rows = tk.StringVar(value="1")
        self.snacks_rows = tk.StringVar(value="1")
        self.dessert_rows = tk.StringVar(value="/")
        
        # New settings variables
        self.empty_cell_display = tk.StringVar(value="-")  # "-" or "nothing"
        self.show_photos = tk.BooleanVar(value=True)
        self.show_sources_box = tk.BooleanVar(value=True)  # Changed to True by default
        self.source_pdf1_name = tk.StringVar(value="Ganze Zutaten Liste")
        self.source_pdf2_name = tk.StringVar(value="Nach Gericht getrennte Zutaten Liste")
        self.file_operation = tk.StringVar(value="copy")  # "copy" or "cut"
        self.rename_subfolder = tk.BooleanVar(value=False)
        
        # Will store dish assignments
        self.dish_assignments = {}
        self.dish_names = {}
        self.empty_cells = {}
        self.total_dishes = 0
        self.source_files = {"pdf1": tk.StringVar(), "pdf2": tk.StringVar()}
        
        # Meal library variables
        self.meals_library = {}
        self.meals_data_path = ""
        self.meal_file_operation = tk.StringVar(value="copy")  # "copy" or "cut" for meal library files
        self.current_selected_meal_id = None  # Track if current meal is from database
        
        # Initialize week dates
        self.set_current_week()
        
        # Initialize meal library and create pages
        self.init_meal_library()
        self.setup_meal_library_page()
    
    def set_current_week(self):
        """Set current week Monday to Sunday"""
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        self.week_start.set(monday.strftime("%d.%m.%y"))
        self.week_end.set(sunday.strftime("%d.%m.%y"))
    
    def previous_week(self):
        """Set previous week"""
        try:
            current_start = datetime.strptime(self.week_start.get(), "%d.%m.%y")
            new_start = current_start - timedelta(days=7)
            new_end = new_start + timedelta(days=6)
            self.week_start.set(new_start.strftime("%d.%m.%y"))
            self.week_end.set(new_end.strftime("%d.%m.%y"))
        except ValueError:
            self.set_current_week()
    
    def next_week(self):
        """Set next week"""
        try:
            current_start = datetime.strptime(self.week_start.get(), "%d.%m.%y")
            new_start = current_start + timedelta(days=7)
            new_end = new_start + timedelta(days=6)
            self.week_start.set(new_start.strftime("%d.%m.%y"))
            self.week_end.set(new_end.strftime("%d.%m.%y"))
        except ValueError:
            self.set_current_week()
    
    def init_meal_library(self):
        """Initialize meal library and create data directory"""
        # Create meals data directory next to script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.meals_data_path = os.path.join(script_dir, "meals_data")
        
        if not os.path.exists(self.meals_data_path):
            os.makedirs(self.meals_data_path)
        
        # Load existing meals
        self.load_meals_library()
    
    def load_meals_library(self):
        """Load meals from library"""
        library_file = os.path.join(self.meals_data_path, "meals_library.json")
        if os.path.exists(library_file):
            try:
                with open(library_file, 'r', encoding='utf-8') as f:
                    self.meals_library = json.load(f)
            except:
                self.meals_library = {}
        else:
            self.meals_library = {}
    
    def save_meals_library(self):
        """Save meals to library"""
        library_file = os.path.join(self.meals_data_path, "meals_library.json")
        try:
            with open(library_file, 'w', encoding='utf-8') as f:
                json.dump(self.meals_library, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Speichern der Gerichte: {str(e)}")
    
    def setup_meal_library_page(self):
        """New start page for meal library management"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Gerichte Bibliothek", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Search and sort controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        # Search
        ttk.Label(control_frame, text="Suchen:").grid(row=0, column=0, padx=(0, 5), sticky=tk.W)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.update_meals_display())
        search_entry = ttk.Entry(control_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=(0, 10), sticky=(tk.W, tk.E))
        
        # Sort options
        ttk.Label(control_frame, text="Sortieren:").grid(row=0, column=2, padx=(0, 5), sticky=tk.W)
        self.sort_var = tk.StringVar(value="erstellungsdatum")
        sort_combo = ttk.Combobox(control_frame, textvariable=self.sort_var, 
                                 values=["erstellungsdatum", "alphabet", "zuletzt_verwendet"], 
                                 state="readonly", width=15)
        sort_combo.grid(row=0, column=3, sticky=tk.W)
        sort_combo.bind('<<ComboboxSelected>>', lambda *args: self.update_meals_display())
        
        # Meals data folder location
        ttk.Label(main_frame, text="Speicherort der Gerichte-Datenbank:").grid(row=2, column=0, sticky=tk.W, pady=5)
        meals_data_var = tk.StringVar(value=self.meals_data_path)
        meals_data_entry = ttk.Entry(main_frame, textvariable=meals_data_var, width=50)
        meals_data_entry.grid(row=2, column=1, padx=5, sticky=(tk.W, tk.E))
        ttk.Button(main_frame, text="Durchsuchen", 
                  command=lambda: self.browse_meals_data_directory(meals_data_var)).grid(row=2, column=2, padx=5)
        
        # Create scrollable frame for meals with mouse wheel support
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Store references for updating display
        self.meals_canvas = canvas
        self.meals_scrollable_frame = scrollable_frame
        
        # Bind mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel events
        canvas.bind("<Enter>", bind_to_mousewheel)
        canvas.bind("<Leave>", unbind_from_mousewheel)
        scrollable_frame.bind("<Enter>", bind_to_mousewheel)
        scrollable_frame.bind("<Leave>", unbind_from_mousewheel)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S), pady=(10, 0))
        
        # Display meals
        self.update_meals_display()
        
        # Add meal button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="+ Neues Gericht hinzufügen",
                  command=self.add_new_meal).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Weiter zum Essensplan", 
                  command=self.setup_page1).pack(side=tk.RIGHT, padx=5)
    
    def browse_meals_data_directory(self, path_var):
        """Browse for meals data directory"""
        directory = filedialog.askdirectory(title="Gerichte-Datenbank Ordner auswählen", 
                                          initialdir=self.meals_data_path)
        if directory:
            self.meals_data_path = directory
            path_var.set(directory)
            self.load_meals_library()  # Reload meals from new location
            self.setup_meal_library_page()  # Refresh display
    
    def update_meals_display(self):
        """Update the display of meals based on search and sort criteria"""
        # Clear existing widgets
        for widget in self.meals_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.meals_library:
            ttk.Label(self.meals_scrollable_frame, text="Noch keine Gerichte vorhanden. Füge dein erstes Gericht hinzu!", 
                     font=("Arial", 12), foreground="gray").pack(pady=50)
            return
        
        # Get search term
        search_term = self.search_var.get().lower().strip()
        
        # Filter meals based on search
        filtered_meals = {}
        for meal_id, meal_data in self.meals_library.items():
            if (not search_term or 
                search_term in meal_data['name'].lower() or 
                search_term in meal_data.get('additional_info', '').lower() or
                search_term in meal_id.lower()):
                filtered_meals[meal_id] = meal_data
        
        # Sort meals
        sort_option = self.sort_var.get()
        if sort_option == "alphabet":
            # Sort by name alphabetically
            sorted_meals = sorted(filtered_meals.items(), key=lambda x: x[1]['name'].lower())
        elif sort_option == "zuletzt_verwendet":
            # Sort by last used (if available, otherwise by creation order)
            sorted_meals = sorted(filtered_meals.items(), 
                                key=lambda x: x[1].get('last_used', ''), reverse=True)
        else:  # erstellungsdatum (default)
            # Keep original order from JSON (creation order)
            sorted_meals = list(filtered_meals.items())
        
        if not sorted_meals:
            ttk.Label(self.meals_scrollable_frame, text="Keine Gerichte gefunden.", 
                     font=("Arial", 12), foreground="gray").pack(pady=50)
            return
        
        # Create grid of meal cards
        row = 0
        col = 0
        max_cols = 3
        
        for meal_id, meal_data in sorted_meals:
            # Create meal card
            card_frame = ttk.LabelFrame(self.meals_scrollable_frame, text=meal_data['name'], padding="10")
            card_frame.grid(row=row, column=col, padx=10, pady=10, sticky=(tk.W, tk.E))
            
            # Image display
            if meal_data.get('image_path') and os.path.exists(meal_data['image_path']):
                try:
                    # Load and resize image
                    img = Image.open(meal_data['image_path'])
                    img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    img_label = ttk.Label(card_frame, image=photo)
                    img_label.image = photo  # Keep a reference
                    img_label.pack(pady=5)
                except:
                    ttk.Label(card_frame, text="Bild nicht verfügbar", 
                             foreground="gray").pack(pady=5)
            else:
                ttk.Label(card_frame, text="Kein Bild", foreground="gray").pack(pady=5)
            
            # Additional info
            if meal_data.get('additional_info'):
                info_text = meal_data['additional_info'][:50] + ("..." if len(meal_data['additional_info']) > 50 else "")
                ttk.Label(card_frame, text=info_text, font=("Arial", 9), 
                         foreground="gray").pack(pady=2)
            
            # Buttons
            btn_frame = ttk.Frame(card_frame)
            btn_frame.pack(pady=5)
            
            ttk.Button(btn_frame, text="Bearbeiten", 
                      command=lambda m_id=meal_id: self.edit_meal(m_id)).pack(side=tk.LEFT, padx=2)
            ttk.Button(btn_frame, text="Löschen", 
                      command=lambda m_id=meal_id: self.delete_meal(m_id)).pack(side=tk.LEFT, padx=2)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Configure column weights
        for i in range(max_cols):
            self.meals_scrollable_frame.columnconfigure(i, weight=1)
        
        # Update scroll region
        self.meals_scrollable_frame.update_idletasks()
        self.meals_canvas.configure(scrollregion=self.meals_canvas.bbox("all"))
    
    def add_new_meal(self):
        """Open dialog to add new meal"""
        self.meal_dialog(None)
    
    def edit_meal(self, meal_id):
        """Open dialog to edit existing meal"""
        self.meal_dialog(meal_id)
    
    def meal_dialog(self, meal_id=None):
        """Dialog for adding/editing meals"""
        is_edit = meal_id is not None
        meal_data = self.meals_library.get(meal_id, {}) if is_edit else {}
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Gericht bearbeiten" if is_edit else "Neues Gericht hinzufügen")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show Meal ID for editing
        if is_edit:
            id_frame = ttk.Frame(main_frame)
            id_frame.pack(fill=tk.X, pady=(0, 15))
            ttk.Label(id_frame, text="Meal ID:", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
            id_label = ttk.Label(id_frame, text=meal_id, font=("Arial", 9), foreground="gray")
            id_label.pack(side=tk.LEFT, padx=(5, 0))
            
            # Add copy button for meal ID
            def copy_meal_id():
                dialog.clipboard_clear()
                dialog.clipboard_append(meal_id)
                messagebox.showinfo("Kopiert", "Meal ID wurde in die Zwischenablage kopiert!")
            
            ttk.Button(id_frame, text="📋 Kopieren", command=copy_meal_id).pack(side=tk.RIGHT)
        
        # Name
        ttk.Label(main_frame, text="Name des Gerichts:").pack(anchor=tk.W, pady=(0, 5))
        name_var = tk.StringVar(value=meal_data.get('name', ''))
        name_entry = ttk.Entry(main_frame, textvariable=name_var, width=50)
        name_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Image
        ttk.Label(main_frame, text="Bild des Gerichts:").pack(anchor=tk.W, pady=(0, 5))
        image_path_var = tk.StringVar(value=meal_data.get('image_path', ''))
        
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(fill=tk.X, pady=(0, 15))
        
        image_entry = ttk.Entry(image_frame, textvariable=image_path_var, width=40)
        image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(image_frame, text="Durchsuchen", 
                  command=lambda: self.browse_image(image_path_var)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(image_frame, text="📋", 
                  command=lambda: self.paste_image_from_clipboard_for_meal(image_path_var)).pack(side=tk.RIGHT, padx=(5, 0))
        
        # PDF Recipe
        ttk.Label(main_frame, text="PDF Rezept:").pack(anchor=tk.W, pady=(0, 5))
        pdf_path_var = tk.StringVar(value=meal_data.get('pdf_path', ''))
        
        pdf_frame = ttk.Frame(main_frame)
        pdf_frame.pack(fill=tk.X, pady=(0, 15))
        
        pdf_entry = ttk.Entry(pdf_frame, textvariable=pdf_path_var, width=40)
        pdf_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(pdf_frame, text="Durchsuchen", 
                  command=lambda: self.browse_pdf_for_meal(pdf_path_var)).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(pdf_frame, text="📋", 
                  command=lambda: self.paste_pdf_from_clipboard_for_meal(pdf_path_var)).pack(side=tk.RIGHT, padx=(5, 0))
        
        # File operation setting
        ttk.Label(main_frame, text="Datei-Operation:").pack(anchor=tk.W, pady=(0, 5))
        file_op_frame = ttk.Frame(main_frame)
        file_op_frame.pack(anchor=tk.W, pady=(0, 15))
        ttk.Radiobutton(file_op_frame, text="Kopieren", variable=self.meal_file_operation, value="copy").pack(side=tk.LEFT)
        ttk.Radiobutton(file_op_frame, text="Ausschneiden", variable=self.meal_file_operation, value="cut").pack(side=tk.LEFT, padx=(20, 0))
        
        # Additional info
        ttk.Label(main_frame, text="Zusätzliche Informationen:").pack(anchor=tk.W, pady=(0, 5))
        info_text = tk.Text(main_frame, height=8, width=50)
        info_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        if meal_data.get('additional_info'):
            info_text.insert('1.0', meal_data['additional_info'])
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def save_meal():
            nonlocal meal_id  # Allow access to meal_id from outer scope
            
            name = name_var.get().strip()
            if not name:
                messagebox.showerror("Fehler", "Bitte geben Sie einen Namen für das Gericht ein.")
                return
            
            # Check for changes
            has_changes = False
            changes_made = []
            
            # Check name change
            if not is_edit or name != meal_data.get('name', ''):
                has_changes = True
                changes_made.append("Name")
            
            # Check additional info change
            new_additional_info = info_text.get('1.0', 'end-1c').strip()
            if not is_edit or new_additional_info != meal_data.get('additional_info', ''):
                has_changes = True
                changes_made.append("Zusätzliche Informationen")
            
            # Check image path change
            current_image_path = image_path_var.get()
            original_image_path = meal_data.get('image_path', '') if is_edit else ''
            image_changed = current_image_path != original_image_path
            if image_changed:
                has_changes = True
                changes_made.append("Bild")
            
            # Check PDF path change
            current_pdf_path = pdf_path_var.get()
            original_pdf_path = meal_data.get('pdf_path', '') if is_edit else ''
            pdf_changed = current_pdf_path != original_pdf_path
            if pdf_changed:
                has_changes = True
                changes_made.append("PDF")
            
            # If editing and no changes detected, show message
            if is_edit and not has_changes:
                messagebox.showinfo("Information", "Keine Änderungen erkannt. Das Gericht wurde nicht gespeichert.")
                return
            
            # Create meal data
            new_meal_data = {
                'name': name,
                'image_path': '',
                'pdf_path': '',
                'additional_info': new_additional_info
            }
            
            # Generate meal ID if new, otherwise use existing ID
            if not is_edit:
                meal_id = str(uuid.uuid4())
            # For editing, meal_id is already available from the function parameter
            
            # Create meal directory
            meal_dir = os.path.join(self.meals_data_path, f"meal_{meal_id}")
            if not os.path.exists(meal_dir):
                os.makedirs(meal_dir)
            
            # Handle image file only if it has changed
            if current_image_path and os.path.exists(current_image_path):
                if image_changed:
                    try:
                        image_ext = os.path.splitext(current_image_path)[1]
                        new_image_path = os.path.join(meal_dir, f"image{image_ext}")
                        
                        # Only copy/move if the source is different from destination
                        if os.path.abspath(current_image_path) != os.path.abspath(new_image_path):
                            if self.meal_file_operation.get() == "copy":
                                shutil.copy2(current_image_path, new_image_path)
                            else:  # cut
                                shutil.move(current_image_path, new_image_path)
                        
                        new_meal_data['image_path'] = new_image_path
                    except Exception as e:
                        messagebox.showwarning("Warnung", f"Bild konnte nicht {'kopiert' if self.meal_file_operation.get() == 'copy' else 'verschoben'} werden: {str(e)}")
                        # Keep the original path if copy/move failed
                        new_meal_data['image_path'] = current_image_path
                else:
                    # No change, keep original path
                    new_meal_data['image_path'] = current_image_path
            elif is_edit:
                # Keep existing image path if no new image provided
                new_meal_data['image_path'] = original_image_path
            
            # Handle PDF file only if it has changed
            if current_pdf_path and os.path.exists(current_pdf_path):
                if pdf_changed:
                    try:
                        pdf_ext = os.path.splitext(current_pdf_path)[1]
                        new_pdf_path = os.path.join(meal_dir, f"recipe{pdf_ext}")
                        
                        # Only copy/move if the source is different from destination
                        if os.path.abspath(current_pdf_path) != os.path.abspath(new_pdf_path):
                            if self.meal_file_operation.get() == "copy":
                                shutil.copy2(current_pdf_path, new_pdf_path)
                            else:  # cut
                                shutil.move(current_pdf_path, new_pdf_path)
                        
                        new_meal_data['pdf_path'] = new_pdf_path
                    except Exception as e:
                        messagebox.showwarning("Warnung", f"PDF konnte nicht {'kopiert' if self.meal_file_operation.get() == 'copy' else 'verschoben'} werden: {str(e)}")
                        # Keep the original path if copy/move failed
                        new_meal_data['pdf_path'] = current_pdf_path
                else:
                    # No change, keep original path
                    new_meal_data['pdf_path'] = current_pdf_path
            elif is_edit:
                # Keep existing PDF path if no new PDF provided
                new_meal_data['pdf_path'] = original_pdf_path
            
            # Save to library
            self.meals_library[meal_id] = new_meal_data
            self.save_meals_library()
            
            # Clean up temporary files after successful save
            self.cleanup_temp_meal_files()
            
            # Show success message with what was changed
            if is_edit:
                if changes_made:
                    messagebox.showinfo("Erfolg", f"Gericht wurde erfolgreich aktualisiert!\nGeänderte Bereiche: {', '.join(changes_made)}")
                else:
                    messagebox.showinfo("Information", "Gericht wurde gespeichert (keine Änderungen erkannt).")
            else:
                messagebox.showinfo("Erfolg", "Neues Gericht wurde erfolgreich hinzugefügt!")
            
            dialog.destroy()
            # Check if we have the attributes needed for updating display
            if hasattr(self, 'meals_scrollable_frame') and hasattr(self, 'update_meals_display'):
                self.update_meals_display()  # Refresh display
            else:
                self.setup_meal_library_page()  # Fallback for full refresh
        
        def cancel_meal():
            """Cancel and clean up temporary files"""
            self.cleanup_temp_meal_files()
            dialog.destroy()
        
        ttk.Button(button_frame, text="Speichern", command=save_meal).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Abbrechen", command=cancel_meal).pack(side=tk.RIGHT)
        
        # Focus on name entry
        name_entry.focus_set()
    
    def cleanup_temp_meal_files(self):
        """Clean up temporary files in meals_data/temp directory"""
        temp_dir = os.path.join(self.meals_data_path, "temp")
        if os.path.exists(temp_dir):
            try:
                for filename in os.listdir(temp_dir):
                    if filename.startswith("temp_"):
                        file_path = os.path.join(temp_dir, filename)
                        try:
                            os.remove(file_path)
                        except:
                            pass  # Ignore if file can't be deleted
            except:
                pass  # Ignore any directory access errors
    
    def update_file_operation_state(self):
        """Update file operation radio buttons based on whether database meals are selected"""
        has_database_meals = False
        
        # Check if any dish uses a meal from database
        for dish_num in self.file_entries:
            pdf_path = self.file_entries[dish_num]["pdf"].get()
            photo_path = self.file_entries[dish_num]["photo"].get()
            
            # Check if paths are from meals_data folder (indicating database meal)
            if ((pdf_path and self.meals_data_path in pdf_path) or 
                (photo_path and self.meals_data_path in photo_path)):
                has_database_meals = True
                break
        
        if has_database_meals:
            # Disable cut option and show warning
            self.cut_radio.config(state='disabled')
            if self.file_operation.get() == "cut":
                self.file_operation.set("copy")  # Force to copy
            self.file_op_warning.config(text="⚠️ Ausschneiden deaktiviert - Gerichte aus der Datenbank würden beschädigt werden!")
        else:
            # Enable cut option and clear warning
            self.cut_radio.config(state='normal')
            self.file_op_warning.config(text="")
    
    def browse_image(self, path_var):
        """Browse for image file"""
        filetypes = [
            ("Bild Dateien", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("Alle Dateien", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Bild auswählen", filetypes=filetypes)
        if filename:
            path_var.set(filename)
    
    def browse_pdf_for_meal(self, path_var):
        """Browse for PDF file for meal library"""
        filetypes = [
            ("PDF Dateien", "*.pdf"),
            ("Alle Dateien", "*.*")
        ]
        filename = filedialog.askopenfilename(title="PDF auswählen", filetypes=filetypes)
        if filename:
            path_var.set(filename)
    
    def paste_pdf_from_clipboard_for_meal(self, path_var):
        """Paste PDF from clipboard for meal library - creates temporary file"""
        try:
            # First, try to get file path from clipboard
            clipboard_content = self.root.clipboard_get()
            if clipboard_content and os.path.exists(clipboard_content) and clipboard_content.lower().endswith('.pdf'):
                # Create temporary copy in meals_data folder
                temp_dir = os.path.join(self.meals_data_path, "temp")
                os.makedirs(temp_dir, exist_ok=True)
                temp_filename = f"temp_pdf_{uuid.uuid4().hex[:8]}.pdf"
                temp_path = os.path.join(temp_dir, temp_filename)
                shutil.copy2(clipboard_content, temp_path)
                path_var.set(temp_path)
                messagebox.showinfo("Erfolg", "PDF aus Zwischenablage eingefügt!")
                return
            
            # If no valid file path, check if there's actual file data in clipboard (not implemented for PDFs)
            messagebox.showwarning("Warnung", "Kein gültiger PDF-Pfad in der Zwischenablage gefunden!\nBitte kopieren Sie den Dateipfad einer PDF-Datei.")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Einfügen aus Zwischenablage: {str(e)}")
    
    def paste_image_from_clipboard_for_meal(self, path_var):
        """Paste image from clipboard for meal library - creates temporary file"""
        try:
            # First, try to get actual image data from clipboard
            from PIL import ImageGrab
            img = ImageGrab.grabclipboard()
            if img:
                # Create temporary directory in meals_data
                temp_dir = os.path.join(self.meals_data_path, "temp")
                os.makedirs(temp_dir, exist_ok=True)
                
                # Determine format and save
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    temp_filename = f"temp_image_{uuid.uuid4().hex[:8]}.png"
                    temp_path = os.path.join(temp_dir, temp_filename)
                    img.save(temp_path, "PNG")
                else:
                    temp_filename = f"temp_image_{uuid.uuid4().hex[:8]}.jpg"
                    temp_path = os.path.join(temp_dir, temp_filename)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(temp_path, "JPEG", quality=90)
                
                path_var.set(temp_path)
                messagebox.showinfo("Erfolg", "Bild aus Zwischenablage eingefügt!")
                return
            
            # If no image data, try file path from clipboard
            clipboard_content = self.root.clipboard_get()
            valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
            if clipboard_content and os.path.exists(clipboard_content) and clipboard_content.lower().endswith(valid_extensions):
                # Create temporary copy in meals_data folder
                temp_dir = os.path.join(self.meals_data_path, "temp")
                os.makedirs(temp_dir, exist_ok=True)
                file_ext = os.path.splitext(clipboard_content)[1]
                temp_filename = f"temp_image_{uuid.uuid4().hex[:8]}{file_ext}"
                temp_path = os.path.join(temp_dir, temp_filename)
                shutil.copy2(clipboard_content, temp_path)
                path_var.set(temp_path)
                messagebox.showinfo("Erfolg", "Bild aus Zwischenablage eingefügt!")
                return
            
            messagebox.showwarning("Warnung", "Keine Bilddaten oder gültiger Bild-Pfad in der Zwischenablage gefunden!")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Einfügen aus Zwischenablage: {str(e)}")
    
    def browse_pdf(self, dish_num, path_var):
        """Browse for PDF file with dish number"""
        filetypes = [
            ("PDF Dateien", "*.pdf"),
            ("Alle Dateien", "*.*")
        ]
        filename = filedialog.askopenfilename(title=f"PDF für Gericht {dish_num} auswählen", filetypes=filetypes)
        if filename:
            path_var.set(filename)
    
    def delete_meal(self, meal_id):
        """Delete a meal from the library"""
        meal_name = self.meals_library[meal_id]['name']
        if messagebox.askyesno("Löschen bestätigen", 
                              f"Möchten Sie das Gericht '{meal_name}' wirklich löschen?"):
            # Delete meal directory
            meal_dir = os.path.join(self.meals_data_path, f"meal_{meal_id}")
            if os.path.exists(meal_dir):
                try:
                    shutil.rmtree(meal_dir)
                except:
                    pass
            
            # Remove from library
            del self.meals_library[meal_id]
            self.save_meals_library()
            self.update_meals_display()  # Refresh display
    
    def setup_page1(self):
        """Configuration page"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Auto-create default folder if website_path is not set or empty
        if not self.website_path.get():
            script_dir = os.path.dirname(os.path.abspath(__file__))
            date_range = f"{self.week_start.get()}-{self.week_end.get()}"
            default_folder = os.path.join(script_dir, f"Essensplan {date_range}")
            
            if not os.path.exists(default_folder):
                try:
                    os.makedirs(default_folder)
                except Exception as e:
                    print(f"Could not create default folder: {e}")
                    default_folder = script_dir
            
            self.website_path.set(default_folder)
            
        # Initialize form change tracking
        self.form_changed = False
        self.original_values = {
            'website_path': self.website_path.get(),
            'week_start': self.week_start.get(),
            'week_end': self.week_end.get(),
            'breakfast_rows': self.breakfast_rows.get(),
            'lunch_rows': self.lunch_rows.get(),
            'snacks_rows': self.snacks_rows.get(),
            'dessert_rows': self.dessert_rows.get(),
            'empty_cell_display': self.empty_cell_display.get(),
            'show_photos': self.show_photos.get(),
            'show_sources_box': self.show_sources_box.get(),
            'source_pdf1_name': self.source_pdf1_name.get(),
            'source_pdf2_name': self.source_pdf2_name.get(),
            'rename_subfolder': self.rename_subfolder.get()
        }
            
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Essensplan Generator - Konfiguration", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Website path selection
        ttk.Label(main_frame, text="Speicherort der Webseite:").grid(row=1, column=0, sticky=tk.W, pady=5)
        website_entry = ttk.Entry(main_frame, textvariable=self.website_path, width=50)
        website_entry.grid(row=1, column=1, columnspan=2, padx=5, sticky=(tk.W, tk.E))
        website_entry.bind('<KeyPress>', self.on_form_change)
        ttk.Button(main_frame, text="Durchsuchen", 
                  command=self.browse_directory).grid(row=1, column=3, padx=5)
        
        # Week date range
        ttk.Label(main_frame, text="Wochenspanne:", 
                 font=("Arial", 12, "bold")).grid(row=2, column=0, columnspan=4, pady=(20, 10))
        
        # Week navigation frame
        week_frame = ttk.Frame(main_frame)
        week_frame.grid(row=3, column=0, columnspan=4, pady=5)
        
        ttk.Button(week_frame, text="◄ Vorherige Woche", 
                  command=self.previous_week).grid(row=0, column=0, padx=5)
        
        ttk.Label(week_frame, text="Von:").grid(row=0, column=1, sticky=tk.W, pady=5, padx=(20, 5))
        ttk.Entry(week_frame, textvariable=self.week_start, width=12).grid(row=0, column=2, sticky=tk.W, padx=5)
        ttk.Label(week_frame, text="Bis:").grid(row=0, column=3, sticky=tk.W, pady=5, padx=(20, 5))
        ttk.Entry(week_frame, textvariable=self.week_end, width=12).grid(row=0, column=4, sticky=tk.W, padx=5)
        
        ttk.Button(week_frame, text="Nächste Woche ►", 
                  command=self.next_week).grid(row=0, column=5, padx=(20, 5))
        
        # Category rows configuration
        ttk.Label(main_frame, text="Anzahl Zeilen pro Kategorie:", 
                 font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=4, pady=(20, 10))
        
        ttk.Label(main_frame, text="Frühstück:").grid(row=5, column=0, sticky=tk.W, pady=5)
        breakfast_entry = ttk.Entry(main_frame, textvariable=self.breakfast_rows, width=10)
        breakfast_entry.grid(row=5, column=1, sticky=tk.W, padx=5)
        breakfast_entry.bind('<KeyPress>', self.on_form_change)
        
        ttk.Label(main_frame, text="Mittag-/Abendessen:").grid(row=6, column=0, sticky=tk.W, pady=5)
        lunch_entry = ttk.Entry(main_frame, textvariable=self.lunch_rows, width=10)
        lunch_entry.grid(row=6, column=1, sticky=tk.W, padx=5)
        lunch_entry.bind('<KeyPress>', self.on_form_change)
        
        ttk.Label(main_frame, text="Snacks:").grid(row=7, column=0, sticky=tk.W, pady=5)
        snacks_entry = ttk.Entry(main_frame, textvariable=self.snacks_rows, width=10)
        snacks_entry.grid(row=7, column=1, sticky=tk.W, padx=5)
        snacks_entry.bind('<KeyPress>', self.on_form_change)
        
        ttk.Label(main_frame, text="Nachtisch:").grid(row=8, column=0, sticky=tk.W, pady=5)
        dessert_entry = ttk.Entry(main_frame, textvariable=self.dessert_rows, width=10)
        dessert_entry.grid(row=8, column=1, sticky=tk.W, padx=5)
        dessert_entry.bind('<KeyPress>', self.on_form_change)
        
        # Info label
        info_label = ttk.Label(main_frame, text="Hinweis: Eingabe '/' bedeutet, dass die Kategorie nicht angezeigt wird",
                              font=("Arial", 9), foreground="gray")
        info_label.grid(row=9, column=0, columnspan=4, pady=10)
        
        # Settings section
        ttk.Label(main_frame, text="Einstellungen:", 
                 font=("Arial", 12, "bold")).grid(row=10, column=0, columnspan=4, pady=(20, 10))
        
        # Empty cell display
        ttk.Label(main_frame, text="Anzeige für leere Zellen:").grid(row=11, column=0, sticky=tk.W, pady=5)
        empty_frame = ttk.Frame(main_frame)
        empty_frame.grid(row=11, column=1, columnspan=3, sticky=tk.W, padx=5)
        ttk.Radiobutton(empty_frame, text='"-" anzeigen', variable=self.empty_cell_display, value="-").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(empty_frame, text="Gar nichts anzeigen", variable=self.empty_cell_display, value="nothing").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Show photos
        photos_checkbox = ttk.Checkbutton(main_frame, text="Fotos anzeigen", variable=self.show_photos, command=self.on_form_change)
        photos_checkbox.grid(row=12, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Removed file operation setting from page 1 - moved to page 2
        
        # Rename subfolder option
        rename_checkbox = ttk.Checkbutton(main_frame, text="Unterordner zu 'Essensplan [Zeitspanne]' umbenennen", 
                       variable=self.rename_subfolder, command=self.on_form_change)
        rename_checkbox.grid(row=13, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        # Show sources box
        sources_checkbox = ttk.Checkbutton(main_frame, text="Download Links anzeigen", variable=self.show_sources_box, 
                                         command=lambda: [self.toggle_sources_options(), self.on_form_change()])
        sources_checkbox.grid(row=14, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Source PDF names
        self.sources_frame = ttk.LabelFrame(main_frame, text="Download Links Namen", padding="10")
        self.sources_frame.grid(row=15, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.sources_frame, text="PDF 1:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pdf1_entry = ttk.Entry(self.sources_frame, textvariable=self.source_pdf1_name, width=40)
        self.pdf1_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.pdf1_entry.bind('<KeyPress>', self.on_form_change)
        
        ttk.Label(self.sources_frame, text="PDF 2:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.pdf2_entry = ttk.Entry(self.sources_frame, textvariable=self.source_pdf2_name, width=40)
        self.pdf2_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        self.pdf2_entry.bind('<KeyPress>', self.on_form_change)
        
        self.sources_frame.columnconfigure(1, weight=1)
        
        # Notes Mode Button
        ttk.Button(main_frame, text="Notizen-Modus öffnen", 
                  command=self.open_notes_mode).grid(row=16, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Back and Continue buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=17, column=0, columnspan=4, pady=20)
        
        ttk.Button(button_frame, text="← Zurück", 
                  command=self.go_back_to_library_with_warning).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Weiter", command=self.validate_and_continue).pack(side=tk.RIGHT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Initialize sources options state
        self.toggle_sources_options()
    
    def open_notes_mode(self):
        """Open notes planning window with adaptive layout"""
        notes_window = tk.Toplevel(self.root)
        notes_window.title("Notizen-Modus - Essensplan Planung")
        notes_window.geometry("1400x800")  # Made larger to accommodate weekend visibility
        
        main_frame = ttk.Frame(notes_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a paned window to separate table from instructions
        paned_window = ttk.PanedWindow(main_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Top frame for the table
        table_frame = ttk.Frame(paned_window)
        paned_window.add(table_frame, weight=4)
        
        ttk.Label(table_frame, text="Essensplan Notizen", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Create a simple table for notes
        canvas = tk.Canvas(table_frame)
        scrollbar_v = ttk.Scrollbar(table_frame, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(table_frame, orient="horizontal", command=canvas.xview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Table headers
        days = ["", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        for i, day in enumerate(days):
            label = ttk.Label(scrollable_frame, text=day, font=("Arial", 10, "bold"))
            label.grid(row=0, column=i, padx=2, pady=2, sticky="ew")
        
        # Build categories based on current settings
        categories = []
        try:
            if self.breakfast_rows.get() != "/":
                for i in range(int(self.breakfast_rows.get())):
                    categories.append(f"Frühstück {i+1}" if int(self.breakfast_rows.get()) > 1 else "Frühstück")
            if self.lunch_rows.get() != "/":
                for i in range(int(self.lunch_rows.get())):
                    categories.append(f"Mittag-/Abendessen {i+1}" if int(self.lunch_rows.get()) > 1 else "Mittag-/Abendessen")
            if self.snacks_rows.get() != "/":
                for i in range(int(self.snacks_rows.get())):
                    categories.append(f"Snacks {i+1}" if int(self.snacks_rows.get()) > 1 else "Snacks")
            if self.dessert_rows.get() != "/":
                for i in range(int(self.dessert_rows.get())):
                    categories.append(f"Nachtisch {i+1}" if int(self.dessert_rows.get()) > 1 else "Nachtisch")
        except ValueError:
            # Fallback to default categories if values are invalid
            categories = ["Frühstück", "Mittag-/Abendessen", "Snacks", "Nachtisch"]
        
        # Table rows with dish numbers - column-wise numbering
        self.notes_entries = {}
        self.notes_text_widgets = []  # For arrow key navigation
        
        for row_idx, category in enumerate(categories, 1):
            ttk.Label(scrollable_frame, text=category, font=("Arial", 10, "bold")).grid(row=row_idx, column=0, padx=2, pady=2, sticky="w")
            for col_idx in range(1, 8):  # Days 1-7
                # Create frame for text widget with background number
                cell_frame = tk.Frame(scrollable_frame, relief="solid", bd=1, bg="white")
                cell_frame.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="ew")
                
                # Calculate dish number column-wise (by day first, then by category)
                day_idx = col_idx - 1  # 0-6 for Monday-Sunday
                category_idx = row_idx - 1  # 0-based category index
                total_categories = len(categories)
                dish_counter = (day_idx * total_categories) + category_idx + 1
                
                # Create a text widget with placeholder background text
                entry = tk.Text(cell_frame, width=15, height=3, bg="white", wrap="word")
                entry.pack(fill="both", expand=True)
                
                # Add dish number as placeholder text in the background
                entry.insert("1.0", f"[{dish_counter}]\n\n")
                entry.tag_add("dish_number", "1.0", "1.end")
                entry.tag_config("dish_number", foreground="#cccccc", font=("Arial", 8))
                
                # Bind events to maintain dish number display
                def on_focus_in(event, widget=entry, number=dish_counter):
                    # Keep the dish number visible but allow editing after it
                    current_content = widget.get("1.0", "end-1c")
                    if not current_content.startswith(f"[{number}]"):
                        widget.delete("1.0", "end")
                        widget.insert("1.0", f"[{number}]\n\n")
                        widget.tag_add("dish_number", "1.0", "1.end")
                        widget.tag_config("dish_number", foreground="#cccccc", font=("Arial", 8))
                        widget.mark_set("insert", "2.0")
                
                def on_key_press(event, widget=entry, number=dish_counter):
                    # Prevent editing of the dish number line
                    if widget.index("insert").split('.')[0] == "1":
                        if event.keysym not in ["Down", "Right", "End"]:
                            widget.mark_set("insert", "2.0")
                            return "break"
                
                entry.bind("<FocusIn>", on_focus_in)
                entry.bind("<KeyPress>", on_key_press)
                
                # Store for navigation
                self.notes_text_widgets.append(entry)
                self.notes_entries[f"{category}_{col_idx}"] = entry
        
        # Add arrow key navigation
        def navigate_cells(event):
            widget = event.widget
            if widget in self.notes_text_widgets:
                current_idx = self.notes_text_widgets.index(widget)
                total_widgets = len(self.notes_text_widgets)
                cols = 7  # 7 days
                
                if event.keysym == "Up" and event.state & 0x4:  # Ctrl+Up
                    new_idx = current_idx - cols if current_idx >= cols else current_idx
                elif event.keysym == "Down" and event.state & 0x4:  # Ctrl+Down
                    new_idx = current_idx + cols if current_idx + cols < total_widgets else current_idx
                elif event.keysym == "Left" and event.state & 0x4:  # Ctrl+Left
                    new_idx = current_idx - 1 if current_idx > 0 else current_idx
                elif event.keysym == "Right" and event.state & 0x4:  # Ctrl+Right
                    new_idx = current_idx + 1 if current_idx < total_widgets - 1 else current_idx
                else:
                    return
                
                self.notes_text_widgets[new_idx].focus_set()
                return "break"
        
        # Bind navigation to all text widgets
        for widget in self.notes_text_widgets:
            widget.bind("<Control-Up>", navigate_cells)
            widget.bind("<Control-Down>", navigate_cells)
            widget.bind("<Control-Left>", navigate_cells)
            widget.bind("<Control-Right>", navigate_cells)
        
        # Configure scrollable frame
        for i in range(8):
            scrollable_frame.columnconfigure(i, weight=1)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar_v.pack(side="right", fill="y")
        scrollbar_h.pack(side="bottom", fill="x")
        
        # Bottom frame for instructions and controls
        control_frame = ttk.Frame(paned_window)
        paned_window.add(control_frame, weight=1)
        
        # Instructions
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill=tk.X, pady=10)
        ttk.Label(info_frame, text="Tipp: Verwende Strg + Pfeiltasten zur Navigation zwischen den Zellen", 
                 font=("Arial", 10), foreground="gray").pack()
        
        # Close button
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Schließen", command=notes_window.destroy).pack()
    
    def toggle_sources_options(self):
        """Enable/disable sources options based on checkbox state"""
        if self.show_sources_box.get():
            self.pdf1_entry.config(state='normal')
            self.pdf2_entry.config(state='normal')
        else:
            self.pdf1_entry.config(state='disabled')
            self.pdf2_entry.config(state='disabled')
    
    def browse_directory(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory()
        if directory:
            self.website_path.set(directory)
    
    def validate_and_continue(self):
        """Validate inputs and proceed to page 2"""
        if not self.website_path.get():
            messagebox.showerror("Fehler", "Bitte wählen Sie einen Speicherort aus!")
            return
            
        if not self.week_start.get() or not self.week_end.get():
            messagebox.showerror("Fehler", "Bitte geben Sie die Wochenspanne an!")
            return
            
        # Calculate total dishes needed - column-wise numbering
        try:
            self.total_dishes = 0
            categories = []
            
            if self.breakfast_rows.get() != "/":
                breakfast_count = int(self.breakfast_rows.get()) * 7
                self.total_dishes += breakfast_count
                categories.append(("Frühstück", int(self.breakfast_rows.get())))
                
            if self.lunch_rows.get() != "/":
                lunch_count = int(self.lunch_rows.get()) * 7
                self.total_dishes += lunch_count
                categories.append(("Mittag-/Abendessen", int(self.lunch_rows.get())))
                
            if self.snacks_rows.get() != "/":
                snacks_count = int(self.snacks_rows.get()) * 7
                self.total_dishes += snacks_count
                categories.append(("Snacks", int(self.snacks_rows.get())))
                
            if self.dessert_rows.get() != "/":
                dessert_count = int(self.dessert_rows.get()) * 7
                self.total_dishes += dessert_count
                categories.append(("Nachtisch", int(self.dessert_rows.get())))
                
            self.categories = categories
            
        except ValueError:
            messagebox.showerror("Fehler", "Bitte geben Sie gültige Zahlen ein!")
            return
            
        # Generate website structure
        self.generate_website_structure()
        
        # Move to page 2
        self.setup_page2()
    
    def generate_website_structure(self):
        """Generate the HTML and CSS files with placeholders"""
        website_dir = self.website_path.get()
        
        # Create directories
        os.makedirs(os.path.join(website_dir, "media", "photos"), exist_ok=True)
        os.makedirs(os.path.join(website_dir, "media", "pdfs"), exist_ok=True)
        
        # Initialize dish names with default values - column-wise numbering
        total_categories = sum(row_count for _, row_count in self.categories)
        dish_counter = 1
        
        for day in range(7):  # 7 days
            for category_idx, (category_name, row_count) in enumerate(self.categories):
                for row in range(row_count):
                    # Column-wise numbering: (day * total_categories) + category_row_index + 1
                    category_row_index = sum(prev_row_count for _, prev_row_count in self.categories[:category_idx]) + row
                    dish_num = (day * total_categories) + category_row_index + 1
                    self.dish_names[dish_num] = f"Gericht {dish_num}"
                    self.empty_cells[dish_num] = False
        
        # Generate HTML
        html_content = self.generate_html()
        with open(os.path.join(website_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Generate CSS
        css_content = self.generate_css()
        with open(os.path.join(website_dir, "styles.css"), "w", encoding="utf-8") as f:
            f.write(css_content)
            
        messagebox.showinfo("Erfolg", "Webseiten-Struktur wurde erstellt!")
    
    def generate_html(self):
        """Generate HTML content based on configuration - column-wise numbering"""
        week_range = f"Woche: {self.week_start.get()} - {self.week_end.get()}"
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        
        html = f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Essensplan {week_range}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>{week_range}</h1>
    </header>
    <main>
        <table>
            <thead>
                <tr>
                    <th></th>'''
        
        for day in days:
            html += f'\n                    <th>{day}</th>'
            
        html += '''
                </tr>
            </thead>
            <tbody>'''
        
        # Generate table with column-wise dish numbering
        # Calculate total categories for proper numbering
        total_categories = sum(row_count for _, row_count in self.categories)
        
        category_row_counter = 0  # Track current category row across all categories
        
        for category_name, row_count in self.categories:
            for row in range(row_count):
                # Only show category name in first row, leave others empty
                if row == 0:
                    category_display = category_name
                else:
                    category_display = ""
                    
                html += f'''
                <tr>
                    <th>{category_display}</th>'''
                
                for day_idx in range(7):
                    # Calculate dish number column-wise (by day first, then by category)
                    dish_counter = (day_idx * total_categories) + category_row_counter + 1
                    
                    day_name = days[day_idx]
                    dish_name = self.dish_names.get(dish_counter, f"Gericht {dish_counter}")
                    
                    if self.empty_cells.get(dish_counter, False):
                        if self.empty_cell_display.get() == "-":
                            html += '''
                    <td class="empty-cell">
                        <span class="no-food">-</span>
                    </td>'''
                        else:
                            html += '''
                    <td class="empty-cell">
                        <span class="dish-name"></span>
                    </td>'''
                    else:
                        html += f'''
                    <td>
                        <span class="dish-name">{dish_name}</span>'''
                        
                        # Check if photo path should be hidden
                        photo_path = self.file_entries.get(dish_counter, {}).get("photo", tk.StringVar()).get() if hasattr(self, 'file_entries') else ""
                        pdf_path = self.file_entries.get(dish_counter, {}).get("pdf", tk.StringVar()).get() if hasattr(self, 'file_entries') else ""
                        
                        if self.show_photos.get() and photo_path != "/":
                            html += f'''
                        <img src="media/photos/photo{dish_counter}.jpg" alt="{category_name} {day_name}">'''
                        
                        if pdf_path != "/":
                            html += f'''
                        <a href="media/pdfs/recipe{dish_counter}.pdf" target="_blank">Rezept PDF</a>'''
                        
                        html += '''
                    </td>'''
                    
                html += '''
                </tr>'''
                
                category_row_counter += 1  # Increment for next category row
        
        html += '''
            </tbody>
        </table>'''
        
        # Add sources box if enabled
        if self.show_sources_box.get():
            html += f'''

    <div class="pdf-links-container">
        <h2>Download Links:</h2>
        <a href="media/pdfs/ingredients-full-list.pdf" target="_blank" class="pdf-link">{self.source_pdf1_name.get()}</a>
        <a href="media/pdfs/ingredients-separated-by-dish.pdf" target="_blank" class="pdf-link">{self.source_pdf2_name.get()}</a>
    </div>'''
        
        html += '''

    </main>
</body>
</html>'''
        
        return html
    
    def generate_css(self):
        """Generate CSS content"""
        return '''body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f0f0f5;
    color: #333;
}

header {
    background-color: #444;
    color: #fff;
    text-align: center;
    padding: 15px 0;
}

h1 {
    margin: 0;
    font-size: 24px;
}

main {
    padding: 20px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background-color: #fff;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

th, td {
    border: 1px solid #ddd;
    text-align: center;
    padding: 10px;
}

th {
    background-color: #f8f8f8;
    font-weight: bold;
}

td img {
    max-width: 80px;
    height: auto;
    display: block;
    margin: 10px auto;
}

.dish-name {
    display: block;
    text-decoration: underline;
    margin-bottom: 8px;
    font-weight: bold;
    color: #555;
}

.empty-cell {
    background-color: #f9f9f9;
}

.no-food {
    font-size: 24px;
    color: #ccc;
    font-weight: bold;
}

a {
    color: #007bff;
    text-decoration: none;
    display: inline-block;
    margin-top: 5px;
}

a:hover {
    text-decoration: underline;
}

.pdf-links-container {
    border: 2px solid #007bff;
    border-radius: 8px;
    background-color: #fff;
    padding: 20px;
    margin-top: 20px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.pdf-links-container h2 {
    margin-top: 0;
    font-size: 20px;
    color: #007bff;
}

.pdf-link {
    display: block;
    color: #007bff;
    text-decoration: none;
    font-size: 16px;
    margin-bottom: 10px;
}

.pdf-link:hover {
    text-decoration: underline;
}

@media (max-width: 768px) {
    table, th, td {
        font-size: 14px;
    }

    th, td {
        padding: 8px;
    }

    td img {
        max-width: 60px;
    }
}'''
    
    def setup_page2(self):
        """File assignment page"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Datei-Zuordnung und Anpassungen", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=6, pady=(0, 20))
        
        # Test website button
        test_button = ttk.Button(main_frame, text="Webseite im Browser öffnen (Test)", 
                                command=self.open_website)
        test_button.grid(row=1, column=0, columnspan=6, pady=(0, 10))
        
        # Info about placeholder words
        info_label = ttk.Label(main_frame, text="Hinweis: Eingabe '/' wird als Platzhalter erkannt und blendet PDF/Foto Links aus",
                              font=("Arial", 9), foreground="gray", wraplength=800)
        info_label.grid(row=2, column=0, columnspan=6, pady=(0, 20))
        
        # Create scrollable frame with mouse wheel support
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Bind mouse wheel scrolling to canvas and scrollable frame
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_to_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_from_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        # Bind to both canvas and scrollable frame
        canvas.bind('<Enter>', bind_to_mousewheel)
        canvas.bind('<Leave>', unbind_from_mousewheel)
        scrollable_frame.bind('<Enter>', bind_to_mousewheel)
        scrollable_frame.bind('<Leave>', unbind_from_mousewheel)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        ttk.Label(scrollable_frame, text="Gericht", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Name", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Leer", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="PDF Datei", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=5, pady=5)
        ttk.Label(scrollable_frame, text="Foto Datei", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, pady=5)
        
        # Select All Empty checkbox
        self.select_all_empty = tk.BooleanVar()
        ttk.Checkbutton(scrollable_frame, text="Alle Leer", variable=self.select_all_empty,
                       command=self.toggle_all_empty).grid(row=0, column=2, padx=5, pady=2, sticky="s")
        
        # Create file selection rows with column-wise dish numbering
        self.file_entries = {}
        self.name_entries = {}
        self.empty_checkboxes = {}
        self.input_widgets = {}
        
        total_categories = sum(row_count for _, row_count in self.categories)
        row_counter = 1
        
        for day in range(7):
            for category_idx, (category_name, row_count) in enumerate(self.categories):
                for row in range(row_count):
                    # Column-wise numbering: (day * total_categories) + category_row_index + 1
                    category_row_index = sum(prev_row_count for _, prev_row_count in self.categories[:category_idx]) + row
                    dish_counter = (day * total_categories) + category_row_index + 1
                    # Dish number
                    ttk.Label(scrollable_frame, text=f"Gericht {dish_counter}").grid(row=row_counter, column=0, padx=5, pady=2)
                    
                    # Dish name with meal search
                    name_var = tk.StringVar(value=self.dish_names[dish_counter])
                    
                    # Create frame for name entry and search button
                    name_frame = ttk.Frame(scrollable_frame)
                    name_frame.grid(row=row_counter, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
                    
                    name_entry = ttk.Entry(name_frame, textvariable=name_var, width=15)
                    name_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
                    name_frame.columnconfigure(0, weight=1)
                    
                    # Search button for pre-set meals
                    search_button = ttk.Button(name_frame, text="🔍", width=3,
                                             command=lambda i=dish_counter, var=name_var: self.search_meal(i, var))
                    search_button.grid(row=0, column=1, padx=(2, 0))
                    
                    # Bind double-click to search as well
                    name_entry.bind("<Double-Button-1>", lambda e, i=dish_counter, var=name_var: self.search_meal(i, var))
                    
                    self.name_entries[dish_counter] = name_var
                    
                    # Empty checkbox
                    empty_var = tk.BooleanVar(value=self.empty_cells[dish_counter])
                    empty_checkbox = ttk.Checkbutton(scrollable_frame, variable=empty_var,
                                                   command=lambda i=dish_counter: self.toggle_empty_cell(i))
                    empty_checkbox.grid(row=row_counter, column=2, padx=5, pady=2)
                    self.empty_checkboxes[dish_counter] = empty_var
                    
                    # PDF file selection with clipboard support
                    pdf_var = tk.StringVar()
                    pdf_frame = ttk.Frame(scrollable_frame)
                    pdf_frame.grid(row=row_counter, column=3, padx=5, pady=2, sticky=(tk.W, tk.E))
                    
                    pdf_entry = ttk.Entry(pdf_frame, textvariable=pdf_var, width=25)
                    pdf_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
                    pdf_frame.columnconfigure(0, weight=1)
                    
                    pdf_button = ttk.Button(pdf_frame, text="...", width=3,
                          command=lambda i=dish_counter, var=pdf_var: self.browse_pdf(i, var))
                    pdf_button.grid(row=0, column=1, padx=(2, 0))
                    
                    # PDF Clipboard button 
                    pdf_clipboard_button = ttk.Button(pdf_frame, text="📋", width=3,
                          command=lambda i=dish_counter, var=pdf_var: self.paste_pdf_from_clipboard(i, var))
                    pdf_clipboard_button.grid(row=0, column=2, padx=(2, 0))
                    
                    # Photo file selection with clipboard support
                    photo_var = tk.StringVar()
                    photo_frame = ttk.Frame(scrollable_frame)
                    photo_frame.grid(row=row_counter, column=4, padx=5, pady=2, sticky=(tk.W, tk.E))
                    
                    photo_entry = ttk.Entry(photo_frame, textvariable=photo_var, width=25)
                    photo_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
                    photo_frame.columnconfigure(0, weight=1)
                    
                    photo_button = ttk.Button(photo_frame, text="...", width=3,
                          command=lambda i=dish_counter, var=photo_var: self.browse_photo(i, var))
                    photo_button.grid(row=0, column=1, padx=(2, 0))
                    
                    # Clipboard button for photos
                    clipboard_button = ttk.Button(photo_frame, text="📋", width=3,
                          command=lambda i=dish_counter, var=photo_var: self.paste_from_clipboard(i, var))
                    clipboard_button.grid(row=0, column=2, padx=(2, 0))
                    
                    self.file_entries[dish_counter] = {"pdf": pdf_var, "photo": photo_var}
                    
                    # Store widget references for graying out
                    self.input_widgets[dish_counter] = {
                        "name_entry": name_entry,
                        "search_button": search_button,
                        "pdf_entry": pdf_entry,
                        "pdf_button": pdf_button,
                        "pdf_clipboard_button": pdf_clipboard_button,
                        "photo_entry": photo_entry,
                        "photo_button": photo_button,
                        "clipboard_button": clipboard_button
                    }
                    
                    # Apply initial gray state if needed
                    if self.empty_cells[dish_counter]:
                        self.update_widget_state(dish_counter, disabled=True)
                    
                    row_counter += 1
        
        # Add file operation setting at the top of the settings section
        settings_start_row = row_counter + 1
        
        # Settings header
        ttk.Label(scrollable_frame, text="Einstellungen", font=("Arial", 12, "bold")).grid(row=settings_start_row, column=0, columnspan=5, pady=(20, 10))
        
        # File operation setting
        ttk.Label(scrollable_frame, text="Datei-Operation:").grid(row=settings_start_row + 1, column=0, sticky=tk.W, pady=5)
        file_op_frame = ttk.Frame(scrollable_frame)
        file_op_frame.grid(row=settings_start_row + 1, column=1, columnspan=3, sticky=tk.W, padx=5)
        self.copy_radio = ttk.Radiobutton(file_op_frame, text="Kopieren", variable=self.file_operation, value="copy")
        self.copy_radio.grid(row=0, column=0, sticky=tk.W)
        self.cut_radio = ttk.Radiobutton(file_op_frame, text="Ausschneiden", variable=self.file_operation, value="cut")
        self.cut_radio.grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Warning label for database meals
        self.file_op_warning = ttk.Label(scrollable_frame, text="", foreground="red", font=("Arial", 9))
        self.file_op_warning.grid(row=settings_start_row + 2, column=0, columnspan=4, sticky=tk.W, pady=2)
        
        # Add sources section if enabled
        if self.show_sources_box.get():
            sources_start_row = settings_start_row + 3
            
            # Sources header
            ttk.Label(scrollable_frame, text="Download Links", font=("Arial", 12, "bold")).grid(row=sources_start_row, column=0, columnspan=5, pady=(20, 10))
            
            # Source PDF 1
            ttk.Label(scrollable_frame, text=self.source_pdf1_name.get()).grid(row=sources_start_row + 1, column=0, columnspan=2, padx=5, pady=2, sticky=tk.W)
            source1_frame = ttk.Frame(scrollable_frame)
            source1_frame.grid(row=sources_start_row + 1, column=3, padx=5, pady=2, sticky=(tk.W, tk.E))
            source1_entry = ttk.Entry(source1_frame, textvariable=self.source_files["pdf1"], width=25)
            source1_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
            source1_frame.columnconfigure(0, weight=1)
            ttk.Button(source1_frame, text="...", width=3,
                      command=lambda: self.browse_source_pdf("pdf1")).grid(row=0, column=1, padx=(2, 0))
            
            # Source PDF 2
            ttk.Label(scrollable_frame, text=self.source_pdf2_name.get()).grid(row=sources_start_row + 2, column=0, columnspan=2, padx=5, pady=2, sticky=tk.W)
            source2_frame = ttk.Frame(scrollable_frame)
            source2_frame.grid(row=sources_start_row + 2, column=3, padx=5, pady=2, sticky=(tk.W, tk.E))
            source2_entry = ttk.Entry(source2_frame, textvariable=self.source_files["pdf2"], width=25)
            source2_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
            source2_frame.columnconfigure(0, weight=1)
            ttk.Button(source2_frame, text="...", width=3,
                      command=lambda: self.browse_source_pdf("pdf2")).grid(row=0, column=1, padx=(2, 0))
        
        # Configure scrollable frame
        scrollable_frame.columnconfigure(1, weight=1)
        scrollable_frame.columnconfigure(3, weight=1)
        scrollable_frame.columnconfigure(4, weight=1)
        
        canvas.grid(row=3, column=0, columnspan=5, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        scrollbar.grid(row=3, column=5, sticky=(tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(3, weight=1)
        
        # Initial update of file operation state
        self.update_file_operation_state()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="← Zurück", command=self.go_back_to_page1_with_warning).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Dateien kopieren und fertigstellen", 
                  command=self.copy_files_and_finish).grid(row=0, column=1, padx=5)
    
    def paste_pdf_from_clipboard(self, dish_num, var):
        """Paste PDF path from clipboard"""
        try:
            clipboard_content = self.root.clipboard_get()
            if clipboard_content and (clipboard_content.lower().endswith('.pdf') or os.path.exists(clipboard_content)):
                var.set(clipboard_content)
                messagebox.showinfo("Erfolg", "PDF-Pfad aus Zwischenablage eingefügt!")
            else:
                messagebox.showwarning("Warnung", "Kein gültiger PDF-Pfad in der Zwischenablage gefunden!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Einfügen aus Zwischenablage: {str(e)}")
    
    def toggle_all_empty(self):
        """Toggle all empty checkboxes"""
        select_all = self.select_all_empty.get()
        for dish_num, empty_var in self.empty_checkboxes.items():
            empty_var.set(select_all)
            self.empty_cells[dish_num] = select_all
            self.update_widget_state(dish_num, disabled=select_all)
    
    def paste_from_clipboard(self, dish_num, var):
        """Paste image from clipboard - supports PNG and JPEG formats"""
        try:
            from PIL import ImageGrab
            img = ImageGrab.grabclipboard()
            if img:
                # Determine format based on image mode and save appropriately
                website_dir = self.website_path.get()
                
                # Check if image has transparency (RGBA)
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    # Save as PNG to preserve transparency
                    temp_path = os.path.join(website_dir, "media", "photos", f"temp_clipboard_{dish_num}.png")
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                    img.save(temp_path, "PNG")
                else:
                    # Save as JPEG for better file size
                    temp_path = os.path.join(website_dir, "media", "photos", f"temp_clipboard_{dish_num}.jpg")
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                    # Convert to RGB if necessary (JPEG doesn't support RGBA)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(temp_path, "JPEG", quality=90)
                
                var.set(temp_path)
                messagebox.showinfo("Erfolg", "Bild aus Zwischenablage eingefügt!")
            else:
                messagebox.showwarning("Warnung", "Keine Bilddaten in der Zwischenablage gefunden!")
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Einfügen aus Zwischenablage: {str(e)}")
    
    def update_widget_state(self, dish_num, disabled=False):
        """Enable or disable widgets for a dish based on empty cell state"""
        widgets = self.input_widgets.get(dish_num, {})
        state = 'disabled' if disabled else 'normal'
        
        for widget_name, widget in widgets.items():
            if widget_name in ['name_entry', 'pdf_entry', 'photo_entry']:
                widget.config(state=state)
            elif widget_name in ['pdf_button', 'photo_button', 'clipboard_button', 'pdf_clipboard_button', 'search_button']:
                widget.config(state=state)
    
    def search_meal(self, dish_num, name_var):
        """Open search dialog for pre-set meals"""
        if not self.meals_library:
            messagebox.showinfo("Info", "Noch keine Gerichte in der Bibliothek vorhanden.")
            return
        
        # Create search dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Gericht auswählen")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Search entry
        ttk.Label(main_frame, text="Suche nach Gericht:").pack(anchor=tk.W, pady=(0, 5))
        search_var = tk.StringVar()
        search_entry = ttk.Entry(main_frame, textvariable=search_var, width=50)
        search_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Results listbox
        ttk.Label(main_frame, text="Verfügbare Gerichte:").pack(anchor=tk.W, pady=(0, 5))
        
        # Create frame for listbox and scrollbar
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        listbox = tk.Listbox(list_frame, height=15)
        scrollbar_list = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
        listbox.configure(yscrollcommand=scrollbar_list.set)
        
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Store meal data for quick access
        meal_items = []
        
        def update_results():
            """Update search results based on search term"""
            search_term = search_var.get().lower()
            listbox.delete(0, tk.END)
            meal_items.clear()
            
            for meal_id, meal_data in self.meals_library.items():
                meal_name = meal_data['name']
                if search_term in meal_name.lower() or search_term == "":
                    listbox.insert(tk.END, meal_name)
                    meal_items.append((meal_id, meal_data))
        
        # Bind search as you type
        search_var.trace('w', lambda *args: update_results())
        
        # Initial population
        update_results()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        def select_meal():
            """Select the highlighted meal and apply it to the dish"""
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Warnung", "Bitte wählen Sie ein Gericht aus.")
                return
            
            meal_id, meal_data = meal_items[selection[0]]
            
            # Set dish name
            name_var.set(meal_data['name'])
            
            # Auto-set PDF and photo if available
            if meal_data.get('pdf_path') and os.path.exists(meal_data['pdf_path']):
                if dish_num in self.file_entries:
                    self.file_entries[dish_num]['pdf'].set(meal_data['pdf_path'])
            
            if meal_data.get('image_path') and os.path.exists(meal_data['image_path']):
                if dish_num in self.file_entries:
                    self.file_entries[dish_num]['photo'].set(meal_data['image_path'])
            
            # Update file operation state after selecting database meal
            self.update_file_operation_state()
            
            dialog.destroy()
        
        # Double-click to select
        listbox.bind("<Double-Button-1>", lambda e: select_meal())
        
        ttk.Button(button_frame, text="Auswählen", command=select_meal).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Abbrechen", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # Focus on search entry
        search_entry.focus_set()
    
    def toggle_empty_cell(self, dish_num):
        """Toggle empty cell state and update widget appearance"""
        self.empty_cells[dish_num] = self.empty_checkboxes[dish_num].get()
        self.update_widget_state(dish_num, disabled=self.empty_cells[dish_num])
    
    def open_website(self):
        """Open the generated website in the default browser"""
        website_dir = self.website_path.get()
        html_path = os.path.join(website_dir, "index.html")
        
        if os.path.exists(html_path):
            webbrowser.open(f"file://{os.path.abspath(html_path)}")
        else:
            messagebox.showerror("Fehler", "Website-Datei nicht gefunden!")
    
    def open_project_folder(self, folder_path):
        """Open the project folder in the file explorer"""
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden: {str(e)}")
    
    def browse_pdf(self, dish_num, var):
        """Browse for PDF file"""
        filename = filedialog.askopenfilename(
            title=f"PDF für Gericht {dish_num} auswählen",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)
    
    def browse_photo(self, dish_num, var):
        """Browse for photo file"""
        filename = filedialog.askopenfilename(
            title=f"Foto für Gericht {dish_num} auswählen",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)
    
    def browse_source_pdf(self, pdf_key):
        """Browse for source PDF file"""
        filename = filedialog.askopenfilename(
            title=f"Download Link PDF auswählen",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.source_files[pdf_key].set(filename)
    
    def create_zip_file(self, website_dir):
        """Create ZIP file of the project in the same directory as the website"""
        zip_filename = f"Essensplan_{self.week_start.get().replace('.', '_')}-{self.week_end.get().replace('.', '_')}.zip"
        zip_path = os.path.join(website_dir, zip_filename)  # Save in same directory as website
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(website_dir):
                for file in files:
                    # Skip the ZIP file itself to avoid recursion
                    if file == zip_filename:
                        continue
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, website_dir)
                    zipf.write(file_path, arc_name)
        
        return zip_path
    
    def copy_files_and_finish(self):
        """Copy and rename files to website directory"""
        website_dir = self.website_path.get()
        
        # Handle subfolder renaming
        if self.rename_subfolder.get():
            parent_dir = os.path.dirname(website_dir)
            new_folder_name = f"Essensplan {self.week_start.get()} - {self.week_end.get()}"
            new_website_dir = os.path.join(parent_dir, new_folder_name)
            
            if website_dir != new_website_dir:
                try:
                    os.rename(website_dir, new_website_dir)
                    website_dir = new_website_dir
                    self.website_path.set(website_dir)
                except Exception as e:
                    messagebox.showwarning("Warnung", f"Ordner konnte nicht umbenannt werden: {str(e)}")
        
        try:
            # Update dish names
            for dish_num, name_var in self.name_entries.items():
                self.dish_names[dish_num] = name_var.get()
            
            # Update empty cells
            for dish_num, empty_var in self.empty_checkboxes.items():
                self.empty_cells[dish_num] = empty_var.get()
            
            # Regenerate HTML with updated names and empty cells
            html_content = self.generate_html()
            with open(os.path.join(website_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(html_content)
            
            for dish_num, files in self.file_entries.items():
                # Skip file copying for empty cells
                if self.empty_cells.get(dish_num, False):
                    continue
                    
                pdf_path = files["pdf"].get()
                photo_path = files["photo"].get()
                
                # Handle special placeholder paths - only "/" now
                if pdf_path and pdf_path != "/":
                    if os.path.exists(pdf_path):
                        dest_pdf = os.path.join(website_dir, "media", "pdfs", f"recipe{dish_num}.pdf")
                        if self.file_operation.get() == "copy":
                            shutil.copy2(pdf_path, dest_pdf)
                        else:  # cut
                            shutil.move(pdf_path, dest_pdf)
                
                # Handle special placeholder paths for photos - only "/" now
                if photo_path and photo_path != "/":
                    if os.path.exists(photo_path):
                        # Get file extension
                        _, ext = os.path.splitext(photo_path)
                        dest_photo = os.path.join(website_dir, "media", "photos", f"photo{dish_num}{ext}")
                        if self.file_operation.get() == "copy":
                            shutil.copy2(photo_path, dest_photo)
                        else:  # cut
                            # Delete old temp files if they exist before moving
                            if "temp_clipboard_" in photo_path and self.file_operation.get() == "copy":
                                self.cleanup_temp_files(website_dir)
                            shutil.move(photo_path, dest_photo)
                        
                        # If extension is not .jpg, update HTML to reflect correct extension
                        if ext.lower() != '.jpg':
                            self.update_html_for_image_extension(dish_num, ext)
            
            # Clean up temporary files in copy mode
            if self.file_operation.get() == "copy":
                self.cleanup_temp_files(website_dir)
            
            # Copy source PDFs if enabled
            if self.show_sources_box.get():
                if self.source_files["pdf1"].get() and os.path.exists(self.source_files["pdf1"].get()):
                    dest_pdf1 = os.path.join(website_dir, "media", "pdfs", "ingredients-full-list.pdf")
                    if self.file_operation.get() == "copy":
                        shutil.copy2(self.source_files["pdf1"].get(), dest_pdf1)
                    else:
                        shutil.move(self.source_files["pdf1"].get(), dest_pdf1)
                
                if self.source_files["pdf2"].get() and os.path.exists(self.source_files["pdf2"].get()):
                    dest_pdf2 = os.path.join(website_dir, "media", "pdfs", "ingredients-separated-by-dish.pdf")
                    if self.file_operation.get() == "copy":
                        shutil.copy2(self.source_files["pdf2"].get(), dest_pdf2)
                    else:
                        shutil.move(self.source_files["pdf2"].get(), dest_pdf2)
            
            # Custom success dialog - no automatic ZIP creation
            self.show_success_dialog(website_dir)
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Kopieren der Dateien: {str(e)}")
    
    def show_success_dialog(self, website_dir):
        """Show custom success dialog with all options"""
        success_dialog = tk.Toplevel(self.root)
        success_dialog.title("Erfolg")
        success_dialog.geometry("600x300")  # Made larger to accommodate more buttons
        success_dialog.resizable(False, False)
        
        # Center the dialog
        success_dialog.transient(self.root)
        success_dialog.grab_set()
        
        # Success message
        message_frame = ttk.Frame(success_dialog, padding="20")
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(message_frame, text="✓ Essensplan wurde erfolgreich erstellt!", 
                 font=("Arial", 12, "bold"), foreground="green").pack(pady=(0, 10))
        
        ttk.Label(message_frame, text=f"Speicherort: {website_dir}", 
                 font=("Arial", 9), wraplength=550).pack(pady=(0, 20))
        
        # Buttons frame - organized in two rows
        button_frame = ttk.Frame(message_frame)
        button_frame.pack(pady=10)
        
        # First row of buttons
        first_row = ttk.Frame(button_frame)
        first_row.pack(pady=(0, 10))
        
        # Netlify button
        def open_netlify():
            webbrowser.open("https://app.netlify.com/drop")
        
        ttk.Button(first_row, text="Netlify öffnen", 
                  command=open_netlify).pack(side=tk.LEFT, padx=(0, 10))
        
        # Open project folder button
        ttk.Button(first_row, text="Projektordner öffnen", 
                  command=lambda: self.open_project_folder(website_dir)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Open website button
        ttk.Button(first_row, text="Website öffnen", 
                  command=self.open_website).pack(side=tk.LEFT, padx=(0, 10))
        
        # Screenshot button
        ttk.Button(first_row, text="Screenshot", 
                  command=lambda: self.show_screenshot_dialog(website_dir)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Second row of buttons
        second_row = ttk.Frame(button_frame)
        second_row.pack()
        
        # Create ZIP in same folder button
        def create_zip_in_folder():
            try:
                zip_path_in_folder = self.create_zip_file(website_dir)
                messagebox.showinfo("ZIP erstellt", f"ZIP-Datei wurde im Projektordner erstellt:\n{os.path.basename(zip_path_in_folder)}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Erstellen der ZIP-Datei: {str(e)}")
        
        ttk.Button(second_row, text="ZIP im Projektordner erstellen", 
                  command=create_zip_in_folder).pack(side=tk.LEFT, padx=(0, 10))
        
        # Copy week name button  
        def copy_week_name():
            try:
                # Convert date format to week name format
                start_date = datetime.strptime(self.week_start.get(), "%d.%m.%y")
                end_date = datetime.strptime(self.week_end.get(), "%d.%m.%y")
                
                # Format dates as required: dd-mm-yy
                start_formatted = start_date.strftime("%d-%m-%y")
                end_formatted = end_date.strftime("%d-%m-%y")
                
                # Create week name in the format: woche-14-07-25bis20-07-25
                week_name = f"woche-{start_formatted}bis{end_formatted}"
                
                # Copy to clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(week_name)
                
                messagebox.showinfo("Erfolg", f"Wochenname '{week_name}' in Zwischenablage kopiert!")
                
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Erstellen des Wochennamens: {str(e)}")
        
        ttk.Button(second_row, text="Wochenname kopieren", 
                  command=copy_week_name).pack(side=tk.LEFT, padx=(0, 10))
        
        # OK button
        def close_dialog():
            success_dialog.destroy()
            self.root.quit()
        
        ttk.Button(second_row, text="OK", 
                  command=close_dialog).pack(side=tk.LEFT)
        
        # Center the window
        success_dialog.update_idletasks()
        x = (success_dialog.winfo_screenwidth() // 2) - (success_dialog.winfo_width() // 2)
        y = (success_dialog.winfo_screenheight() // 2) - (success_dialog.winfo_height() // 2)
        success_dialog.geometry(f"+{x}+{y}")
    
    def update_html_for_image_extension(self, dish_num, ext):
        """Update HTML file to use correct image extension"""
        website_dir = self.website_path.get()
        html_path = os.path.join(website_dir, "index.html")
        
        try:
            with open(html_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Replace the image source
            old_src = f"photo{dish_num}.jpg"
            new_src = f"photo{dish_num}{ext}"
            content = content.replace(old_src, new_src)
            
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        except Exception as e:
            print(f"Warning: Could not update HTML for image extension: {e}")
    
    def cleanup_temp_files(self, website_dir):
        """Clean up temporary clipboard files"""
        try:
            photos_dir = os.path.join(website_dir, "media", "photos")
            if os.path.exists(photos_dir):
                for filename in os.listdir(photos_dir):
                    if filename.startswith("temp_clipboard_"):
                        temp_file = os.path.join(photos_dir, filename)
                        try:
                            os.remove(temp_file)
                        except OSError:
                            pass  # File might already be moved/deleted
        except Exception as e:
            print(f"Warning: Could not clean up temp files: {e}")
    
    def show_screenshot_dialog(self, website_dir):
        """Show screenshot options dialog"""
        screenshot_dialog = tk.Toplevel(self.root)
        screenshot_dialog.title("Screenshot Optionen")
        screenshot_dialog.geometry("400x200")
        screenshot_dialog.resizable(False, False)
        
        # Center the dialog
        screenshot_dialog.transient(self.root)
        screenshot_dialog.grab_set()
        
        main_frame = ttk.Frame(screenshot_dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Screenshot der HTML-Seite erstellen:", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 20))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        def screenshot_to_clipboard():
            try:
                self.take_website_screenshot(website_dir, to_clipboard=True)
                screenshot_dialog.destroy()
                messagebox.showinfo("Erfolg", "Screenshot wurde in die Zwischenablage kopiert!")
            except Exception as e:
                messagebox.showerror("Fehler", f"Screenshot-Fehler: {str(e)}")
        
        def screenshot_to_file():
            try:
                save_path = filedialog.asksaveasfilename(
                    title="Screenshot speichern als",
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
                )
                if save_path:
                    self.take_website_screenshot(website_dir, save_path=save_path)
                    screenshot_dialog.destroy()
                    messagebox.showinfo("Erfolg", f"Screenshot wurde gespeichert: {save_path}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Screenshot-Fehler: {str(e)}")
        
        ttk.Button(button_frame, text="In Zwischenablage", 
                  command=screenshot_to_clipboard).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Als Datei speichern", 
                  command=screenshot_to_file).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Abbrechen", 
                  command=screenshot_dialog.destroy).pack(side=tk.LEFT, padx=(10, 0))
        
        # Center the window
        screenshot_dialog.update_idletasks()
        x = (screenshot_dialog.winfo_screenwidth() // 2) - (screenshot_dialog.winfo_width() // 2)
        y = (screenshot_dialog.winfo_screenheight() // 2) - (screenshot_dialog.winfo_height() // 2)
        screenshot_dialog.geometry(f"+{x}+{y}")
    
    def take_website_screenshot(self, website_dir, to_clipboard=False, save_path=None):
        """Take screenshot of the website"""
        try:
            # Install selenium and webdriver-manager if not available
            try:
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
            except ImportError:
                messagebox.showerror("Fehler", "Selenium ist nicht installiert.\nInstallieren Sie es mit: pip install selenium webdriver-manager")
                return
            
            html_path = os.path.join(website_dir, "index.html")
            if not os.path.exists(html_path):
                raise Exception("HTML-Datei nicht gefunden!")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Create driver
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Load the HTML file
                driver.get(f"file://{os.path.abspath(html_path)}")
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Take screenshot
                if to_clipboard:
                    # Save to temp file first, then copy to clipboard
                    temp_path = os.path.join(website_dir, "temp_screenshot.png")
                    driver.save_screenshot(temp_path)
                    
                    # Copy to clipboard using PIL
                    from PIL import Image
                    img = Image.open(temp_path)
                    output = io.BytesIO()
                    img.convert("RGB").save(output, "BMP")
                    data = output.getvalue()[14:]
                    output.close()
                    
                    import win32clipboard
                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                    
                    # Clean up temp file
                    os.remove(temp_path)
                    
                elif save_path:
                    driver.save_screenshot(save_path)
                    
            finally:
                driver.quit()
                
        except Exception as e:
            raise Exception(f"Screenshot konnte nicht erstellt werden: {str(e)}")
    
    def on_form_change(self, event=None):
        """Track when form fields change"""
        self.form_changed = True
    
    def has_form_changes(self):
        """Check if any form values have changed"""
        if not hasattr(self, 'original_values'):
            return False
        
        current_values = {
            'website_path': self.website_path.get(),
            'week_start': self.week_start.get(),
            'week_end': self.week_end.get(),
            'breakfast_rows': self.breakfast_rows.get(),
            'lunch_rows': self.lunch_rows.get(),
            'snacks_rows': self.snacks_rows.get(),
            'dessert_rows': self.dessert_rows.get(),
            'empty_cell_display': self.empty_cell_display.get(),
            'show_photos': self.show_photos.get(),
            'show_sources_box': self.show_sources_box.get(),
            'source_pdf1_name': self.source_pdf1_name.get(),
            'source_pdf2_name': self.source_pdf2_name.get(),
            'rename_subfolder': self.rename_subfolder.get()
        }
        
        return current_values != self.original_values
    
    def go_back_to_library_with_warning(self):
        """Go back to meal library page with unsaved changes warning"""
        if self.has_form_changes():
            if messagebox.askyesno("Ungespeicherte Änderungen", 
                                 "Sie haben ungespeicherte Änderungen. Sind Sie sicher, dass Sie zurück gehen möchten? Alle Änderungen gehen verloren."):
                self.setup_meal_library_page()
        else:
            self.setup_meal_library_page()
    
    def go_back_to_page1_with_warning(self):
        """Go back to page1 with unsaved changes warning for page2"""
        if hasattr(self, 'file_entries') and self.file_entries:
            # Check if any file assignments have been made
            has_assignments = False
            for dish_num in self.file_entries:
                name_changed = False
                if hasattr(self, 'name_entries') and dish_num in self.name_entries:
                    name_changed = self.name_entries[dish_num].get() != f"Gericht {dish_num}"
                
                if (self.file_entries[dish_num]["photo"].get() or 
                    self.file_entries[dish_num]["pdf"].get() or
                    name_changed):
                    has_assignments = True
                    break
            
            if has_assignments:
                if messagebox.askyesno("Ungespeicherte Änderungen", 
                                     "Sie haben ungespeicherte Datei-Zuordnungen. Sind Sie sicher, dass Sie zurück gehen möchten? Alle Änderungen gehen verloren."):
                    self.setup_page1()
            else:
                self.setup_page1()
        else:
            self.setup_page1()

def main():
    root = tk.Tk()
    app = MealPlanGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
