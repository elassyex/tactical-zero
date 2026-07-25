"""Threat intelligence adapters: Shodan, VirusTotal, and OSINT feeds."""
import json, os, time
from typing import Dict, List, Optional
import requests


class ShodanIntel:
    """Shodan integration for attack surface expansion."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base = "https://api.shodan.io"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "TacticalZero-Framework/3.0"})

    def _get(self, endpoint: str, params: dict = None) -> dict:
        params = params or {}
        params["key"] = self.api_key
        try:
            r = self.session.get(f"{self.base}{endpoint}", params=params, timeout=30)
            if r.status_code == 200:
                return r.json()
            return {"error": f"HTTP {r.status_code}", "raw": r.text[:200]}
        except Exception as e:
            return {"error": str(e)}

    def search_domain(self, domain: str) -> Dict:
        data = self._get("/shodan/host/search", {"query": f"hostname:{domain}", "limit": 100})
        results = []
        for match in data.get("matches", [])[:100]:
            results.append({
                "ip": match.get("ip_str"),
                "port": match.get("port"),
                "org": match.get("org"),
                "asn": match.get("asn"),
                "hostnames": match.get("hostnames", []),
                "os": match.get("os"),
                "product": match.get("product"),
                "version": match.get("version"),
                "cpe": match.get("cpe", []),
                "vulns": list(match.get("vulns", {}).keys()) if match.get("vulns") else [],
                "http_title": match.get("http", {}).get("title", ""),
                "http_server": match.get("http", {}).get("server", ""),
                "location": match.get("location", {}),
                "ssl": bool(match.get("ssl")),
                "timestamp": match.get("timestamp"),
            })
        return {"total": data.get("total", 0), "matches": results}

    def search_ip(self, ip: str) -> Dict:
        return self._get(f"/shodan/host/{ip}")

    def search_org(self, domain: str) -> Dict:
        data = self._get("/shodan/host/search", {"query": f"org:{domain}", "limit": 50})
        return data

    def discover_services(self, domain: str) -> List[Dict]:
        results = []
        for query in [
            f"hostname:{domain}",
            f"ssl.cert.subject.CN:{domain}",
            f"http.title:{domain}",
        ]:
            data = self._get("/shodan/host/search", {"query": query, "limit": 50})
            for match in data.get("matches", []):
                results.append({
                    "ip": match.get("ip_str"),
                    "port": match.get("port"),
                    "product": match.get("product"),
                    "version": match.get("version"),
                    "vulns": list(match.get("vulns", {}).keys()) if match.get("vulns") else [],
                })
            time.sleep(1.2)  # Rate limit
        return results

    def export_for_recon(self, domain: str) -> Dict:
        host_data = self.search_domain(domain)
        services = []
        subdomains = set()
        vulns = set()
        for m in host_data.get("matches", []):
            subdomains.update(m.get("hostnames", []))
            vulns.update(m.get("vulns", []))
            services.append({
                "ip": m["ip"], "port": m["port"], "product": m.get("product"),
                "version": m.get("version"), "org": m.get("org"),
            })
        return {
            "subdomains": sorted(subdomains),
            "services": services,
            "vulnerabilities": sorted(vulns),
            "total_hosts": host_data.get("total", 0),
        }


class VirusTotalIntel:
    """VirusTotal integration for domain/IP intelligence."""
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base = "https://www.virustotal.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            "x-apikey": api_key,
            "User-Agent": "TacticalZero-Framework/3.0"
        })

    def _get(self, endpoint: str) -> dict:
        try:
            r = self.session.get(f"{self.base}{endpoint}", timeout=30)
            if r.status_code == 200:
                return r.json()
            return {"error": f"HTTP {r.status_code}", "raw": r.text[:200]}
        except Exception as e:
            return {"error": str(e)}

    def get_domain_report(self, domain: str) -> Dict:
        return self._get(f"/domains/{domain}")

    def get_ip_report(self, ip: str) -> Dict:
        return self._get(f"/ip_addresses/{ip}")

    def get_subdomains(self, domain: str) -> List[str]:
        data = self._get(f"/domains/{domain}/subdomains?limit=1000")
        subs = []
        for item in data.get("data", []):
            subs.append(item.get("id", ""))
        return subs

    def get_communicating_files(self, domain: str) -> List[Dict]:
        data = self._get(f"/domains/{domain}/communicating_files?limit=100")
        files = []
        for item in data.get("data", []):
            attr = item.get("attributes", {})
            files.append({
                "name": attr.get("meaningful_name", attr.get("names", [""])[0]),
                "type": attr.get("type_description"),
                "reputation": attr.get("reputation"),
                "sha256": item.get("id"),
            })
        return files

    def export_for_recon(self, domain: str) -> Dict:
        report = self.get_domain_report(domain)
        attr = report.get("data", {}).get("attributes", {})
        subs = self.get_subdomains(domain)
        return {
            "subdomains": subs,
            "last_dns_records": attr.get("last_dns_records", []),
            "popularity_ranks": attr.get("popularity_ranks", {}),
            "categories": attr.get("categories", {}),
            "total_votes": attr.get("total_votes", {}),
            "reputation": attr.get("reputation"),
            "whois": attr.get("whois", ""),
            "creation_date": attr.get("creation_date"),
        }


class ThreatIntelAggregator:
    """Aggregates multiple threat intelligence sources."""
    def __init__(self, shodan_key: str = "", vt_key: str = ""):
        self.shodan = ShodanIntel(shodan_key) if shodan_key else None
        self.vt = VirusTotalIntel(vt_key) if vt_key else None

    def gather(self, domain: str) -> Dict:
        intel = {"domain": domain, "sources": {}}
        if self.shodan:
            intel["sources"]["shodan"] = self.shodan.export_for_recon(domain)
        if self.vt:
            intel["sources"]["virustotal"] = self.vt.export_for_recon(domain)
        intel["all_subdomains"] = sorted(set(
            intel.get("sources", {}).get("shodan", {}).get("subdomains", []) +
            intel.get("sources", {}).get("virustotal", {}).get("subdomains", [])
        ))
        intel["target_priority"] = self._calculate_priority(intel)
        return intel

    def _calculate_priority(self, intel: Dict) -> Dict:
        score = 0
        reasons = []
        shodan = intel.get("sources", {}).get("shodan", {})
        if shodan.get("vulnerabilities"):
            score += len(shodan["vulnerabilities"]) * 10
            reasons.append(f"Shodan: {len(shodan['vulnerabilities'])} known CVEs")
        if shodan.get("total_hosts", 0) > 50:
            score += 5
            reasons.append("Large attack surface (50+ hosts)")
        services = shodan.get("services", [])
        old_tech = [s for s in services if s.get("version") and any(v in s["version"] for v in ["201", "2020", "1.0", "2.0", "2.2", "5.0", "6.0", "7.0"])]
        if old_tech:
            score += len(old_tech) * 3
            reasons.append(f"{len(old_tech)} potentially outdated services")
        vt = intel.get("sources", {}).get("virustotal", {})
        if vt.get("reputation", 0) < 0:
            score += abs(vt["reputation"]) * 2
            reasons.append("Negative VT reputation")
        return {"score": score, "reasons": reasons, "priority": "high" if score > 30 else "medium" if score > 10 else "low"}
