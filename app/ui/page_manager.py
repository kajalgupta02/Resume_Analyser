import customtkinter as ctk
from .pages.landing_page import LandingPage
from .pages.upload_page import UploadPage
from .pages.results_page import ResultsPage
from .pages.settings_page import SettingsPage

class PageManager(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.pages = {}
        self.current_page = None

        for Page in (LandingPage, UploadPage, ResultsPage, SettingsPage):
            page_name = Page.__name__
            page = Page(self, self.app)
            self.pages[page_name] = page
            page.pack(fill="both", expand=True)

        self.show_page("LandingPage")

    def show_page(self, page_name):
        if self.current_page:
            self.current_page.pack_forget()
        
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)
        
        # Update sidebar selection
        if hasattr(self.app, "sidebar"):
            self.app.sidebar.set_active(page_name)
        
        # Refresh page content with a tiny delay to keep UI responsive
        if hasattr(self.current_page, "refresh"):
            self.after(10, self.current_page.refresh)
