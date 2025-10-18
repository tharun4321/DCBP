import json
import os
import tempfile

class EnhancedSemgrepAnalyzer:
    def __init__(self):
        self.custom_rules = {
            "sql_injection": {
                "id": "sql-injection-detection",
                "message": "Potential SQL injection vulnerability detected",
                "severity": "ERROR",
                "languages": ["python"],
                "pattern-either": [
                    {"pattern": "cursor.execute($QUERY + $VAR)"},
                    {"pattern": "cursor.execute(f\"...{$VAR}...\")"},
                    {"pattern": "cursor.execute(\"...\" + $VAR + \"...\")"},
                    {"pattern": "$CURSOR.execute($QUERY % $VAR)"}
                ]
            },
            "hardcoded_secrets": {
                "id": "hardcoded-credentials",
                "message": "Hardcoded credentials detected",
                "severity": "ERROR", 
                "languages": ["python"],
                "pattern-either": [
                    {"pattern": "password=\"$PASSWORD\""},
                    {"pattern": "api_key=\"$KEY\""},
                    {"pattern": "secret=\"$SECRET\""},
                    {"pattern": "token=\"$TOKEN\""}
                ]
            },
            "command_injection": {
                "id": "command-injection",
                "message": "Potential command injection vulnerability",
                "severity": "ERROR",
                "languages": ["python"],
                "pattern-either": [
                    {"pattern": "subprocess.call($CMD, shell=True)"},
                    {"pattern": "os.system($CMD)"},
                    {"pattern": "subprocess.run($CMD, shell=True)"},
                    {"pattern": "subprocess.Popen($CMD, shell=True)"}
                ]
            },
            "path_traversal": {
                "id": "path-traversal",
                "message": "Potential path traversal vulnerability",
                "severity": "ERROR",
                "languages": ["python"],
                "pattern-either": [
                    {"pattern": "open(f\"...{$VAR}...\", ...)"},
                    {"pattern": "open($PATH + $VAR, ...)"},
                    {"pattern": "open($VAR, ...)"}
                ]
            },
            "weak_crypto": {
                "id": "weak-cryptography",
                "message": "Weak cryptographic algorithm detected",
                "severity": "WARNING",
                "languages": ["python"],
                "pattern-either": [
                    {"pattern": "hashlib.md5(...)"},
                    {"pattern": "hashlib.sha1(...)"},
                    {"pattern": "random.randint(...)"}
                ]
            },
            "unsafe_deserialization": {
                "id": "unsafe-deserialization",
                "message": "Unsafe deserialization detected",
                "severity": "ERROR",
                "languages": ["python"],
                "pattern-either": [
                    {"pattern": "pickle.loads($DATA)"},
                    {"pattern": "pickle.load($FILE)"},
                    {"pattern": "yaml.load($DATA)"}
                ]
            }
        }
    
    def create_custom_rules_file(self):
        """Create a temporary YAML file with custom Semgrep rules"""
        rules_content = {
            "rules": list(self.custom_rules.values())
        }
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        
        # Convert to YAML format
        import yaml
        yaml.dump(rules_content, temp_file, default_flow_style=False)
        temp_file.close()
        
        return temp_file.name
    
    def analyze_with_custom_rules(self, file_path):
        """Run Semgrep with custom rules"""
        import subprocess
        
        rules_file = self.create_custom_rules_file()
        
        try:
            cmd = [
                'semgrep',
                '--config', rules_file,
                '--json',
                '--quiet',
                file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    findings = json.loads(result.stdout)
                    return findings.get('results', [])
                except json.JSONDecodeError:
                    return []
            else:
                print(f"Semgrep error: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Error running custom analysis: {e}")
            return []
        finally:
            # Clean up temporary file
            try:
                os.unlink(rules_file)
            except:
                pass
    
    def get_vulnerability_details(self, rule_id):
        """Get detailed information about a vulnerability"""
        vulnerability_info = {
            "sql-injection-detection": {
                "description": "SQL injection occurs when user input is directly concatenated into SQL queries without proper sanitization.",
                "impact": "Attackers can execute arbitrary SQL commands, potentially accessing, modifying, or deleting data.",
                "fix": "Use parameterized queries or prepared statements instead of string concatenation.",
                "example_fix": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
            },
            "hardcoded-credentials": {
                "description": "Hardcoded credentials in source code pose a security risk.",
                "impact": "Credentials can be exposed to anyone with access to the source code.",
                "fix": "Use environment variables or secure configuration files.",
                "example_fix": "password = os.getenv('DB_PASSWORD')"
            },
            "command-injection": {
                "description": "Command injection occurs when user input is used in system commands without proper validation.",
                "impact": "Attackers can execute arbitrary system commands.",
                "fix": "Validate and sanitize input, avoid shell=True, use subprocess with list arguments.",
                "example_fix": "subprocess.run(['tar', '-czf', backup_file, source_dir])"
            },
            "path-traversal": {
                "description": "Path traversal allows attackers to access files outside the intended directory.",
                "impact": "Attackers can read sensitive files from the system.",
                "fix": "Validate file paths and use os.path.join() with proper validation.",
                "example_fix": "safe_path = os.path.join(base_dir, os.path.basename(filename))"
            },
            "weak-cryptography": {
                "description": "Weak cryptographic algorithms are vulnerable to attacks.",
                "impact": "Data can be easily compromised or passwords cracked.",
                "fix": "Use strong algorithms like SHA-256 or bcrypt for password hashing.",
                "example_fix": "import bcrypt; hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())"
            },
            "unsafe-deserialization": {
                "description": "Unsafe deserialization can lead to code execution vulnerabilities.",
                "impact": "Attackers can execute arbitrary code by providing malicious serialized data.",
                "fix": "Use safe serialization formats like JSON, or validate data before deserialization.",
                "example_fix": "import json; data = json.loads(user_input)"
            }
        }
        
        return vulnerability_info.get(rule_id, {
            "description": "Security vulnerability detected",
            "impact": "Potential security risk",
            "fix": "Review and fix the identified issue",
            "example_fix": "Implement proper security measures"
        })
