# main.py
import os
from scrapers.scraper_site1 import PlantDiseaseScraper
import config

def main():
    # Inicializar e executar o scraper
    scraper = PlantDiseaseScraper(
        base_url=config.SITE1_URL,
        output_dir=config.OUTPUT_DIR
    )
    
    # Iniciar o scraping da página de lista de doenças
    scraper.scrape_disease_list(config.SITE1_DISEASE_LIST_URL)
    
    # Salvar metadados
    scraper.save_metadata()
    
    print("Scraping concluído! Dataset criado em:", config.OUTPUT_DIR)

if __name__ == "__main__":
    main()