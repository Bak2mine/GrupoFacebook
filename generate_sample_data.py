"""
Generate realistic sample data for testing
Based on pilot project: 258 unique groups from 43 cities
Fixed: Unique IDs, correct city association, proper population data
"""

import json
from pathlib import Path

# Real cities from properties found in Post folder
CITIES_DATA = {
    'Salvador': ('BA', 2355039),
    'São Paulo': ('SP', 11451245),
    'Rio de Janeiro': ('RJ', 6747430),
    'Brasília': ('DF', 3034235),
    'Curitiba': ('PR', 1948626),
    'Fortaleza': ('CE', 2703766),
    'Belo Horizonte': ('MG', 2338968),
    'Manaus': ('AM', 2219580),
    'Recife': ('PE', 1563471),
    'Porto Alegre': ('RS', 1437592),
    'Belém': ('PA', 1303481),
    'Goiânia': ('GO', 1516113),
    'Guarulhos': ('SP', 1378363),
    'Campinas': ('SP', 1213792),
    'São Gonçalo': ('RJ', 999728),
    'Maceió': ('AL', 1018948),
    'Duque de Caxias': ('RJ', 885238),
    'São Bernardo do Campo': ('SP', 844507),
    'Teresina': ('PI', 868075),
    'Natal': ('RN', 884122),
    'Campo Grande': ('MS', 874136),
    'São Luís': ('MA', 1108975),
    'Aracaju': ('SE', 571149),
    'João Pessoa': ('PB', 809051),
    'Jaboatão': ('PE', 653960),
    'Ananindeua': ('PA', 533254),
    'Santa Maria': ('RS', 283109),
    'Camaçari': ('BA', 252051),
    'Feira de Santana': ('BA', 612504),
    'Itabuna': ('BA', 406348),
    'Ilhéus': ('BA', 184236),
    'Barreiras': ('BA', 158292),
    'Santana': ('BA', 28645),
    'Sinop': ('MT', 129753),
    'Tangará da Serra': ('MT', 86559),
    'Cuiabá': ('MT', 612371),
    'Lorena': ('SP', 82716),
    'Cachoeirinha': ('RS', 128020),
    'Florianópolis': ('SC', 492977),
    'Uberlândia': ('MG', 716840),
    'Goiás': ('GO', 138675),
    'Mossoró': ('RN', 288390),
}

# Generate realistic group names for each city
GROUP_NAME_TEMPLATES = [
    "Grupo de Imóveis {city}",
    "Imóveis em {city} - {state}",
    "Compra e Venda de Imóveis {city}",
    "Leilões de Imóveis {city}",
    "Imóveis à Venda {city}",
    "Grupo Imobiliário {city}",
    "Imoveis {city} e Região",
    "Venda de Terrenos {city}",
    "Casas e Apartamentos {city}",
    "Leilão Imobiliário {city}",
    "Propriedades {city}",
    "Grupo de Casas {city}",
    "Apartamentos em {city}",
    "Terrenos {city}",
    "Imóvel Certo {city}",
]

def generate_sample_data():
    """Generate sample data mimicking the pilot project"""

    all_searches = []
    group_names = {}

    group_id_counter = 100000001  # Start from 100M, ensure unique per group

    for city, (state, population) in CITIES_DATA.items():
        search_term = f"{city} {state}"

        # Large cities get 5-12 groups, small cities get 2-6 groups
        if population > 1000000:
            num_groups = 12
        elif population > 500000:
            num_groups = 8
        elif population > 200000:
            num_groups = 5
        else:
            num_groups = 3

        group_ids_for_city = []

        for i in range(num_groups):
            group_id = str(group_id_counter)
            group_ids_for_city.append(group_id)

            # Generate realistic group name with city name
            template = GROUP_NAME_TEMPLATES[i % len(GROUP_NAME_TEMPLATES)]
            group_name = template.format(city=city, state=state)
            group_names[group_id] = group_name

            group_id_counter += 1

        # Create search entry with correct city and population
        search_entry = {
            "city": city,
            "state": state,
            "type": "city",
            "search_term": search_term,
            "group_ids": group_ids_for_city
        }
        all_searches.append(search_entry)

    print(f"Generated {len(all_searches)} searches")
    print(f"Generated {len(group_names)} unique groups")
    print(f"Group ID range: 100000001 to {group_id_counter - 1}")

    # Save searches
    searches_file = Path("data/searches_with_group_ids.json")
    with open(searches_file, 'w', encoding='utf-8') as f:
        json.dump(all_searches, f, ensure_ascii=False, indent=2)
    print(f"Saved searches to {searches_file}")

    # Save group names
    names_file = Path("data/group_names.json")
    with open(names_file, 'w', encoding='utf-8') as f:
        json.dump(group_names, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(group_names)} group names to {names_file}")

    # Verify data integrity
    print("\nData Integrity Check:")
    total_groups = sum(len(search['group_ids']) for search in all_searches)
    print(f"  Total groups in searches: {total_groups}")
    print(f"  Total groups in names dict: {len(group_names)}")
    print(f"  Match: {total_groups == len(group_names)}")

    # Check for duplicates
    all_ids = [gid for search in all_searches for gid in search['group_ids']]
    unique_ids = set(all_ids)
    print(f"  Duplicate IDs: {len(all_ids) - len(unique_ids)}")

    # Check population coverage
    total_pop = sum(city_data[1] for city_data in CITIES_DATA.values())
    print(f"  Total population covered: {total_pop:,}")

    return all_searches, group_names

if __name__ == '__main__':
    generate_sample_data()
