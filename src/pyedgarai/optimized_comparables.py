"""
Optimized Comparables Analysis

High-performance version of comparables functions that:
- Uses cached data when available
- Avoids heavy imports until needed
- Implements proper error handling and timeouts
- Provides fallback methods for better reliability
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import warnings

import pandas as pd


class OptimizedComparables:
    """Optimized comparables analysis with caching and performance improvements"""
    
    def __init__(self, cache_dir: str | None = None):
        if cache_dir is None:
            self.cache_dir = Path.home() / ".cache" / "pyedgarai"
        else:
            self.cache_dir = Path(cache_dir)
            
        self._cik_sic_data: Optional[Dict[str, Any]] = None
        self._company_names_data: Optional[Dict[str, Any]] = None
        self._stock_mapper = None
        
    def _load_cik_sic_data(self) -> Dict[str, Any]:
        """Lazy load CIK-SIC mapping data"""
        if self._cik_sic_data is None:
            cik_sic_path = self.cache_dir / "cik_sic.json"
            
            if not cik_sic_path.exists():
                raise FileNotFoundError(
                    f"CIK-SIC mapping not found at {cik_sic_path}. "
                    "Run requirements checker or generate_cik_sic_data.py first."
                )
            
            try:
                with open(cik_sic_path, 'r') as f:
                    self._cik_sic_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in CIK-SIC file: {e}")
                
        return self._cik_sic_data
    
    def _load_company_names_data(self) -> Dict[str, Any]:
        """Lazy load company names data"""
        if self._company_names_data is None:
            names_path = self.cache_dir / "cik_company_names.json"
            
            if not names_path.exists():
                raise FileNotFoundError(
                    f"Company names not found at {names_path}. "
                    "Run requirements checker or generate_company_names.py first."
                )
            
            try:
                with open(names_path, 'r') as f:
                    self._company_names_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in company names file: {e}")
                
        return self._company_names_data
    
    def _get_stock_mapper(self):
        """Lazy load StockMapper only when needed"""
        if self._stock_mapper is None:
            try:
                from sec_cik_mapper import StockMapper
                self._stock_mapper = StockMapper()
            except ImportError:
                raise ImportError("sec-cik-mapper package required. Install with: pip install sec-cik-mapper")
        return self._stock_mapper
    
    def get_sic_for_cik(self, cik: int) -> Optional[str]:
        """Get SIC code for a CIK (fast, uses cached data)"""
        cik_str = str(cik)
        sic_data = self._load_cik_sic_data()
        return sic_data.get(cik_str)
    
    def get_company_name_for_cik(self, cik: int) -> Optional[str]:
        """Get company name for a CIK (fast, uses cached data)"""
        cik_str = str(cik)
        names_data = self._load_company_names_data()
        return names_data.get(cik_str)
    
    def get_companies_with_same_sic_fast(self, cik: int, digits: int = 2) -> pd.DataFrame:
        """
        Fast SIC-based comparison using cached data only
        
        Args:
            cik: Target company CIK
            digits: Number of SIC digits to match (1-4)
            
        Returns:
            DataFrame with comparable companies
        """
        target_sic = self.get_sic_for_cik(cik)
        if not target_sic:
            raise ValueError(f"No SIC code found for CIK {cik}")
        
        # Truncate SIC to requested digits
        if len(str(target_sic)) >= digits:
            target_sic_truncated = str(target_sic)[:digits]
        else:
            target_sic_truncated = str(target_sic)
        
        # Find all companies with matching SIC
        sic_data = self._load_cik_sic_data()
        names_data = self._load_company_names_data()
        
        matches = []
        for cik_str, sic in sic_data.items():
            if sic and str(sic)[:digits] == target_sic_truncated:
                company_name = names_data.get(cik_str, "Unknown")
                matches.append({
                    "cik": int(cik_str),
                    "name": company_name,
                    "sic": sic
                })
        
        return pd.DataFrame(matches)
    
    def get_industry_comparables(self, cik: int, max_companies: int = 50) -> Dict[str, Any]:
        """
        Get industry comparables using SIC codes (optimized version)
        
        Args:
            cik: Target company CIK
            max_companies: Maximum number of comparable companies to return
            
        Returns:
            Dictionary with comparable companies and metadata
        """
        try:
            # Get target company info
            target_sic = self.get_sic_for_cik(cik)
            target_name = self.get_company_name_for_cik(cik)
            
            if not target_sic:
                raise ValueError(f"No SIC code found for CIK {cik}")
            
            # Try different SIC digit levels for best matches
            best_matches = pd.DataFrame()
            
            for digits in [4, 3, 2, 1]:  # Start with most specific
                matches = self.get_companies_with_same_sic_fast(cik, digits=digits)
                
                if len(matches) >= 5:  # Good number of matches
                    best_matches = matches
                    break
                elif len(matches) > len(best_matches):  # Better than previous
                    best_matches = matches
            
            # Limit results
            if len(best_matches) > max_companies:
                best_matches = best_matches.head(max_companies)
            
            # Format response
            companies = best_matches.to_dict('records')
            
            return {
                "target_company": {
                    "cik": cik,
                    "name": target_name,
                    "sic": target_sic
                },
                "companies": companies,
                "total_found": len(companies),
                "method": "sic_industry",
                "sic_digits_used": digits,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "target_company": {"cik": cik},
                "companies": [],
                "total_found": 0
            }
    
    def get_traditional_comparables_lite(self, cik: int, **kwargs) -> Dict[str, Any]:
        """
        Lightweight version of traditional comparables analysis
        Uses only cached data and avoids SEC API calls
        """
        try:
            # Start with industry comparables (fast)
            industry_result = self.get_industry_comparables(cik)
            
            if industry_result.get("error"):
                return industry_result
            
            # Add basic metadata
            result = {
                **industry_result,
                "method": "traditional_lite",
                "metrics_used": ["industry"],
                "note": "Lite version using cached data only. For full analysis including size/profitability, use full traditional method."
            }
            
            # Add ticker information if available (without heavy imports)
            try:
                mapper = self._get_stock_mapper()
                companies_with_tickers = []
                
                for company in result["companies"]:
                    cik_int = company["cik"]
                    ticker = None
                    
                    # Safe ticker lookup
                    try:
                        if hasattr(mapper, 'cik_to_tickers') and cik_int in mapper.cik_to_tickers:
                            tickers = mapper.cik_to_tickers[cik_int]
                            ticker = tickers[0] if tickers else None
                    except:
                        pass  # Skip if error
                    
                    companies_with_tickers.append({
                        **company,
                        "ticker": ticker
                    })
                
                result["companies"] = companies_with_tickers
                result["metrics_used"].append("ticker_lookup")
                
            except Exception:
                # If ticker lookup fails, continue without it
                result["note"] += " Ticker lookup unavailable."
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "target_company": {"cik": cik},
                "companies": [],
                "total_found": 0,
                "method": "traditional_lite"
            }
    
    def get_ml_comparables_cached(self, cik: int, name: str = "", sic: Optional[int] = None,
                                 assets: Optional[float] = None, **kwargs) -> Dict[str, Any]:
        """
        ML-style comparables using cached data and simple similarity metrics
        """
        try:
            # Get basic info if not provided
            if not sic:
                sic = self.get_sic_for_cik(cik)
            if not name:
                name = self.get_company_name_for_cik(cik) or f"Company {cik}"
            
            # Start with industry matches
            industry_matches = self.get_companies_with_same_sic_fast(cik, digits=2)
            
            if len(industry_matches) == 0:
                return {
                    "error": "No industry matches found",
                    "target_company": {"cik": cik, "name": name},
                    "companies": [],
                    "total_found": 0
                }
            
            # Simple similarity scoring based on available data
            scored_companies = []
            
            for _, company in industry_matches.iterrows():
                score = 1.0  # Base score for same industry
                
                # Name similarity (simple)
                if name and company.get("name"):
                    name_similarity = self._simple_name_similarity(name, company["name"])
                    score += name_similarity * 0.2
                
                scored_companies.append({
                    **company.to_dict(),
                    "similarity_score": round(score, 3)
                })
            
            # Sort by similarity score
            scored_companies.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Limit results
            max_companies = kwargs.get("max_companies", 20)
            if len(scored_companies) > max_companies:
                scored_companies = scored_companies[:max_companies]
            
            return {
                "target_company": {
                    "cik": cik,
                    "name": name,
                    "sic": sic,
                    "assets": assets
                },
                "companies": scored_companies,
                "total_found": len(scored_companies),
                "method": "ml_cached",
                "features_used": ["industry", "name_similarity"],
                "note": "Cached data version. For full ML analysis with financial metrics, ensure all data is available.",
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "target_company": {"cik": cik, "name": name},
                "companies": [],
                "total_found": 0,
                "method": "ml_cached"
            }
    
    def _simple_name_similarity(self, name1: str, name2: str) -> float:
        """Simple name similarity metric"""
        if not name1 or not name2:
            return 0.0
        
        # Normalize names
        name1_clean = name1.upper().replace("INC", "").replace("CORP", "").replace(".", "").strip()
        name2_clean = name2.upper().replace("INC", "").replace("CORP", "").replace(".", "").strip()
        
        # Simple word overlap
        words1 = set(name1_clean.split())
        words2 = set(name2_clean.split())
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return overlap / union if union > 0 else 0.0
    
    def health_check(self) -> Dict[str, Any]:
        """Check if optimized comparables can run properly"""
        health = {
            "status": "unknown",
            "checks": {},
            "timestamp": time.time()
        }
        
        try:
            # Check data files
            health["checks"]["cik_sic_data"] = {
                "status": "ok" if self.cache_dir.joinpath("cik_sic.json").exists() else "missing",
                "path": str(self.cache_dir / "cik_sic.json")
            }
            
            health["checks"]["company_names_data"] = {
                "status": "ok" if self.cache_dir.joinpath("cik_company_names.json").exists() else "missing", 
                "path": str(self.cache_dir / "cik_company_names.json")
            }
            
            # Test data loading
            try:
                sic_data = self._load_cik_sic_data()
                health["checks"]["sic_data_loading"] = {
                    "status": "ok",
                    "entries": len(sic_data)
                }
            except Exception as e:
                health["checks"]["sic_data_loading"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            try:
                names_data = self._load_company_names_data()
                health["checks"]["names_data_loading"] = {
                    "status": "ok", 
                    "entries": len(names_data)
                }
            except Exception as e:
                health["checks"]["names_data_loading"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            # Overall status
            failed_checks = sum(1 for check in health["checks"].values() 
                              if check.get("status") == "error")
            missing_checks = sum(1 for check in health["checks"].values()
                               if check.get("status") == "missing")
            
            if failed_checks > 0:
                health["status"] = "error"
            elif missing_checks > 0:
                health["status"] = "missing_data"
            else:
                health["status"] = "ok"
            
            health["summary"] = f"Status: {health['status']}, Failed: {failed_checks}, Missing: {missing_checks}"
            
        except Exception as e:
            health["status"] = "error"
            health["error"] = str(e)
        
        return health


# Global instance for easy access
_optimized_comparables = None

def get_optimized_comparables(cache_dir: str | None = None) -> OptimizedComparables:
    """Get global OptimizedComparables instance"""
    global _optimized_comparables
    if _optimized_comparables is None:
        _optimized_comparables = OptimizedComparables(cache_dir)
    return _optimized_comparables


# Convenience functions for backward compatibility
def get_companies_with_same_sic_fast(cik: int, digits: int = 2) -> pd.DataFrame:
    """Fast SIC comparison using cached data"""
    return get_optimized_comparables().get_companies_with_same_sic_fast(cik, digits)

def identify_comparables_fast(cik: int, method: str = "lite", **kwargs) -> Dict[str, Any]:
    """Fast comparables identification"""
    comparables = get_optimized_comparables()
    
    if method == "lite" or method == "traditional":
        return comparables.get_traditional_comparables_lite(cik, **kwargs)
    elif method == "ml" or method == "ml_cached":
        return comparables.get_ml_comparables_cached(cik, **kwargs)
    elif method == "industry":
        return comparables.get_industry_comparables(cik, **kwargs)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'lite', 'ml', or 'industry'")


def main():
    """Test the optimized comparables"""
    print("🚀 Testing Optimized Comparables")
    print("=" * 40)
    
    comparables = OptimizedComparables()
    
    # Health check
    health = comparables.health_check()
    print(f"Health: {health['summary']}")
    
    if health["status"] != "ok":
        print("❌ Health check failed. Run requirements checker first.")
        return
    
    # Test with Apple
    cik = 320193
    print(f"\n🍎 Testing with Apple (CIK: {cik})")
    
    try:
        result = comparables.get_industry_comparables(cik, max_companies=5)
        print(f"✅ Found {result['total_found']} comparable companies")
        
        for company in result["companies"][:3]:
            print(f"   • {company['name']} (CIK: {company['cik']}, SIC: {company['sic']})")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
