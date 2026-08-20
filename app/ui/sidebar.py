# -*- coding: utf-8 -*-
import customtkinter as ctk

class Sidebar(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, width=240, corner_radius=0, fg_color="#0B1120")
        self.parent = parent
        
        # Logo and Branding Header
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(pady=(28, 32), padx=18, anchor="w", fill="x")
        
        # Logo Icon Badge
        self.logo_badge = ctk.CTkFrame(self.logo_frame, width=38, height=38, corner_radius=10, fg_color="#1E293B", border_width=1, border_color="#334155")
        self.logo_badge.pack(side="left", padx=(0, 10))
        self.logo_badge.pack_propagate(False)
        
        self.logo_icon = ctk.CTkLabel(self.logo_badge, text="AI", font=("Arial", 14, "bold"), text_color="#38BDF8")
        self.logo_icon.place(relx=0.5, rely=0.5, anchor="center")
        
        self.logo_text_frame = ctk.CTkFrame(self.logo_frame, fg_color="transparent")
        self.logo_text_frame.pack(side="left", fill="y")
        
        self.logo_label_title = ctk.CTkLabel(self.logo_text_frame, text="AI Resume", font=("Arial", 15, "bold"), text_color="#FFFFFF", anchor="w")
        self.logo_label_title.pack(anchor="w")
        
        self.logo_label_sub = ctk.CTkLabel(self.logo_text_frame, text="Improver Pro", font=("Arial", 12, "bold"), text_color="#38BDF8", anchor="w")
        self.logo_label_sub.pack(anchor="w")
        
        # Navigation Buttons
        self.buttons = {}
        
        self.add_button("  Home", "LandingPage", symbol="\u2302")
        self.add_button("  Analyze Resume", "UploadPage", symbol="\u2315")
        self.add_button("  Results", "ResultsPage", symbol="\u2630")
        self.add_button("  Settings", "SettingsPage", symbol="\u2699")
        self.add_button("  History", "HistoryPage", symbol="\u23F1")
        
        # Bottom Utility Buttons
        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.pack(side="bottom", fill="x", padx=12, pady=20)
        
        # Divider line
        self.divider = ctk.CTkFrame(self.bottom_frame, height=1, fg_color="#1E293B")
        self.divider.pack(fill="x", padx=8, pady=(0, 14))
        
        self.help_button = ctk.CTkButton(
            self.bottom_frame,
            text=" ?   Help & Docs",
            fg_color="transparent",
            hover_color="#1E293B",
            text_color="#94A3B8",
            anchor="w",
            height=38,
            corner_radius=8,
            font=("Arial", 13),
            command=self.show_help
        )
        self.help_button.pack(fill="x", pady=2)
        
        self.quit_button = ctk.CTkButton(
            self.bottom_frame,
            text=" \u23FB   Quit",
            fg_color="transparent",
            hover_color="#7F1D1D",
            text_color="#94A3B8",
            anchor="w",
            height=38,
            corner_radius=8,
            font=("Arial", 13),
            command=self.parent.quit
        )
        self.quit_button.pack(fill="x", pady=2)

    def add_button(self, name, page_name, symbol=""):
        btn_container = ctk.CTkFrame(self, fg_color="transparent")
        btn_container.pack(pady=3, padx=12, fill="x")
        
        display_text = f" {symbol} {name}" if symbol else name
        
        button = ctk.CTkButton(
            btn_container,
            text=display_text,
            height=44,
            fg_color="transparent",
            text_color="#94A3B8",
            hover_color="#1E293B",
            anchor="w",
            corner_radius=8,
            font=("Arial", 13, "bold"),
            command=lambda: self.parent.page_manager.show_page(page_name)
        )
        button.pack(side="left", fill="x", expand=True)
        
        self.buttons[page_name] = button

    def set_active(self, page_name):
        for name, btn in self.buttons.items():
            if name == page_name:
                btn.configure(fg_color="#2563EB", text_color="#FFFFFF", hover_color="#1D4ED8")
            else:
                btn.configure(fg_color="transparent", text_color="#94A3B8", hover_color="#1E293B")

    def show_help(self):
        import tkinter.messagebox as messagebox
        messagebox.showinfo(
            "AI Resume Improver Pro - Guide",
            "How to use the application:\n\n"
            "1. Upload Resume: Upload your resume in PDF, DOCX, or TXT format.\n"
            "2. Add Job Description: Select a target role from sample roles or paste your target job description.\n"
            "3. Analyze: Click 'Analyze Resume' to get detailed ATS matching, breakdown scores, missing keywords, and AI suggestions.\n"
            "4. History: Track and compare your previous resume scores anytime."
        )
