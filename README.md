# Scraper Agidra

This project contains a Python application with a graphical user interface (GUI) to scrape product information and images from the Agidra website.

## Prerequisites

- Python 3.x
- Git

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/RIPRED14/SCRAP_image.git
    cd SCRAP_image
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    Activate the virtual environment:
    - On Windows:
      ```bash
      .\venv\Scripts\activate
      ```
    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Building the Application

To create the executable file, run the following command in the root of the project:

```bash
pyinstaller gui.spec
```

This will generate a `dist` folder containing the `gui.exe` application.

## Running the Application

Navigate to the `dist` folder and run the executable:

```bash
cd dist
./gui.exe
```

This will launch the GUI, and you can start scraping by clicking the "Run Scraper" button. The scraped images will be saved in the `product_images` directory, which will be created inside the `dist` folder.