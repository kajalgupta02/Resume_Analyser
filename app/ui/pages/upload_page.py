# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from ...logic.sample_data import SAMPLE_JOB_DESCRIPTIONS

class UploadPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#070B14")
        self.app = app
        
        # Scrollable container for responsive layout
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)
        self.main_scroll.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=45, pady=(32, 18))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Analyze Your Resume", 
            font=("Arial", 28, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Upload your resume and add a job description to receive clear, role-specific improvement suggestions.", 
            font=("Arial", 14), 
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(4, 0))
        
        # 3-Column Steps Layout
        self.content_grid = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.content_grid.pack(fill="both", expand=True, padx=45, pady=(0, 30))
        self.content_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="steps")
        self.content_grid.grid_rowconfigure(0, weight=1)
        
        self._create_step1_upload()
        self._create_step2_job_desc()
        self._create_step3_review()

    def _create_step_header(self, parent, num, title, subtitle):
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 6))
        
        circle = ctk.CTkFrame(header, width=28, height=28, corner_radius=14, fg_color="#2563EB")
        circle.pack(side="left")
        circle.pack_propagate(False)
        ctk.CTkLabel(circle, text=num, font=("Arial", 12, "bold"), text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(header, text=title, font=("Arial", 15, "bold"), text_color="#FFFFFF").pack(side="left", padx=10)
        
        if subtitle:
            ctk.CTkLabel(parent, text=subtitle, font=("Arial", 12), text_color="#94A3B8", justify="left").pack(anchor="w", padx=24, pady=(0, 12))

    def _create_step1_upload(self):
        # Column 1: Resume Upload
        self.col1 = ctk.CTkFrame(self.content_grid, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        self.col1.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self._create_step_header(self.col1, "1", "Upload Your Resume", "Upload your resume in PDF, DOCX, or TXT format.")
        
        # Upload Box Area
        self.upload_area = ctk.CTkFrame(self.col1, fg_color="#1A2234", corner_radius=12, border_width=2, border_color="#2A374F")
        self.upload_area.pack(pady=(0, 16), padx=20, fill="both", expand=True)
        
        self.upload_icon = ctk.CTkLabel(self.upload_area, text="\u2601", font=("Arial", 42), text_color="#38BDF8")
        self.upload_icon.place(relx=0.5, rely=0.32, anchor="center")
        
        self.upload_label = ctk.CTkLabel(
            self.upload_area, 
            text="Drag & drop your file here\nor", 
            font=("Arial", 13), 
            text_color="#94A3B8"
        )
        self.upload_label.place(relx=0.5, rely=0.54, anchor="center")
        
        self.browse_button = ctk.CTkButton(
            self.upload_area, 
            text="Choose Resume", 
            fg_color="#2563EB", 
            hover_color="#1D4ED8", 
            text_color="#FFFFFF",
            font=("Arial", 13, "bold"), 
            corner_radius=8,
            height=36,
            command=self.browse_files
        )
        self.browse_button.place(relx=0.5, rely=0.76, anchor="center")
        
        # Selected File Status Box
        self.file_status_frame = ctk.CTkFrame(self.col1, fg_color="#1A2234", corner_radius=8, border_width=1, border_color="#2A374F")
        self.file_status_frame.pack(fill="x", padx=20, pady=(0, 14))
        
        self.file_name_label = ctk.CTkLabel(
            self.file_status_frame, 
            text="No file selected yet", 
            font=("Arial", 12), 
            text_color="#94A3B8"
        )
        self.file_name_label.pack(side="left", padx=12, pady=10)
        
        self.change_file_btn = ctk.CTkButton(
            self.file_status_frame, 
            text="Change", 
            fg_color="transparent", 
            border_width=1, 
            border_color="#334155", 
            hover_color="#1E293B", 
            text_color="#FFFFFF",
            width=70, 
            height=28,
            font=("Arial", 11),
            command=self.browse_files
        )
        self.change_file_btn.pack(side="right", padx=10, pady=8)
        self.change_file_btn.pack_forget() # hide until file is picked
        
        # Supported format footer
        ctk.CTkLabel(
            self.col1, 
            text="Supported formats: PDF, DOCX, TXT", 
            font=("Arial", 11), 
            text_color="#64748B"
        ).pack(anchor="w", padx=20, pady=(0, 16))

    def _create_step2_job_desc(self):
        # Column 2: Job Description
        self.col2 = ctk.CTkFrame(self.content_grid, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        self.col2.grid(row=0, column=1, padx=10, sticky="nsew")
        
        self._create_step_header(self.col2, "2", "Add a Job Description", "Choose a sample role (optional)")
        
        # Sample Role Dropdown
        roles_list = ["Select a role..."] + list(SAMPLE_JOB_DESCRIPTIONS.keys())
        self.role_var = ctk.StringVar(value="Select a role...")
        self.role_dropdown = ctk.CTkOptionMenu(
            self.col2, 
            values=roles_list,
            variable=self.role_var,
            fg_color="#1E293B", 
            button_color="#2563EB", 
            button_hover_color="#1D4ED8", 
            dropdown_fg_color="#1E293B",
            text_color="#FFFFFF",
            height=38, 
            corner_radius=8,
            font=("Arial", 13),
            command=self.on_role_select
        )
        self.role_dropdown.pack(fill="x", padx=20, pady=(0, 12))
        
        ctk.CTkLabel(
            self.col2, 
            text="Job Description Text", 
            font=("Arial", 13, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=20, pady=(0, 6))
        
        # Textbox for Job Description
        self.jd_text = ctk.CTkTextbox(
            self.col2, 
            fg_color="#1A2234", 
            corner_radius=8, 
            border_width=1, 
            border_color="#2A374F",
            text_color="#E2E8F0",
            font=("Arial", 12)
        )
        self.jd_text.pack(pady=(0, 18), padx=20, fill="both", expand=True)
        self.jd_text.insert("0.0", "Paste the job description here or choose a sample role above...")

    def _create_step3_review(self):
        # Column 3: Review and Action
        self.col3 = ctk.CTkFrame(self.content_grid, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        self.col3.grid(row=0, column=2, padx=(10, 0), sticky="nsew")
        
        self._create_step_header(self.col3, "3", "Review Your Results", "Click the button below to\nstart analyzing your resume.")
        
        # Stylized Review Graphic in center
        self.review_center = ctk.CTkFrame(self.col3, fg_color="transparent")
        self.review_center.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Icon Badge Frame
        icon_card = ctk.CTkFrame(self.review_center, fg_color="#1A2234", corner_radius=16, border_width=1, border_color="#2A374F")
        icon_card.place(relx=0.5, rely=0.42, anchor="center", relwidth=0.85, relheight=0.7)
        
        doc_symbol = ctk.CTkLabel(icon_card, text="\u25A4", font=("Arial", 46), text_color="#38BDF8")
        doc_symbol.place(relx=0.45, rely=0.4, anchor="center")
        
        mag_symbol = ctk.CTkLabel(icon_card, text="\u2315", font=("Arial", 36, "bold"), text_color="#60A5FA")
        mag_symbol.place(relx=0.62, rely=0.58, anchor="center")
        
        sparkle = ctk.CTkLabel(icon_card, text="\u2726", font=("Arial", 18), text_color="#F59E0B")
        sparkle.place(relx=0.25, rely=0.25, anchor="center")
        
        ready_label = ctk.CTkLabel(icon_card, text="Instant ATS Score & AI Feedback", font=("Arial", 11, "bold"), text_color="#94A3B8")
        ready_label.place(relx=0.5, rely=0.84, anchor="center")
        
        # Analyze CTA Button
        self.analyze_button = ctk.CTkButton(
            self.col3, 
            text="Analyze Resume", 
            height=48, 
            fg_color="#2563EB", 
            hover_color="#1D4ED8", 
            text_color="#FFFFFF",
            font=("Arial", 15, "bold"), 
            corner_radius=10,
            command=self.run_analysis
        )
        self.analyze_button.pack(fill="x", padx=20, pady=(10, 16))
        
        # Indeterminate Loading Bar
        self.loading_bar = ctk.CTkProgressBar(self.col3, mode="indeterminate", progress_color="#38BDF8", height=6)
        self.loading_bar.pack(fill="x", padx=20, pady=(0, 16))
        self.loading_bar.set(0)
        self.loading_bar.pack_forget()

    def browse_files(self):
        file_path = filedialog.askopenfilename(
            title="Choose your resume",
            filetypes=(("Supported Resumes (*.pdf;*.docx;*.txt)", "*.pdf;*.docx;*.txt"), ("PDF files", "*.pdf"), ("Word files", "*.docx"), ("Text files", "*.txt"), ("All files", "*.*"))
        )
        if file_path:
            self.app.resume_path = file_path
            filename = os.path.basename(file_path)
            self.file_name_label.configure(text=f"\u2714 {filename}", text_color="#34D399")
            self.change_file_btn.pack(side="right", padx=10, pady=8)
            self.upload_label.configure(text=f"Loaded: {filename}", text_color="#38BDF8")

    def on_role_select(self, role):
        if role in SAMPLE_JOB_DESCRIPTIONS:
            job_text = SAMPLE_JOB_DESCRIPTIONS[role]
            self.jd_text.delete("0.0", "end")
            self.jd_text.insert("0.0", job_text)

    def run_analysis(self):
        if not self.app.resume_path:
            messagebox.showerror("No Resume Selected", "Please upload your resume (PDF, DOCX, or TXT) before starting the analysis.")
            return

        job_description = self.jd_text.get("0.0", "end").strip()
        if not job_description or job_description.startswith("Paste the job description here"):
            messagebox.showerror("Job Description Needed", "Please select a sample role or paste a job description to receive role-specific recommendations.")
            return

        self.analyze_button.configure(text="Analyzing Resume...", state="disabled")
        self.loading_bar.pack(fill="x", padx=20, pady=(0, 16))
        self.loading_bar.start()

        def analysis_thread():
            try:
                self.app.analyser.load_resume(self.app.resume_path)
                self.app.analyser.set_job_description(job_description)
                self.app.analyser.set_similarity_mode("tfidf")
                self.app.analysis_results = self.app.analyser.analyze()
                
                self.app.after(100, self.on_analysis_complete)
            except Exception as e:
                self.app.after(100, lambda: self.on_analysis_error(e))

        threading.Thread(target=analysis_thread, daemon=True).start()

    def on_analysis_complete(self):
        self.analyze_button.configure(text="Analyze Resume", state="normal")
        self.loading_bar.stop()
        self.loading_bar.pack_forget()
        
        # Save to history automatically upon analysis
        if self.app.analysis_results:
            self.app.history_manager.add_analysis(self.app.analysis_results)
            
        self.app.page_manager.show_page("ResultsPage")
        results_page = self.app.page_manager.pages.get("ResultsPage")
        if results_page:
            results_page.refresh()

    def on_analysis_error(self, error):
        self.analyze_button.configure(text="Analyze Resume", state="normal")
        self.loading_bar.stop()
        self.loading_bar.pack_forget()
        messagebox.showerror("Analysis Error", f"Your resume could not be processed: {str(error)}")

    def refresh(self):
        # Keep selected resume if user returns, but reset role if empty
        if not self.app.resume_path:
            self.file_name_label.configure(text="No file selected yet", text_color="#94A3B8")
            self.change_file_btn.pack_forget()
            self.upload_label.configure(text="Drag & drop your file here\nor", text_color="#94A3B8")
            self.role_var.set("Select a role...")
            self.jd_text.delete("0.0", "end")
            self.jd_text.insert("0.0", "Paste the job description here or choose a sample role above...")
