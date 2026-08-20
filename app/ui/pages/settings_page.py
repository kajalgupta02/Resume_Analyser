# -*- coding: utf-8 -*-
import customtkinter as ctk
import os
import tkinter.messagebox as messagebox

class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="#070B14")
        self.app = app
        
        self.main_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_scroll.pack(fill="both", expand=True)
        self.main_scroll.grid_columnconfigure(0, weight=1)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=45, pady=(32, 18))
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Settings", 
            font=("Arial", 28, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            self.header_frame, 
            text="Customize the application and manage optional AI-powered suggestions.", 
            font=("Arial", 14), 
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(4, 0))
        
        self._create_theme_section()
        self._create_ai_section()
        self._create_about_section()

    def _create_theme_section(self):
        theme_card = ctk.CTkFrame(self.main_scroll, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        theme_card.pack(fill="x", padx=45, pady=(0, 16))
        
        ctk.CTkLabel(
            theme_card, 
            text="Appearance", 
            font=("Arial", 16, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=24, pady=(20, 4))
        
        ctk.CTkLabel(
            theme_card, 
            text="Choose how the application looks.", 
            font=("Arial", 13), 
            text_color="#94A3B8"
        ).pack(anchor="w", padx=24, pady=(0, 16))
        
        row = ctk.CTkFrame(theme_card, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 24))
        
        ctk.CTkLabel(row, text="Theme Mode", font=("Arial", 14), text_color="#E2E8F0").pack(side="left")
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        self.theme_option = ctk.CTkOptionMenu(
            row, 
            values=["Dark", "Light", "System"],
            variable=self.theme_var,
            fg_color="#1E293B", 
            button_color="#2563EB", 
            button_hover_color="#1D4ED8", 
            dropdown_fg_color="#1E293B",
            text_color="#FFFFFF",
            height=36,
            corner_radius=8,
            command=self.change_appearance_mode
        )
        self.theme_option.pack(side="right")

    def _create_ai_section(self):
        ai_card = ctk.CTkFrame(self.main_scroll, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        ai_card.pack(fill="x", padx=45, pady=(0, 16))

        ctk.CTkLabel(
            ai_card, 
            text="AI-Powered Suggestions", 
            font=("Arial", 16, "bold"), 
            text_color="#FFFFFF"
        ).pack(anchor="w", padx=24, pady=(20, 4))
        
        ctk.CTkLabel(
            ai_card, 
            text="Set additional, personalized suggestions using AI. This feature is optional.", 
            font=("Arial", 13), 
            text_color="#94A3B8"
        ).pack(anchor="w", padx=24, pady=(0, 16))
        
        row = ctk.CTkFrame(ai_card, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=(0, 16))
        
        ctk.CTkLabel(row, text="Enable AI Suggestions", font=("Arial", 14), text_color="#E2E8F0").pack(side="left")
        
        self.ai_enabled_var = ctk.BooleanVar(value=bool(os.getenv("RESUME_ANALYSER_LLM_ENABLED", "1") in {"1", "true", "True"}))
        self.ai_switch = ctk.CTkSwitch(
            row, 
            text="", 
            variable=self.ai_enabled_var, 
            progress_color="#2563EB",
            command=self.on_toggle_ai
        )
        self.ai_switch.pack(side="right")
        
        # Info Callout Box
        info_box = ctk.CTkFrame(ai_card, fg_color="#1A2234", corner_radius=10, border_width=1, border_color="#2A374F")
        info_box.pack(fill="x", padx=24, pady=(0, 18))
        
        info_icon = ctk.CTkLabel(info_box, text="\u2139", font=("Arial", 18, "bold"), text_color="#38BDF8")
        info_icon.pack(side="left", padx=(14, 10), pady=14)
        
        info_text = ctk.CTkLabel(
            info_box, 
            text="AI suggestions are currently enabled.\nMake sure your OpenAI API key is configured for best results.", 
            font=("Arial", 12), 
            text_color="#CBD5E1", 
            justify="left"
        )
        info_text.pack(side="left", pady=14)
        
        # Actions Row
        btn_row = ctk.CTkFrame(ai_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=24, pady=(0, 24))
        
        config_btn = ctk.CTkButton(
            btn_row, 
            text="Configure AI Settings", 
            fg_color="#2563EB", 
            hover_color="#1D4ED8", 
            text_color="#FFFFFF",
            font=("Arial", 13, "bold"),
            height=38,
            corner_radius=8,
            command=self.open_ai_config_dialog
        )
        config_btn.pack(side="right")

    def _create_about_section(self):
        about_card = ctk.CTkFrame(self.main_scroll, fg_color="#111827", corner_radius=14, border_width=1, border_color="#1F2937")
        about_card.pack(fill="x", padx=45, pady=(0, 30))
        
        row = ctk.CTkFrame(about_card, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=24)
        
        logo = ctk.CTkFrame(row, width=48, height=48, corner_radius=12, fg_color="#1E293B", border_width=1, border_color="#334155")
        logo.pack(side="left", padx=(0, 16))
        logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="AI", font=("Arial", 16, "bold"), text_color="#38BDF8").place(relx=0.5, rely=0.5, anchor="center")
        
        text_frame = ctk.CTkFrame(row, fg_color="transparent")
        text_frame.pack(side="left")
        
        ctk.CTkLabel(text_frame, text="About AI Resume Improver Pro", font=("Arial", 15, "bold"), text_color="#FFFFFF", anchor="w").pack(fill="x")
        ctk.CTkLabel(text_frame, text="Version 1.0.0", font=("Arial", 12), text_color="#64748B", anchor="w").pack(fill="x", pady=(1, 4))
        ctk.CTkLabel(
            text_frame, 
            text="AI Resume Improver Pro helps you review your resume against job requirements\nand improve your chances of getting noticed by recruiters and ATS systems.", 
            font=("Arial", 13), 
            text_color="#94A3B8", 
            justify="left", 
            anchor="w"
        ).pack(fill="x")

    def change_appearance_mode(self, new_mode):
        ctk.set_appearance_mode(new_mode)

    def on_toggle_ai(self):
        enabled = self.ai_enabled_var.get()
        os.environ["RESUME_ANALYSER_LLM_ENABLED"] = "1" if enabled else "0"
        if hasattr(self.app, "analyser") and hasattr(self.app.analyser, "feedback_service"):
            self.app.analyser.feedback_service.config.enabled = enabled

    def open_ai_config_dialog(self):
        dialog = ctk.CTkInputDialog(text="Enter your OpenAI API Key (or leave empty):", title="Configure AI API Key")
        key = dialog.get_input()
        if key is not None:
            clean_key = key.strip()
            os.environ["RESUME_ANALYSER_LLM_API_KEY"] = clean_key
            os.environ["OPENAI_API_KEY"] = clean_key
            if hasattr(self.app, "analyser") and hasattr(self.app.analyser, "feedback_service"):
                self.app.analyser.feedback_service.config.api_key = clean_key
                self.app.analyser.feedback_service.config.enabled = bool(clean_key)
            messagebox.showinfo("AI Settings Updated", "Your AI API configuration has been updated for this session.")
