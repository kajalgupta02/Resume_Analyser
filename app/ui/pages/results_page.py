import customtkinter as ctk
import tkinter.messagebox as messagebox
from textwrap import wrap


class ResultsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(34, 12))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkLabel(
            self.header_frame,
            text="Analysis Report",
            font=("Arial", 32, "bold"),
            text_color="#4cc9f0"
        )
        self.header.grid(row=0, column=0, sticky="w")

        self.subheader = ctk.CTkLabel(
            self.header_frame,
            text="A practical breakdown of resume fit, gaps, and next actions.",
            font=("Arial", 16),
            text_color=("gray35", "gray80")
        )
        self.subheader.grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=(0, 40))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

    def refresh(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        results = self.app.analysis_results
        if not results:
            self.header.configure(text="No Analysis Available")
            self.subheader.configure(text="Run a resume analysis to see a score, keyword gaps, and tailored recommendations.")

            empty_state = ctk.CTkFrame(self.scrollable_frame, corner_radius=20, border_width=1, border_color="gray30")
            empty_state.pack(fill="x", pady=(12, 20))

            ctk.CTkLabel(
                empty_state,
                text="Upload a resume and start an analysis to generate this report.",
                font=("Arial", 18, "bold")
            ).pack(pady=(22, 8), padx=20)
            ctk.CTkLabel(
                empty_state,
                text="You will get a match score, keyword coverage, section checks, and a clear set of improvements.",
                font=("Arial", 14),
                wraplength=780,
                justify="center"
            ).pack(pady=(0, 22), padx=20)
            return

        self.header.configure(text="Resume Match Report")
        self.subheader.configure(text="A concise summary of alignment, evidence, and the highest-value edits.")

        score = float(results.get('similarity_score', 0)) * 100
        score_color, score_label, score_message = self.get_score_context(score)

        hero_card = ctk.CTkFrame(self.scrollable_frame, corner_radius=24, border_width=2, border_color=score_color)
        hero_card.pack(fill="x", pady=(0, 18))
        hero_card.grid_columnconfigure(0, weight=1)
        hero_card.grid_columnconfigure(1, weight=1)

        hero_left = ctk.CTkFrame(hero_card, fg_color="transparent")
        hero_left.grid(row=0, column=0, sticky="nsew", padx=(22, 12), pady=22)

        ctk.CTkLabel(hero_left, text=score_label, font=("Arial", 18, "bold"), text_color=score_color).pack(anchor="w")
        ctk.CTkLabel(hero_left, text=f"{score:.1f}%", font=("Arial", 58, "bold"), text_color=score_color).pack(anchor="w", pady=(4, 0))
        ctk.CTkLabel(hero_left, text=score_message, font=("Arial", 15), wraplength=480, justify="left").pack(anchor="w", pady=(8, 0))

        hero_right = ctk.CTkFrame(hero_card, fg_color="transparent")
        hero_right.grid(row=0, column=1, sticky="nsew", padx=(12, 22), pady=22)

        self.create_metric_row(hero_right, "Similarity mode", results.get('similarity_mode', 'tfidf').upper())
        self.create_metric_row(hero_right, "Keywords found", f"{len(results.get('present_keywords', []))}/{len(results.get('jd_keywords', []))}")
        self.create_metric_row(hero_right, "Action verbs", f"{len(results.get('action_verbs', []))}")
        self.create_metric_row(hero_right, "Quantifiable metrics", f"{results.get('quantifiable_metrics', 0)}")
        self.create_metric_row(hero_right, "Readability", f"{results.get('readability', 0):.1f}/100")

        self.create_section(
            "What this means",
            [
                ("Alignment", self.get_alignment_text(score)),
                ("Word count", f"{results.get('word_count', 'N/A')} words"),
                ("Readability", f"{results.get('readability', 0):.1f}/100"),
            ],
            self.scrollable_frame
        )

        keyword_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=18, border_width=1, border_color="gray30")
        keyword_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(keyword_frame, text="Keyword Coverage", font=("Arial", 20, "bold"), text_color="#4cc9f0").pack(pady=(15, 8), anchor="w", padx=20)
        self.create_metric_row(keyword_frame, "Keywords in job description", f"{len(results.get('jd_keywords', []))}", pad_x=20)
        self.create_metric_row(keyword_frame, "Keywords already present", f"{len(results.get('present_keywords', []))}", pad_x=20)
        self.create_metric_row(keyword_frame, "Keywords to add", f"{len(results.get('missing_keywords', []))}", pad_x=20)

        missing_keywords = results.get('missing_keywords', [])
        missing_keywords_text = ", ".join(missing_keywords) if missing_keywords else "No major keyword gaps were detected."
        wrapped_text = '\n'.join(wrap(missing_keywords_text, 78))

        kw_box = ctk.CTkLabel(
            keyword_frame,
            text=wrapped_text,
            font=("Arial", 14),
            fg_color=("gray92", "gray18"),
            corner_radius=12,
            justify="left",
            anchor="w"
        )
        kw_box.pack(fill="x", padx=20, pady=(10, 18), ipady=10)

        self.create_section(
            "Resume Signals",
            [
                ("Action verbs found", f"{len(results.get('action_verbs', []))}"),
                ("Quantifiable metrics", f"{results.get('quantifiable_metrics', 0)}"),
            ],
            self.scrollable_frame
        )

        tfidf_similarity = float(results.get('tfidf_similarity_score', results.get('similarity_score', 0.0))) * 100
        semantic_similarity = results.get('semantic_similarity_score')
        semantic_available = bool(results.get('semantic_similarity_available', False))
        self.create_section(
            "Similarity Comparison",
            [
                ("TF-IDF score", f"{tfidf_similarity:.1f}%"),
                ("Semantic score", f"{float(semantic_similarity) * 100:.1f}%" if semantic_similarity is not None else "Unavailable"),
                ("Semantic mode", "Ready" if semantic_available else "Falling back to TF-IDF"),
            ],
            self.scrollable_frame,
        )

        sections = results.get('sections', {})
        if sections:
            section_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=18, border_width=1, border_color="gray30")
            section_frame.pack(fill="x", pady=10)
            ctk.CTkLabel(section_frame, text="ATS Section Check", font=("Arial", 20, "bold"), text_color="#4cc9f0").pack(pady=(15, 8), anchor="w", padx=20)
            for section_name, present in sections.items():
                row = ctk.CTkFrame(section_frame, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=4)
                status_text = "Included" if present else "Missing"
                status_color = "#2ec4b6" if present else "#e71d36"
                ctk.CTkLabel(row, text=section_name, font=("Arial", 15)).pack(side="left")
                ctk.CTkLabel(row, text=status_text, font=("Arial", 15, "bold"), text_color=status_color).pack(side="right")

        suggestions = results.get('suggestions', [])
        if suggestions:
            suggestions_frame = ctk.CTkFrame(self.scrollable_frame, corner_radius=15, border_width=1, border_color="#fca311")
            suggestions_frame.pack(fill="x", pady=10)

            ctk.CTkLabel(suggestions_frame, text="Priority Improvements", font=("Arial", 20, "bold"), text_color="#fca311").pack(pady=(15, 10), anchor="w", padx=20)

            for suggestion in suggestions:
                ctk.CTkLabel(suggestions_frame, text=f"• {suggestion}", font=("Arial", 14), wraplength=750, justify="left").pack(anchor="w", padx=25, pady=5)

            ctk.CTkLabel(suggestions_frame, text="").pack()

        save_button = ctk.CTkButton(self.scrollable_frame, text="Save to History", command=self.save_report, height=42, font=("Arial", 16, "bold"))
        save_button.pack(pady=(20, 0), padx=20, fill="x")

    def save_report(self):
        if self.app.analysis_results:
            self.app.history_manager.add_analysis(self.app.analysis_results)
            messagebox.showinfo("Report Saved", "The report has been added to your history.")
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

    def create_metric_row(self, parent, label, value, pad_x=0):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=pad_x, pady=4)
        ctk.CTkLabel(row, text=label, font=("Arial", 14)).pack(side="left")
        ctk.CTkLabel(row, text=value, font=("Arial", 14, "bold")).pack(side="right")

    def get_score_context(self, score):
        if score >= 75:
            return "#2ec4b6", "Strong Match", "Your resume is closely aligned with the role. Focus on sharpening impact statements and keeping the strongest evidence near the top."
        if score >= 45:
            return "#fca311", "Moderate Match", "The foundation is there, but several keywords and signals still need to be added or tightened to improve fit."
        return "#e71d36", "Low Match", "The resume needs more role-specific language and stronger evidence before it will read as a competitive fit."

    def get_alignment_text(self, score):
        if score >= 75:
            return "High alignment with the target role"
        if score >= 45:
            return "Moderate alignment, with several clear gaps"
        return "Low alignment; the resume needs deeper tailoring"
