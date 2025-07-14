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
        
        # Initialize week dates
        self.set_current_week()
        
        # Create pages
        self.setup_page1()
    
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
    
    def setup_page1(self):
        """Configuration page"""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
            
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Essensplan Generator - Konfiguration", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=(0, 20))
        
        # Website path selection
        ttk.Label(main_frame, text="Speicherort der Webseite:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.website_path, width=50).grid(row=1, column=1, columnspan=2, padx=5, sticky=(tk.W, tk.E))
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
        ttk.Entry(main_frame, textvariable=self.breakfast_rows, width=10).grid(row=5, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(main_frame, text="Mittag-/Abendessen:").grid(row=6, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.lunch_rows, width=10).grid(row=6, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(main_frame, text="Snacks:").grid(row=7, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.snacks_rows, width=10).grid(row=7, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(main_frame, text="Nachtisch:").grid(row=8, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.dessert_rows, width=10).grid(row=8, column=1, sticky=tk.W, padx=5)
        
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
        ttk.Checkbutton(main_frame, text="Fotos anzeigen", variable=self.show_photos).grid(row=12, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # File operation setting
        ttk.Label(main_frame, text="Datei-Operation:").grid(row=13, column=0, sticky=tk.W, pady=5)
        file_op_frame = ttk.Frame(main_frame)
        file_op_frame.grid(row=13, column=1, columnspan=3, sticky=tk.W, padx=5)
        ttk.Radiobutton(file_op_frame, text="Kopieren", variable=self.file_operation, value="copy").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(file_op_frame, text="Ausschneiden", variable=self.file_operation, value="cut").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Rename subfolder option
        ttk.Checkbutton(main_frame, text="Unterordner zu 'Essensplan [Zeitspanne]' umbenennen", 
                       variable=self.rename_subfolder).grid(row=14, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        # Show sources box
        sources_checkbox = ttk.Checkbutton(main_frame, text="Download Links anzeigen", variable=self.show_sources_box, command=self.toggle_sources_options)
        sources_checkbox.grid(row=15, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Source PDF names
        self.sources_frame = ttk.LabelFrame(main_frame, text="Download Links Namen", padding="10")
        self.sources_frame.grid(row=16, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.sources_frame, text="PDF 1:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pdf1_entry = ttk.Entry(self.sources_frame, textvariable=self.source_pdf1_name, width=40)
        self.pdf1_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        ttk.Label(self.sources_frame, text="PDF 2:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.pdf2_entry = ttk.Entry(self.sources_frame, textvariable=self.source_pdf2_name, width=40)
        self.pdf2_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        
        self.sources_frame.columnconfigure(1, weight=1)
        
        # Notes Mode Button
        ttk.Button(main_frame, text="Notizen-Modus öffnen", 
                  command=self.open_notes_mode).grid(row=17, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Continue button
        ttk.Button(main_frame, text="Weiter", command=self.validate_and_continue).grid(row=18, column=1, pady=20)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Initialize sources options state
        self.toggle_sources_options()
    
    def open_notes_mode(self):
        """Open notes planning window with adaptive layout"""
        notes_window = tk.Toplevel(self.root)
        notes_window.title("Notizen-Modus - Essensplan Planung")
        notes_window.geometry("1200x700")  # Made larger to accommodate more content
        
        main_frame = ttk.Frame(notes_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Essensplan Notizen", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Create a simple table for notes
        canvas = tk.Canvas(main_frame)
        scrollbar_v = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollbar_h = ttk.Scrollbar(main_frame, orient="horizontal", command=canvas.xview)
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
        
        # Instructions and close button
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(pady=5)
        ttk.Label(info_frame, text="Tipp: Verwende Strg + Pfeiltasten zur Navigation zwischen den Zellen", 
                 font=("Arial", 9), foreground="gray").pack()
        ttk.Button(main_frame, text="Schließen", command=notes_window.destroy).pack(pady=10)
    
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
                    
                    # Dish name
                    name_var = tk.StringVar(value=self.dish_names[dish_counter])
                    name_entry = ttk.Entry(scrollable_frame, textvariable=name_var, width=20)
                    name_entry.grid(row=row_counter, column=1, padx=5, pady=2)
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
        
        # Add sources section if enabled
        if self.show_sources_box.get():
            sources_start_row = row_counter + 1
            
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
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=6, pady=10)
        
        ttk.Button(button_frame, text="Zurück", command=self.setup_page1).grid(row=0, column=0, padx=5)
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
            elif widget_name in ['pdf_button', 'photo_button', 'clipboard_button', 'pdf_clipboard_button']:
                widget.config(state=state)
    
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

def main():
    root = tk.Tk()
    app = MealPlanGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
