import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import json
import os
import tempfile
import threading
import sqlite3
from datetime import datetime
import re
from pathlib import Path

class ResponsiveFrame(ttk.Frame):
    """Custom frame that handles responsive behavior"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind('<Configure>', self.on_configure)
        
    def on_configure(self, event):
        """Handle window resize events"""
        if event.widget == self:
            self.update_layout()
    
    def update_layout(self):
        """Override in subclasses for custom responsive behavior"""
        pass

class SemgrepAnalyzer:
    def __init__(self):
        pass

    def check_semgrep_installation(self):
        try:
            result = subprocess.run(
                ['semgrep', '--version'], 
                capture_output=True, 
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False

    def run_semgrep_analysis(self, file_path, language):
        try:
            # Semgrep command with proper encoding handling
            cmd = [
                'semgrep', 
                '--config=auto', 
                '--json', 
                '--quiet',
                file_path
            ]
            
            # Fix encoding issue for Windows
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',  # Force UTF-8 encoding
                errors='replace',  # Replace problematic characters
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    findings = json.loads(result.stdout)
                    return findings.get('results', [])
                except json.JSONDecodeError:
                    return []
            else:
                # Log error but don't crash
                print(f"Semgrep error: {result.stderr}")
                return []
            
        except subprocess.TimeoutExpired:
            print("Semgrep analysis timed out")
            return []
        except FileNotFoundError:
            print("Semgrep not found. Please install semgrep first.")
            return []
        except Exception as e:
            print(f"Error running semgrep: {e}")
            return []

    def analyze_code(self, file_path, language):
        if not self.check_semgrep_installation():
            print("Semgrep is not installed or not in PATH.")
            return []

        findings = self.run_semgrep_analysis(file_path, language)
        return findings

class ModernBugPredictionGUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.setup_database()
        self.create_modern_ui()
        self.setup_responsive_behavior()
        
    def setup_window(self):
        """Configure main window for 14-inch screen optimization"""
        self.root.title("🔍 Developer Centric Bug Prediction Model v2.0")
        
        # Optimized for 14-inch screens (typically 1366x768 or 1920x1080)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate optimal window size (85% of screen for 14-inch displays)
        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.85)
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 700)  # Minimum size for usability
        
        # Configure window properties
        self.root.configure(bg='#1e1e1e')
        
        # Make window resizable with proper weight distribution
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
    def setup_variables(self):
        """Initialize all tkinter variables"""
        self.selected_file = tk.StringVar()
        self.selected_language = tk.StringVar(value="python")
        self.analysis_status = tk.StringVar(value="Ready")
        self.enable_semgrep = tk.BooleanVar(value=True)
        self.enable_custom_rules = tk.BooleanVar(value=True)
        self.enable_ai_enhancement = tk.BooleanVar(value=False)
        self.min_severity = tk.StringVar(value="INFO")
        self.current_tab = tk.StringVar(value="analysis")
        
    def setup_database(self):
        """Initialize SQLite database"""
        try:
            self.conn = sqlite3.connect('bug_analysis.db')
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    filename TEXT,
                    language TEXT,
                    total_vulnerabilities INTEGER,
                    critical_count INTEGER,
                    high_count INTEGER,
                    medium_count INTEGER,
                    low_count INTEGER,
                    info_count INTEGER,
                    results_json TEXT
                )
            ''')
            self.conn.commit()
        except Exception as e:
            print(f"Database setup error: {e}")
            
    def create_modern_ui(self):
        """Create the modern, responsive UI"""
        # Configure modern styling
        self.setup_styles()
        
        # Main container with responsive behavior
        self.main_container = ResponsiveFrame(self.root, style='Main.TFrame')
        self.main_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.main_container.grid_rowconfigure(1, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Header section
        self.create_header()
        
        # Main content area with tabs
        self.create_tabbed_interface()
        
        # Status bar
        self.create_status_bar()
        
    def setup_styles(self):
        """Configure modern dark theme styles"""
        style = ttk.Style()
        
        # Configure dark theme
        style.theme_use('clam')
        
        # Main frame style
        style.configure('Main.TFrame', background='#1e1e1e')
        
        # Header style
        style.configure('Header.TFrame', background='#2d2d2d', relief='raised', borderwidth=1)
        style.configure('Header.TLabel', background='#2d2d2d', foreground='#ffffff', 
                       font=('Segoe UI', 16, 'bold'))
        
        # Tab styles
        style.configure('Custom.TNotebook', background='#1e1e1e', borderwidth=0)
        style.configure('Custom.TNotebook.Tab', background='#3d3d3d', foreground='#ffffff',
                       padding=[20, 10], font=('Segoe UI', 10))
        style.map('Custom.TNotebook.Tab', 
                 background=[('selected', '#0078d4'), ('active', '#4d4d4d')])
        
        # Button styles
        style.configure('Primary.TButton', background='#0078d4', foreground='#ffffff',
                       font=('Segoe UI', 10, 'bold'), padding=[15, 8])
        style.map('Primary.TButton',
                 background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        
        style.configure('Secondary.TButton', background='#404040', foreground='#ffffff',
                       font=('Segoe UI', 9), padding=[12, 6])
        style.map('Secondary.TButton',
                 background=[('active', '#505050'), ('pressed', '#303030')])
        
        # Frame styles
        style.configure('Card.TFrame', background='#2d2d2d', relief='raised', borderwidth=1)
        style.configure('Content.TFrame', background='#1e1e1e')
        
        # Label styles
        style.configure('Title.TLabel', background='#1e1e1e', foreground='#ffffff',
                       font=('Segoe UI', 12, 'bold'))
        style.configure('Content.TLabel', background='#1e1e1e', foreground='#e0e0e0',
                       font=('Segoe UI', 9))
        style.configure('Success.TLabel', background='#1e1e1e', foreground='#4caf50',
                       font=('Segoe UI', 9, 'bold'))
        style.configure('Warning.TLabel', background='#1e1e1e', foreground='#ff9800',
                       font=('Segoe UI', 9, 'bold'))
        style.configure('Error.TLabel', background='#1e1e1e', foreground='#f44336',
                       font=('Segoe UI', 9, 'bold'))
        
        # Entry and combobox styles
        style.configure('Modern.TEntry', fieldbackground='#404040', foreground='#ffffff',
                       borderwidth=1, insertcolor='#ffffff')
        style.configure('Modern.TCombobox', fieldbackground='#404040', foreground='#ffffff',
                       borderwidth=1)
        
        # Progressbar style
        style.configure('Modern.Horizontal.TProgressbar', background='#0078d4',
                       troughcolor='#404040', borderwidth=0, lightcolor='#0078d4',
                       darkcolor='#0078d4')
        
    def create_header(self):
        """Create responsive header section"""
        header_frame = ttk.Frame(self.main_container, style='Header.TFrame')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Logo and title
        title_frame = ttk.Frame(header_frame, style='Header.TFrame')
        title_frame.grid(row=0, column=0, sticky='w', padx=20, pady=15)
        
        ttk.Label(title_frame, text="🔍", style='Header.TLabel', font=('Segoe UI', 24)).pack(side='left')
        ttk.Label(title_frame, text="Bug Prediction Model", style='Header.TLabel').pack(side='left', padx=(10, 0))
        
        # Status indicator
        status_frame = ttk.Frame(header_frame, style='Header.TFrame')
        status_frame.grid(row=0, column=1, sticky='e', padx=20, pady=15)
        
        ttk.Label(status_frame, text="Status:", style='Header.TLabel', font=('Segoe UI', 10)).pack(side='left')
        self.status_label = ttk.Label(status_frame, textvariable=self.analysis_status, 
                                     style='Success.TLabel', font=('Segoe UI', 10, 'bold'))
        self.status_label.pack(side='left', padx=(5, 0))
        
    def create_tabbed_interface(self):
        """Create responsive tabbed interface"""
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.main_container, style='Custom.TNotebook')
        self.notebook.grid(row=1, column=0, sticky='nsew')
        
        # Analysis tab
        self.analysis_frame = ResponsiveFrame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.analysis_frame, text='🔍 Analysis')
        self.create_analysis_tab()
        
        # Dashboard tab
        self.dashboard_frame = ResponsiveFrame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.dashboard_frame, text='📊 Dashboard')
        self.create_dashboard_tab()
        
        # History tab
        self.history_frame = ResponsiveFrame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.history_frame, text='📋 History')
        self.create_history_tab()
        
        # Settings tab
        self.settings_frame = ResponsiveFrame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.settings_frame, text='⚙️ Settings')
        self.create_settings_tab()
        
    def create_analysis_tab(self):
        """Create responsive analysis tab"""
        # Configure grid weights for responsiveness
        self.analysis_frame.grid_rowconfigure(1, weight=1)
        self.analysis_frame.grid_columnconfigure(0, weight=1)
        self.analysis_frame.grid_columnconfigure(1, weight=2)
        
        # Left panel - Input controls
        left_panel = ttk.Frame(self.analysis_frame, style='Card.TFrame')
        left_panel.grid(row=0, column=0, rowspan=2, sticky='nsew', padx=(0, 5), pady=5)
        left_panel.grid_columnconfigure(0, weight=1)
        
        self.create_input_controls(left_panel)
        
        # Right panel - Results
        right_panel = ttk.Frame(self.analysis_frame, style='Card.TFrame')
        right_panel.grid(row=0, column=1, rowspan=2, sticky='nsew', padx=(5, 0), pady=5)
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        self.create_results_panel(right_panel)
        
    def create_input_controls(self, parent):
        """Create responsive input controls"""
        # Title
        ttk.Label(parent, text="Code Analysis Input", style='Title.TLabel').grid(
            row=0, column=0, sticky='w', padx=15, pady=(15, 10))
        
        # File selection section
        file_frame = ttk.LabelFrame(parent, text="File Selection", style='Card.TFrame')
        file_frame.grid(row=1, column=0, sticky='ew', padx=15, pady=5)
        file_frame.grid_columnconfigure(0, weight=1)
        
        # File path display
        self.file_entry = ttk.Entry(file_frame, textvariable=self.selected_file, 
                                   style='Modern.TEntry', state='readonly')
        self.file_entry.grid(row=0, column=0, sticky='ew', padx=10, pady=10)
        
        # File buttons
        button_frame = ttk.Frame(file_frame, style='Content.TFrame')
        button_frame.grid(row=1, column=0, sticky='ew', padx=10, pady=(0, 10))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        
        ttk.Button(button_frame, text="📁 Select File", command=self.select_file,
                  style='Secondary.TButton').grid(row=0, column=0, sticky='ew', padx=(0, 2))
        ttk.Button(button_frame, text="📂 Select Directory", command=self.select_directory,
                  style='Secondary.TButton').grid(row=0, column=1, sticky='ew', padx=2)
        ttk.Button(button_frame, text="🗑️ Clear", command=self.clear_selection,
                  style='Secondary.TButton').grid(row=0, column=2, sticky='ew', padx=(2, 0))
        
        # Code input section
        code_frame = ttk.LabelFrame(parent, text="Direct Code Input", style='Card.TFrame')
        code_frame.grid(row=2, column=0, sticky='nsew', padx=15, pady=5)
        code_frame.grid_rowconfigure(0, weight=1)
        code_frame.grid_columnconfigure(0, weight=1)
        
        # Code text area with scrollbar
        self.code_text = scrolledtext.ScrolledText(
            code_frame, 
            height=12, 
            bg='#2d2d2d', 
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#0078d4',
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        self.code_text.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Configuration section
        config_frame = ttk.LabelFrame(parent, text="Analysis Configuration", style='Card.TFrame')
        config_frame.grid(row=3, column=0, sticky='ew', padx=15, pady=5)
        config_frame.grid_columnconfigure(1, weight=1)
        
        # Language selection
        ttk.Label(config_frame, text="Language:", style='Content.TLabel').grid(
            row=0, column=0, sticky='w', padx=10, pady=5)
        
        language_combo = ttk.Combobox(config_frame, textvariable=self.selected_language,
                                     style='Modern.TCombobox', state='readonly')
        language_combo['values'] = ('python', 'javascript', 'java', 'c', 'cpp', 'php', 'ruby', 'go', 'rust')
        language_combo.grid(row=0, column=1, sticky='ew', padx=(5, 10), pady=5)
        
        # Severity filter
        ttk.Label(config_frame, text="Min Severity:", style='Content.TLabel').grid(
            row=1, column=0, sticky='w', padx=10, pady=5)
        
        severity_combo = ttk.Combobox(config_frame, textvariable=self.min_severity,
                                     style='Modern.TCombobox', state='readonly')
        severity_combo['values'] = ('INFO', 'WARNING', 'ERROR')
        severity_combo.grid(row=1, column=1, sticky='ew', padx=(5, 10), pady=5)
        
        # Analysis button
        analyze_frame = ttk.Frame(parent, style='Content.TFrame')
        analyze_frame.grid(row=4, column=0, sticky='ew', padx=15, pady=15)
        analyze_frame.grid_columnconfigure(0, weight=1)
        
        self.analyze_button = ttk.Button(analyze_frame, text="🔍 Analyze Code", 
                                        command=self.start_analysis, style='Primary.TButton')
        self.analyze_button.grid(row=0, column=0, sticky='ew')
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(analyze_frame, style='Modern.Horizontal.TProgressbar',
                                           mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky='ew', pady=(10, 0))
        
        # Make the parent expand properly
        parent.grid_rowconfigure(2, weight=1)
        
    def create_results_panel(self, parent):
        """Create responsive results panel"""
        # Results header
        results_header = ttk.Frame(parent, style='Content.TFrame')
        results_header.grid(row=0, column=0, sticky='ew', padx=15, pady=(15, 5))
        results_header.grid_columnconfigure(0, weight=1)
        
        ttk.Label(results_header, text="Analysis Results", style='Title.TLabel').grid(
            row=0, column=0, sticky='w')
        
        # Export buttons
        export_frame = ttk.Frame(results_header, style='Content.TFrame')
        export_frame.grid(row=0, column=1, sticky='e')
        
        ttk.Button(export_frame, text="📄 JSON", command=lambda: self.export_results('json'),
                  style='Secondary.TButton').pack(side='left', padx=2)
        ttk.Button(export_frame, text="📊 CSV", command=lambda: self.export_results('csv'),
                  style='Secondary.TButton').pack(side='left', padx=2)
        ttk.Button(export_frame, text="🌐 HTML", command=lambda: self.export_results('html'),
                  style='Secondary.TButton').pack(side='left', padx=2)
        
        # Results display area
        results_container = ttk.Frame(parent, style='Card.TFrame')
        results_container.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        results_container.grid_rowconfigure(0, weight=1)
        results_container.grid_columnconfigure(0, weight=1)
        
        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_container,
            bg='#2d2d2d',
            fg='#ffffff',
            insertbackground='#ffffff',
            selectbackground='#0078d4',
            font=('Consolas', 9),
            wrap=tk.WORD,
            state='disabled'
        )
        self.results_text.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Configure text tags for colored output
        self.results_text.tag_configure('critical', foreground='#f44336', font=('Consolas', 9, 'bold'))
        self.results_text.tag_configure('high', foreground='#ff9800', font=('Consolas', 9, 'bold'))
        self.results_text.tag_configure('medium', foreground='#ffeb3b', font=('Consolas', 9, 'bold'))
        self.results_text.tag_configure('low', foreground='#4caf50', font=('Consolas', 9, 'bold'))
        self.results_text.tag_configure('info', foreground='#2196f3', font=('Consolas', 9, 'bold'))
        self.results_text.tag_configure('header', foreground='#ffffff', font=('Consolas', 10, 'bold'))
        
    def create_dashboard_tab(self):
        """Create responsive dashboard tab"""
        self.dashboard_frame.grid_rowconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_columnconfigure(1, weight=1)
        
        # Statistics cards
        stats_frame = ttk.Frame(self.dashboard_frame, style='Content.TFrame')
        stats_frame.grid(row=0, column=0, columnspan=2, sticky='ew', padx=15, pady=15)
        stats_frame.grid_columnconfigure(0, weight=1)
        stats_frame.grid_columnconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(2, weight=1)
        stats_frame.grid_columnconfigure(3, weight=1)
        
        # Create statistics cards
        self.create_stat_card(stats_frame, "Total Scans", "0", "#2196f3", 0, 0)
        self.create_stat_card(stats_frame, "Critical Issues", "0", "#f44336", 0, 1)
        self.create_stat_card(stats_frame, "Files Analyzed", "0", "#4caf50", 0, 2)
        self.create_stat_card(stats_frame, "Success Rate", "0%", "#ff9800", 0, 3)
        
        # Charts area (placeholder for now)
        charts_frame = ttk.LabelFrame(self.dashboard_frame, text="Vulnerability Trends", style='Card.TFrame')
        charts_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=15, pady=(0, 15))
        charts_frame.grid_rowconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(0, weight=1)
        
        # Placeholder for charts
        chart_placeholder = ttk.Label(charts_frame, text="📈 Vulnerability trends will be displayed here\n(Charts require matplotlib - install for full functionality)", 
                                     style='Content.TLabel', anchor='center')
        chart_placeholder.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        
    def create_stat_card(self, parent, title, value, color, row, col):
        """Create a statistics card"""
        card = ttk.Frame(parent, style='Card.TFrame')
        card.grid(row=row, column=col, sticky='ew', padx=5, pady=5)
        card.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(card, text=title, style='Content.TLabel', anchor='center')
        title_label.grid(row=0, column=0, sticky='ew', padx=10, pady=(10, 5))
        
        # Value
        value_label = ttk.Label(card, text=value, style='Title.TLabel', anchor='center',
                               font=('Segoe UI', 18, 'bold'))
        value_label.grid(row=1, column=0, sticky='ew', padx=10, pady=(0, 10))
        
        # Store reference for updates
        setattr(self, f"{title.lower().replace(' ', '_')}_label", value_label)
        
    def create_history_tab(self):
        """Create responsive history tab"""
        self.history_frame.grid_rowconfigure(1, weight=1)
        self.history_frame.grid_columnconfigure(0, weight=1)
        
        # History header
        history_header = ttk.Frame(self.history_frame, style='Content.TFrame')
        history_header.grid(row=0, column=0, sticky='ew', padx=15, pady=15)
        history_header.grid_columnconfigure(0, weight=1)
        
        ttk.Label(history_header, text="Analysis History", style='Title.TLabel').grid(
            row=0, column=0, sticky='w')
        
        ttk.Button(history_header, text="🔄 Refresh", command=self.refresh_history,
                  style='Secondary.TButton').grid(row=0, column=1, sticky='e')
        
        # History list
        history_container = ttk.Frame(self.history_frame, style='Card.TFrame')
        history_container.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        history_container.grid_rowconfigure(0, weight=1)
        history_container.grid_columnconfigure(0, weight=1)
        
        # Treeview for history
        columns = ('Timestamp', 'File', 'Language', 'Vulnerabilities', 'Critical', 'High')
        self.history_tree = ttk.Treeview(history_container, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(history_container, orient='vertical', command=self.history_tree.yview)
        h_scrollbar = ttk.Scrollbar(history_container, orient='horizontal', command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.history_tree.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        v_scrollbar.grid(row=0, column=1, sticky='ns', pady=10)
        h_scrollbar.grid(row=1, column=0, sticky='ew', padx=10)
        
    def create_settings_tab(self):
        """Create responsive settings tab"""
        self.settings_frame.grid_columnconfigure(0, weight=1)
        
        # Settings sections
        sections = [
            ("Analysis Settings", self.create_analysis_settings),
            ("Export Settings", self.create_export_settings),
            ("Advanced Settings", self.create_advanced_settings)
        ]
        
        for i, (title, create_func) in enumerate(sections):
            section_frame = ttk.LabelFrame(self.settings_frame, text=title, style='Card.TFrame')
            section_frame.grid(row=i, column=0, sticky='ew', padx=15, pady=10)
            section_frame.grid_columnconfigure(1, weight=1)
            create_func(section_frame)
            
    def create_analysis_settings(self, parent):
        """Create analysis settings section"""
        settings = [
            ("Enable Semgrep Integration", self.enable_semgrep),
            ("Enable Custom Rules", self.enable_custom_rules),
            ("Enable AI Enhancement", self.enable_ai_enhancement)
        ]
        
        for i, (text, var) in enumerate(settings):
            ttk.Checkbutton(parent, text=text, variable=var, style='Content.TLabel').grid(
                row=i, column=0, sticky='w', padx=15, pady=8)
                
    def create_export_settings(self, parent):
        """Create export settings section"""
        ttk.Label(parent, text="Default Export Format:", style='Content.TLabel').grid(
            row=0, column=0, sticky='w', padx=15, pady=8)
        
        export_combo = ttk.Combobox(parent, values=['JSON', 'CSV', 'HTML'], 
                                   style='Modern.TCombobox', state='readonly')
        export_combo.set('JSON')
        export_combo.grid(row=0, column=1, sticky='ew', padx=(5, 15), pady=8)
        
    def create_advanced_settings(self, parent):
        """Create advanced settings section"""
        ttk.Label(parent, text="Analysis Timeout (seconds):", style='Content.TLabel').grid(
            row=0, column=0, sticky='w', padx=15, pady=8)
        
        timeout_entry = ttk.Entry(parent, style='Modern.TEntry')
        timeout_entry.insert(0, "30")
        timeout_entry.grid(row=0, column=1, sticky='ew', padx=(5, 15), pady=8)
        
    def create_status_bar(self):
        """Create responsive status bar"""
        status_frame = ttk.Frame(self.main_container, style='Header.TFrame')
        status_frame.grid(row=2, column=0, sticky='ew', pady=(10, 0))
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Status text
        ttk.Label(status_frame, text="Ready", style='Content.TLabel').grid(
            row=0, column=0, sticky='w', padx=15, pady=8)
        
        # Version info
        ttk.Label(status_frame, text="v2.0 | Responsive UI", style='Content.TLabel').grid(
            row=0, column=1, sticky='e', padx=15, pady=8)
            
    def setup_responsive_behavior(self):
        """Setup responsive behavior for window resizing"""
        self.root.bind('<Configure>', self.on_window_resize)
        
    def on_window_resize(self, event):
        """Handle window resize events"""
        if event.widget == self.root:
            # Adjust UI elements based on window size
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            # Adjust font sizes for smaller screens
            if width < 1200:
                # Smaller font for compact view
                self.update_font_sizes('small')
            else:
                # Normal font sizes
                self.update_font_sizes('normal')
                
    def update_font_sizes(self, size_mode):
        """Update font sizes based on screen size"""
        if size_mode == 'small':
            # Smaller fonts for compact displays
            header_font = ('Segoe UI', 14, 'bold')
            title_font = ('Segoe UI', 10, 'bold')
            content_font = ('Segoe UI', 8)
        else:
            # Normal fonts
            header_font = ('Segoe UI', 16, 'bold')
            title_font = ('Segoe UI', 12, 'bold')
            content_font = ('Segoe UI', 9)
            
        # Update styles (this is a simplified version)
        style = ttk.Style()
        style.configure('Header.TLabel', font=header_font)
        style.configure('Title.TLabel', font=title_font)
        style.configure('Content.TLabel', font=content_font)
        
    # Analysis methods (keeping existing functionality)
    def select_file(self):
        """Select a single file for analysis"""
        file_path = filedialog.askopenfilename(
            title="Select Code File",
            filetypes=[
                ("Python files", "*.py"),
                ("JavaScript files", "*.js"),
                ("Java files", "*.java"),
                ("C files", "*.c"),
                ("C++ files", "*.cpp"),
                ("PHP files", "*.php"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.selected_file.set(file_path)
            self.code_text.delete(1.0, tk.END)  # Clear code input when file is selected
            
    def select_directory(self):
        """Select a directory for bulk analysis"""
        dir_path = filedialog.askdirectory(title="Select Directory")
        if dir_path:
            self.selected_file.set(f"Directory: {dir_path}")
            self.code_text.delete(1.0, tk.END)
            
    def clear_selection(self):
        """Clear file selection and code input"""
        self.selected_file.set("")
        self.code_text.delete(1.0, tk.END)
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        
    def start_analysis(self):
        """Start the analysis in a separate thread"""
        # Disable analyze button and show progress
        self.analyze_button.config(state='disabled')
        self.progress_bar.start()
        self.analysis_status.set("Analyzing...")
        self.status_label.config(style='Warning.TLabel')
        
        # Start analysis in background thread
        analysis_thread = threading.Thread(target=self.run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
        
    def run_analysis(self):
        """Run the actual analysis"""
        try:
            # Determine input source
            code_content = self.code_text.get(1.0, tk.END).strip()
            file_path = self.selected_file.get()
            
            if code_content and not file_path:
                # Analyze direct code input
                results = self.analyze_direct_code(code_content)
            elif file_path and not code_content:
                # Analyze selected file(s)
                if file_path.startswith("Directory:"):
                    dir_path = file_path.replace("Directory: ", "")
                    results = self.analyze_directory(dir_path)
                else:
                    results = self.analyze_file(file_path)
            elif code_content and file_path:
                # Prioritize direct code input
                results = self.analyze_direct_code(code_content)
            else:
                results = {"error": "No code or file selected for analysis"}
                
            # Update UI in main thread
            self.root.after(0, self.display_results, results)
            
        except Exception as e:
            error_result = {"error": f"Analysis failed: {str(e)}"}
            self.root.after(0, self.display_results, error_result)
            
    def analyze_direct_code(self, code_content):
        """Analyze code content directly"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{self.selected_language.get()}', 
                                           delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code_content)
                temp_file_path = temp_file.name
                
            # Run analysis on temporary file
            results = self.analyze_file(temp_file_path)
            
            # Clean up
            os.unlink(temp_file_path)
            
            return results
            
        except Exception as e:
            return {"error": f"Failed to analyze code: {str(e)}"}
            
    def analyze_file(self, file_path):
        """Analyze a single file"""
        try:
            # Built-in vulnerability patterns
            vulnerabilities = self.detect_vulnerabilities(file_path)
            
            # Add Semgrep analysis if enabled
            if self.enable_semgrep.get():
                semgrep_results = self.run_semgrep_analysis(file_path)
                vulnerabilities.extend(semgrep_results)
                
            # Categorize by severity
            categorized = self.categorize_vulnerabilities(vulnerabilities)
            
            # Save to database
            self.save_analysis_result(file_path, categorized, vulnerabilities)
            
            return {
                "file": file_path,
                "vulnerabilities": vulnerabilities,
                "summary": categorized,
                "total": len(vulnerabilities)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze file {file_path}: {str(e)}"}
            
    def analyze_directory(self, dir_path):
        """Analyze all files in a directory"""
        results = []
        supported_extensions = {'.py', '.js', '.java', '.c', '.cpp', '.php', '.rb', '.go', '.rs'}
        
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if Path(file_path).suffix.lower() in supported_extensions:
                        file_result = self.analyze_file(file_path)
                        if "error" not in file_result:
                            results.append(file_result)
                            
            return {
                "directory": dir_path,
                "files_analyzed": len(results),
                "results": results,
                "total_vulnerabilities": sum(r.get("total", 0) for r in results)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze directory {dir_path}: {str(e)}"}
            
    def detect_vulnerabilities(self, file_path):
        """Detect vulnerabilities using built-in patterns"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Vulnerability patterns
            patterns = {
                'SQL Injection': [
                    (r'(?i)(SELECT|INSERT|UPDATE|DELETE).*\+.*', 'String concatenation in SQL query'),
                    (r'(?i)1\s*OR\s*1\s*=\s*1', 'Classic SQL injection pattern'),
                    (r'(?i)UNION\s+SELECT', 'UNION-based SQL injection'),
                    (r'(?i);\s*DROP\s+TABLE', 'SQL injection with DROP statement'),
                ],
                'Cross-Site Scripting (XSS)': [
                    (r'innerHTML\s*=\s*[^;]*\+', 'Unsafe innerHTML assignment'),
                    (r'document\.write\s*\([^)]*\+', 'Unsafe document.write usage'),
                    (r'<script[^>]*>[^<]*</script>', 'Inline script tag'),
                ],
                'Command Injection': [
                    (r'os\.system\s*\([^)]*\+', 'Command injection via os.system'),
                    (r'subprocess\.[^(]*\([^)]*shell\s*=\s*True', 'Shell injection risk'),
                    (r'eval\s*\([^)]*input', 'Code injection via eval'),
                ],
                'Path Traversal': [
                    (r'\.\./', 'Directory traversal pattern'),
                    (r'open\s*\([^)]*\+[^)]*["\'][^"\']*["\']', 'Unsafe file path construction'),
                ],
                'Hardcoded Credentials': [
                    (r'(?i)(password|pwd|pass)\s*=\s*["\'][^"\']{3,}["\']', 'Hardcoded password'),
                    (r'(?i)(api_key|apikey|secret)\s*=\s*["\'][^"\']{10,}["\']', 'Hardcoded API key'),
                ],
                'Weak Cryptography': [
                    (r'hashlib\.md5\s*\(', 'Weak MD5 hash usage'),
                    (r'hashlib\.sha1\s*\(', 'Weak SHA1 hash usage'),
                    (r'(?i)DES|RC4', 'Weak encryption algorithm'),
                ],
                'Unsafe Deserialization': [
                    (r'pickle\.loads?\s*\(', 'Unsafe pickle deserialization'),
                    (r'yaml\.load\s*\([^)]*Loader', 'Unsafe YAML loading'),
                ],
                'Information Disclosure': [
                    (r'(?i)debug\s*=\s*True', 'Debug mode enabled'),
                    (r'print\s*\([^)]*password', 'Password in debug output'),
                    (r'console\.log\s*\([^)]*token', 'Token in console output'),
                ]
            }
            
            # Scan for patterns
            for vuln_type, pattern_list in patterns.items():
                for pattern, description in pattern_list:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line):
                            severity = self.get_severity(vuln_type)
                            vulnerabilities.append({
                                'type': vuln_type,
                                'description': description,
                                'line': line_num,
                                'code': line.strip(),
                                'severity': severity,
                                'file': file_path
                            })
                            
        except Exception as e:
            print(f"Error detecting vulnerabilities: {e}")
            
        return vulnerabilities
        
    def get_severity(self, vuln_type):
        """Get severity level for vulnerability type"""
        critical_types = ['SQL Injection', 'Command Injection', 'Unsafe Deserialization', 'Hardcoded Credentials']
        high_types = ['Cross-Site Scripting (XSS)', 'Path Traversal']
        medium_types = ['Weak Cryptography', 'Information Disclosure']
        
        if vuln_type in critical_types:
            return 'CRITICAL'
        elif vuln_type in high_types:
            return 'HIGH'
        elif vuln_type in medium_types:
            return 'MEDIUM'
        else:
            return 'LOW'
            
    def run_semgrep_analysis(self, file_path):
        """Run Semgrep analysis if available"""
        try:
            cmd = ['semgrep', '--config=auto', '--json', '--quiet', file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  encoding='utf-8', errors='replace', timeout=30)
            
            if result.returncode == 0:
                findings = json.loads(result.stdout)
                semgrep_vulns = []
                
                for finding in findings.get('results', []):
                    semgrep_vulns.append({
                        'type': finding.get('check_id', 'Unknown'),
                        'description': finding.get('extra', {}).get('message', 'Semgrep finding'),
                        'line': finding.get('start', {}).get('line', 0),
                        'code': finding.get('extra', {}).get('lines', ''),
                        'severity': finding.get('extra', {}).get('severity', 'INFO').upper(),
                        'file': file_path,
                        'source': 'Semgrep'
                    })
                    
                return semgrep_vulns
                
        except Exception as e:
            print(f"Semgrep analysis failed: {e}")
            
        return []
        
    def categorize_vulnerabilities(self, vulnerabilities):
        """Categorize vulnerabilities by severity"""
        categories = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'INFO')
            if severity in categories:
                categories[severity] += 1
                
        return categories
        
    def save_analysis_result(self, filename, summary, vulnerabilities):
        """Save analysis result to database"""
        try:
            timestamp = datetime.now().isoformat()
            total_vulns = sum(summary.values())
            
            self.cursor.execute('''
                INSERT INTO analysis_results 
                (timestamp, filename, language, total_vulnerabilities, 
                 critical_count, high_count, medium_count, low_count, info_count, results_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp, filename, self.selected_language.get(), total_vulns,
                summary.get('CRITICAL', 0), summary.get('HIGH', 0), 
                summary.get('MEDIUM', 0), summary.get('LOW', 0), 
                summary.get('INFO', 0), json.dumps(vulnerabilities)
            ))
            self.conn.commit()
            
        except Exception as e:
            print(f"Database save error: {e}")
            
    def display_results(self, results):
        """Display analysis results in the UI"""
        # Stop progress bar and re-enable button
        self.progress_bar.stop()
        self.analyze_button.config(state='normal')
        self.analysis_status.set("Complete")
        self.status_label.config(style='Success.TLabel')
        
        # Clear previous results
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        
        if "error" in results:
            self.results_text.insert(tk.END, f"❌ Error: {results['error']}\n", 'error')
        else:
            # Display results
            if "directory" in results:
                self.display_directory_results(results)
            else:
                self.display_file_results(results)
                
        self.results_text.config(state='disabled')
        
        # Update dashboard statistics
        self.update_dashboard_stats()
        
    def display_file_results(self, results):
        """Display results for single file analysis"""
        file_name = os.path.basename(results.get('file', 'Direct Code Input'))
        total_vulns = results.get('total', 0)
        
        # Header
        self.results_text.insert(tk.END, f"🔍 Analysis Results for: {file_name}\n", 'header')
        self.results_text.insert(tk.END, "=" * 60 + "\n\n", 'header')
        
        # Summary
        summary = results.get('summary', {})
        self.results_text.insert(tk.END, f"📊 Summary:\n", 'header')
        self.results_text.insert(tk.END, f"  Total Vulnerabilities: {total_vulns}\n")
        
        for severity, count in summary.items():
            if count > 0:
                tag = severity.lower()
                self.results_text.insert(tk.END, f"  {severity}: {count}\n", tag)
                
        self.results_text.insert(tk.END, "\n")
        
        # Detailed findings
        vulnerabilities = results.get('vulnerabilities', [])
        if vulnerabilities:
            self.results_text.insert(tk.END, "🔍 Detailed Findings:\n", 'header')
            self.results_text.insert(tk.END, "-" * 40 + "\n\n")
            
            for i, vuln in enumerate(vulnerabilities, 1):
                severity = vuln.get('severity', 'INFO')
                tag = severity.lower()
                
                self.results_text.insert(tk.END, f"{i}. ", 'header')
                self.results_text.insert(tk.END, f"[{severity}] ", tag)
                self.results_text.insert(tk.END, f"{vuln.get('type', 'Unknown')}\n")
                self.results_text.insert(tk.END, f"   Description: {vuln.get('description', 'No description')}\n")
                self.results_text.insert(tk.END, f"   Line: {vuln.get('line', 'Unknown')}\n")
                self.results_text.insert(tk.END, f"   Code: {vuln.get('code', 'No code snippet')}\n")
                if vuln.get('source'):
                    self.results_text.insert(tk.END, f"   Source: {vuln.get('source')}\n")
                self.results_text.insert(tk.END, "\n")
        else:
            self.results_text.insert(tk.END, "✅ No vulnerabilities detected!\n", 'info')
            
    def display_directory_results(self, results):
        """Display results for directory analysis"""
        dir_name = os.path.basename(results.get('directory', 'Unknown'))
        files_analyzed = results.get('files_analyzed', 0)
        total_vulns = results.get('total_vulnerabilities', 0)
        
        # Header
        self.results_text.insert(tk.END, f"📂 Directory Analysis: {dir_name}\n", 'header')
        self.results_text.insert(tk.END, "=" * 60 + "\n\n", 'header')
        
        # Summary
        self.results_text.insert(tk.END, f"📊 Summary:\n", 'header')
        self.results_text.insert(tk.END, f"  Files Analyzed: {files_analyzed}\n")
        self.results_text.insert(tk.END, f"  Total Vulnerabilities: {total_vulns}\n\n")
        
        # Per-file results
        file_results = results.get('results', [])
        if file_results:
            self.results_text.insert(tk.END, "📋 Per-File Results:\n", 'header')
            self.results_text.insert(tk.END, "-" * 40 + "\n\n")
            
            for file_result in file_results:
                file_name = os.path.basename(file_result.get('file', 'Unknown'))
                file_vulns = file_result.get('total', 0)
                
                if file_vulns > 0:
                    self.results_text.insert(tk.END, f"📄 {file_name}: ", 'header')
                    self.results_text.insert(tk.END, f"{file_vulns} vulnerabilities\n", 'warning')
                    
                    # Show top vulnerabilities for this file
                    vulns = file_result.get('vulnerabilities', [])[:3]  # Show top 3
                    for vuln in vulns:
                        severity = vuln.get('severity', 'INFO')
                        tag = severity.lower()
                        self.results_text.insert(tk.END, f"    • ", 'content')
                        self.results_text.insert(tk.END, f"[{severity}] ", tag)
                        self.results_text.insert(tk.END, f"{vuln.get('type', 'Unknown')}\n")
                    
                    if len(file_result.get('vulnerabilities', [])) > 3:
                        remaining = len(file_result.get('vulnerabilities', [])) - 3
                        self.results_text.insert(tk.END, f"    ... and {remaining} more\n")
                    self.results_text.insert(tk.END, "\n")
        else:
            self.results_text.insert(tk.END, "✅ No vulnerabilities detected in any files!\n", 'info')
            
    def update_dashboard_stats(self):
        """Update dashboard statistics"""
        try:
            # Get statistics from database
            self.cursor.execute('SELECT COUNT(*) FROM analysis_results')
            total_scans = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT SUM(critical_count) FROM analysis_results')
            critical_issues = self.cursor.fetchone()[0] or 0
            
            self.cursor.execute('SELECT COUNT(DISTINCT filename) FROM analysis_results')
            files_analyzed = self.cursor.fetchone()[0]
            
            # Calculate success rate (scans with no critical issues)
            self.cursor.execute('SELECT COUNT(*) FROM analysis_results WHERE critical_count = 0')
            successful_scans = self.cursor.fetchone()[0]
            success_rate = (successful_scans / total_scans * 100) if total_scans > 0 else 0
            
            # Update labels
            if hasattr(self, 'total_scans_label'):
                self.total_scans_label.config(text=str(total_scans))
            if hasattr(self, 'critical_issues_label'):
                self.critical_issues_label.config(text=str(critical_issues))
            if hasattr(self, 'files_analyzed_label'):
                self.files_analyzed_label.config(text=str(files_analyzed))
            if hasattr(self, 'success_rate_label'):
                self.success_rate_label.config(text=f"{success_rate:.1f}%")
                
        except Exception as e:
            print(f"Error updating dashboard stats: {e}")
            
    def refresh_history(self):
        """Refresh the history display"""
        try:
            # Clear existing items
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
                
            # Fetch recent analysis results
            self.cursor.execute('''
                SELECT timestamp, filename, language, total_vulnerabilities, 
                       critical_count, high_count 
                FROM analysis_results 
                ORDER BY timestamp DESC 
                LIMIT 100
            ''')
            
            results = self.cursor.fetchall()
            
            for result in results:
                timestamp, filename, language, total_vulns, critical, high = result
                # Format timestamp
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                # Get just filename without path
                short_filename = os.path.basename(filename)
                
                self.history_tree.insert('', 'end', values=(
                    formatted_time, short_filename, language, 
                    total_vulns, critical, high
                ))
                
        except Exception as e:
            print(f"Error refreshing history: {e}")
            
    def export_results(self, format_type):
        """Export analysis results"""
        try:
            # Get current results from the display
            current_text = self.results_text.get(1.0, tk.END)
            
            if not current_text.strip():
                messagebox.showwarning("Export Warning", "No results to export!")
                return
                
            # Choose file location
            file_types = {
                'json': [("JSON files", "*.json")],
                'csv': [("CSV files", "*.csv")],
                'html': [("HTML files", "*.html")]
            }
            
            file_path = filedialog.asksaveasfilename(
                title=f"Export as {format_type.upper()}",
                filetypes=file_types[format_type],
                defaultextension=f".{format_type}"
            )
            
            if file_path:
                if format_type == 'json':
                    self.export_json(file_path)
                elif format_type == 'csv':
                    self.export_csv(file_path)
                elif format_type == 'html':
                    self.export_html(file_path)
                    
                messagebox.showinfo("Export Complete", f"Results exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
            
    def export_json(self, file_path):
        """Export results as JSON"""
        # Get latest analysis from database
        self.cursor.execute('''
            SELECT results_json FROM analysis_results 
            ORDER BY timestamp DESC LIMIT 1
        ''')
        result = self.cursor.fetchone()
        
        if result:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result[0])
        else:
            # Fallback to empty results
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({"message": "No analysis results available"}, f, indent=2)
                
    def export_csv(self, file_path):
        """Export results as CSV"""
        import csv
        
        # Get all analysis results
        self.cursor.execute('''
            SELECT timestamp, filename, language, total_vulnerabilities,
                   critical_count, high_count, medium_count, low_count, info_count
            FROM analysis_results ORDER BY timestamp DESC
        ''')
        
        results = self.cursor.fetchall()
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Filename', 'Language', 'Total Vulnerabilities',
                           'Critical', 'High', 'Medium', 'Low', 'Info'])
            writer.writerows(results)
            
    def export_html(self, file_path):
        """Export results as HTML report"""
        # Get latest analysis
        self.cursor.execute('''
            SELECT * FROM analysis_results 
            ORDER BY timestamp DESC LIMIT 1
        ''')
        result = self.cursor.fetchone()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bug Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                .header {{ background: #2d2d2d; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; flex: 1; text-align: center; }}
                .critical {{ color: #f44336; font-weight: bold; }}
                .high {{ color: #ff9800; font-weight: bold; }}
                .medium {{ color: #ffeb3b; font-weight: bold; }}
                .low {{ color: #4caf50; font-weight: bold; }}
                .info {{ color: #2196f3; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 Bug Analysis Report</h1>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
        """
        
        if result:
            html_content += f"""
                <div class="stats">
                    <div class="stat-card">
                        <h3>Total Vulnerabilities</h3>
                        <h2>{result[4]}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>Critical</h3>
                        <h2 class="critical">{result[5]}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>High</h3>
                        <h2 class="high">{result[6]}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>Medium</h3>
                        <h2 class="medium">{result[7]}</h2>
                    </div>
                    <div class="stat-card">
                        <h3>Low</h3>
                        <h2 class="low">{result[8]}</h2>
                    </div>
                </div>
                <h2>Analysis Details</h2>
                <p><strong>File:</strong> {result[2]}</p>
                <p><strong>Language:</strong> {result[3]}</p>
                <p><strong>Timestamp:</strong> {result[1]}</p>
            """
        else:
            html_content += "<p>No analysis results available.</p>"
            
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = ModernBugPredictionGUI(root)
    
    # Load history on startup
    root.after(1000, app.refresh_history)
    
    root.mainloop()

if __name__ == "__main__":
    main()
