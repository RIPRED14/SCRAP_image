import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import os
import sys
from multiprocessing import freeze_support
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from scrapaga import main as run_scraper_main
except ImportError:
    logging.error("Failed to import run_scraper_main from scrapaga")
    run_scraper_main = None

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ScraperGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agidra Scraper")
        self.geometry("800x600")
        self.scraper_thread = None
        self.stop_event = threading.Event()

        # Configure logging
        logging.info("Application started")

        # Main frame
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Controls Frame ---
        self.controls_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding="10")
        self.controls_frame.pack(fill=tk.X, pady=5)

        self.run_button = ttk.Button(self.controls_frame, text="Run Scraper", command=self.run_scraper)
        self.run_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ttk.Button(self.controls_frame, text="Stop Scraper", command=self.stop_scraper, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        self.view_images_button = ttk.Button(self.controls_frame, text="View Images", command=self.view_images)
        self.view_images_button.grid(row=0, column=2, padx=5, pady=5)

        self.processors_label = ttk.Label(self.controls_frame, text="Processes:")
        self.processors_label.grid(row=0, column=3, padx=(10, 2), pady=5)

        self.processors_var = tk.StringVar(value=os.cpu_count())
        self.processors_entry = ttk.Entry(self.controls_frame, textvariable=self.processors_var, width=5)
        self.processors_entry.grid(row=0, column=4, padx=5, pady=5)

        # --- Output Frame ---
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Output", padding="10")
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.output_text = scrolledtext.ScrolledText(self.output_frame, wrap=tk.WORD, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def threaded_output_append(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def run_scraper(self):
        logging.info("Run Scraper button clicked")
        if self.scraper_thread and self.scraper_thread.is_alive():
            messagebox.showwarning("Scraper Running", "The scraper is already running.")
            return

        self.output_text.delete(1.0, tk.END)
        self.threaded_output_append("Scraping in progress...\n")
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.stop_event.clear()

        num_processes = int(self.processors_entry.get())

        self.scraper_thread = threading.Thread(target=self._execute_scraper, args=(num_processes, self.stop_event))
        self.scraper_thread.start()

    def _execute_scraper(self, num_processes, stop_event):
        logging.info("Starting _execute_scraper thread")
        try:
            if run_scraper_main:
                image_dir = get_resource_path('product_images')
                run_scraper_main(num_processes, self.threaded_output_append, stop_event, image_dir)
            else:
                self.threaded_output_append("Scraper function not loaded.\n")
        except Exception as e:
            logging.error(f"Exception in scraper thread: {e}", exc_info=True)
            self.threaded_output_append(f"An error occurred: {e}\n")
        finally:
            logging.info("_execute_scraper thread finished")
            self.after(0, self.on_scraper_finish)

    def on_scraper_finish(self):
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.threaded_output_append("Scraping finished or stopped.\n")

    def stop_scraper(self):
        if self.scraper_thread and self.scraper_thread.is_alive():
            self.stop_event.set()

    def view_images(self):
        image_dir = get_resource_path('product_images')
        if not os.path.exists(image_dir):
            self.threaded_output_append("IMAGE DIRECTORY NOT FOUND\n")
            return
        os.startfile(image_dir)

if __name__ == "__main__":
    freeze_support()
    app = ScraperGUI()
    app.mainloop()