import json
import os
from datetime import datetime

class HistoryManager:
    def __init__(self, history_file='resume_analysis_history.json'):
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def _save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def add_analysis(self, analysis_result):
        if not analysis_result:
            return
        
        entry = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': analysis_result
        }
        self.history.insert(0, entry)
        self._save_history()

    def get_history(self):
        return self.history

    def get_analysis_by_id(self, entry_id):
        for entry in self.history:
            if entry['id'] == entry_id:
                return entry
        return None
