"""
Configuration for Leiloaria Facebook Groups Automation
"""

from pathlib import Path
import json

# Base paths
LEILOARIA_DIR = Path(r"C:\Users\andre\Desktop\Leiloaria")
GRUPO_DIR = LEILOARIA_DIR / "Grupo"
POST_DIR = LEILOARIA_DIR / "Post"
OUTPUT_DIR = GRUPO_DIR / "output"
TEMP_DIR = GRUPO_DIR / ".temp"
DATA_DIR = GRUPO_DIR / "data"

# Create directories if they don't exist
for directory in [OUTPUT_DIR, TEMP_DIR, DATA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# File paths for intermediate outputs
BUILD_SCRIPT = DATA_DIR / "build_grupos_fb.py"
UNIQUE_IDS_JSON = DATA_DIR / "unique_group_ids.json"
GROUP_NAMES_JSON = DATA_DIR / "group_names.json"
FINAL_EXCEL = OUTPUT_DIR / "Leiloaria_Smart_Grupos_Facebook_COMPLETO.xlsx"
PROPERTIES_EXCEL = OUTPUT_DIR / "propriedades_scrapeadas.xlsx"

# Population data (IBGE 2022 - can be extended)
CITY_POPULATION = {
    'Barreiras': 158292,
    'Bauru': 372601,
    'Bebedouro': 71503,
    'Brasília': 3034235,
    'Cachoeirinha': 128020,
    'Camaçari': 252051,
    'Campinas': 1213792,
    'Curitiba': 1948626,
    'Extremoz': 18643,
    'Florianópolis': 492977,
    'Goiás': 138675,
    'Jacarepaguá': 600000,
    'Rio de Janeiro': 6748000,  # Was: Janeiro
    'São José': 268847,  # Was: José
    'Joviânia': 6000,
    'São Leopoldo': 82244,  # Was: Leopoldo
    'Lorena': 82716,
    'Matão': 78651,
    'Belo Horizonte': 432000,  # Was: Minas
    'Mossoró': 288390,
    'Natal': 884122,
    'Nilópolis': 159460,
    'Odessa': 6000,
    'São Paulo': 11451245,  # Was: Paulo
    'João Pessoa': 809051,  # Was: Pessoa
    'Salvador': 2355039,
    'Santana': 28645,
    'Seguro': 45675,
    'Sinop': 129753,
    'Uberlândia': 716840,
}

# Bairro population estimates (when available)
BAIRRO_POPULATION = {
    'Amaralina': 120000,  # Salvador bairro estimate
    'Federação': 95000,  # Salvador bairro estimate
    'Ondina': 110000,  # Salvador bairro estimate
    'Pituaçu': 105000,  # Salvador bairro estimate
    'Tocantins I': 85000,  # Uberlândia bairro estimate
    'Caonze': 60000,  # Rio de Janeiro area estimate
}

# Large cities threshold for search type
LARGE_CITY_THRESHOLD = 500000

# Google search configuration
GOOGLE_SEARCH_PATTERNS = [
    'site:facebook.com/groups imoveis "{search_term}"',
    'site:facebook.com/groups imoveis {search_term}',
]

# File paths for scraper integration
SCRAPER_OUTPUT = POST_DIR / "output"

# Playwright configuration for group name navigation
BROWSER_BATCH_SIZE = 4  # Number of parallel tabs
SAVE_INTERVAL = 10  # Save group_names.json every N rounds
RETRY_ATTEMPTS = 2  # Retry private groups this many times

# Logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Excel configuration
EXCEL_COLUMNS = {
    'grupos_facebook': [
        'Busca', 'Cidade', 'Tipo', 'ID', 'URL', 'Nome do Grupo', 'Habitantes'
    ],
    'resumo_busca': [
        'Busca', 'Cidade', 'Tipo', 'Qtd. Grupos', 'Habitantes'
    ]
}
