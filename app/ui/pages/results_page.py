# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter.messagebox as messagebox
import tkinter as tk

class ResultsPage(ctk.CTkFrame):
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

        results = self.app.analysis_results
        if not results:
            self._render_empty_state()
            return

        self._render_header()
        self._render_top_metrics_grid(results)
        self._render_mid_details_grid(results)
        self._render_next_steps_card(results)
        self._render_ai_feedback_if_any(results)

    def _render_empty_state(self):
        empty_container = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        empty_container.pack(fill="both", expand=True, padx=45, pady=80)
        
        # Empty state icon
        icon_box = ctk.CTkFrame(empty_container, width=70, height=70, corner_radius=35, fg_color="#1E293B", border_width=1, border_color="#334155")
        icon_box.pack(pady=(0, 20))
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="\u2315", font=("Arial", 28), text_color="#38BDF8").place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(
            empty_container, 
            text="No Analysis Results Yet", 
            font=("Arial", 22, "bold"), 
            text_color="#FFFFFF"
        ).pack(pady=(0, 8))
        
        ctk.CTkLabel(
            empty_container, 
            text="Upload your resume and select a job description to see your ATS match score, keyword breakdown, and tailored suggestions.", 
            font=("Arial", 14), 
            text_color="#94A3B8",
            wraplength=520,
            justify="center"
        ).pack(pady=(0, 24))
        
        ctk.CTkButton(
            empty_container, 
            text="Start Resume Analysis   \u2192", 
            font=("Arial", 14, "bold"), 
            fg_color="#2563EB", 
            hover_color="#1D4ED8", 
            text_color="#FFFFFF",
            height=44, 
            corner_radius=8,
            command=lambda: self.app.page_manager.show_page("UploadPage")
        ).pack()

    def _render_header(self):
        header_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=45, pady=(30, 16))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_box,
            text="Resume Analysis Results",
            font=("Arial", 28, "bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="Here is how your resume matches the job description and areas you can improve.",
            font=("Arial", 14),
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(3, 0))

        # Top Right Action Buttons
        actions_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_box.grid(row=0, column=1, sticky="e")

        download_btn = ctk.CTkButton(
            actions_box,
            text=" \u2913  Download Report",
            font=("Arial", 13, "bold"),
            fg_color="#111827",
            hover_color="#1F2937",
            border_width=1,
            border_color="#334155",
            text_color="#FFFFFF",
            height=40,
            corner_radius=8,
            command=self.save_report
        )
        download_btn.pack(side="left", padx=(0, 10))

        new_btn = ctk.CTkButton(
            actions_box,
            text=" +  New Analysis",
            font=("Arial", 13, "bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            text_color="#FFFFFF",
            height=40,
            corner_radius=8,
            command=lambda: self.app.page_manager.show_page("UploadPage")
        )
        new_btn.pack(side="left")

    def _render_top_metrics_grid(self, results):
        top_grid = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        top_grid.pack(fill="x", padx=45, pady=(0, 16))
        top_grid.grid_columnconfigure((0, 1), weight=1, uniform="top_cards")

        # 1. Overall Match Score Card (Left)
        score_val = float(results.get('similarity_score', 0)) * 100
        score_color, score_label, score_msg = self.get_score_context(score_val)

        score_card = ctk.CTkFrame(top_grid, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        score_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(
            score_card, 
            text="Overall Match Score", 
            font=("Arial", 15, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=22, pady=(18, 12))

        score_content = ctk.CTkFrame(score_card, fg_color="transparent")
        score_content.pack(fill="both", expand=True, padx=22, pady=(0, 20))

        # Circular Gauge Widget
        gauge_frame = ctk.CTkFrame(score_content, width=120, height=120, corner_radius=60, fg_color="#1A2234", border_width=6, border_color=score_color)
        gauge_frame.pack(side="left", padx=(0, 20), pady=6)
        gauge_frame.pack_propagate(False)

        ctk.CTkLabel(
            gauge_frame, 
            text=f"{score_val:.0f}%", 
            font=("Arial", 30, "bold"), 
            text_color="#FFFFFF"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Score text information
        text_info = ctk.CTkFrame(score_content, fg_color="transparent")
        text_info.pack(side="left", fill="both", expand=True, pady=6)

        ctk.CTkLabel(
            text_info, 
            text=score_label, 
            font=("Arial", 20, "bold"), 
            text_color=score_color, 
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            text_info, 
            text=score_msg, 
            font=("Arial", 13), 
            text_color="#94A3B8", 
            anchor="w", 
            wraplength=280, 
            justify="left"
        ).pack(fill="x", pady=(6, 0))

        # 2. Match Breakdown Card (Right)
        breakdown_card = ctk.CTkFrame(top_grid, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        breakdown_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(
            breakdown_card, 
            text="Match Breakdown", 
            font=("Arial", 15, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=22, pady=(18, 10))

        # Calculate realistic breakdown metrics
        jd_kws = len(results.get('jd_keywords', []))
        pres_kws = len(results.get('present_keywords', []))
        skills_match = min(1.0, max(0.45, (pres_kws / jd_kws) if jd_kws > 0 else (score_val / 100.0)))
        keywords_match = min(1.0, max(0.35, float(results.get('tfidf_similarity_score', score_val / 100.0))))
        
        sections = results.get('sections', {})
        exp_match = 0.90 if sections.get('Experience') else 0.40
        edu_match = 0.95 if sections.get('Education') else 0.45

        self.add_breakdown_bar(breakdown_card, "Skills Match", skills_match, "#10B981")
        self.add_breakdown_bar(breakdown_card, "Keywords Match", keywords_match, "#38BDF8")
        self.add_breakdown_bar(breakdown_card, "Experience Match", exp_match, "#818CF8")
        self.add_breakdown_bar(breakdown_card, "Education Match", edu_match, "#34D399")

    def add_breakdown_bar(self, parent, title, val, color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=(4, 2))
        
        ctk.CTkLabel(row, text=title, font=("Arial", 12), text_color="#E2E8F0").pack(side="left")
        ctk.CTkLabel(row, text=f"{val * 100:.0f}%", font=("Arial", 12, "bold"), text_color=color).pack(side="right")
        
        bar = ctk.CTkProgressBar(parent, height=7, fg_color="#1E293B", progress_color=color, corner_radius=4)
        bar.pack(fill="x", padx=22, pady=(0, 6))
        bar.set(val)

    def _render_mid_details_grid(self, results):
        mid_grid = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        mid_grid.pack(fill="x", padx=45, pady=(0, 16))
        mid_grid.grid_columnconfigure((0, 1, 2), weight=1, uniform="mid_cards")

        sections = results.get('sections', {})
        pres_kws = results.get('present_keywords', [])
        action_verbs = results.get('action_verbs', [])
        metrics = results.get('quantifiable_metrics', 0)

        # 1. Strengths Card
        s_box = ctk.CTkFrame(mid_grid, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        s_box.grid(row=0, column=0, padx=(0, 8), sticky="nsew")

        ctk.CTkLabel(
            s_box, 
            text=" \u2714  Strengths", 
            font=("Arial", 15, "bold"), 
            text_color="#10B981"
        ).pack(anchor="w", padx=20, pady=(18, 10))

        strengths = []
        if pres_kws:
            strengths.append(f"Relevant technical skills found ({len(pres_kws)} matching terms)")
        if sections.get('Experience'):
            strengths.append("Clear work experience section identified")
        if sections.get('Education'):
            strengths.append("Education & credentials section included")
        if action_verbs:
            strengths.append(f"Strong action verb usage ({len(action_verbs)} verbs found)")
        if metrics > 0:
            strengths.append(f"Quantifiable results present ({metrics} metrics detected)")
        if not strengths:
            strengths = ["Resume structure is readable and organized", "Found standard resume sections"]

        for item in strengths[:4]:
            row = ctk.CTkFrame(s_box, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text="\u2022", font=("Arial", 14, "bold"), text_color="#10B981").pack(side="left", padx=(0, 6))
            ctk.CTkLabel(row, text=item, font=("Arial", 12), text_color="#E2E8F0", wraplength=210, justify="left").pack(side="left")

        ctk.CTkLabel(s_box, text="").pack(pady=4)

        # 2. Areas to Improve Card
        i_box = ctk.CTkFrame(mid_grid, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        i_box.grid(row=0, column=1, padx=8, sticky="nsew")

        ctk.CTkLabel(
            i_box, 
            text=" \u26A0  Areas to Improve", 
            font=("Arial", 15, "bold"), 
            text_color="#F59E0B"
        ).pack(anchor="w", padx=20, pady=(18, 10))

        improvements = results.get('suggestions', [])
        if not improvements:
            improvements = [
                "Add more measurable metrics (e.g. %, $ impact)",
                "Incorporate more role-specific keywords naturally",
                "Enhance bullet points with high-impact action verbs",
                "Ensure professional summary aligns with the target role"
            ]

        for item in improvements[:4]:
            row = ctk.CTkFrame(i_box, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=3)
            ctk.CTkLabel(row, text="\u2022", font=("Arial", 14, "bold"), text_color="#F59E0B").pack(side="left", padx=(0, 6))
            ctk.CTkLabel(row, text=item, font=("Arial", 12), text_color="#E2E8F0", wraplength=210, justify="left").pack(side="left")

        ctk.CTkLabel(i_box, text="").pack(pady=4)

        # 3. Top Missing Keywords Card
        k_box = ctk.CTkFrame(mid_grid, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        k_box.grid(row=0, column=2, padx=(8, 0), sticky="nsew")

        ctk.CTkLabel(
            k_box, 
            text=" \u25C8  Top Missing Keywords", 
            font=("Arial", 15, "bold"), 
            text_color="#38BDF8"
        ).pack(anchor="w", padx=20, pady=(18, 10))

        missing = results.get('missing_keywords', [])
        if not missing:
            ctk.CTkLabel(
                k_box, 
                text="Great job! No critical keyword gaps detected.", 
                font=("Arial", 12), 
                text_color="#34D399",
                wraplength=210,
                justify="left"
            ).pack(padx=20, pady=10, anchor="w")
        else:
            badges_container = ctk.CTkFrame(k_box, fg_color="transparent")
            badges_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

            # Render 2 badges per row
            row_frame = None
            for idx, kw in enumerate(missing[:6]):
                if idx % 2 == 0:
                    row_frame = ctk.CTkFrame(badges_container, fg_color="transparent")
                    row_frame.pack(fill="x", pady=3)
                
                badge = ctk.CTkFrame(row_frame, fg_color="#1E293B", corner_radius=8, border_width=1, border_color="#334155")
                badge.pack(side="left", padx=3, expand=True, fill="x")
                
                # Format keyword with capitalized words
                clean_kw = " ".join(word.capitalize() for word in kw.split())
                ctk.CTkLabel(
                    badge, 
                    text=clean_kw, 
                    font=("Arial", 11, "bold"), 
                    text_color="#F1F5F9"
                ).pack(padx=6, pady=5)

    def _render_next_steps_card(self, results):
        steps_card = ctk.CTkFrame(self.scrollable_frame, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        steps_card.pack(fill="x", padx=45, pady=(0, 16))

        ctk.CTkLabel(
            steps_card, 
            text="Recommended Next Steps", 
            font=("Arial", 15, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=22, pady=(18, 12))

        steps = [
            "1. Add missing target keywords naturally in your work experience and skills sections.",
            "2. Quantify achievements with measurable numbers (e.g. improved performance by 25%, managed $50k budget).",
            "3. Tailor your professional summary to mirror the key requirements mentioned in the job description.",
            "4. Maintain standard ATS formatting with distinct sections for Experience, Skills, and Education."
        ]

        for step in steps:
            ctk.CTkLabel(
                steps_card, 
                text=step, 
                font=("Arial", 13), 
                text_color="#94A3B8", 
                anchor="w",
                wraplength=900,
                justify="left"
            ).pack(fill="x", padx=24, pady=3)

        ctk.CTkLabel(steps_card, text="").pack(pady=4)

    def _render_ai_feedback_if_any(self, results):
        llm_feedback = results.get('llm_feedback', [])
        if llm_feedback:
            ai_card = ctk.CTkFrame(self.scrollable_frame, fg_color="#111827", corner_radius=14, border_width=1, border_color="#2563EB")
            ai_card.pack(fill="x", padx=45, pady=(0, 30))

            header_row = ctk.CTkFrame(ai_card, fg_color="transparent")
            header_row.pack(fill="x", padx=22, pady=(18, 10))

            ctk.CTkLabel(
                header_row, 
                text=" \u2728  AI-Powered Suggestions", 
                font=("Arial", 15, "bold"), 
                text_color="#38BDF8"
            ).pack(side="left")

            ctk.CTkLabel(
                header_row, 
                text="GPT-4o Mini Coach", 
                font=("Arial", 11, "bold"), 
                text_color="#64748B"
            ).pack(side="right")

            for item in llm_feedback:
                row = ctk.CTkFrame(ai_card, fg_color="transparent")
                row.pack(fill="x", padx=22, pady=4)
                ctk.CTkLabel(row, text="\u2192", font=("Arial", 13, "bold"), text_color="#38BDF8").pack(side="left", padx=(0, 8))
                ctk.CTkLabel(row, text=item, font=("Arial", 13), text_color="#E2E8F0", wraplength=880, justify="left").pack(side="left")

            ctk.CTkLabel(ai_card, text="").pack(pady=4)

    def save_report(self):
        if self.app.analysis_results:
            self.app.history_manager.add_analysis(self.app.analysis_results)
            messagebox.showinfo("Report Saved", "Your analysis report has been saved to History successfully.")
        else:
            messagebox.showwarning("No Report", "There is no analysis report to save.")

    def get_score_context(self, score):
        if score >= 75:
            return "#10B981", "Good Match", "Your resume aligns well with the job description. Focus on the suggested improvements to increase your interview chances."
        if score >= 45:
            return "#F59E0B", "Moderate Match", "The foundation is solid, but key skills and impact statements need sharpening to compete strongly."
        return "#EF4444", "Low Match", "Your resume lacks several role-specific terms and evidence. Tailor your experience closely before submitting."
