import tkinter as tk
from tkinter import messagebox
import subprocess
import json
import os
import tempfile
import sqlite3
from datetime import datetime
import re
from pathlib import Path

# Import the GUI class from the new file
from gui_elements import ModernBugPredictionGUI 

# --- Core Logic Classes ---
class SemgrepAnalyzer:
    def __init__(self):
        # The GUI no longer relies on this being checked in the init
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
                    # Ensure all required keys are present with defaults
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
                
            else:
                print(f"Semgrep error (Code {result.returncode}): {result.stderr}")
                return []
                
        except (json.JSONDecodeError, subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"Semgrep analysis failed: {e}")
            return []
            
    def get_severity(self, vuln_type):
        """Get severity level for vulnerability type (moved from GUI to analyzer)"""
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

    def detect_vulnerabilities(self, file_path):
        """Detect vulnerabilities using built-in patterns (moved from GUI to analyzer)"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                lines = content.split('\n')
                
            # Vulnerability patterns (keeping the same structure for clarity)
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
                    compiled_regex = re.compile(pattern)
                    for line_num, line in enumerate(lines, 1):
                        if compiled_regex.search(line):
                            severity = self.get_severity(vuln_type)
                            vulnerabilities.append({
                                'type': vuln_type,
                                'description': description,
                                'line': line_num,
                                'code': line.strip(),
                                'severity': severity,
                                'file': file_path,
                                'source': 'Internal Scanner'
                            })
                            
        except Exception as e:
            print(f"Error detecting vulnerabilities: {e}")
            
        return vulnerabilities
        
    def categorize_vulnerabilities(self, vulnerabilities):
        """Categorize vulnerabilities by severity (moved from GUI to analyzer)"""
        categories = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'INFO').upper()
            if severity in categories:
                categories[severity] += 1
                
        return categories

    def analyze_file(self, file_path, enable_semgrep):
        """Analyze a single file"""
        try:
            # Built-in vulnerability patterns
            vulnerabilities = self.detect_vulnerabilities(file_path)
            
            # Add Semgrep analysis if enabled
            if enable_semgrep:
                semgrep_results = self.run_semgrep_analysis(file_path)
                vulnerabilities.extend(semgrep_results)
                
            # Categorize by severity
            categorized = self.categorize_vulnerabilities(vulnerabilities)
            
            return {
                "file": file_path,
                "vulnerabilities": vulnerabilities,
                "summary": categorized,
                "total": len(vulnerabilities)
            }
            
        except Exception as e:
            return {"error": f"Failed to analyze file {file_path}: {str(e)}"}
            
    def analyze_directory(self, dir_path, enable_semgrep):
        """Analyze all files in a directory"""
        results = []
        supported_extensions = {'.py', '.js', '.java', '.c', '.cpp', '.php', '.rb', '.go', '.rs'}
        
        try:
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if Path(file_path).suffix.lower() in supported_extensions:
                        file_result = self.analyze_file(file_path, enable_semgrep)
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
            
    def analyze_direct_code(self, code_content, language, enable_semgrep):
        """Analyze code content directly"""
        temp_file_path = None
        try:
            # Create temporary file
            suffix_map = {'python': '.py', 'javascript': '.js', 'java': '.java', 'c': '.c', 'cpp': '.cpp', 'php': '.php', 'ruby': '.rb', 'go': '.go', 'rust': '.rs'}
            suffix = suffix_map.get(language, '.txt')
            
            with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, 
                                             delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code_content)
                temp_file_path = temp_file.name
                
            # Run analysis on temporary file
            results = self.analyze_file(temp_file_path, enable_semgrep)
            results['file'] = 'Direct Code Input' # Override file path for display
            
            # Clean up is in finally block to ensure it runs
            return results
            
        except Exception as e:
            return {"error": f"Failed to analyze direct code: {str(e)}"}
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    # --- Unified Analysis Runner ---
    def run_analysis(self, code_content, file_path, language, enable_semgrep):
        """Unified entry point for analysis from the GUI thread"""
        
        if enable_semgrep and not self.check_semgrep_installation():
             return {"error": "Semgrep is not installed or not in PATH. Please install it to use this feature."}
             
        if code_content and not file_path:
            return self.analyze_direct_code(code_content, language, enable_semgrep)
        elif file_path and not code_content:
            if file_path.startswith("Directory:"):
                dir_path = file_path.replace("Directory: ", "")
                return self.analyze_directory(dir_path, enable_semgrep)
            else:
                return self.analyze_file(file_path, enable_semgrep)
        elif code_content and file_path:
            # Prioritize direct code input
            return self.analyze_direct_code(code_content, language, enable_semgrep)
        else:
            return {"error": "No code or file selected for analysis"}

# --- Application Runner ---
def setup_database():
    """Initialize SQLite database (moved from GUI to main for setup)"""
    try:
        conn = sqlite3.connect('bug_analysis.db')
        cursor = conn.cursor()
        cursor.execute('''
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
        conn.commit()
        return conn, cursor
    except Exception as e:
        messagebox.showerror("Database Error", f"Database setup error: {e}")
        return None, None

def main():
    """Main function to run the application"""
    conn, cursor = setup_database()
    if not conn:
        return # Exit if DB setup failed

    try:
        root = tk.Tk()
        analyzer = SemgrepAnalyzer()
        
        # Pass the database connection and core logic to the GUI
        app = ModernBugPredictionGUI(root, conn, cursor, analyzer)
        
        # Load history and dashboard stats on startup
        root.after(100, app.refresh_history)
        root.after(100, app.update_dashboard_stats)

        root.mainloop()

    finally:
        # Cleanup database connection
        if conn:
            conn.close()

if __name__ == "__main__":
    main()