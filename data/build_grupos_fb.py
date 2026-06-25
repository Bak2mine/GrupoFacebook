"""
Generated search configuration for Facebook groups
Phase 2 output - DO NOT EDIT MANUALLY (regenerate with phase2_build_searches.py)
"""

# Search configuration - format: (search_term, city, type, [group_ids])
# group_ids will be filled by phase 3 (Google search)
SEARCHES = [
    {
        'search_term': "Salvador BA",
        'city': "Salvador",
        'state': "BA",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Uberlândia MG",
        'city': "Uberlândia",
        'state': "MG",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Brasília DF",
        'city': "Brasília",
        'state': "DF",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Janeiro RJ",
        'city': "Janeiro",
        'state': "RJ",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Paulo SP",
        'city': "Paulo",
        'state': "SP",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Jacarepaguá RJ",
        'city': "Jacarepaguá",
        'state': "RJ",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Natal RN",
        'city': "Natal",
        'state': "RN",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Curitiba PR",
        'city': "Curitiba",
        'state': "PR",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Pessoa PB",
        'city': "Pessoa",
        'state': "PB",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Campinas SP",
        'city': "Campinas",
        'state': "SP",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Santana BA",
        'city': "Santana",
        'state': "BA",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Camaçari BA",
        'city': "Camaçari",
        'state': "BA",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Barreiras BA",
        'city': "Barreiras",
        'state': "BA",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "José SC",
        'city': "José",
        'state': "SC",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Preto SP",
        'city': "Preto",
        'state': "SP",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Lorena SP",
        'city': "Lorena",
        'state': "SP",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Bebedouro SP",
        'city': "Bebedouro",
        'state': "SP",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Leopoldo RS",
        'city': "Leopoldo",
        'state': "RS",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Mossoró RN",
        'city': "Mossoró",
        'state': "RN",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Seguro BA",
        'city': "Seguro",
        'state': "BA",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Nilópolis RJ",
        'city': "Nilópolis",
        'state': "RJ",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Goiás GO",
        'city': "Goiás",
        'state': "GO",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Bauru SP",
        'city': "Bauru",
        'state': "SP",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Cachoeirinha RS",
        'city': "Cachoeirinha",
        'state': "RS",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Joviânia GO",
        'city': "Joviânia",
        'state': "GO",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Minas MG",
        'city': "Minas",
        'state': "MG",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Extremoz RN",
        'city': "Extremoz",
        'state': "RN",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Florianópolis SC",
        'city': "Florianópolis",
        'state': "SC",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Odessa SP",
        'city': "Odessa",
        'state': "SP",
        'type': "city",
        'group_ids': []
    },
    {
        'search_term': "Matão SP",
        'city': "Matão",
        'state': "SP",
        'type': "city",
        'group_ids': []
    },
]

def get_search_count():
    """Return total number of searches"""
    return len(SEARCHES)

def get_searches():
    """Return all searches"""
    return SEARCHES

def update_group_ids(search_index, group_ids):
    """Update group IDs for a specific search

    Args:
        search_index: Index in SEARCHES list
        group_ids: List of numeric Facebook group IDs
    """
    if 0 <= search_index < len(SEARCHES):
        SEARCHES[search_index]['group_ids'] = group_ids
