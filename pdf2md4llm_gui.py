# -*- coding: utf-8 -*-
r"""
pdf2md4llm_gui.py
Created by NCagle
2025-06-12
      _
   __(.)<
~~~⋱___)~~~

Standalone Python application for converting PDF files to Markdown format for
use with LLM RAG workflows.
Supports both single file and batch conversion modes.
"""
from pathlib import Path
import threading
from typing import List, Optional
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
# import re
# import pymupdf
import pymupdf4llm


class PDFConverterGUI:
    """
    GUI application for converting PDF files to Markdown or text format.
    Supports both single file and batch conversion modes.
    """
    def __init__(self, root: tk.Tk):
        """
        Initialize the PDF Converter GUI.

        Arguments:
            root (tk.Tk): The main tkinter window
        """
        self.root = root
        self.root.title("PDF to Markdown Converter")
        self.root.geometry("480x320")
        self.root.resizable(False, False)

        # Initialize variables
        self.selected_pdf_path: Optional[Path] = None
        self.output_directory: Optional[Path] = None
        self.batch_files: List[Path] = []
        self.is_batch_mode: bool = False
        self.conversion_running: bool = False

        # Setup GUI elements
        self.setup_main_frame()
        self.setup_variables()
        self.setup_style()
        self.setup_widgets()


    def setup_main_frame(self):
        """Setup the main container frame."""
        self.main_frame = ttk.Frame(self.root, padding="8")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for proper resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)


    def setup_style(self):
        """Configure custom styles for the application."""
        self.style = ttk.Style()

        # Configure custom progress bar style
        self.style.configure(
            "Custom.Horizontal.TProgressbar",
            background="#1b628e",  # Blue progress color
            troughcolor="#e0e0e0",  # Light gray background
            borderwidth=1,
            relief="sunken"  # Sunken relief for nice appearance
        )


    def setup_variables(self):
        """Initialize tkinter variables."""
        self.file_type_var = tk.StringVar(value="md")  # Default to markdown
        self.batch_mode_var = tk.BooleanVar(value=False)

        # Advanced settings variables
        self.show_advanced_var = tk.BooleanVar(value=False)
        self.chunking_mode_var = tk.StringVar(value="none")  # none, pages, words
        self.word_limit_var = tk.StringVar(value="1000")
        self.word_limit_enabled_var = tk.BooleanVar(value=False)


    def setup_widgets(self):
        """Create and arrange all GUI widgets."""
        # Mode selection
        mode_frame = ttk.LabelFrame(self.main_frame, text="Conversion Mode", padding="5")
        mode_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        mode_frame.columnconfigure(0, weight=1)
        mode_frame.columnconfigure(1, weight=1)

        ttk.Radiobutton(
            mode_frame,
            text="Single File",
            variable=self.batch_mode_var,
            value=False,
            command=self.toggle_mode
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(
            mode_frame,
            text="Batch Files",
            variable=self.batch_mode_var,
            value=True,
            command=self.toggle_mode
        ).grid(row=0, column=1, sticky=tk.W)

        # File selection section
        file_frame = ttk.LabelFrame(self.main_frame, text="File Selection", padding="5")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)

        # Single file selection (default view)
        self.single_file_frame = ttk.Frame(file_frame)
        self.single_file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.single_file_frame.columnconfigure(1, weight=1)

        ttk.Label(self.single_file_frame, text="PDF File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pdf_path_var = tk.StringVar()
        self.pdf_entry = ttk.Entry(self.single_file_frame, textvariable=self.pdf_path_var, width=40)
        self.pdf_entry.grid(row=0, column=1, padx=(5, 5), pady=2, sticky=(tk.W, tk.E))
        ttk.Button(
            self.single_file_frame,
            text="Browse",
            command=self.browse_pdf_file
        ).grid(row=0, column=2, pady=2)

        # Batch file selection (hidden by default)
        self.batch_file_frame = ttk.Frame(file_frame)
        self.batch_file_frame.columnconfigure(0, weight=1)

        button_frame = ttk.Frame(self.batch_file_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(button_frame, text="Selected Files:").grid(row=0, column=0, sticky=tk.W)
        ttk.Button(
            button_frame,
            text="Add Files",
            command=self.browse_batch_files
        ).grid(row=0, column=1, padx=(10, 5))
        ttk.Button(
            button_frame,
            text="Clear All",
            command=self.clear_batch_files
        ).grid(row=0, column=2)

        # Listbox for batch files with scrollbar
        listbox_frame = ttk.Frame(self.batch_file_frame)
        listbox_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.batch_listbox = tk.Listbox(listbox_frame, height=6, width=60)
        self.batch_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.batch_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.batch_listbox.config(yscrollcommand=scrollbar.set)

        # Output settings
        output_frame = ttk.LabelFrame(self.main_frame, text="Output Settings", padding="5")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        output_frame.columnconfigure(1, weight=1)

        # Single file output settings (file path with name)
        self.single_output_frame = ttk.Frame(output_frame)
        self.single_output_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        self.single_output_frame.columnconfigure(1, weight=1)

        ttk.Label(
            self.single_output_frame,
            text="Output File (optional):"
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.single_output_path_var = tk.StringVar()
        self.single_output_entry = ttk.Entry(
            self.single_output_frame,
            textvariable=self.single_output_path_var,
            width=40
        )
        self.single_output_entry.grid(row=0, column=1, padx=(5, 5), pady=2, sticky=(tk.W, tk.E))
        ttk.Button(
            self.single_output_frame,
            text="Browse",
            command=self.browse_single_output_file
        ).grid(row=0, column=2, pady=2)

        # Batch output settings (directory only)
        self.batch_output_frame = ttk.Frame(output_frame)
        self.batch_output_frame.columnconfigure(1, weight=1)

        ttk.Label(
            self.batch_output_frame,
            text="Output Directory (optional):"
        ).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.batch_output_path_var = tk.StringVar()
        self.batch_output_entry = ttk.Entry(
            self.batch_output_frame,
            textvariable=self.batch_output_path_var,
            width=40
        )
        self.batch_output_entry.grid(row=0, column=1, padx=(5, 5), pady=2, sticky=(tk.W, tk.E))
        ttk.Button(
            self.batch_output_frame,
            text="Browse",
            command=self.browse_batch_output_directory
        ).grid(row=0, column=2, pady=2)

        # File type selection
        type_frame = ttk.Frame(output_frame)
        type_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        ttk.Label(type_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(
            type_frame,
            text=".md (Markdown)",
            variable=self.file_type_var,
            value="md"
        ).grid(row=0, column=1, padx=(10, 0), sticky=tk.W)
        ttk.Radiobutton(
            type_frame,
            text=".txt (Text)",
            variable=self.file_type_var,
            value="txt"
        ).grid(row=0, column=2, padx=(10, 0), sticky=tk.W)

        # Advanced Settings (collapsible)
        self.advanced_frame = ttk.Frame(output_frame)
        self.advanced_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        self.advanced_frame.columnconfigure(0, weight=1)

        # Advanced settings toggle button
        self.advanced_toggle_button = ttk.Button(
            self.advanced_frame,
            text="▶ Advanced Settings",
            command=self.toggle_advanced_settings
        )
        self.advanced_toggle_button.grid(row=0, column=0, sticky=tk.W)

        # Advanced settings content (hidden by default)
        self.advanced_content_frame = ttk.Frame(self.advanced_frame)
        # Don't grid this initially - it will be shown/hidden by toggle

        # Chunking options
        chunking_label_frame = ttk.LabelFrame(
            self.advanced_content_frame,
            text="Text Chunking Options",
            padding="5"
        )
        chunking_label_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        chunking_label_frame.columnconfigure(0, weight=1)

        # Radio buttons for chunking modes
        ttk.Radiobutton(
            chunking_label_frame,
            text="Export as single file (default)",
            variable=self.chunking_mode_var,
            value="none"
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

        # ttk.Radiobutton(chunking_label_frame, text="Split by pages (one file per page)", 
        #                variable=self.chunking_mode_var, value="pages").grid(row=1, column=0, sticky=tk.W, pady=2)

        # Word limit option with entry
        word_limit_frame = ttk.Frame(chunking_label_frame)
        word_limit_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        word_limit_frame.columnconfigure(1, weight=1)

        ttk.Radiobutton(
            word_limit_frame,
            text="Split by word limit:",
            variable=self.chunking_mode_var,
            value="words"
        ).grid(row=0, column=0, sticky=tk.W)

        self.word_limit_entry = ttk.Entry(word_limit_frame, textvariable=self.word_limit_var, width=8)
        self.word_limit_entry.grid(row=0, column=1, padx=(5, 5), sticky=tk.W)

        ttk.Label(word_limit_frame, text="words per file").grid(row=0, column=2, sticky=tk.W)

        # Conversion button and progress
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=3, column=0, pady=(0, 5))

        self.convert_button = ttk.Button(
            control_frame,
            text="Convert PDF(s)",
            command=self.start_conversion
        )
        self.convert_button.grid(row=0, column=0, padx=(0, 10))

        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(control_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=1)

        self.progress_bar = ttk.Progressbar(
            control_frame,
            length=200,
            mode="indeterminate",
            style="Custom.Horizontal.TProgressbar"
        )
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))


    def toggle_mode(self):
        """Toggle between single file and batch mode."""
        self.is_batch_mode = self.batch_mode_var.get()

        if self.is_batch_mode:
            # Switch to batch mode
            self.single_file_frame.grid_remove()
            self.single_output_frame.grid_remove()
            self.batch_file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.batch_output_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
            if self.show_advanced_var.get():
                self.root.geometry("480x500")
            else:
                self.root.geometry("480x420")
            self.root.resizable(True, True)
        else:
            # Switch to single file mode
            self.batch_file_frame.grid_remove()
            self.batch_output_frame.grid_remove()
            self.single_file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            self.single_output_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
            if self.show_advanced_var.get():
                self.root.geometry("480x400")
            else:
                self.root.geometry("480x320")
            self.root.resizable(False, False)


    def toggle_advanced_settings(self):
        """Toggle the visibility of advanced settings."""
        if self.show_advanced_var.get():
            # Hide advanced settings
            self.advanced_content_frame.grid_remove()
            self.advanced_toggle_button.config(text="▶ Advanced Settings")
            self.show_advanced_var.set(False)
            # Adjust window size
            if self.is_batch_mode:
                self.root.geometry("480x420")
            else:
                self.root.geometry("480x320")
        else:
            # Show advanced settings
            self.advanced_content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
            self.advanced_toggle_button.config(text="▼ Advanced Settings")
            self.show_advanced_var.set(True)
            # Adjust window size to accommodate advanced settings
            if self.is_batch_mode:
                self.root.geometry("480x500")
            else:
                self.root.geometry("480x400")


    def browse_pdf_file(self):
        """Open file dialog to select a single PDF file."""
        file_path = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.selected_pdf_path = Path(file_path)
            self.pdf_path_var.set(str(self.selected_pdf_path))


    def browse_batch_files(self):
        """Open file dialog to select multiple PDF files for batch processing."""
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        for file_path in file_paths:
            pdf_path = Path(file_path)
            if pdf_path not in self.batch_files:
                self.batch_files.append(pdf_path)
                self.batch_listbox.insert(tk.END, pdf_path.name)


    def clear_batch_files(self):
        """Clear all selected batch files."""
        self.batch_files.clear()
        self.batch_listbox.delete(0, tk.END)


    def browse_single_output_file(self):
        """Open file dialog to select output file path and name for single file mode."""
        file_extension = self.file_type_var.get()
        file_types = [
            (f"{file_extension.upper()} files", f"*.{file_extension}"),
            ("All files", "*.*")
        ]

        file_path = filedialog.asksaveasfilename(
            title="Save Output File As",
            defaultextension=f".{file_extension}",
            filetypes=file_types
        )
        if file_path:
            self.single_output_path_var.set(file_path)


    def browse_batch_output_directory(self):
        """Open dialog to select output directory for batch mode."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.batch_output_path_var.set(directory)


    def validate_inputs(self) -> bool:
        """
        Validate user inputs before starting conversion.

        Returns:
            is_valid (bool): True if inputs are valid, False otherwise
        """
        if self.is_batch_mode:
            if not self.batch_files:
                messagebox.showerror("Error", "Please select at least one PDF file for batch conversion.")
                return False
        else:
            if not self.selected_pdf_path or not self.selected_pdf_path.exists():
                messagebox.showerror("Error", "Please select a valid PDF file.")
                return False

        return True


    def get_word_count(self, text: str) -> int:
        """
        Get the word count of a text string.

        Arguments:
            text (str): Text to count words in

        Returns:
            word_count (int): Number of words in the text
        """
        # Split by whitespace and filter out empty strings
        words = [word for word in text.split() if word.strip()]
        return len(words)


    def split_text_by_words(self, text: str, word_limit: int) -> List[str]:
        """
        Split text into chunks based on word limit.

        Arguments:
            text (str): Text to split
            word_limit (int): Maximum words per chunk

        Returns:
            chunks (List[str]): List of text chunks

        Notes:
            Break the string into a list of individual lines.
            Iterate through the list of lines.
            Split lines into words to get the word count per line.
            Join the lines with new lines while below the chunk limit.
            This preserves any original formatting elements.
        """
        lines = text.splitlines()
        chunks = []
        current_chunk = []
        current_word_count = 0

        for line in lines:
            line_count = len(line.split())
            if current_word_count + line_count <= word_limit:
                current_word_count += line_count
                current_chunk.append(line)
            else:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
                current_word_count = 0

        # Add any remaining words as the last chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks


    # def convert_pdf_by_pages(self, pdf_path: Path) -> List[str]:
    #     """
    #     Convert PDF to markdown split by individual pages.

    #     Arguments:
    #         pdf_path (Path): Path to the PDF file

    #     Returns:
    #         page_texts (List[str]): List of markdown text for each page
    #     """
    #     page_texts = []
    #     doc = pymupdf.open(str(pdf_path))

    #     try:
    #         for page_num in range(len(doc)):
    #             # Extract text from individual page
    #             page = doc[page_num]
    #             page_text = page.get_text()

    #             # Convert page text to markdown format
    #             # Note: This is a simplified conversion - pymupdf4llm.to_markdown works on full document
    #             # For individual pages, we'll do basic formatting
    #             page_markdown = f"# Page {page_num + 1}\n\n{page_text}"
    #             page_texts.append(page_markdown)

    #     finally:
    #         doc.close()

    #     return page_texts


    def get_output_path(self, input_path: Path, enum: int = None) -> Path:
        """
        Generate output path for a given input PDF file.

        Arguments:
            input_path (Path): Path to the input PDF file
            enum (int): Enumerator to append to set of file names

        Returns:
            output_path (Path): Path where the converted file will be saved
        """
        file_extension = self.file_type_var.get()
        enumerator = ""
        if enum is not None:
            enumerator = f"_{str(enum).rjust(3, '0')}"

        if self.is_batch_mode:
            # Batch mode: use directory only, keep original filename
            batch_output_dir = self.batch_output_path_var.get().strip()
            if batch_output_dir:
                output_path = Path(batch_output_dir) / f"{input_path.stem}{enumerator}.{file_extension}"
            else:
                # Use same directory as input file
                output_path = input_path.with_name(f"{input_path.stem}{enumerator}.{file_extension}")
        else:
            # Single file mode: use full file path if specified
            single_output_file = self.single_output_path_var.get().strip()
            if single_output_file:
                output_path = Path(single_output_file)
                # Ensure the correct extension is used
                output_path = output_path.with_name(f"{output_path.stem}{enumerator}.{file_extension}")
            else:
                # Use same directory as input file with original name
                output_path = input_path.with_name(f"{input_path.stem}{enumerator}.{file_extension}")

        return output_path


    def convert_single_file(self, pdf_path: Path):
        """
        Convert a single PDF file to markdown/text with chunking options.

        Arguments:
            pdf_path (Path): Path to the PDF file to convert
        """
        try:
            chunking_mode = self.chunking_mode_var.get()

            # if chunking_mode == "pages":
            #     # Split by pages
            #     self.progress_var.set(f"Converting '{pdf_path.name}' by pages...")
            #     self.root.update_idletasks()

            #     page_texts = self.convert_pdf_by_pages(pdf_path)

            #     for i, page_text in enumerate(page_texts, 1):
            #         output_path = self.get_output_path(pdf_path, i)
            #         output_path.write_bytes(page_text.encode("utf-8"))

            #     return len(page_texts)  # Return number of files created

            if chunking_mode == "words":
                # Split by word limit
                try:
                    word_limit = int(self.word_limit_var.get())
                    if word_limit <= 0:
                        raise ValueError("Word limit must be greater than 0")
                except ValueError:
                    raise Exception("Invalid word limit. Please enter a positive number.")

                self.progress_var.set(f"Converting '{pdf_path.name}' with word limit...")
                self.root.update_idletasks()

                # Convert full document first
                md_text = pymupdf4llm.to_markdown(str(pdf_path))

                # Split into chunks
                text_chunks = self.split_text_by_words(md_text, word_limit)

                for i, chunk in enumerate(text_chunks, 1):
                    output_path = self.get_output_path(pdf_path, i)
                    self.progress_var.set(f"Exporting chunk '{output_path.name}'...")
                    self.root.update_idletasks()
                    output_path.write_bytes(chunk.encode("utf-8"))

                return len(text_chunks)  # Return number of files created

            else:
                # Default: single file conversion
                self.progress_var.set(f"Converting '{pdf_path.name}'...")
                self.root.update_idletasks()

                md_text = pymupdf4llm.to_markdown(str(pdf_path))
                output_path = self.get_output_path(pdf_path)
                output_path.write_bytes(md_text.encode("utf-8"))

                return 1  # Return number of files created

        except Exception as e:
            raise Exception(f"Error converting '{pdf_path.name}': {str(e)}")


    def conversion_worker(self):
        """
        Worker function that runs the conversion process in a separate thread.
        This prevents the GUI from freezing during conversion.
        """
        try:
            # Start indeterminate progress bar
            self.progress_bar.start()

            if self.is_batch_mode:
                # Batch conversion
                total_files = len(self.batch_files)
                total_output_files = 0

                for i, pdf_path in enumerate(self.batch_files, 1):
                    files_created = self.convert_single_file(pdf_path)
                    total_output_files += files_created

                    # Update progress text
                    self.progress_var.set(f"Completed {i}/{total_files} PDFs")
                    self.root.update_idletasks()

                self.progress_var.set(f"Batch conversion completed!")
                messagebox.showinfo(
                    "Success",
                    f"Successfully processed {total_files} PDF files!\n"
                    + f"Created {total_output_files} output files."
                )

            else:
                # Single file conversion
                files_created = self.convert_single_file(self.selected_pdf_path)

                self.progress_var.set(f"Conversion completed!")

                if files_created == 1:
                    output_path = self.get_output_path(self.selected_pdf_path)
                    messagebox.showinfo(
                        "Success",
                        f"Successfully converted '{self.selected_pdf_path.name}'!\n\n"
                        + f"Saved to: {output_path}"
                    )
                else:
                    messagebox.showinfo(
                        "Success",
                        f"Successfully converted '{self.selected_pdf_path.name}'!\n"
                        + f"Created {files_created} output files."
                    )

        except Exception as e:
            messagebox.showerror("Conversion Error", str(e))
            self.progress_var.set("Conversion failed")

        finally:
            self.progress_bar.stop()
            self.convert_button.config(state="normal")
            self.conversion_running = False

    def start_conversion(self):
        """Start the PDF conversion process."""
        if self.conversion_running:
            return

        if not self.validate_inputs():
            return

        # Disable convert button to prevent multiple simultaneous conversions
        self.convert_button.config(state="disabled")
        self.conversion_running = True

        # Start conversion in a separate thread to prevent GUI freezing
        conversion_thread = threading.Thread(target=self.conversion_worker)
        conversion_thread.daemon = True
        conversion_thread.start()


def main():
    """
    Main function to run the PDF Converter GUI application.
    """
    root = tk.Tk()
    app = PDFConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
