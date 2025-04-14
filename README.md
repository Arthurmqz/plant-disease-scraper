# Plant Disease Dataset Creator

A Python-based web scraping system designed to collect and organize a dataset of plant disease images and descriptions. This project was created to build a custom database that can be used to train machine learning models (LLM) focused on identifying and diagnosing plant diseases.

## 📋 Overview

This project automatically extracts:
- Images of plants with diseases
- Detailed descriptions of the diseases
- Related metadata (disease name, source, etc.)

The data is organized in a clear directory structure, facilitating its subsequent use for model training or analysis.

## 🚀 Features

- Extraction from multiple configurable web sources
- Automatic download and organization of images
- Saving text descriptions in separate files
- Generation of CSV file with metadata for easy indexing
- Measures to avoid site blocking (delays, custom headers)
- Modular structure allowing easy addition of new sites

## 📁 Project Structure

```
plant-disease-scraper/
├── venv/                  # Python virtual environment
├── scrapers/              # Scraping scripts for different sites
│   ├── __init__.py        # Makes the folder a Python package
│   ├── scraper_site1.py   # Scraper for site 1
│   └── scraper_site2.py   # Scraper for site 2
├── dataset/               # Where data will be saved
│   ├── images/            # Folder for images
│   └── descriptions/      # Folder for descriptive texts
├── utils/                 # Useful functions
│   ├── __init__.py
│   └── helpers.py         # Helper functions
├── requirements.txt       # Project dependencies
├── config.py              # Project settings
└── main.py                # Main entry point
```

## ⚙️ Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/plant-disease-dataset-creator.git
   cd plant-disease-dataset-creator
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure URLs and directories in the `config.py` file

## 🔧 Usage

Run the main script to start the scraping process:

```bash
python main.py
```

The program will:
1. Access the configured sites
2. Extract information about plant diseases
3. Download relevant images
4. Save descriptions in text files
5. Generate a CSV file with metadata

## ⚠️ Ethical and Legal Considerations

This software should be used responsibly. Before using:

- Check the Terms of Service of the sites you intend to access
- Respect the rules in each site's robots.txt file
- Maintain reasonable delays between requests to avoid overloading servers
- Use the collected data only for educational or research purposes

## 🛠️ Technologies Used

- Python 3.x
- BeautifulSoup4 (for HTML parsing)
- Requests (for HTTP requests)
- Selenium (for sites with dynamic content)
- Pandas (for metadata management)
- Pillow (for image processing)

## 📊 Dataset Format

The generated dataset follows this structure:

- **Images**: Saved in `dataset/images/` with standardized names
- **Descriptions**: Texts saved in `dataset/descriptions/` 
- **Metadata**: CSV file in `dataset/metadata.csv` with columns:
  - disease_name: Name of the disease
  - url: Source URL
  - description_file: Name of the file with the description
  - image_files: List of image file names
  - image_count: Number of images collected

## 🔄 Customization

To add a new source site:

1. Create a new file in `scrapers/` based on the existing model
2. Analyze the HTML structure of the target site
3. Adjust CSS selectors to correctly locate the information
4. Add the new site configuration in the `config.py` file
5. Import and use the new scraper in `main.py`

## 👥 Contributions

Contributions are welcome! Feel free to:

- Report bugs
- Suggest new features
- Send pull requests
- Add support for new sites

## 📄 License

This project is licensed under the [MIT License](LICENSE).