"""
Add missing cities from scrape to config with manual population data
"""

import json
from pathlib import Path

# Manual population data for all Brazilian cities in our scrape
POPULATION_DATA = {
    'Salvador': 2355039,
    'Brasília': 3034235,
    'Curitiba': 1948626,
    'Sinop': 129753,
    'Santana': 28645,
    'Camaçari': 252051,
    'Barreiras': 158292,
    'Uberlândia': 716840,
    'Preto': 364254,  # Rio Preto
    'Lorena': 82716,
    'Bebedouro': 71503,
    'Leopoldo': 82244,  # São Leopoldo
    'Janeiro': 6748000,  # Rio de Janeiro
    'Mossoró': 288390,
    'Seguro': 45675,  # Caratinga/area (estimate)
    'Nilópolis': 159460,
    'Goiás': 138675,
    'Bauru': 372601,
    'Cachoeirinha': 128020,
    'Paulo': 11451245,  # São Paulo
    'Joviânia': 6000,  # Small city
    'Jacarepaguá': 600000,  # District of Rio
    'Minas': 432000,  # Estimate for Minas Gerais region
    'Natal': 884122,
    'Extremoz': 18643,
    'Pessoa': 809051,  # João Pessoa
    'Campinas': 1213792,
    'José': 268847,  # São José
    'Florianópolis': 492977,
    'Odessa': 6000,  # Small city
    'Matão': 78651,
}

# Load current scraped data
searches_file = Path("data/searches_with_group_ids.json")
with open(searches_file, 'r', encoding='utf-8') as f:
    searches = json.load(f)

# Extract actual cities from scrape
cities_in_scrape = {}
for search in searches:
    city = search.get('city')
    state = search.get('state')
    if city and state:
        cities_in_scrape[city] = state

print(f"Found {len(cities_in_scrape)} cities in scrape\n")

# Build config dictionary
config_dict = {}
for city, state in sorted(cities_in_scrape.items()):
    pop = POPULATION_DATA.get(city, 0)
    config_dict[city] = pop
    if pop > 0:
        print(f"[OK] {city}: {pop:,}")
    else:
        print(f"[?] {city}: 0 (ESTIMATE NEEDED)")

# Update config.py
config_file = Path("config.py")
with open(config_file, 'r', encoding='utf-8') as f:
    config_content = f.read()

# Build new CITY_POPULATION dictionary
dict_lines = ["CITY_POPULATION = {"]
for city in sorted(config_dict.keys()):
    pop = config_dict[city]
    dict_lines.append(f"    '{city}': {pop},")
dict_lines.append("}")
new_dict_str = "\n".join(dict_lines)

# Replace in config
import re
new_config = re.sub(
    r"CITY_POPULATION = \{[^}]*\}",
    new_dict_str,
    config_content,
    flags=re.DOTALL
)

with open(config_file, 'w', encoding='utf-8') as f:
    f.write(new_config)

print(f"\n[OK] Updated config.py with all {len(config_dict)} cities")
