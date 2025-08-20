import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://www.agidra.com/"
IMAGE_DIR = "product_images"

def get_product_links(url, output_callback):
    try:
        sitemap_url = f"{url}/sitemap.xml"
        response = requests.get(sitemap_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'xml')
        product_links = [loc.get_text() for loc in soup.find_all('loc') if '/produit-' in loc.get_text()]
        return product_links, f"Found {len(product_links)} product links."
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching product links: {e}")
        output_callback(f"Error fetching product links: {e}\n")
        return [], "Error fetching product links."

def get_product_details(product_url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        product_name_tag = soup.find('h1')
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else "unknown_product"
        
        product_ref_tag = soup.find('div', class_='reference')
        if product_ref_tag:
            ref_text = product_ref_tag.get_text(strip=True)
            product_ref = ref_text.replace('Ref', '').strip().split(' ')[0]
        else:
            product_ref = None

        img_tag = soup.find('img', class_='img_slide_produit')
        if img_tag and img_tag.get('data-zoom'):
            relative_url = img_tag['data-zoom']
            absolute_url = urljoin(BASE_URL, relative_url.lstrip('./'))
            return absolute_url, product_name, product_ref, None
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content'], product_name, product_ref, None
        return None, product_name, product_ref, "Image URL not found."
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching product details from {product_url}: {e}")
        return None, None, None, str(e)

def download_image(image_url, folder_path, product_name, product_ref):
    try:
        safe_product_name = "".join(c for c in product_name if c.isalnum() or c in (' ', '-')).rstrip()
        file_extension = os.path.splitext(os.path.basename(image_url))[1]
        image_name = f"{product_ref}_{safe_product_name.replace(' ', '_')}{file_extension}"
        image_path = os.path.join(folder_path, image_name)
        if os.path.exists(image_path):
            return f"Image already exists: {image_path}"
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(image_path, 'wb') as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)
        return image_path
    except requests.exceptions.RequestException as e:
        logging.error(f"Error downloading image {image_url}: {e}")
        return None

def main(num_processes, output_callback, stop_event, image_dir):
    logging.info(f"Scraper started with {num_processes} processes.")
    output_callback("Fetching product links...\n")
    product_links, message = get_product_links(BASE_URL, output_callback)
    output_callback(f"{message}\n")

    if not product_links:
        output_callback("No product links found. Exiting.\n")
        logging.warning("No product links found.")
        return

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    for link in product_links:
        if stop_event.is_set():
            logging.info("Scraper stopped by user.")
            output_callback("Scraper process terminated.\n")
            break
        full_url = urljoin(BASE_URL, link)
        logging.info(f"Processing {full_url}")
        output_callback(f"Scrapping {full_url}\n")
        image_url, product_name, product_ref, error_message = get_product_details(full_url)

        if error_message:
            output_callback(f"Could not get details for {full_url}: {error_message}\n")
            logging.warning(f"Could not get details for {full_url}: {error_message}")
            continue

        if product_name and image_url:
            logging.info(f"Downloading image for {product_name}")
            output_callback(f"Downloading image for {product_name}...\n")
            image_path = download_image(image_url, image_dir, product_name, product_ref)
            if image_path:
                output_callback(f"Image saved to {image_path}\n")
            else:
                output_callback(f"Failed to download image for {product_name}\n")
        else:
            output_callback(f"Could not get details for {full_url}\n")

    logging.info("Scraping finished.")