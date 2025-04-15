# config.py
import os

# Diretório base do projeto (pasta raiz)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Diretório onde o dataset será salvo
OUTPUT_DIR = os.path.join(BASE_DIR, "dataset")

# URLs para scraping
# Substitua pelo site real que você vai usar
SITE1_URL = "https://www.exemplo-site-plantas.com"
SITE1_DISEASE_LIST_URL = "https://www.exemplo-site-plantas.com/doencas-plantas"

# Configurações de delay entre requisições (em segundos)
MIN_DELAY = 1.0
MAX_DELAY = 3.0

# Número máximo de itens para extrair (0 = sem limite)
MAX_ITEMS = 0