import requests

NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def search_cve(keyword: str, limit: int = 5):
    """
    Search NVD CVE database using keyword.
    Returns top matches with CVE ID + description + CVSS if present.
    """

    params = {
        "keywordSearch": keyword,
        "resultsPerPage": limit,
    }

    try:
        r = requests.get(NVD_API, params=params, timeout=5)
        data = r.json()

        results = []

        for item in data.get("vulnerabilities", []):
            cve = item["cve"]
            cve_id = cve["id"]

            description = cve["descriptions"][0]["value"]

            cvss = None
            if "metrics" in cve:
                cvss_data = cve["metrics"].get("cvssMetricV31") or cve["metrics"].get("cvssMetricV30")
                if cvss_data:
                    cvss = cvss_data[0]["cvssData"]["baseScore"]

            cwe = None

            if "weaknesses" in cve:
                try:
                    cwe = cve["weaknesses"][0]["description"][0]["value"]
                except Exception:
                    pass

            if not cwe:
                try:
                    cwe = cve["problemtype"]["problemtype_data"][0]["description"][0]["value"]
                except Exception:
                    pass


            results.append({
                "cve_id": cve_id,
                "description": description,
                "cwe": cwe,
                "cvss": cvss
            })

        return results

    except Exception as e:
        return [{"error": str(e)}]


print(search_cve("XSS")[0])