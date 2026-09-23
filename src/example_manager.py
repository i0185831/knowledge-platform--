import json
import os
from datetime import datetime
from src.category_manager import CategoryManager


class ExampleManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.examples_file = os.path.join(data_dir, "examples.json")
        self.category_manager = CategoryManager(data_dir)
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """确保 examples.json 存在"""
        if not os.path.exists(self.examples_file):
            with open(self.examples_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

    def get_categories(self):
        """获取所有分类（从 category_manager）"""
        return self.category_manager.get_all_categories()

    def add_example(self, title, content, category, source=""):
        """添加例题"""
        if category not in self.get_categories():
            raise ValueError(f"分类 '{category}' 不存在")

        examples = self._load_examples()
        new_example = {
            "id": len(examples) + 1,
            "title": title,
            "content": content,
            "category": category,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        examples.append(new_example)
        self._save_examples(examples)
        return new_example

    def update_example(self, example_id, title=None, content=None, category=None, source=None):
        """更新例题"""
        examples = self._load_examples()
        example = next((e for e in examples if e["id"] == example_id), None)
        if not example:
            raise ValueError(f"例题 ID {example_id} 不存在")

        if category and category not in self.get_categories():
            raise ValueError(f"分类 '{category}' 不存在")

        if title:
            example["title"] = title
        if content:
            example["content"] = content
        if category:
            example["category"] = category
        if source is not None:
            example["source"] = source
        example["updated_at"] = datetime.now().isoformat()

        self._save_examples(examples)
        return example

    def delete_example(self, example_id):
        """删除例题"""
        examples = self._load_examples()
        examples = [e for e in examples if e["id"] != example_id]
        self._save_examples(examples)

    def get_examples_by_category(self, category):
        """按分类获取例题"""
        if category not in self.get_categories():
            raise ValueError(f"分类 '{category}' 不存在")
        examples = self._load_examples()
        return [e for e in examples if e["category"] == category]

    def search_examples(self, keyword):
        """搜索例题（标题或内容）"""
        examples = self._load_examples()
        keyword_lower = keyword.lower()
        return [
            e for e in examples
            if keyword_lower in e["title"].lower() or keyword_lower in e["content"].lower()
        ]

    def get_all_examples(self):
        """获取所有例题"""
        return self._load_examples()

    def get_statistics(self):
        """获取统计信息"""
        examples = self._load_examples()
        stats = {}
        for example in examples:
            category = example["category"]
            stats[category] = stats.get(category, 0) + 1
        return stats

    def _load_examples(self):
        """从文件加载例题"""
        with open(self.examples_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_examples(self, examples):
        """保存例题到文件"""
        with open(self.examples_file, "w", encoding="utf-8") as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)