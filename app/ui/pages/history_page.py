import customtkinter as ctk

class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        ctk.CTkLabel(self, text="Your Saved Reports 📜", font=("Arial", 32, "bold"), text_color="#4cc9f0").grid(row=0, column=0, pady=(40, 20), padx=40, sticky="w")

        # History container
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 40))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def refresh(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        history = self.app.history_manager.get_history()

        if not history:
            ctk.CTkLabel(self.scrollable_frame, text="No saved reports yet. Go analyze a resume!", font=("Arial", 18)).pack(pady=20)
            return

        for entry in history:
            self._create_history_entry(entry)

    def _create_history_entry(self, entry):
        entry_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=15, border_width=1, border_color="gray30")
        entry_frame.pack(fill="x", pady=10)

        score = entry['results'].get('similarity_score', 0) * 100
        score_color = "#4cc9f0" if score > 70 else ("#fca311" if score > 40 else "#e71d36")

        ctk.CTkLabel(entry_frame, text=f"Report from {entry['date']}", font=("Arial", 18, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        ctk.CTkLabel(entry_frame, text=f"Match Score: {score:.1f}%", font=("Arial", 16), text_color=score_color).pack(anchor="w", padx=20)

        view_button = ctk.CTkButton(entry_frame, text="View Report", command=lambda e=entry['id']: self.view_report(e))
        view_button.pack(anchor="e", padx=20, pady=(0, 10))

    def view_report(self, entry_id):
        analysis_entry = self.app.history_manager.get_analysis_by_id(entry_id)
        if analysis_entry:
            self.app.analysis_results = analysis_entry['results']
            self.app.page_manager.show_page("ResultsPage")
