#!/usr/bin/env python3
"""
Comprehensive Test Suite for Optimized PyEdgarAI

Tests all components:
- Requirements checker
- Optimized comparables
- API server functionality
- Error handling and edge cases
"""

import sys
import time
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    import requests
    import json
    from pyedgarai.requirements_checker import RequirementsChecker
    from pyedgarai.optimized_comparables import OptimizedComparables, get_optimized_comparables
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the right directory and dependencies are installed")
    sys.exit(1)


class OptimizedSystemTester:
    """Comprehensive tester for the optimized PyEdgarAI system"""
    
    def __init__(self):
        self.results = {}
        self.api_base = "http://127.0.0.1:5001"
        
    def run_all_tests(self):
        """Run all tests and return results"""
        print("🧪 PyEdgarAI Optimized System Test Suite")
        print("=" * 60)
        
        # Test components in order
        self.test_requirements_checker()
        self.test_optimized_comparables()
        self.test_api_connectivity()
        self.test_optimized_api_endpoints()
        self.test_performance()
        self.test_error_handling()
        
        # Summary
        self._print_summary()
        return self.results
    
    def test_requirements_checker(self):
        """Test the requirements checker"""
        print("\n🔍 Testing Requirements Checker")
        print("-" * 40)
        
        try:
            checker = RequirementsChecker()
            results = checker.check_all()
            
            passed_checks = sum(1 for r in results.values() if r["status"] == "ok")
            total_checks = len(results)
            
            self.results["requirements_checker"] = {
                "status": "passed" if passed_checks >= total_checks * 0.8 else "failed",
                "passed_checks": f"{passed_checks}/{total_checks}",
                "details": results
            }
            
            print(f"✅ Requirements checker completed: {passed_checks}/{total_checks} passed")
            
        except Exception as e:
            print(f"❌ Requirements checker error: {e}")
            self.results["requirements_checker"] = {
                "status": "error",
                "error": str(e)
            }
    
    def test_optimized_comparables(self):
        """Test optimized comparables functionality"""
        print("\n⚡ Testing Optimized Comparables")
        print("-" * 40)
        
        try:
            comparables = OptimizedComparables()
            
            # Health check
            health = comparables.health_check()
            print(f"🏥 Health check: {health['status']}")
            
            if health["status"] != "ok":
                print("⚠️  Health issues detected, continuing with limited tests...")
            
            # Test data loading
            test_results = {}
            
            try:
                # Test SIC data
                apple_sic = comparables.get_sic_for_cik(320193)
                test_results["sic_lookup"] = {"status": "ok", "apple_sic": apple_sic}
                print(f"✅ SIC lookup: Apple SIC = {apple_sic}")
            except Exception as e:
                test_results["sic_lookup"] = {"status": "error", "error": str(e)}
                print(f"❌ SIC lookup failed: {e}")
            
            try:
                # Test company names
                apple_name = comparables.get_company_name_for_cik(320193)
                test_results["name_lookup"] = {"status": "ok", "apple_name": apple_name}
                print(f"✅ Name lookup: {apple_name}")
            except Exception as e:
                test_results["name_lookup"] = {"status": "error", "error": str(e)}
                print(f"❌ Name lookup failed: {e}")
            
            try:
                # Test fast SIC comparison
                sic_matches = comparables.get_companies_with_same_sic_fast(320193, digits=2)
                test_results["sic_comparison"] = {
                    "status": "ok", 
                    "matches_found": len(sic_matches)
                }
                print(f"✅ SIC comparison: {len(sic_matches)} matches found")
            except Exception as e:
                test_results["sic_comparison"] = {"status": "error", "error": str(e)}
                print(f"❌ SIC comparison failed: {e}")
            
            try:
                # Test industry comparables
                industry_result = comparables.get_industry_comparables(320193, max_companies=5)
                test_results["industry_comparables"] = {
                    "status": "ok" if not industry_result.get("error") else "error",
                    "companies_found": industry_result.get("total_found", 0)
                }
                print(f"✅ Industry comparables: {industry_result.get('total_found', 0)} companies")
            except Exception as e:
                test_results["industry_comparables"] = {"status": "error", "error": str(e)}
                print(f"❌ Industry comparables failed: {e}")
            
            self.results["optimized_comparables"] = {
                "status": "passed" if all(t.get("status") == "ok" for t in test_results.values()) else "partial",
                "tests": test_results,
                "health": health
            }
            
        except Exception as e:
            print(f"❌ Optimized comparables error: {e}")
            self.results["optimized_comparables"] = {
                "status": "error",
                "error": str(e)
            }
    
    def test_api_connectivity(self):
        """Test API server connectivity"""
        print("\n🌐 Testing API Connectivity")
        print("-" * 40)
        
        try:
            # Test basic connection
            response = requests.get(f"{self.api_base}/api", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API connected - Version: {data.get('version', 'unknown')}")
                
                # Test health endpoint
                health_response = requests.get(f"{self.api_base}/health", timeout=5)
                health_status = "ok" if health_response.status_code == 200 else "error"
                print(f"✅ Health endpoint: {health_status}")
                
                self.results["api_connectivity"] = {
                    "status": "passed",
                    "version": data.get("version"),
                    "health_status": health_status
                }
            else:
                print(f"❌ API error: HTTP {response.status_code}")
                self.results["api_connectivity"] = {
                    "status": "failed",
                    "http_status": response.status_code
                }
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server")
            print("💡 Start the optimized server: python -m src.pyedgarai.api.optimized_server")
            self.results["api_connectivity"] = {
                "status": "failed",
                "error": "Connection refused"
            }
        except Exception as e:
            print(f"❌ API connectivity error: {e}")
            self.results["api_connectivity"] = {
                "status": "error", 
                "error": str(e)
            }
    
    def test_optimized_api_endpoints(self):
        """Test optimized API endpoints"""
        print("\n🚀 Testing Optimized API Endpoints")
        print("-" * 40)
        
        if self.results.get("api_connectivity", {}).get("status") != "passed":
            print("⏭️  Skipping API tests (no connectivity)")
            self.results["api_endpoints"] = {"status": "skipped", "reason": "No API connectivity"}
            return
        
        endpoints_to_test = [
            {
                "name": "Fast Comparables",
                "url": "/comparables_fast",
                "params": {"cik": 320193, "max_companies": 5, "api_token": ""},
                "timeout": 10
            },
            {
                "name": "SIC Comparables", 
                "url": "/comparables_sic",
                "params": {"cik": 320193, "digits": 2, "api_token": ""},
                "timeout": 5
            },
            {
                "name": "Lite Comparables",
                "url": "/comparables_lite", 
                "params": {"cik": 320193, "max_companies": 3, "api_token": ""},
                "timeout": 15
            }
        ]
        
        endpoint_results = {}
        
        for endpoint in endpoints_to_test:
            print(f"🧪 Testing {endpoint['name']}...")
            
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.api_base}{endpoint['url']}",
                    params=endpoint["params"],
                    timeout=endpoint["timeout"]
                )
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    companies_found = data.get("total_found", 0)
                    
                    print(f"   ✅ {companies_found} companies in {response_time:.2f}s")
                    endpoint_results[endpoint["name"]] = {
                        "status": "passed",
                        "companies_found": companies_found,
                        "response_time": response_time
                    }
                else:
                    print(f"   ❌ HTTP {response.status_code}")
                    endpoint_results[endpoint["name"]] = {
                        "status": "failed",
                        "http_status": response.status_code,
                        "response": response.text[:200]
                    }
                    
            except requests.exceptions.Timeout:
                print(f"   ❌ Timeout ({endpoint['timeout']}s)")
                endpoint_results[endpoint["name"]] = {
                    "status": "timeout",
                    "timeout": endpoint["timeout"]
                }
            except Exception as e:
                print(f"   ❌ Error: {e}")
                endpoint_results[endpoint["name"]] = {
                    "status": "error",
                    "error": str(e)
                }
        
        passed_endpoints = sum(1 for r in endpoint_results.values() if r["status"] == "passed")
        total_endpoints = len(endpoint_results)
        
        self.results["api_endpoints"] = {
            "status": "passed" if passed_endpoints == total_endpoints else "partial",
            "passed": f"{passed_endpoints}/{total_endpoints}",
            "endpoints": endpoint_results
        }
    
    def test_performance(self):
        """Test performance of optimized functions"""
        print("\n⚡ Testing Performance")
        print("-" * 40)
        
        if self.results.get("api_connectivity", {}).get("status") != "passed":
            print("⏭️  Skipping performance tests (no API)")
            self.results["performance"] = {"status": "skipped"}
            return
        
        performance_results = {}
        
        # Test fast SIC endpoint
        try:
            print("🚀 Testing SIC endpoint speed...")
            start_time = time.time()
            
            response = requests.get(
                f"{self.api_base}/comparables_sic",
                params={"cik": 320193, "digits": 2, "api_token": ""},
                timeout=5
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                companies_found = data.get("total_found", 0)
                
                print(f"✅ SIC endpoint: {companies_found} companies in {response_time:.3f}s")
                performance_results["sic_endpoint"] = {
                    "response_time": response_time,
                    "companies_found": companies_found,
                    "status": "fast" if response_time < 2.0 else "slow"
                }
            else:
                performance_results["sic_endpoint"] = {"status": "failed"}
                
        except Exception as e:
            performance_results["sic_endpoint"] = {"status": "error", "error": str(e)}
        
        # Test multiple rapid requests
        try:
            print("🔄 Testing rapid requests...")
            request_times = []
            
            for i in range(3):
                start_time = time.time()
                response = requests.get(
                    f"{self.api_base}/health",
                    timeout=2
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    request_times.append(end_time - start_time)
            
            if request_times:
                avg_time = sum(request_times) / len(request_times)
                print(f"✅ Average response time: {avg_time:.3f}s")
                performance_results["rapid_requests"] = {
                    "average_time": avg_time,
                    "requests": len(request_times),
                    "status": "fast" if avg_time < 1.0 else "slow"
                }
                
        except Exception as e:
            performance_results["rapid_requests"] = {"status": "error", "error": str(e)}
        
        self.results["performance"] = {
            "status": "completed",
            "tests": performance_results
        }
    
    def test_error_handling(self):
        """Test error handling with invalid inputs"""
        print("\n🛡️  Testing Error Handling")
        print("-" * 40)
        
        if self.results.get("api_connectivity", {}).get("status") != "passed":
            print("⏭️  Skipping error tests (no API)")
            self.results["error_handling"] = {"status": "skipped"}
            return
        
        error_test_cases = [
            {
                "name": "Invalid CIK",
                "url": "/comparables_sic",
                "params": {"cik": 999999999, "digits": 2, "api_token": ""},
                "expected": "error_response"
            },
            {
                "name": "Invalid SIC digits",
                "url": "/comparables_sic", 
                "params": {"cik": 320193, "digits": 10, "api_token": ""},
                "expected": "error_response"
            },
            {
                "name": "Missing CIK",
                "url": "/comparables_fast",
                "params": {"api_token": ""},
                "expected": "validation_error"
            }
        ]
        
        error_results = {}
        
        for test_case in error_test_cases:
            print(f"🧪 Testing {test_case['name']}...")
            
            try:
                response = requests.get(
                    f"{self.api_base}{test_case['url']}",
                    params=test_case["params"],
                    timeout=5
                )
                
                # We expect errors, so 400-500 status codes are good
                if 400 <= response.status_code <= 500:
                    print(f"   ✅ Properly handled with HTTP {response.status_code}")
                    error_results[test_case["name"]] = {
                        "status": "passed",
                        "http_status": response.status_code
                    }
                else:
                    print(f"   ⚠️  Unexpected status: {response.status_code}")
                    error_results[test_case["name"]] = {
                        "status": "unexpected",
                        "http_status": response.status_code
                    }
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                error_results[test_case["name"]] = {
                    "status": "error",
                    "error": str(e)
                }
        
        self.results["error_handling"] = {
            "status": "completed",
            "tests": error_results
        }
    
    def _print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_sections = len(self.results)
        passed_sections = sum(1 for r in self.results.values() 
                             if r.get("status") in ["passed", "completed"])
        
        print(f"🧪 Test Sections: {passed_sections}/{total_sections} passed")
        
        for section_name, result in self.results.items():
            status = result.get("status", "unknown")
            status_emoji = {
                "passed": "✅",
                "completed": "✅", 
                "partial": "⚠️",
                "failed": "❌",
                "error": "❌",
                "skipped": "⏭️"
            }.get(status, "❓")
            
            print(f"{status_emoji} {section_name.replace('_', ' ').title()}: {status}")
        
        # Overall assessment
        critical_failures = sum(1 for r in self.results.values() 
                               if r.get("status") in ["failed", "error"])
        
        if critical_failures == 0:
            print(f"\n🎉 All critical tests passed! Optimized PyEdgarAI is ready to use.")
        elif critical_failures <= 2:
            print(f"\n⚠️  {critical_failures} issues found, but system is mostly functional.")
        else:
            print(f"\n❌ {critical_failures} critical issues found. Review and fix before use.")
        
        print(f"\n💡 Run individual components if needed:")
        print(f"   • Requirements: python -m pyedgarai.requirements_checker")
        print(f"   • Optimized Server: python -m pyedgarai.api.optimized_server")


def main():
    """Run the comprehensive test suite"""
    tester = OptimizedSystemTester()
    results = tester.run_all_tests()
    
    # Save results for reference
    try:
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Results saved to: test_results.json")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")
    
    return results


if __name__ == "__main__":
    main()
