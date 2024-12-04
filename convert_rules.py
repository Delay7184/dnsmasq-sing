import os
import requests
import json

def fetch_rules(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def generate_sing_box_format(raw_rules):
    domain_suffix = []
    for line in raw_rules.splitlines():
        if line.startswith('#') or not line.strip():
            continue
        if line.startswith("server=/"):
            parts = line.split("/")
            if len(parts) > 2:
                domain_suffix.append(parts[1])
    domain_suffix = {"domain_suffix": domain_suffix}
    return {"rules": [domain_suffix],"version": 2}

def save_to_file(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    with open("./dnsmasq.txt", 'r') as dnsmasq_file:
        links = dnsmasq_file.read().splitlines()
    links = [l for l in links if l.strip() and not l.strip().startswith("#")]

    os.makedirs("rule", exist_ok=True)
    for link in links:
        print(f"Processing {link}...")
        raw_rules = fetch_rules(link)
        sing_box_data = generate_sing_box_format(raw_rules)
        file_name = os.path.join("rule", f"{os.path.splitext(os.path.basename(link))[0]}.json")
        save_to_file(sing_box_data, file_name)
        srs_path = file_name.replace(".json", ".srs")
        os.system(f"sing-box rule-set compile --output {srs_path} {file_name}")
        print(f"Saved to {srs_path}")

if __name__ == "__main__":
    main()
