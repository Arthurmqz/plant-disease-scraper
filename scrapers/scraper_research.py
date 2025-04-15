# scrapers/scraper_site1.py
import os
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
from urllib.parse import urljoin

class PlantDiseaseScraper:
    def __init__(self, base_url, output_dir):
        """
        Inicializa o scraper
        
        Args:
            base_url (str): URL base do site a ser extraído
            output_dir (str): Diretório onde os dados serão salvos
        """
        self.base_url = base_url
        self.output_dir = output_dir
        self.image_dir = os.path.join(output_dir, "images")
        self.description_dir = os.path.join(output_dir, "descriptions")
        
        # Criar diretórios se não existirem
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.description_dir, exist_ok=True)
        
        # Headers para simular um navegador (evitar bloqueios)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # Para armazenar os metadados
        self.metadata = []
    
    def get_page(self, url):
        """Obtém o conteúdo HTML da página"""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            return None
    
    def download_image(self, img_url, disease_name):
        """Baixa e salva uma imagem"""
        try:
            # Criar nome de arquivo seguro
            safe_name = ''.join(c if c.isalnum() else '_' for c in disease_name)
            # Adicionar timestamp para evitar duplicatas
            timestamp = int(time.time() * 1000)
            filename = f"{safe_name}_{timestamp}.jpg"
            filepath = os.path.join(self.image_dir, filename)
            
            # Baixar a imagem
            img_url = urljoin(self.base_url, img_url)  # Converte URL relativa para absoluta
            response = requests.get(img_url, headers=self.headers, stream=True)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            return filename
        except Exception as e:
            print(f"Erro ao baixar imagem {img_url}: {e}")
            return None
    
    def save_description(self, description, disease_name):
        """Salva a descrição da doença em um arquivo de texto"""
        try:
            safe_name = ''.join(c if c.isalnum() else '_' for c in disease_name)
            filename = f"{safe_name}.txt"
            filepath = os.path.join(self.description_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(description)
            
            return filename
        except Exception as e:
            print(f"Erro ao salvar descrição para {disease_name}: {e}")
            return None
    
    def parse_disease_page(self, url, disease_name):
        """Extrai informações de uma página específica de doença"""
        html = self.get_page(url)
        if not html:
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Exemplo: encontrar a descrição da doença
        # (Ajuste os seletores CSS para o site específico)
        description_div = soup.select_one('div.disease-description')
        if description_div:
            description = description_div.get_text(strip=True)
            desc_filename = self.save_description(description, disease_name)
        else:
            description = "Descrição não encontrada"
            desc_filename = None
        
        # Exemplo: encontrar imagens da doença
        # (Ajuste os seletores CSS para o site específico)
        image_urls = []
        for img in soup.select('div.disease-images img'):
            img_url = img.get('src')
            if img_url:
                image_urls.append(img_url)
        
        # Baixar imagens
        downloaded_images = []
        for i, img_url in enumerate(image_urls):
            img_filename = self.download_image(img_url, f"{disease_name}_{i}")
            if img_filename:
                downloaded_images.append(img_filename)
            # Pequena pausa para evitar sobrecarregar o servidor
            time.sleep(random.uniform(0.5, 1.5))
        
        # Adicionar metadados
        self.metadata.append({
            'disease_name': disease_name,
            'url': url,
            'description_file': desc_filename,
            'image_files': downloaded_images,
            'image_count': len(downloaded_images)
        })
    
    def scrape_disease_list(self, list_url):
        """Extrai a lista de doenças de uma página índice"""
        html = self.get_page(list_url)
        if not html:
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Exemplo: encontrar links para páginas de doenças específicas
        # (Ajuste os seletores CSS para o site específico)
        disease_links = soup.select('ul.disease-list li a')
        
        print(f"Encontradas {len(disease_links)} doenças para extrair.")
        
        for i, link in enumerate(disease_links):
            disease_name = link.get_text(strip=True)
            disease_url = urljoin(list_url, link.get('href'))
            
            print(f"[{i+1}/{len(disease_links)}] Extraindo dados de: {disease_name}")
            self.parse_disease_page(disease_url, disease_name)
            
            # Pausa entre requisições para evitar bloqueios
            time.sleep(random.uniform(1.0, 3.0))
    
    def save_metadata(self):
        """Salva os metadados em um arquivo CSV"""
        if not self.metadata:
            print("Nenhum dado extraído para salvar.")
            return
        
        df = pd.DataFrame(self.metadata)
        csv_path = os.path.join(self.output_dir, "metadata.csv")
        df.to_csv(csv_path, index=False)
        print(f"Metadados salvos em {csv_path}")