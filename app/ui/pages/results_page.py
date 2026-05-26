import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter.messagebox as messagebox
from textwrap import wrap

class ResultsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkLabel(self, text="Analyzing...", font=("Arial", 32, "bold"), text_color="#4cc9f0")
        self.header.grid(row=0, column=0, pady=(40, 20), padx=40, sticky="w")

        # Results container
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 40))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def refresh(self):
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        results = self.app.analysis_results
        if not results:
            self.header.configure(text="Analysis Failed or Incomplete")
            ctk.CTkLabel(self.scrollable_frame, text="Something went wrong. Please try again.", font=("Arial", 18)).pack(pady=20)
            return

        self.header.configure(text="Here's the Tea ☕")

        # --- Score Card ---
        score = results.get('similarity_score', 0) * 100
        score_color = "#4cc9f0" if score > 70 else ("#fca311" if score > 40 else "#e71d36")
        
        score_card = ctk.CTkFrame(self.scrollable_frame, corner_radius=20, border_width=2, border_color=score_color)
        score_card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(score_card, text="Overall Match Score", font=("Arial", 24, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(score_card, text=f"{score:.1f}%", font=("Arial", 60, "bold"), text_color=score_color).pack(pady=5)
        ctk.CTkLabel(score_card, text="This score reflects how well your resume aligns with the job description based on keywords and phrasing.", font=("Arial", 14), wraplength=600).pack(pady=(5, 20))

        # --- Keywords Section ---
        self.create_section("Keywords Analysis 🔑", [
            ("Keywords in Job Description:", f"{len(results.get('jd_keywords', []))}"),
            ("Keywords Found in Your Resume:", f"{len(results.get('present_keywords', []))}"),
            ("Keywords Missing From Your Resume:", f"{len(results.get('missing_keywords', []))}"),
        ], self.scrollable_frame)

        # --- Missing Keywords Details ---
        missing_kw_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        missing_kw_frame.pack(fill="x", pady=(10, 20))
        
        ctk.CTkLabel(missing_kw_frame, text="💡 Pro-Tip: Weave these missing keywords naturally into your resume.", font=("Arial", 16, "italic")).pack()
        
        missing_keywords_text = ", ".join(results.get('missing_keywords', ['None! You rock!']))
        wrapped_text = '\n'.join(wrap(missing_keywords_text, 80))
        
        kw_box = ctk.CTkLabel(missing_kw_frame, text=wrapped_text, font=("Arial", 14), fg_color=("gray90", "gray20"), corner_radius=10, justify="center")
        kw_box.pack(fill="x", pady=10, ipady=10)

        # --- Readability & Stats ---
        self.create_section("Resume Stats 📊", [
            ("Word Count:", f"{results.get('word_count', 'N/A')} (Tip: Aim for 400-600 words)"),
            ("Readability Score:", f"{results.get('readability', 0):.1f}/100 (Higher is better)"),
        ], self.scrollable_frame)

        # --- Action Verbs & Metrics ---
        self.create_section("Impact Analysis 💪", [
            ("Action Verbs Found:", f"{len(results.get('action_verbs', []))}"),
            ("Quantifiable Metrics:", f"{results.get('quantifiable_metrics', 0)}"),
        ], self.scrollable_frame)

        # --- Suggestions Section ---
        suggestions = results.get('suggestions', [])
        if suggestions:
            suggestions_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=15, border_width=1, border_color="#fca311")
            suggestions_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(suggestions_frame, text="Suggestions for Improvement 💡", font=("Arial", 20, "bold"), text_color="#fca311").pack(pady=(15, 10), anchor="w", padx=20)
            
            for suggestion in suggestions:
                ctk.CTkLabel(suggestions_frame, text=f"• {suggestion}", font=("Arial", 14), wraplength=750, justify="left").pack(anchor="w", padx=25, pady=5)
            
            # Add some padding at the bottom
            ctk.CTkLabel(suggestions_frame, text="").pack()

        # --- Save Report Button ---
        save_button = ctk.CTkButton(self.scrollable_frame, text="Save Report 💾", command=self.save_report, height=40, font=("Arial", 16, "bold"))
        save_button.pack(pady=(20, 0), padx=20, fill="x")

    def save_report(self):
        if self.app.analysis_results:
            self.app.history_manager.add_analysis(self.app.analysis_results)
            messagebox.showinfo("Report Saved", "Your analysis report has been saved to your history.")
        else:
            messagebox.showwarning("No Report", "There is no analysis report to save.")

    def create_section(self, title, data, parent):
        section_frame = ctk.CTkFrame(parent, corner_radius=15, border_width=1, border_color="gray30")
        section_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(section_frame, text=title, font=("Arial", 20, "bold"), text_color="#4cc9f0").pack(pady=(15, 10), anchor="w", padx=20)
        
        for label, value in data:
            item_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            item_frame.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(item_frame, text=label, font=("Arial", 16)).pack(side="left")
            ctk.CTkLabel(item_frame, text=value, font=("Arial", 16, "bold")).pack(side="right")
