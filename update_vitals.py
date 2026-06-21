#!/usr/bin/env python3
"""
Update the system vitals section of the ax-portfolio index.html
with live data from the host machine.
"""
import re
import subprocess
import json
from pathlib import Path

PORTFOLIO = Path("/home/hash/projects/ax-portfolio/index.html")

def get_vitals() -> dict:
    # Disk free %
    disk_used = int(subprocess.check_output(
        ["df", "/", "--output=pcent"], text=True
    ).strip().split("\n")[-1].strip().rstrip("%"))
    disk = str(100 - disk_used)
    
    # Load average
    load = subprocess.check_output(["cat", "/proc/loadavg"], text=True).split()[0]
    
    # Temperature
    temp = "?"
    try:
        out = subprocess.check_output(
            ["sensors", "-j"], text=True, timeout=2
        )
        data = json.loads(out)
        for chip_name, chip in data.items():
            if chip_name == "Adapter" or not isinstance(chip, dict):
                continue
            for name, vals in chip.items():
                if not isinstance(vals, dict):
                    continue
                for k, v in vals.items():
                    if k.endswith("_input") and "temp" in k and isinstance(v, (int, float)) and v > 20:
                        temp = str(round(v))
                        break
                if temp != "?":
                    break
            if temp != "?":
                break
    except Exception:
        pass
    
    return {
        "disk": disk,
        "load": load,
        "temp": temp,
    }

def update_html(vitals: dict):
    html = PORTFOLIO.read_text()
    
    # Update disk free
    html = re.sub(
        r'(<div class="stat-value">)\d+(%</div>\s*\n\s*<div class="stat-label">Disk Free)',
        rf'\g<1>{vitals["disk"]}\2',
        html
    )
    
    # Update load avg
    html = re.sub(
        r'(<div class="stat-value">)[\d.]+(</div>\s*\n\s*<div class="stat-label">Load Avg)',
        rf'\g<1>{vitals["load"]}\2',
        html
    )
    
    # Update temp (match everything between stat-value and Temp C)
    html = re.sub(
        r'(<div class="stat-value">)[^<]+(</div>\s*\n\s*<div class="stat-label">Temp C)',
        rf'\g<1>{vitals["temp"]}°\2',
        html
    )
    
    PORTFOLIO.write_text(html)
    return vitals

if __name__ == "__main__":
    v = get_vitals()
    result = update_html(v)
    print(json.dumps(result))
