# -*- coding: utf-8 -*-
import customtkinter as ctk

class HistoryPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#070B14")
        self.app = app

        # Scrollable container
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.pack(fill="both", expand=True)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def refresh(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        history = self.app.history_manager.get_history()

        # Header
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=45, pady=(32, 20))
        
        ctk.CTkLabel(
            header_frame, 
            text="Analysis History", 
            font=("Arial", 28, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame, 
            text="View your previous resume analyses and track your improvement journey.", 
            font=("Arial", 14), 
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(4, 0))

        if not history:
            self._render_empty_state()
            return

        # History Items List
        history_list = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        history_list.pack(fill="both", expand=True, padx=45, pady=(0, 30))

        for entry in reversed(history):
            self._create_history_card(history_list, entry)

    def _render_empty_state(self):
        empty_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        empty_container.pack(fill="both", expand=True, padx=45, pady=(60, 40))

        # Stylized Folder Box Graphic
        folder_box = ctk.CTkFrame(empty_container, width=90, height=80, corner_radius=16, fg_color="#1E293B", border_width=1, border_color="#334155")
        folder_box.pack(pady=(0, 18))
        folder_box.pack_propagate(False)

        folder_icon = ctk.CTkLabel(folder_box, text="\u25A4", font=("Arial", 36), text_color="#38BDF8")
        folder_icon.place(relx=0.5, rely=0.45, anchor="center")

        sparkle = ctk.CTkLabel(folder_box, text="\u2726", font=("Arial", 14), text_color="#F59E0B")
        sparkle.place(relx=0.8, rely=0.25, anchor="center")

        ctk.CTkLabel(
            empty_container, 
            text="No analyses yet", 
            font=("Arial", 22, "bold"), 
            text_color="#FFFFFF"
        ).pack(pady=(0, 6))

        ctk.CTkLabel(
            empty_container, 
            text="Your completed resume analyses will appear here.", 
            font=("Arial", 14), 
            text_color="#94A3B8"
        ).pack(pady=(0, 24))

        ctk.CTkButton(
            empty_container, 
            text="Analyze My Resume", 
            font=("Arial", 14, "bold"), 
            fg_color="#2563EB", 
            hover_color="#1D4ED8", 
            text_color="#FFFFFF",
            height=44, 
            corner_radius=8,
            command=lambda: self.app.page_manager.show_page("UploadPage")
        ).pack()

    def _create_history_card(self, parent, entry):
        card = ctk.CTkFrame(parent, fg_color="#111827", corner_radius=12, border_width=1, border_color="#1F2937")
        card.pack(fill="x", pady=6)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=16)

        left_col = ctk.CTkFrame(content, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True)

        date_str = entry.get('date', 'Recent Analysis')
        ctk.CTkLabel(left_col, text=f"Resume Analysis \u2014 {date_str}", font=("Arial", 15, "bold"), text_color="#FFFFFF", anchor="w").pack(anchor="w")

        results = entry.get('results', {})
        score = float(results.get('similarity_score', 0)) * 100
        score_color = "#10B981" if score >= 75 else ("#F59E0B" if score >= 45 else "#EF4444")
        match_label = "Good Match" if score >= 75 else ("Moderate Match" if score >= 45 else "Low Match")

        metrics_text = f"ATS Match Score: {score:.0f}% ({match_label})   \u2022   Readability: {results.get('readability', 0):.0f}/100"
        ctk.CTkLabel(left_col, text=metrics_text, font=("Arial", 13), text_color=score_color, anchor="w").pack(anchor="w", pady=(4, 0))

        # View Button
        view_btn = ctk.CTkButton(
            content, 
            text="View Analysis   \u2192", 
            font=("Arial", 12, "bold"),
            fg_color="#1E293B",
            hover_color="#2563EB",
            text_color="#FFFFFF",
            border_width=1,
            border_color="#334155",
            height=36,
            corner_radius=8,
            command=lambda e=entry.get('id'): self.view_report(e)
        )
        view_btn.pack(side="right", padx=(10, 0))

    def view_report(self, entry_id):
        analysis_entry = self.app.history_manager.get_analysis_by_id(entry_id)
        if analysis_entry:
            self.app.analysis_results = analysis_entry['results']
            self.app.page_manager.show_page("ResultsPage")
