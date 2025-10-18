import re
import json
from typing import List, Dict, Any
from collections import defaultdict

class AIBugPredictor:
    """AI-powered bug prediction and enhancement features"""
    
    def __init__(self):
        self.vulnerability_patterns = {
            'sql_injection': [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'query\s*\(\s*["\'].*\+.*["\']',
                r'cursor\.execute\s*\(\s*["\'].*%.*["\']'
            ],
            'xss': [
                r'innerHTML\s*=\s*.*\+',
                r'document\.write\s*\(\s*.*\+',
                r'eval\s*\(\s*.*input'
            ],
            'hardcoded_secrets': [
                r'password\s*=\s*["\'][^"\']{8,}["\']',
                r'api_key\s*=\s*["\'][^"\']{20,}["\']',
                r'secret\s*=\s*["\'][^"\']{16,}["\']'
            ],
            'buffer_overflow': [
                r'strcpy\s*\(',
                r'strcat\s*\(',
                r'sprintf\s*\('
            ],
            'race_condition': [
                r'threading\.',
                r'multiprocessing\.',
                r'async\s+def'
            ]
        }
        
        self.severity_weights = {
            'sql_injection': 0.9,
            'xss': 0.8,
            'hardcoded_secrets': 0.85,
            'buffer_overflow': 0.95,
            'race_condition': 0.7
        }
    
    def predict_vulnerabilities(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Predict potential vulnerabilities using pattern matching"""
        predictions = []
        
        for vuln_type, patterns in self.vulnerability_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    line_num = code[:match.start()].count('\n') + 1
                    predictions.append({
                        'type': vuln_type,
                        'line': line_num,
                        'severity': self.calculate_severity(vuln_type, match.group()),
                        'confidence': self.calculate_confidence(vuln_type, match.group()),
                        'suggestion': self.get_fix_suggestion(vuln_type),
                        'match': match.group()
                    })
        
        return predictions
    
    def calculate_severity(self, vuln_type: str, match: str) -> float:
        """Calculate severity score for a vulnerability"""
        base_severity = self.severity_weights.get(vuln_type, 0.5)
        
        # Adjust based on context
        if 'user' in match.lower() or 'input' in match.lower():
            base_severity += 0.1
        
        if 'admin' in match.lower() or 'root' in match.lower():
            base_severity += 0.15
        
        return min(base_severity, 1.0)
    
    def calculate_confidence(self, vuln_type: str, match: str) -> float:
        """Calculate confidence score for a prediction"""
        # Simple confidence calculation based on pattern specificity
        confidence_map = {
            'sql_injection': 0.8,
            'xss': 0.75,
            'hardcoded_secrets': 0.9,
            'buffer_overflow': 0.85,
            'race_condition': 0.6
        }
        
        return confidence_map.get(vuln_type, 0.5)
    
    def get_fix_suggestion(self, vuln_type: str) -> str:
        """Get fix suggestions for vulnerability types"""
        suggestions = {
            'sql_injection': "Use parameterized queries or prepared statements instead of string concatenation",
            'xss': "Sanitize user input and use safe DOM manipulation methods",
            'hardcoded_secrets': "Move secrets to environment variables or secure configuration files",
            'buffer_overflow': "Use safer string functions like strncpy, strncat, or snprintf",
            'race_condition': "Use proper synchronization mechanisms like locks or atomic operations"
        }
        
        return suggestions.get(vuln_type, "Review code for potential security issues")
    
    def analyze_code_complexity(self, code: str) -> Dict[str, Any]:
        """Analyze code complexity metrics"""
        lines = code.split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            'comment_lines': len([line for line in lines if line.strip().startswith('#')]),
            'cyclomatic_complexity': self.calculate_cyclomatic_complexity(code),
            'nesting_depth': self.calculate_max_nesting_depth(code),
            'function_count': len(re.findall(r'def\s+\w+', code)),
            'class_count': len(re.findall(r'class\s+\w+', code))
        }
        
        return metrics
    
    def calculate_cyclomatic_complexity(self, code: str) -> int:
        """Calculate cyclomatic complexity"""
        # Count decision points
        decision_keywords = ['if', 'elif', 'while', 'for', 'except', 'and', 'or']
        complexity = 1  # Base complexity
        
        for keyword in decision_keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', code))
        
        return complexity
    
    def calculate_max_nesting_depth(self, code: str) -> int:
        """Calculate maximum nesting depth"""
        lines = code.split('\n')
        max_depth = 0
        current_depth = 0
        
        for line in lines:
            stripped = line.lstrip()
            if stripped and not stripped.startswith('#'):
                # Calculate indentation level
                indent_level = (len(line) - len(stripped)) // 4
                max_depth = max(max_depth, indent_level)
        
        return max_depth
    
    def generate_risk_score(self, semgrep_results: List[Dict], ai_predictions: List[Dict]) -> float:
        """Generate overall risk score"""
        semgrep_score = len([r for r in semgrep_results if r.get('extra', {}).get('severity') == 'ERROR']) * 0.3
        semgrep_score += len([r for r in semgrep_results if r.get('extra', {}).get('severity') == 'WARNING']) * 0.2
        semgrep_score += len([r for r in semgrep_results if r.get('extra', {}).get('severity') == 'INFO']) * 0.1
        
        ai_score = sum([p['severity'] * p['confidence'] for p in ai_predictions])
        
        total_score = (semgrep_score + ai_score) / 10  # Normalize to 0-1 scale
        return min(total_score, 1.0)
