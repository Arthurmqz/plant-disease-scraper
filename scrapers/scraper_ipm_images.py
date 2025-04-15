# scrapers/scraper_research.py
import os
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
from urllib.parse import urljoin, quote_plus
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import io
from PIL import Image
import base64
import hashlib

class ResearchScraper:
    def __init__(self, output_dir):
        """
        Inicializa o scraper para ResearchGate e SciELO
        
        Args:
            output_dir (str): Diretório onde os dados serão salvos
        """
        self.researchgate_base_url = "https://www.researchgate.net"
        self.scielo_base_url = "https://search.scielo.org"
        self.output_dir = output_dir
        self.image_dir = os.path.join(output_dir, "images", "research")
        self.description_dir = os.path.join(output_dir, "descriptions", "research")
        self.pdf_dir = os.path.join(output_dir, "pdfs")
        
        # Criar diretórios se não existirem
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.description_dir, exist_ok=True)
        os.makedirs(self.pdf_dir, exist_ok=True)
        
        # Headers para simular um navegador
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        # Lista de nomes científicos de plantas ornamentais comuns
        self.ornamental_plants = [
            "Rosa sp", "Tulipa sp", "Orchidaceae", "Chrysanthemum", "Lilium",
            "Anthurium", "Begonia", "Cyclamen", "Dianthus", "Fuchsia", 
            "Geranium", "Helianthus", "Impatiens", "Narcissus", "Petunia",
            "Pelargonium", "Saintpaulia", "Tagetes", "Viola", "Zinnia",
            "Calathea", "Monstera", "Philodendron", "Ficus", "Dracaena",
            "Spathiphyllum", "Sansevieria", "Kalanchoe", "Primula", "Poinsettia"
        ]
        
        # Termos relacionados a doenças
        self.disease_terms = [
            "disease", "pathogen", "fungus", "bacteria", "virus", 
            "infection", "rot", "blight", "mildew", "rust",
            "necrosis", "spot", "wilt", "mosaic", "canker"
        ]
        
        # Para armazenar os metadados
        self.metadata = []
        
        # Configuração do Selenium para ResearchGate (que precisa de JavaScript)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)  # Timeout em segundos
        except Exception as e:
            print(f"Erro ao inicializar o Selenium: {e}")
            print("Continuando sem suporte ao Selenium (alguns sites podem não funcionar corretamente)")
            self.driver = None
    
    def __del__(self):
        """Fechar o driver do Selenium quando o objeto for destruído"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
    
    def get_page(self, url, use_selenium=False):
        """Obtém o conteúdo HTML da página"""
        if use_selenium and self.driver:
            try:
                self.driver.get(url)
                # Esperar a página carregar
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return self.driver.page_source
            except Exception as e:
                print(f"Erro ao acessar {url} com Selenium: {e}")
                return None
        else:
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                return response.text
            except requests.exceptions.RequestException as e:
                print(f"Erro ao acessar {url}: {e}")
                return None
    
    def download_image(self, img_url, filename):
        """Baixa e salva uma imagem"""
        try:
            # Criar nome de arquivo seguro
            safe_name = ''.join(c if c.isalnum() else '_' for c in filename)
            # Adicionar um hash da URL para evitar duplicatas
            url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
            filepath = os.path.join(self.image_dir, f"{safe_name}_{url_hash}.jpg")
            
            # Verificar se a URL é uma URL de dados (base64)
            if img_url.startswith('data:image'):
                # Extrair dados base64
                header, encoded = img_url.split(",", 1)
                data = base64.b64decode(encoded)
                
                # Salvar a imagem
                with open(filepath, 'wb') as f:
                    f.write(data)
            else:
                # URL normal - baixar a imagem
                if not img_url.startswith(('http:', 'https:')):
                    img_url = urljoin(self.researchgate_base_url, img_url)
                    
                response = requests.get(img_url, headers=self.headers, stream=True)
                response.raise_for_status()
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
            
            return os.path.basename(filepath)
        except Exception as e:
            print(f"Erro ao baixar imagem {img_url}: {e}")
            return None
    
    def download_pdf(self, pdf_url, filename):
        """Baixa e salva um arquivo PDF"""
        try:
            # Criar nome de arquivo seguro
            safe_name = ''.join(c if c.isalnum() else '_' for c in filename)
            # Adicionar um hash da URL para evitar duplicatas
            url_hash = hashlib.md5(pdf_url.encode()).hexdigest()[:8]
            filepath = os.path.join(self.pdf_dir, f"{safe_name}_{url_hash}.pdf")
            
            # Baixar o PDF
            if not pdf_url.startswith(('http:', 'https:')):
                pdf_url = urljoin(self.researchgate_base_url, pdf_url)
                
            response = requests.get(pdf_url, headers=self.headers, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            return os.path.basename(filepath)
        except Exception as e:
            print(f"Erro ao baixar PDF {pdf_url}: {e}")
            return None
    
    def save_description(self, description_data, filename):
        """Salva os detalhes do artigo em um arquivo de texto"""
        try:
            safe_name = ''.join(c if c.isalnum() else '_' for c in filename)
            # Adicionar timestamp para evitar duplicatas
            timestamp = int(time.time() * 1000)
            filepath = os.path.join(self.description_dir, f"{safe_name}_{timestamp}.txt")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                for key, value in description_data.items():
                    f.write(f"{key}: {value}\n\n")
                    
            return os.path.basename(filepath)
        except Exception as e:
            print(f"Erro ao salvar descrição para {filename}: {e}")
            return None
    
    def is_relevant_to_ornamental_diseases(self, title, abstract):
        """Verifica se o artigo é relevante para doenças em plantas ornamentais"""
        
        # Verificar se o título ou resumo contém nomes de plantas ornamentais
        contains_ornamental = False
        for plant in self.ornamental_plants:
            if (plant.lower() in title.lower() or 
                (abstract and plant.lower() in abstract.lower())):
                contains_ornamental = True
                break
        
        # Verificar se o título ou resumo contém termos relacionados a doenças
        contains_disease = False
        for term in self.disease_terms:
            if (term.lower() in title.lower() or 
                (abstract and term.lower() in abstract.lower())):
                contains_disease = True
                break
        
        # O artigo é relevante se contiver tanto plantas ornamentais quanto doenças
        return contains_ornamental and contains_disease
    
    def scrape_researchgate_article(self, url):
        """Extrai dados de um artigo específico do ResearchGate"""
        html = self.get_page(url, use_selenium=True)
        if not html:
            return False
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extrair título
        title_elem = soup.select_one('h1.research-detail-header-section__title')
        if title_elem:
            title = title_elem.get_text(strip=True)
        else:
            title = "Sem título"
        
        # Extrair autores
        authors = []
        author_elems = soup.select('div.research-detail-author-list__item-text a')
        for author in author_elems:
            authors.append(author.get_text(strip=True))
        
        # Extrair resumo
        abstract_elem = soup.select_one('div.research-detail-middle-section__abstract')
        if abstract_elem:
            abstract = abstract_elem.get_text(strip=True)
        else:
            abstract = ""
        
        # Verificar se é relevante para doenças em plantas ornamentais
        if not self.is_relevant_to_ornamental_diseases(title, abstract):
            print(f"  ✗ Artigo não é relevante para doenças em plantas ornamentais: {title}")
            return False
        
        # Extrair imagens
        images = []
        img_elems = soup.select('div.research-detail-middle-section figure img')
        
        for i, img in enumerate(img_elems):
            img_src = img.get('src')
            if img_src:
                # Baixar a imagem
                img_filename = self.download_image(img_src, f"{title}_img{i+1}")
                if img_filename:
                    images.append(img_filename)
        
        # Extrair link para PDF, se disponível
        pdf_link = None
        pdf_elem = soup.select_one('a[data-testid="publication-read-link"]')
        if pdf_elem:
            pdf_link = pdf_elem.get('href')
        
        pdf_filename = None
        if pdf_link:
            pdf_filename = self.download_pdf(pdf_link, title)
        
        # Criar dicionário com os detalhes do artigo
        article_details = {
            'Title': title,
            'Authors': ', '.join(authors),
            'Abstract': abstract,
            'URL': url,
            'Images': ', '.join(images) if images else 'No images found',
            'PDF': pdf_filename if pdf_filename else 'No PDF available'
        }
        
        # Salvar descrição
        description_filename = self.save_description(article_details, title)
        
        # Adicionar aos metadados
        self.metadata.append({
            'title': title,
            'authors': ', '.join(authors),
            'abstract': abstract,
            'url': url,
            'image_files': ', '.join(images) if images else '',
            'pdf_file': pdf_filename if pdf_filename else '',
            'description_file': description_filename,
            'source_site': 'ResearchGate'
        })
        
        return True
    
    def scrape_scielo_article(self, url):
        """Extrai dados de um artigo específico da SciELO"""
        html = self.get_page(url)
        if not html:
            return False
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extrair título
        title_elem = soup.select_one('h1.article-title')
        if title_elem:
            title = title_elem.get_text(strip=True)
        else:
            title = "Sem título"
        
        # Extrair autores
        authors = []
        author_elems = soup.select('a.author-name')
        for author in author_elems:
            authors.append(author.get_text(strip=True))
        
        # Extrair resumo
        abstract = ""
        abstract_sections = soup.select('div.abstract p')
        for p in abstract_sections:
            abstract += p.get_text(strip=True) + " "
        
        # Verificar se é relevante para doenças em plantas ornamentais
        if not self.is_relevant_to_ornamental_diseases(title, abstract):
            print(f"  ✗ Artigo não é relevante para doenças em plantas ornamentais: {title}")
            return False
        
        # Extrair imagens
        images = []
        img_elems = soup.select('div.modal-body img, figure img')
        
        for i, img in enumerate(img_elems):
            img_src = img.get('src')
            if img_src:
                # Baixar a imagem
                img_filename = self.download_image(img_src, f"{title}_img{i+1}")
                if img_filename:
                    images.append(img_filename)
        
        # Extrair link para PDF, se disponível
        pdf_link = None
        pdf_elem = soup.select_one('a.pdf')
        if pdf_elem:
            pdf_link = pdf_elem.get('href')
        
        pdf_filename = None
        if pdf_link:
            pdf_filename = self.download_pdf(pdf_link, title)
        
        # Criar dicionário com os detalhes do artigo
        article_details = {
            'Title': title,
            'Authors': ', '.join(authors),
            'Abstract': abstract,
            'URL': url,
            'Images': ', '.join(images) if images else 'No images found',
            'PDF': pdf_filename if pdf_filename else 'No PDF available'
        }
        
        # Salvar descrição
        description_filename = self.save_description(article_details, title)
        
        # Adicionar aos metadados
        self.metadata.append({
            'title': title,
            'authors': ', '.join(authors),
            'abstract': abstract,
            'url': url,
            'image_files': ', '.join(images) if images else '',
            'pdf_file': pdf_filename if pdf_filename else '',
            'description_file': description_filename,
            'source_site': 'SciELO'
        })
        
        return True
    
    def search_researchgate(self, query, max_articles=10):
        """Pesquisa artigos no ResearchGate com base em uma consulta"""
        search_url = f"{self.researchgate_base_url}/search/publication?q={quote_plus(query)}"
        
        print(f"Pesquisando ResearchGate: {query}")
        print(f"URL: {search_url}")
        
        html = self.get_page(search_url, use_selenium=True)
        if not html:
            return 0
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extrair links para artigos
        article_links = []
        for link in soup.select('a.publication-title'):
            href = link.get('href')
            if href and '/publication/' in href:
                full_url = urljoin(self.researchgate_base_url, href)
                article_links.append(full_url)
        
        print(f"Encontrados {len(article_links)} artigos no ResearchGate")
        
        # Limitar o número de artigos
        if max_articles > 0:
            article_links = article_links[:max_articles]
        
        successful_extractions = 0
        
        # Processar cada link de artigo
        for i, article_url in enumerate(article_links):
            print(f"[{i+1}/{len(article_links)}] Processando artigo do ResearchGate: {article_url}")
            result = self.scrape_researchgate_article(article_url)
            
            if result:
                print(f"  ✓ Artigo extraído com sucesso")
                successful_extractions += 1
            else:
                print(f"  ✗ Falha na extração do artigo")
                
            # Pausa entre requisições
            time.sleep(random.uniform(2.0, 5.0))
        
        return successful_extractions
    
    def search_scielo(self, query, max_articles=10):
        """Pesquisa artigos na SciELO com base em uma consulta"""
        search_url = f"{self.scielo_base_url}/en/index.php?q={quote_plus(query)}"
        
        print(f"Pesquisando SciELO: {query}")
        print(f"URL: {search_url}")
        
        html = self.get_page(search_url)
        if not html:
            return 0
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extrair links para artigos
        article_links = []
        for link in soup.select('div.results a.showTooltip'):
            href = link.get('href')
            if href and 'scielo' in href:
                article_links.append(href)
        
        print(f"Encontrados {len(article_links)} artigos na SciELO")
        
        # Limitar o número de artigos
        if max_articles > 0:
            article_links = article_links[:max_articles]
        
        successful_extractions = 0
        
        # Processar cada link de artigo
        for i, article_url in enumerate(article_links):
            print(f"[{i+1}/{len(article_links)}] Processando artigo da SciELO: {article_url}")
            result = self.scrape_scielo_article(article_url)
            
            if result:
                print(f"  ✓ Artigo extraído com sucesso")
                successful_extractions += 1
            else:
                print(f"  ✗ Falha na extração do artigo")
                
            # Pausa entre requisições
            time.sleep(random.uniform(2.0, 5.0))
        
        return successful_extractions
        
    def run_searches(self, max_articles_per_search=5):
        """Executa pesquisas para plantas ornamentais e doenças"""
        total_articles = 0
        
        # Combinar plantas ornamentais com termos de doenças
        for plant in self.ornamental_