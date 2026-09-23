import json
import os
from datetime import datetime
import uuid
from src.category_manager import CategoryManager

class NoteManager:
    def __init__(self, data_dir="data/notes"):
        self.data_dir = data_dir
        self.notes_file = os.path.join(data_dir, "notes.json")
        self._ensure_data_dir()
        self.notes = self._load_notes()
        self.category_manager = CategoryManager("data")  # ← 修复：固定指向 data/

    def _ensure_data_dir(self):
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.notes_file):
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def _load_notes(self):
        try:
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def _save_notes(self):
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)

    def add_note(self, title, content, category="未分类", tags=None):
        note = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "category": category,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.notes.append(note)
        self._save_notes()
        return note

    def get_note(self, note_id):
        for note in self.notes:
            if note["id"] == note_id:
                return note
        return None

    def get_all_notes(self):
        return sorted(self.notes, key=lambda x: x["created_at"], reverse=True)

    def update_note(self, note_id, **kwargs):
        for note in self.notes:
            if note["id"] == note_id:
                note.update(kwargs)
                note["updated_at"] = datetime.now().isoformat()
                self._save_notes()
                return note
        return None

    def delete_note(self, note_id):
        self.notes = [n for n in self.notes if n["id"] != note_id]
        self._save_notes()

    def search_notes(self, query):
        query = query.lower()
        return [n for n in self.notes
                if query in n["title"].lower()
                or query in n["content"].lower()]

    def get_by_category(self, category):
        return [n for n in self.notes if n.get("category") == category]

    def get_categories(self):
        return self.category_manager.get_all_categories()

    def get_statistics(self):
        total = len(self.notes)
        by_category = {}
        for note in self.notes:
            cat = note.get("category", "未分类")
            by_category[cat] = by_category.get(cat, 0) + 1
        all_tags = []
        for note in self.notes:
            all_tags.extend(note.get("tags", []))
        return {
            "total": total,
            "by_category": by_category,
            "tags_count": len(set(all_tags))
        }