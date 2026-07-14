import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4


DEFAULT_HISTORY_FILE = Path(__file__).resolve().parents[3] / "resume_analysis_history.json"

class HistoryManager:
    def __init__(self, history_file=DEFAULT_HISTORY_FILE):
        self.history_file = Path(history_file)
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
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def add_analysis(self, analysis_result):
        if not analysis_result:
            return
        
        entry = {
            'id': uuid4().hex,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': analysis_result
        }
        self.history.insert(0, entry)
        self._save_history()
        return entry

    def get_history(self):
        return self.history

    def get_analysis_by_id(self, entry_id):
        for entry in self.history:
            if entry['id'] == entry_id:
                return entry
        return None
