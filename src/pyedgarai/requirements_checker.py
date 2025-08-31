"""
PyEdgarAI Requirements Checker

This module validates all prerequisites before running the library to ensure
smooth operation and provide clear error messages for missing dependencies.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

import requests


class RequirementsChecker:
    """Comprehensive requirements and dependency checker for PyEdgarAI"""
    
    def __init__(self, cache_dir: str | None = None):
        if cache_dir is None:
            self.cache_dir = Path.home() / ".cache" / "pyedgarai"
        else:
            self.cache_dir = Path(cache_dir)
            
        self.results: Dict[str, Dict[str, Any]] = {}
        
    def check_all(self) -> Dict[str, Dict[str, Any]]:
        """Run all checks and return comprehensive results"""
        print("🔍 PyEdgarAI Requirements Checker")
        print("=" * 50)
        
        # Run all checks
        self.check_python_environment()
        self.check_required_packages()
        self.check_cache_directory()
        self.check_data_files()
        self.check_sec_api_access()
        self.check_api_server_requirements()
        
        # Summary
        self._print_summary()
        return self.results
    
    def check_python_environment(self) -> bool:
        """Check Python version and environment"""
        print("\n🐍 Python Environment")
        print("-" * 30)
        
        result = {
            "status": "unknown",
            "details": {},
            "issues": [],
            "recommendations": []
        }
        
        # Python version
        version = sys.version_info
        result["details"]["python_version"] = f"{version.major}.{version.minor}.{version.micro}"
        
        if version >= (3, 8):
            print(f"✅ Python {result['details']['python_version']} (compatible)")
            result["status"] = "ok"
        else:
            print(f"❌ Python {result['details']['python_version']} (requires 3.8+)")
            result["status"] = "error"
            result["issues"].append("Python version too old")
            result["recommendations"].append("Upgrade to Python 3.8 or higher")
        
        # Virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment detected")
            result["details"]["virtual_env"] = True
        else:
            print("⚠️  No virtual environment detected")
            result["details"]["virtual_env"] = False
            result["recommendations"].append("Consider using a virtual environment")
        
        self.results["python_environment"] = result
        return result["status"] == "ok"
    
    def check_required_packages(self) -> bool:
        """Check if all required packages are installed"""
        print("\n📦 Required Packages")
        print("-" * 30)
        
        required_packages = [
            "pandas",
            "requests", 
            "scikit-learn",
            "sec-cik-mapper",
            "flask",
            "flask-openapi3",
            "yfinance"
        ]
        
        result = {
            "status": "unknown",
            "details": {"packages": {}},
            "issues": [],
            "recommendations": []
        }
        
        all_installed = True
        
        for package in required_packages:
            try:
                if package == "flask-openapi3":
                    import flask_openapi3
                    version = getattr(flask_openapi3, '__version__', 'unknown')
                elif package == "sec-cik-mapper":
                    import sec_cik_mapper
                    version = getattr(sec_cik_mapper, '__version__', 'unknown')
                elif package == "scikit-learn":
                    import sklearn
                    version = getattr(sklearn, '__version__', 'unknown')
                else:
                    module = __import__(package.replace('-', '_'))
                    version = getattr(module, '__version__', 'unknown')
                
                print(f"✅ {package} ({version})")
                result["details"]["packages"][package] = {"installed": True, "version": version}
                
            except ImportError:
                print(f"❌ {package} (not installed)")
                result["details"]["packages"][package] = {"installed": False, "version": None}
                result["issues"].append(f"Missing package: {package}")
                all_installed = False
        
        if all_installed:
            result["status"] = "ok"
        else:
            result["status"] = "error"
            result["recommendations"].append("Install missing packages with: pip install pyedgarai[all]")
        
        self.results["required_packages"] = result
        return result["status"] == "ok"
    
    def check_cache_directory(self) -> bool:
        """Check cache directory setup"""
        print("\n📁 Cache Directory")
        print("-" * 30)
        
        result = {
            "status": "unknown", 
            "details": {"path": str(self.cache_dir)},
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Create if doesn't exist
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = self.cache_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            
            print(f"✅ Cache directory: {self.cache_dir}")
            print(f"✅ Write access confirmed")
            
            result["status"] = "ok"
            result["details"]["writable"] = True
            
        except PermissionError:
            print(f"❌ No write permission: {self.cache_dir}")
            result["status"] = "error"
            result["details"]["writable"] = False
            result["issues"].append("No write permission to cache directory")
            result["recommendations"].append("Check directory permissions or use different cache location")
            
        except Exception as e:
            print(f"❌ Cache directory error: {e}")
            result["status"] = "error"
            result["issues"].append(f"Cache directory error: {e}")
        
        self.results["cache_directory"] = result
        return result["status"] == "ok"
    
    def check_data_files(self) -> bool:
        """Check required data files"""
        print("\n📊 Data Files")
        print("-" * 30)
        
        required_files = {
            "cik_sic.json": "CIK to SIC code mapping",
            "cik_company_names.json": "CIK to company name mapping"
        }
        
        result = {
            "status": "unknown",
            "details": {"files": {}},
            "issues": [],
            "recommendations": []
        }
        
        all_files_ok = True
        
        for filename, description in required_files.items():
            file_path = self.cache_dir / filename
            file_info = {"path": str(file_path), "description": description}
            
            if file_path.exists():
                try:
                    # Test if file is valid JSON
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    file_size = file_path.stat().st_size
                    entry_count = len(data) if isinstance(data, dict) else "unknown"
                    
                    print(f"✅ {filename} ({entry_count} entries, {file_size:,} bytes)")
                    file_info.update({
                        "exists": True,
                        "valid": True,
                        "size": file_size,
                        "entries": entry_count
                    })
                    
                except json.JSONDecodeError:
                    print(f"❌ {filename} (invalid JSON)")
                    file_info.update({"exists": True, "valid": False})
                    result["issues"].append(f"Invalid JSON in {filename}")
                    all_files_ok = False
                    
                except Exception as e:
                    print(f"❌ {filename} (error: {e})")
                    file_info.update({"exists": True, "valid": False, "error": str(e)})
                    result["issues"].append(f"Error reading {filename}: {e}")
                    all_files_ok = False
            else:
                print(f"❌ {filename} (missing)")
                file_info.update({"exists": False, "valid": False})
                result["issues"].append(f"Missing file: {filename}")
                all_files_ok = False
            
            result["details"]["files"][filename] = file_info
        
        if all_files_ok:
            result["status"] = "ok"
        else:
            result["status"] = "error"
            result["recommendations"].append("Generate missing data files with: python generate_cik_sic_data.py")
            result["recommendations"].append("Generate missing data files with: python generate_company_names.py")
        
        self.results["data_files"] = result
        return result["status"] == "ok"
    
    def check_sec_api_access(self) -> bool:
        """Check SEC API connectivity"""
        print("\n🌐 SEC API Access")
        print("-" * 30)
        
        result = {
            "status": "unknown",
            "details": {},
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Test SEC API with proper headers
            headers = {
                "User-Agent": "Academic Research Tool - pyedgarai 0.8.0 - Contact: jfimbett@gmail.com"
            }
            
            # Test with a simple company facts request
            test_url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
            
            print("🔍 Testing SEC API connectivity...")
            response = requests.get(test_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("✅ SEC API accessible")
                result["status"] = "ok"
                result["details"]["api_accessible"] = True
                result["details"]["response_time"] = response.elapsed.total_seconds()
                
            elif response.status_code == 403:
                print("❌ SEC API blocked (User-Agent issue)")
                result["status"] = "error"
                result["details"]["api_accessible"] = False
                result["issues"].append("SEC API requires proper User-Agent header")
                result["recommendations"].append("Ensure User-Agent header includes contact information")
                
            else:
                print(f"⚠️  SEC API responded with status {response.status_code}")
                result["status"] = "warning"
                result["details"]["api_accessible"] = True
                result["details"]["status_code"] = response.status_code
                
        except requests.exceptions.Timeout:
            print("⚠️  SEC API request timed out")
            result["status"] = "warning"
            result["details"]["api_accessible"] = False
            result["issues"].append("SEC API timeout")
            result["recommendations"].append("Check internet connection")
            
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to SEC API")
            result["status"] = "error"
            result["details"]["api_accessible"] = False
            result["issues"].append("No internet connection or SEC API unavailable")
            result["recommendations"].append("Check internet connection")
            
        except Exception as e:
            print(f"❌ SEC API error: {e}")
            result["status"] = "error"
            result["details"]["api_accessible"] = False
            result["issues"].append(f"SEC API error: {e}")
        
        self.results["sec_api_access"] = result
        return result["status"] == "ok"
    
    def check_api_server_requirements(self) -> bool:
        """Check if API server can be started"""
        print("\n🚀 API Server Requirements")
        print("-" * 30)
        
        result = {
            "status": "unknown",
            "details": {},
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Check if port 5000 is available
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result_code = s.connect_ex(('127.0.0.1', 5000))
                
                if result_code == 0:
                    print("⚠️  Port 5000 already in use")
                    result["details"]["port_available"] = False
                    result["recommendations"].append("Stop existing service on port 5000 or use different port")
                else:
                    print("✅ Port 5000 available")
                    result["details"]["port_available"] = True
            
            # Check Flask imports
            try:
                from flask_openapi3 import APIBlueprint
                print("✅ Flask-OpenAPI3 imports working")
                result["details"]["flask_imports"] = True
                result["status"] = "ok"
                
            except ImportError as e:
                print(f"❌ Flask import error: {e}")
                result["details"]["flask_imports"] = False
                result["issues"].append(f"Flask import error: {e}")
                result["status"] = "error"
                
        except Exception as e:
            print(f"❌ API server check error: {e}")
            result["status"] = "error"
            result["issues"].append(f"API server check error: {e}")
        
        self.results["api_server"] = result
        return result["status"] == "ok"
    
    def _print_summary(self):
        """Print overall summary"""
        print("\n" + "=" * 50)
        print("📋 SUMMARY")
        print("=" * 50)
        
        total_checks = len(self.results)
        passed_checks = sum(1 for r in self.results.values() if r["status"] == "ok")
        warning_checks = sum(1 for r in self.results.values() if r["status"] == "warning")
        failed_checks = sum(1 for r in self.results.values() if r["status"] == "error")
        
        print(f"✅ Passed: {passed_checks}/{total_checks}")
        if warning_checks > 0:
            print(f"⚠️  Warnings: {warning_checks}")
        if failed_checks > 0:
            print(f"❌ Failed: {failed_checks}")
        
        # Show critical issues
        critical_issues = []
        for check_name, result in self.results.items():
            if result["status"] == "error":
                critical_issues.extend(result["issues"])
        
        if critical_issues:
            print(f"\n🚨 Critical Issues:")
            for issue in critical_issues[:5]:  # Show top 5
                print(f"   • {issue}")
        
        # Show recommendations  
        all_recommendations = []
        for result in self.results.values():
            all_recommendations.extend(result["recommendations"])
        
        if all_recommendations:
            print(f"\n💡 Recommendations:")
            for rec in list(set(all_recommendations))[:3]:  # Show top 3 unique
                print(f"   • {rec}")
        
        if failed_checks == 0:
            print(f"\n🎉 All systems ready! PyEdgarAI should work properly.")
        else:
            print(f"\n⚠️  {failed_checks} issues need to be resolved before using PyEdgarAI.")

    def generate_data_files(self) -> bool:
        """Generate missing data files"""
        print("\n🔧 Generating Missing Data Files")
        print("-" * 30)
        
        missing_files = []
        for filename, file_info in self.results.get("data_files", {}).get("details", {}).get("files", {}).items():
            if not file_info.get("exists", False) or not file_info.get("valid", False):
                missing_files.append(filename)
        
        if not missing_files:
            print("✅ All data files present and valid")
            return True
        
        print(f"📁 Missing files: {', '.join(missing_files)}")
        
        try:
            if "cik_sic.json" in missing_files:
                print("🏭 Generating CIK-SIC mapping...")
                from .features import cik_sic_table
                cik_sic_table()
                print("✅ CIK-SIC mapping generated")
            
            if "cik_company_names.json" in missing_files:
                print("🏢 Generating company names...")
                from .features import get_cik_company_names
                get_cik_company_names()
                print("✅ Company names generated")
            
            return True
            
        except Exception as e:
            print(f"❌ Error generating data files: {e}")
            return False


def main():
    """Run requirements check as standalone script"""
    checker = RequirementsChecker()
    results = checker.check_all()
    
    # Exit with error code if critical issues found
    failed_checks = sum(1 for r in results.values() if r["status"] == "error")
    sys.exit(failed_checks)


if __name__ == "__main__":
    main()
