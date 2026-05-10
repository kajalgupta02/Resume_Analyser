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
            filetypes=[("Resume files", "*.pdf *.docx *.txt")]
        )
        if file_path:
            self.app.resume_path = file_path
            self.upload_label.configure(text=f"Selected: {os.path.basename(file_path)}", text_color="#4cc9f0")
            try:
                self.app.analyser.load_resume(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load resume: {str(e)}")

    def on_role_select(self, role):
        if role in self.app.analyser.job_roles:
            keywords = ", ".join(self.app.analyser.job_roles[role])
            self.jd_text.delete("1.0", "end")
            self.jd_text.insert("1.0", f"Role: {role}\n\nKey Requirements: {keywords}")

    def run_analysis(self):
        jd = self.jd_text.get("1.0", "end-1c").strip()
        if not self.app.resume_path:
            messagebox.showwarning("Hold Up!", "You forgot to upload your resume, babe.")
            return
        if not jd or "paste the job description" in jd:
            messagebox.showwarning("Wait a minute...", "We need to know what job you're aiming for!")
            return
            
        # Show loading state with animation
        self.analyze_button.configure(state="disabled", text="DECODING YOUR FUTURE... 🧠")
        self.loading_bar.pack(pady=10)
        self.loading_bar.start()
        
        # Run analysis in a separate thread
        def thread_target():
            import time
            time.sleep(1.5) # Dramatic pause for "AI thinking"
            try:
                self.app.analyser.set_job_description(jd)
                results = self.app.analyser.analyze()
                self.after(0, lambda: self.finish_analysis(results))
            except Exception as e:
                self.after(0, lambda: self.handle_analysis_error(e))

        threading.Thread(target=thread_target, daemon=True).start()

    def finish_analysis(self, results):
        self.loading_bar.stop()
        self.loading_bar.pack_forget()
        self.analyze_button.configure(state="normal", text="WORK YOUR MAGIC ✨")
        if results:
            self.app.analysis_results = results
            self.master.show_page("ResultsPage")
        else:
            messagebox.showerror("Oops!", "Something went wrong. Even AI has bad days.")

    def handle_analysis_error(self, error):
        self.loading_bar.stop()
        self.loading_bar.pack_forget()
        self.analyze_button.configure(state="normal", text="WORK YOUR MAGIC ✨")
        messagebox.showerror("Oops!", f"Error during analysis: {str(error)}")
