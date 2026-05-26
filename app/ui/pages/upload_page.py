import customtkinter as ctk

from tkinter import filedialog, messagebox
import os

import threading

class UploadPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        # Sassy Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=40, pady=(40, 20))
        
        ctk.CTkLabel(self.header_frame, 
                     text="Let's Get Analyzing. 🔍", 
                     font=("Arial", 32, "bold"),
                     text_color="#4cc9f0").pack(side="left")
        
        ctk.CTkLabel(self, 
                     text="Upload your resume and tell us what job you're eyeing. We'll handle the rest.",
                     font=("Arial", 16)).pack(anchor="w", padx=40, pady=(0, 30))
        
        # Main Layout: Two columns
        self.content_grid = ctk.CTkFrame(self, fg_color="transparent")
        self.content_grid.pack(fill="both", expand=True, padx=40)
        self.content_grid.grid_columnconfigure((0, 1), weight=1)
        self.content_grid.grid_rowconfigure(0, weight=1)
        
        # Left Column: Upload
        self.left_col = ctk.CTkFrame(self.content_grid, corner_radius=20, border_width=1, border_color="#4361ee")
        self.left_col.grid(row=0, column=0, padx=(0, 15), sticky="nsew")
        
        ctk.CTkLabel(self.left_col, text="1. The Goods 📄", font=("Arial", 22, "bold"), text_color="#4cc9f0").pack(pady=20)
        
        self.upload_area = ctk.CTkFrame(self.left_col, height=200, fg_color=("gray90", "gray15"), corner_radius=20, border_width=0)
        self.upload_area.pack(pady=10, padx=25, fill="x")
        self.upload_area.pack_propagate(False)
        
        # Hover effects for upload area
        self.upload_area.bind("<Enter>", lambda e: self.upload_area.configure(border_width=2, border_color="#4cc9f0"))
        self.upload_area.bind("<Leave>", lambda e: self.upload_area.configure(border_width=0))
        
        self.upload_label = ctk.CTkLabel(self.upload_area, 
                                        text="Drop your resume here\nor click to browse",
                                        font=("Arial", 14),
                                        text_color="gray")
        self.upload_label.place(relx=0.5, rely=0.4, anchor="center")
        
        self.browse_button = ctk.CTkButton(self.upload_area, 
                                          text="Browse Files", 
                                          fg_color="#4cc9f0",
                                          hover_color="#4361ee",
                                          text_color="black",
                                          font=("Arial", 13, "bold"),
                                          command=self.browse_files)
        self.browse_button.place(relx=0.5, rely=0.7, anchor="center")
        
        # Right Column: JD
        self.right_col = ctk.CTkFrame(self.content_grid, corner_radius=20, border_width=1, border_color="#4361ee")
        self.right_col.grid(row=0, column=1, padx=(15, 0), sticky="nsew")
        
        ctk.CTkLabel(self.right_col, text="2. The Goal 🎯", font=("Arial", 22, "bold"), text_color="#4cc9f0").pack(pady=20)
        
        # Role selection
        self.role_var = ctk.StringVar(value="Pick a dream role...")
        self.role_dropdown = ctk.CTkOptionMenu(self.right_col, 
                                             values=list(self.app.analyser.job_roles.keys()),
                                             variable=self.role_var,
                                             fg_color="#4361ee",
                                             button_color="#4361ee",
                                             height=40,
                                             corner_radius=10,
                                             command=self.on_role_select)
        self.role_dropdown.pack(fill="x", padx=25, pady=(0, 15))
        
        self.jd_text = ctk.CTkTextbox(self.right_col, height=140, corner_radius=20, border_width=1, border_color="gray30")
        self.jd_text.pack(pady=10, padx=25, fill="both", expand=True)
        self.jd_text.insert("0.0", "Or paste the job description here...")
        
        # Footer Action
        self.right_col.grid_rowconfigure(2, weight=1) # Push button down
        
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.pack(pady=(20, 40), fill="x", padx=40)

        ctk.CTkLabel(self.action_frame, text="3. The Magic Moment ✨", font=("Arial", 22, "bold"), text_color="#4cc9f0").pack(pady=(0, 20))

        self.analyze_button = ctk.CTkButton(self.action_frame, 
                                          text="WORK YOUR MAGIC ✨", 
                                          height=70,
                                          width=500,
                                          fg_color="#4cc9f0",
                                          hover_color="#4361ee",
                                          text_color="#000000",
                                          font=("Arial", 20, "bold"),
                                          corner_radius=35,
                                          command=self.run_analysis)
        self.analyze_button.pack()

        self.loading_bar = ctk.CTkProgressBar(self.action_frame, width=500, mode="indeterminate", 
                                             progress_color="#4cc9f0", height=10, corner_radius=5)
        self.loading_bar.pack(pady=15)
        self.loading_bar.set(0)
        self.loading_bar.pack_forget() # Hide initially

    def browse_files(self):
        file_path = filedialog.askopenfilename(
            title="Select your masterpiece (aka resume)",
            filetypes=(("PDF files", "*.pdf"), ("Word files", "*.docx"), ("Text files", "*.txt"), ("All files", "*.*"))
        )
        if file_path:
            self.app.resume_path = file_path
            filename = os.path.basename(file_path)
            self.upload_label.configure(text=f"Selected: {filename}", text_color="#4cc9f0")
            self.browse_button.configure(text="Change File")

    def on_role_select(self, role):
        if role in self.app.analyser.job_roles:
            keywords = ", ".join(self.app.analyser.job_roles[role])
            self.jd_text.delete("0.0", "end")
            self.jd_text.insert("0.0", f"Keywords for {role}:\n{keywords}")

    def run_analysis(self):
        if not self.app.resume_path:
            messagebox.showerror("Hold Up!", "You forgot to upload your resume. Let's not get ahead of ourselves.")
            return

        job_description = self.jd_text.get("0.0", "end").strip()
        if not job_description or job_description == "Or paste the job description here...":
            messagebox.showerror("What's the Goal?", "Please select a role or paste a job description. I'm smart, but not a mind reader.")
            return

        self.analyze_button.configure(text="ANALYZING...", state="disabled")
        self.app.page_manager.show_page("ResultsPage")

        def analysis_thread():
            try:
                self.app.analyser.load_resume(self.app.resume_path)
                self.app.analyser.set_job_description(job_description)
                self.app.analysis_results = self.app.analyser.analyze()
                
                # Switch back to main thread to update UI
                self.app.after(100, self.on_analysis_complete)
            except Exception as e:
                self.app.after(100, lambda: self.on_analysis_error(e))

        threading.Thread(target=analysis_thread, daemon=True).start()

    def on_analysis_complete(self):
        self.analyze_button.configure(text="WORK YOUR MAGIC ✨", state="normal")
        results_page = self.app.page_manager.pages.get("ResultsPage")
        if results_page:
            results_page.refresh()

    def on_analysis_error(self, error):
        self.analyze_button.configure(text="WORK YOUR MAGIC ✨", state="normal")
        messagebox.showerror("Uh Oh!", f"An error occurred during analysis:\n{error}")
        self.app.page_manager.show_page("UploadPage")

    def refresh(self):
        # Reset fields on page view
        self.app.resume_path = None
        self.upload_label.configure(text="Drop your resume here\nor click to browse", text_color="gray")
        self.browse_button.configure(text="Browse Files")
        self.role_var.set("Pick a dream role...")
        self.jd_text.delete("0.0", "end")
        self.jd_text.insert("0.0", "Or paste the job description here...")
