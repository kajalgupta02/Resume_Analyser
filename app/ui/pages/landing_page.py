# -*- coding: utf-8 -*-
import customtkinter as ctk

class LandingPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#070B14")
        self.app = app
        
        # Scrollable container for perfect responsive display on all screens
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)
        self.main_scroll.grid_columnconfigure(0, weight=1)
        
        # Top Hero Section (Split into Left Copy and Right Graphic Card)
        self.top_section = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.top_section.pack(fill="x", padx=45, pady=(35, 20))
        self.top_section.grid_columnconfigure(0, weight=6)
        self.top_section.grid_columnconfigure(1, weight=5)
        
        self._create_hero_copy()
        self._create_resume_mockup()
        
        # Bottom "How it works" Section
        self.bottom_section = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.bottom_section.pack(fill="x", padx=45, pady=(15, 40))
        
        self._create_how_it_works_section()

    def _create_hero_copy(self):
        self.hero_frame = ctk.CTkFrame(self.top_section, fg_color="transparent")
        self.hero_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 25), pady=10)
        
        # Welcome tag
        welcome_tag = ctk.CTkLabel(
            self.hero_frame, 
            text="Welcome to", 
            font=("Arial", 22, "bold"), 
            text_color="#38BDF8", 
            anchor="w"
        )
        welcome_tag.pack(fill="x", pady=(20, 2))
        
        # Main Title
        title_label = ctk.CTkLabel(
            self.hero_frame, 
            text="AI Resume\nImprover Pro", 
            font=("Arial", 38, "bold"), 
            text_color="#FFFFFF", 
            justify="left",
            anchor="w"
        )
        title_label.pack(fill="x", pady=(0, 16))
        
        # Description
        desc_label = ctk.CTkLabel(
            self.hero_frame, 
            text="Analyze your resume, identify improvement areas, and create a stronger resume for your next opportunity.", 
            font=("Arial", 15), 
            text_color="#94A3B8", 
            anchor="w", 
            wraplength=460, 
            justify="left"
        )
        desc_label.pack(fill="x", pady=(0, 32))
        
        # Action Buttons Row
        btn_frame = ctk.CTkFrame(self.hero_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        start_btn = ctk.CTkButton(
            btn_frame, 
            text="Analyze My Resume   \u2192", 
            font=("Arial", 15, "bold"), 
            fg_color="#2563EB", 
            hover_color="#1D4ED8", 
            text_color="#FFFFFF",
            height=48, 
            corner_radius=10,
            command=lambda: self.app.page_manager.show_page("UploadPage")
        )
        start_btn.pack(side="left", padx=(0, 16))
                      
        history_btn = ctk.CTkButton(
            btn_frame, 
            text="View History   \u23F1", 
            font=("Arial", 14, "bold"), 
            fg_color="#111827", 
            hover_color="#1F2937", 
            border_width=1, 
            border_color="#334155", 
            text_color="#FFFFFF",
            height=48, 
            corner_radius=10,
            command=lambda: self.app.page_manager.show_page("HistoryPage")
        )
        history_btn.pack(side="left")

    def _create_resume_mockup(self):
        self.mockup_container = ctk.CTkFrame(self.top_section, fg_color="transparent")
        self.mockup_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        
        # Main Stylized Document Card
        doc_card = ctk.CTkFrame(
            self.mockup_container, 
            fg_color="#111827", 
            corner_radius=16, 
            border_width=1, 
            border_color="#1F2937"
        )
        doc_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header inside document
        doc_header = ctk.CTkFrame(doc_card, fg_color="#1E293B", corner_radius=12)
        doc_header.pack(fill="x", padx=16, pady=16)
        
        # Avatar circle
        avatar = ctk.CTkFrame(doc_header, width=38, height=38, corner_radius=19, fg_color="#38BDF8")
        avatar.pack(side="left", padx=12, pady=10)
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text="\u263A", font=("Arial", 16, "bold"), text_color="#0F172A").place(relx=0.5, rely=0.5, anchor="center")
        
        info_col = ctk.CTkFrame(doc_header, fg_color="transparent")
        info_col.pack(side="left", fill="y", pady=10)
        ctk.CTkLabel(info_col, text="Alex Morgan", font=("Arial", 13, "bold"), text_color="#FFFFFF", anchor="w").pack(anchor="w")
        ctk.CTkLabel(info_col, text="Senior Software Engineer", font=("Arial", 11), text_color="#94A3B8", anchor="w").pack(anchor="w")
        
        # Star Rating Badge
        stars = ctk.CTkLabel(doc_header, text="\u2605 \u2605 \u2605 \u2605 \u2605", font=("Arial", 13, "bold"), text_color="#F59E0B")
        stars.pack(side="right", padx=14)
        
        # Resume Body Content Lines
        body_frame = ctk.CTkFrame(doc_card, fg_color="transparent")
        body_frame.pack(fill="x", padx=18, pady=(4, 16))
        
        # Section 1: Summary lines
        ctk.CTkLabel(body_frame, text="PROFESSIONAL SUMMARY", font=("Arial", 10, "bold"), text_color="#38BDF8", anchor="w").pack(fill="x", pady=(0, 4))
        for width_ratio in [1.0, 0.85, 0.6]:
            line = ctk.CTkFrame(body_frame, height=6, fg_color="#1E293B", corner_radius=3)
            line.pack(fill="x", pady=2)
            if width_ratio < 1.0:
                line.pack_configure(padx=(0, int(280 * (1.0 - width_ratio))))
        
        # Section 2: Skills Badges
        ctk.CTkLabel(body_frame, text="KEY SKILLS & STACK", font=("Arial", 10, "bold"), text_color="#38BDF8", anchor="w").pack(fill="x", pady=(12, 6))
        skill_row = ctk.CTkFrame(body_frame, fg_color="transparent")
        skill_row.pack(fill="x")
        for skill in ["Python", "React", "Docker", "AWS Cloud", "SQL"]:
            badge = ctk.CTkFrame(skill_row, fg_color="#1E293B", corner_radius=6, border_width=1, border_color="#334155")
            badge.pack(side="left", padx=(0, 6))
            ctk.CTkLabel(badge, text=skill, font=("Arial", 10, "bold"), text_color="#E2E8F0").pack(padx=8, pady=3)
            
        # Floating Match Score Callout Badge
        score_badge = ctk.CTkFrame(doc_card, fg_color="#064E3B", corner_radius=10, border_width=1, border_color="#059669")
        score_badge.pack(fill="x", padx=16, pady=(8, 16))
        
        badge_left = ctk.CTkLabel(score_badge, text="  \u2714  ATS Fit Score: 94% - Strong Match", font=("Arial", 12, "bold"), text_color="#34D399", anchor="w")
        badge_left.pack(side="left", padx=10, pady=8)
        
    def _create_how_it_works_section(self):
        ctk.CTkLabel(
            self.bottom_section, 
            text="How it works", 
            font=("Arial", 20, "bold"), 
            text_color="#FFFFFF", 
            anchor="w"
        ).pack(fill="x", pady=(10, 16))
        
        cards_grid = ctk.CTkFrame(self.bottom_section, fg_color="transparent")
        cards_grid.pack(fill="x")
        cards_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        steps = [
            ("1", "Upload your resume", "Upload your resume in PDF, DOCX, or TXT format.", "\u2912", 0),
            ("2", "Add a job description", "Paste the job description or choose a sample role.", "\u25A4", 1),
            ("3", "Review suggestions", "Get actionable insights, match scores, and AI recommendations.", "\u2197", 2)
        ]
        
        for num, title, desc, icon, col in steps:
            card = ctk.CTkFrame(
                cards_grid, 
                fg_color="#111827", 
                corner_radius=14, 
                border_width=1, 
                border_color="#1F2937"
            )
            card.grid(row=0, column=col, padx=(0 if col==0 else (12 if col==1 else 12), 0 if col==2 else 0), sticky="nsew")
            
            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=18, pady=(18, 10))
            
            # Circle badge for step number
            circle = ctk.CTkFrame(top, width=28, height=28, corner_radius=14, fg_color="#2563EB")
            circle.pack(side="left")
            circle.pack_propagate(False)
            ctk.CTkLabel(circle, text=num, font=("Arial", 12, "bold"), text_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="center")
            
            ctk.CTkLabel(top, text=icon, font=("Arial", 18), text_color="#38BDF8").pack(side="right")
            
            ctk.CTkLabel(card, text=title, font=("Arial", 15, "bold"), text_color="#FFFFFF", anchor="w").pack(fill="x", padx=18, pady=(0, 4))
            ctk.CTkLabel(card, text=desc, font=("Arial", 12), text_color="#94A3B8", anchor="w", wraplength=220, justify="left").pack(fill="x", padx=18, pady=(0, 18))

    def refresh(self):
        pass
