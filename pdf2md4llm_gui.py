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
        self.root.geometry("500x200")
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
        self.setup_widgets()


    def setup_main_frame(self):
        """Setup the main container frame."""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))


    def setup_variables(self):
        """Initialize tkinter variables."""
        self.file_type_var = tk.StringVar(value="md")  # Default to markdown
        self.batch_mode_var = tk.BooleanVar(value=False)


    def setup_widgets(self):
        """Create and arrange all GUI widgets."""
        # Mode selection
        mode_frame = ttk.LabelFrame(self.main_frame, text="Conversion Mode", padding="5")
        mode_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

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
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Single file selection (default view)
        self.single_file_frame = ttk.Frame(file_frame)
        self.single_file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(self.single_file_frame, text="PDF File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.pdf_path_var = tk.StringVar()
        self.pdf_entry = ttk.Entry(self.single_file_frame, textvariable=self.pdf_path_var, width=50)
        self.pdf_entry.grid(row=0, column=1, padx=(5, 0), pady=2)
        ttk.Button(
            self.single_file_frame,
            text="Browse",
            command=self.browse_pdf_file
        ).grid(row=0, column=2, padx=(5, 0), pady=2)

        # Batch file selection (hidden by default)
        self.batch_file_frame = ttk.Frame(file_frame)

        ttk.Label(self.batch_file_frame, text="Selected Files:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Button(
            self.batch_file_frame,
            text="Add Files",
            command=self.browse_batch_files
        ).grid(row=0, column=1, padx=(5, 0), pady=2)
        ttk.Button(
            self.batch_file_frame,
            text="Clear All",
            command=self.clear_batch_files
        ).grid(row=0, column=2, padx=(5, 0), pady=2)

        # Listbox for batch files
        self.batch_listbox = tk.Listbox(self.batch_file_frame, height=6, width=70)
        self.batch_listbox.grid(row=1, column=0, columnspan=3, pady=(5, 0), sticky=(tk.W, tk.E))

        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(self.batch_file_frame, orient=tk.VERTICAL, command=self.batch_listbox.yview)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S), pady=(5, 0))
        self.batch_listbox.config(yscrollcommand=scrollbar.set)

        # Output settings
        output_frame = ttk.LabelFrame(self.main_frame, text="Output Settings", padding="5")
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Output directory selection
        ttk.Label(output_frame, text="Output Directory (optional):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.output_path_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=50)
        self.output_entry.grid(row=0, column=1, padx=(5, 0), pady=2)
        ttk.Button(
            output_frame,
            text="Browse",
            command=self.browse_output_directory
        ).grid(row=0, column=2, padx=(5, 0), pady=2)

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

        # Conversion button and progress
        control_frame = ttk.Frame(self.main_frame)
        control_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        self.convert_button = ttk.Button(control_frame, text="Convert PDF(s)", command=self.start_conversion)
        self.convert_button.grid(row=0, column=0, padx=(0, 10))

        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(control_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=1)

        self.progress_bar = ttk.Progressbar(control_frame, mode="indeterminate")
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))


    def toggle_mode(self):
        """Toggle between single file and batch mode."""
        self.is_batch_mode = self.batch_mode_var.get()

        if self.is_batch_mode:
            # Switch to batch mode
            self.single_file_frame.grid_remove()
            self.batch_file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
            self.root.geometry("600x400")
            self.root.resizable(True, True)
        else:
            # Switch to single file mode
            self.batch_file_frame.grid_remove()
            self.single_file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
            self.root.geometry("500x200")
            self.root.resizable(False, False)


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


    def browse_output_directory(self):
        """Open dialog to select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory = Path(directory)
            self.output_path_var.set(str(self.output_directory))


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


    def get_output_path(self, input_path: Path) -> Path:
        """
        Generate output path for a given input PDF file.

        Arguments:
            input_path (Path): Path to the input PDF file

        Returns:
            output_path (Path): Path where the converted file will be saved
        """
        file_extension = self.file_type_var.get()

        if self.output_directory:
            # Use specified output directory
            output_path = self.output_directory / f"{input_path.stem}.{file_extension}"
        else:
            # Use same directory as input file
            output_path = input_path.with_suffix(f".{file_extension}")

        return output_path


    def convert_single_file(self, pdf_path: Path, output_path: Path):
        """
        Convert a single PDF file to markdown/text.

        Arguments:
            pdf_path (Path): Path to the PDF file to convert
            output_path (Path): Path where the converted file will be saved
        """
        try:
            # Update progress
            self.progress_var.set(f"Converting '{pdf_path.name}'...")
            self.root.update_idletasks()

            # Convert the document to markdown
            md_text = pymupdf4llm.to_markdown(str(pdf_path))

            # Write the converted text to the output file
            output_path.write_bytes(md_text.encode("utf-8"))

        except Exception as e:
            raise Exception(f"Error converting '{pdf_path.name}': {str(e)}") from e


    def conversion_worker(self):
        """
        Worker function that runs the conversion process in a separate thread.
        This prevents the GUI from freezing during conversion.
        """
        try:
            self.progress_bar.start()

            if self.is_batch_mode:
                # Batch conversion
                total_files = len(self.batch_files)
                for i, pdf_path in enumerate(self.batch_files, 1):
                    output_path = self.get_output_path(pdf_path)
                    self.convert_single_file(pdf_path, output_path)

                    # Update progress
                    self.progress_var.set(f"Completed {i}/{total_files} files")
                    self.root.update_idletasks()

                self.progress_var.set(f"Batch conversion completed! {total_files} files processed.")
                messagebox.showinfo("Success", f"Successfully converted {total_files} PDF files!")

            else:
                # Single file conversion
                output_path = self.get_output_path(self.selected_pdf_path)
                self.convert_single_file(self.selected_pdf_path, output_path)

                self.progress_var.set(f"Conversion completed!")
                messagebox.showinfo(
                    "Success",
                    f"Successfully converted '{self.selected_pdf_path.name}' to '{output_path.name}'!\n\n"
                    + f"Saved to: {output_path}"
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
