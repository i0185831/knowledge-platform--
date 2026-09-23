import json
import os

class CategoryManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.categories_file = os.path.join(data_dir, "categories.json")
        self._ensure_data_dir()
        self.categories = self._load_categories()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.categories_file):
            # 初始化默认分类
            default_categories = ["高数", "动物学", "其他"]
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(default_categories, f, ensure_ascii=False, indent=2)
    
    def _load_categories(self):
        """从文件加载分类列表"""
        try:
            with open(self.categories_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return ["高数", "动物学", "其他"]
    
    def _save_categories(self):
        """保存分类列表到文件"""
        with open(self.categories_file, 'w', encoding='utf-8') as f:
            json.dump(self.categories, f, ensure_ascii=False, indent=2)
    
    def add_category(self, category_name):
        """添加新分类"""
        if category_name and category_name not in self.categories:
            self.categories.append(category_name)
            self._save_categories()
            return True
        return False
    
    def delete_category(self, category_name):
        """删除分类"""
        if category_name in self.categories:
            self.categories.remove(category_name)
            self._save_categories()
            return True
        return False
    
    def rename_category(self, old_name, new_name):
        """重命名分类"""
        if old_name in self.categories and new_name not in self.categories:
            index = self.categories.index(old_name)
            self.categories[index] = new_name
            self._save_categories()
            return True
        return False
    
    def get_all_categories(self):
        """获取所有分类"""
        return self.categories.copy()
    
    def category_exists(self, category_name):
        """检查分类是否存在"""
        return category_name in self.categories