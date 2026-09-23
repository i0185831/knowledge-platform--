import streamlit as st
import json
import os
import sys
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from note_manager import NoteManager
from example_manager import ExampleManager
from category_manager import CategoryManager

# ─────────────────────────────────────────────
# 页面配置
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="个人知识管理平台",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# 自定义 CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    .card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .card-example {
        border-left: 4px solid #ff7f0e;
    }
    .tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1565c0;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.8rem;
        margin: 2px;
    }
    .difficulty-easy   { color: #2e7d32; font-weight: bold; }
    .difficulty-medium { color: #f57f17; font-weight: bold; }
    .difficulty-hard   { color: #c62828; font-weight: bold; }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
    }
    .stat-number { font-size: 2.5rem; font-weight: bold; }
    .stat-label  { font-size: 0.9rem; opacity: 0.9; }
    .reviewed-badge {
        background-color: #c8e6c9;
        color: #1b5e20;
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 0.75rem;
    }
    .not-reviewed-badge {
        background-color: #ffccbc;
        color: #bf360c;
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 0.75rem;
    }
    .category-item {
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 初始化管理器（缓存，避免重复加载）
# ─────────────────────────────────────────────
@st.cache_resource
def get_managers():
    base_dir = os.path.dirname(__file__)
    note_mgr     = NoteManager(os.path.join(base_dir, 'data', 'notes'))
    example_mgr  = ExampleManager(os.path.join(base_dir, 'data', 'examples'))
    category_mgr = CategoryManager(os.path.join(base_dir, 'data'))
    return note_mgr, example_mgr, category_mgr

note_manager, example_manager, category_manager = get_managers()

# ─────────────────────────────────────────────
# Session State 初始化
# ─────────────────────────────────────────────
for key, default in {
    'edit_note_id':              None,
    'edit_example_id':           None,
    'confirm_delete_note':       None,
    'confirm_delete_example':    None,
    'edit_category_name':        None,
    'confirm_delete_category':   None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────
DIFFICULTY_MAP         = {'简单': 'easy', '中等': 'medium', '困难': 'hard'}
DIFFICULTY_MAP_REVERSE = {v: k for k, v in DIFFICULTY_MAP.items()}
DIFFICULTY_COLOR       = {'简单': '🟢', '中等': '🟡', '困难': '🔴'}

def format_datetime(dt_str: str) -> str:
    try:
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime('%Y-%m-%d %H:%M')
    except Exception:
        return dt_str or '—'

def render_tags(tags: list) -> str:
    if not tags:
        return ''
    return ' '.join(f'<span class="tag">#{t}</span>' for t in tags)

def difficulty_label(level: str) -> str:
    zh   = DIFFICULTY_MAP_REVERSE.get(level, level)
    icon = DIFFICULTY_COLOR.get(zh, '')
    return f"{icon} {zh}"

# ─────────────────────────────────────────────
# 顶部标题
# ─────────────────────────────────────────────
st.markdown('<div class="main-header">📚 个人知识管理平台</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 侧边栏导航
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/books.png", width=80)
    st.markdown("## 🗂️ 导航菜单")
    tab_choice = st.radio(
        "选择功能模块",
        ["📝 笔记管理", "📖 例题库", "📂 分类管理", "📊 数据统计"],
        label_visibility="collapsed"
    )
    st.markdown("---")

    st.markdown("### 🔄 数据备份")

    if st.button("⬇️ 导出所有数据", use_container_width=True):
        try:
            export_data = {
                'export_time': datetime.now().isoformat(),
                'notes':       note_manager.get_all_notes(),
                'examples':    example_manager.get_all_examples(),
                'categories':  category_manager.get_all_categories(),
            }
            st.download_button(
                label="📥 点击下载 JSON",
                data=json.dumps(export_data, ensure_ascii=False, indent=2),
                file_name=f"knowledge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"导出失败：{e}")

    uploaded = st.file_uploader("⬆️ 导入备份文件", type=['json'], label_visibility="collapsed")
    if uploaded:
        try:
            import_data    = json.load(uploaded)
            notes_count    = len(import_data.get('notes', []))
            examples_count = len(import_data.get('examples', []))
            st.info(f"检测到 {notes_count} 条笔记、{examples_count} 道例题")
            if st.button("✅ 确认导入", use_container_width=True):
                imported_n = imported_e = 0
                for note in import_data.get('notes', []):
                    try:
                        note_manager.add_note(
                            title=note['title'], content=note['content'],
                            category=note.get('category', '未分类'),
                            tags=note.get('tags', [])
                        )
                        imported_n += 1
                    except Exception:
                        pass
                for ex in import_data.get('examples', []):
                    try:
                        example_manager.add_example(
                            title=ex['title'], content=ex.get('content', ''),
                            category=ex.get('category', '未分类'),
                            source=ex.get('source', '')
                        )
                        imported_e += 1
                    except Exception:
                        pass
                st.success(f"成功导入 {imported_n} 条笔记、{imported_e} 道例题！")
                st.cache_resource.clear()
                st.rerun()
        except Exception as e:
            st.error(f"导入失败，请检查文件格式：{e}")

    st.markdown("---")
    st.caption("💡 数据保存在本地 JSON 文件中")

# ═══════════════════════════════════════════════════════════════
# TAB 1：笔记管理
# ═══════════════════════════════════════════════════════════════
if tab_choice == "📝 笔记管理":
    st.header("📝 笔记管理")

    all_notes            = note_manager.get_all_notes()
    all_categories_notes = sorted(category_manager.get_all_categories()) or ['未分类']

    with st.expander("➕ 新增笔记", expanded=not bool(all_notes)):
        with st.form("add_note_form", clear_on_submit=True):
            st.markdown("#### 填写笔记信息")
            col1, col2 = st.columns([2, 1])
            with col1:
                new_title = st.text_input("📌 标题 *", placeholder="请输入笔记标题")
            with col2:
                new_category = st.selectbox("🗂️ 分类", all_categories_notes)
            new_content  = st.text_area("📄 内容 *", placeholder="在此输入笔记内容...", height=200)
            new_tags_raw = st.text_input("🏷️ 标签（用逗号分隔）", placeholder="例：极限, 导数, 重点")
            submitted    = st.form_submit_button("💾 保存笔记", use_container_width=True)
            if submitted:
                if not new_title.strip():
                    st.error("❌ 标题不能为空！")
                elif not new_content.strip():
                    st.error("❌ 内容不能为空！")
                else:
                    tags = [t.strip() for t in new_tags_raw.split(',') if t.strip()]
                    try:
                        note_manager.add_note(
                            title=new_title.strip(),
                            content=new_content.strip(),
                            category=new_category or '未分类',
                            tags=tags
                        )
                        st.success(f"✅ 笔记《{new_title}》已保存！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败：{e}")

    st.markdown("---")
    st.markdown("#### 🔍 搜索与筛选")
    col1, col2, col3 = st.columns([3, 2, 2])
    with col1:
        search_note = st.text_input("搜索关键词", placeholder="搜索标题或内容...", label_visibility="collapsed")
    with col2:
        filter_category_note = st.selectbox("按分类筛选", ["全部分类"] + all_categories_notes, label_visibility="collapsed")
    with col3:
        filter_tag_note = st.text_input("按标签筛选", placeholder="输入标签名...", label_visibility="collapsed")

    filtered_notes = all_notes
    if search_note.strip():
        kw = search_note.strip().lower()
        filtered_notes = [n for n in filtered_notes
                          if kw in n.get('title', '').lower() or kw in n.get('content', '').lower()]
    if filter_category_note != "全部分类":
        filtered_notes = [n for n in filtered_notes if n.get('category') == filter_category_note]
    if filter_tag_note.strip():
        ft = filter_tag_note.strip().lower()
        filtered_notes = [n for n in filtered_notes
                          if any(ft in t.lower() for t in n.get('tags', []))]

    st.markdown(f"**共找到 {len(filtered_notes)} 条笔记**")

    if not filtered_notes:
        st.info("📭 暂无笔记，请点击上方「新增笔记」开始记录！")
    else:
        for note in filtered_notes:
            nid = note['id']
            if st.session_state.edit_note_id == nid:
                with st.container():
                    st.markdown(f"##### ✏️ 编辑笔记：{note['title']}")
                    with st.form(f"edit_note_{nid}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            e_title = st.text_input("标题", value=note['title'])
                        with col2:
                            e_category = st.selectbox(
                                "分类", all_categories_notes,
                                index=all_categories_notes.index(note.get('category'))
                                      if note.get('category') in all_categories_notes else 0
                            )
                        e_content = st.text_area("内容", value=note['content'], height=200)
                        e_tags    = st.text_input("标签（逗号分隔）", value=', '.join(note.get('tags', [])))
                        c1, c2 = st.columns(2)
                        with c1:
                            save_edit = st.form_submit_button("💾 保存修改", use_container_width=True)
                        with c2:
                            cancel_edit = st.form_submit_button("❌ 取消", use_container_width=True)
                        if save_edit:
                            if not e_title.strip():
                                st.error("标题不能为空！")
                            else:
                                try:
                                    note_manager.update_note(
                                        note_id=nid,
                                        title=e_title.strip(),
                                        content=e_content.strip(),
                                        category=e_category or '未分类',
                                        tags=[t.strip() for t in e_tags.split(',') if t.strip()]
                                    )
                                    st.success("✅ 笔记已更新！")
                                    st.session_state.edit_note_id = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"更新失败：{e}")
                        if cancel_edit:
                            st.session_state.edit_note_id = None
                            st.rerun()
            else:
                with st.expander(f"📄 {note['title']}  |  🗂️ {note.get('category', '未分类')}"):
                    col_main, col_actions = st.columns([5, 1])
                    with col_main:
                        st.markdown(note['content'])
                        if note.get('tags'):
                            st.markdown(render_tags(note['tags']), unsafe_allow_html=True)
                        st.caption(
                            f"🕐 创建：{format_datetime(note.get('created_at', ''))}　"
                            f"🔄 更新：{format_datetime(note.get('updated_at', ''))}"
                        )
                    with col_actions:
                        if st.button("✏️ 编辑", key=f"edit_n_{nid}", use_container_width=True):
                            st.session_state.edit_note_id = nid
                            st.rerun()
                        if st.session_state.confirm_delete_note == nid:
                            st.warning("确认删除？")
                            if st.button("✅ 确认", key=f"confirm_del_n_{nid}", use_container_width=True):
                                try:
                                    note_manager.delete_note(nid)
                                    st.success("已删除！")
                                    st.session_state.confirm_delete_note = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"删除失败：{e}")
                            if st.button("❌ 取消", key=f"cancel_del_n_{nid}", use_container_width=True):
                                st.session_state.confirm_delete_note = None
                                st.rerun()
                        else:
                            if st.button("🗑️ 删除", key=f"del_n_{nid}", use_container_width=True):
                                st.session_state.confirm_delete_note = nid
                                st.rerun()

# ═══════════════════════════════════════════════════════════════
# TAB 2：例题库
# ═══════════════════════════════════════════════════════════════
elif tab_choice == "📖 例题库":
    st.header("📖 例题库")

    all_examples      = example_manager.get_all_examples()
    all_categories_ex = sorted(category_manager.get_all_categories()) or ['未分类']

    with st.expander("➕ 新增例题", expanded=not bool(all_examples)):
        with st.form("add_example_form", clear_on_submit=True):
            st.markdown("#### 填写例题信息")
            col1, col2 = st.columns([2, 1])
            with col1:
                ex_title = st.text_input("📌 标题 *", placeholder="例题标题")
            with col2:
                ex_category = st.selectbox("🗂️ 分类", all_categories_ex)
            ex_content  = st.text_area("📝 内容 *", placeholder="在此输入例题内容...", height=300)
            ex_source   = st.text_input("📚 来源", placeholder="例：教科书、网络资源等")
            submitted_ex = st.form_submit_button("💾 保存例题", use_container_width=True)
            if submitted_ex:
                if not ex_title.strip():
                    st.error("❌ 标题不能为空！")
                elif not ex_content.strip():
                    st.error("❌ 内容不能为空！")
                else:
                    try:
                        example_manager.add_example(
                            title=ex_title.strip(),
                            content=ex_content.strip(),
                            category=ex_category or '未分类',
                            source=ex_source.strip()
                        )
                        st.success(f"✅ 例题《{ex_title}》已保存！")
                        st.rerun()
                    except Exception as e:
                        st.error(f"保存失败：{e}")

    st.markdown("---")
    st.markdown("#### 🔍 搜索与筛选")
    col1, col2 = st.columns([3, 2])
    with col1:
        search_ex = st.text_input("搜索关键词", placeholder="搜索标题或内容...", label_visibility="collapsed")
    with col2:
        filter_cat_ex = st.selectbox("按分类筛选", ["全部分类"] + all_categories_ex, label_visibility="collapsed")

    filtered_ex = all_examples
    if search_ex.strip():
        kw = search_ex.strip().lower()
        filtered_ex = [e for e in filtered_ex
                       if kw in e.get('title', '').lower() or kw in e.get('content', '').lower()]
    if filter_cat_ex != "全部分类":
        filtered_ex = [e for e in filtered_ex if e.get('category') == filter_cat_ex]

    st.markdown(f"**共找到 {len(filtered_ex)} 道例题**")

    if not filtered_ex:
        st.info("📭 暂无例题，请点击上方「新增例题」开始添加！")
    else:
        for ex in filtered_ex:
            eid = ex['id']
            if st.session_state.edit_example_id == eid:
                with st.container():
                    st.markdown(f"##### ✏️ 编辑例题：{ex['title']}")
                    with st.form(f"edit_ex_{eid}"):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            ee_title = st.text_input("标题", value=ex['title'])
                        with col2:
                            ee_category = st.selectbox(
                                "分类", all_categories_ex,
                                index=all_categories_ex.index(ex.get('category'))
                                      if ex.get('category') in all_categories_ex else 0
                            )
                        ee_content = st.text_area("内容", value=ex['content'], height=300)
                        ee_source  = st.text_input("来源", value=ex.get('source', ''))
                        c1, c2 = st.columns(2)
                        with c1:
                            save_ex_edit = st.form_submit_button("💾 保存修改", use_container_width=True)
                        with c2:
                            cancel_ex_edit = st.form_submit_button("❌ 取消", use_container_width=True)
                        if save_ex_edit:
                            if not ee_title.strip():
                                st.error("标题不能为空！")
                            else:
                                try:
                                    example_manager.update_example(
                                        example_id=eid,
                                        title=ee_title.strip(),
                                        content=ee_content.strip(),
                                        category=ee_category or '未分类',
                                        source=ee_source.strip()
                                    )
                                    st.success("✅ 例题已更新！")
                                    st.session_state.edit_example_id = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"更新失败：{e}")
                        if cancel_ex_edit:
                            st.session_state.edit_example_id = None
                            st.rerun()
            else:
                with st.expander(f"📖 {ex['title']}  |  🗂️ {ex.get('category', '未分类')}"):
                    col_content, col_actions = st.columns([5, 1])
                    with col_content:
                        st.markdown(ex['content'])
                        if ex.get('source'):
                            st.caption(f"📚 来源：{ex['source']}")
                        st.caption(
                            f"🕐 创建：{format_datetime(ex.get('created_at', ''))}　"
                            f"🔄 更新：{format_datetime(ex.get('updated_at', ''))}"
                        )
                    with col_actions:
                        if st.button("✏️ 编辑", key=f"edit_e_{eid}", use_container_width=True):
                            st.session_state.edit_example_id = eid
                            st.rerun()
                        if st.session_state.confirm_delete_example == eid:
                            st.warning("确认删除？")
                            if st.button("✅ 确认", key=f"confirm_del_e_{eid}", use_container_width=True):
                                try:
                                    example_manager.delete_example(eid)
                                    st.success("已删除！")
                                    st.session_state.confirm_delete_example = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"删除失败：{e}")
                            if st.button("❌ 取消", key=f"cancel_del_e_{eid}", use_container_width=True):
                                st.session_state.confirm_delete_example = None
                                st.rerun()
                        else:
                            if st.button("🗑️ 删除", key=f"del_e_{eid}", use_container_width=True):
                                st.session_state.confirm_delete_example = eid
                                st.rerun()

# ═══════════════════════════════════════════════════════════════
# TAB 3：分类管理
# ═══════════════════════════════════════════════════════════════
elif tab_choice == "📂 分类管理":
    st.header("📂 分类管理")
    st.markdown("在这里管理你的知识分类，所有笔记和例题都会使用这些分类。")

    all_categories = sorted(category_manager.get_all_categories())

    st.markdown("### ➕ 新增分类")
    with st.form("add_category_form", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            new_cat_name = st.text_input("分类名称", placeholder="例：高数、动物学、编程...", label_visibility="collapsed")
        with col2:
            add_cat_btn = st.form_submit_button("➕ 添加", use_container_width=True)
        if add_cat_btn:
            if not new_cat_name.strip():
                st.error("❌ 分类名称不能为空！")
            elif new_cat_name.strip() in all_categories:
                st.error(f"❌ 分类「{new_cat_name}」已存在！")
            else:
                try:
                    category_manager.add_category(new_cat_name.strip())
                    st.cache_resource.clear()  # ← 清除缓存，让其他页面立即看到新分类
                    st.success(f"✅ 分类「{new_cat_name}」已添加！")
                    st.rerun()
                except Exception as e:
                    st.error(f"添加失败：{e}")

    st.markdown("---")
    st.markdown("### 📋 所有分类")

    if not all_categories:
        st.info("📭 暂无分类，请点击上方「添加」创建第一个分类！")
    else:
        for cat in all_categories:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.markdown(f"#### 🏷️ {cat}")
            with col2:
                notes_count = len([n for n in note_manager.get_all_notes() if n.get('category') == cat])
                st.metric("笔记", notes_count)
            with col3:
                examples_count = len([e for e in example_manager.get_all_examples() if e.get('category') == cat])
                st.metric("例题", examples_count)
            with col4:
                col_rename, col_delete = st.columns(2)
                with col_rename:
                    if st.button("✏️ 重命名", key=f"rename_{cat}", use_container_width=True):
                        st.session_state.edit_category_name = cat
                        st.rerun()
                with col_delete:
                    if st.button("🗑️ 删除", key=f"del_cat_{cat}", use_container_width=True):
                        st.session_state.confirm_delete_category = cat
                        st.rerun()

            # 重命名模式
            if st.session_state.edit_category_name == cat:
                st.markdown(f"##### ✏️ 重命名「{cat}」")
                with st.form(f"rename_cat_{cat}"):
                    new_name = st.text_input("新名称", value=cat, placeholder="输入新的分类名称")
                    c1, c2 = st.columns(2)
                    with c1:
                        save_rename = st.form_submit_button("💾 保存", use_container_width=True)
                    with c2:
                        cancel_rename = st.form_submit_button("❌ 取消", use_container_width=True)
                    if save_rename:
                        if not new_name.strip():
                            st.error("新名称不能为空！")
                        elif new_name.strip() == cat:
                            st.warning("新名称与原名称相同！")
                        elif new_name.strip() in all_categories:
                            st.error(f"分类「{new_name}」已存在！")
                        else:
                            try:
                                category_manager.rename_category(cat, new_name.strip())
                                for note in note_manager.get_all_notes():
                                    if note.get('category') == cat:
                                        note_manager.update_note(note['id'], category=new_name.strip())
                                for example in example_manager.get_all_examples():
                                    if example.get('category') == cat:
                                        example_manager.update_example(example['id'], category=new_name.strip())
                                st.cache_resource.clear()  # ← 清除缓存
                                st.success(f"✅ 分类已重命名为「{new_name}」！")
                                st.session_state.edit_category_name = None
                                st.rerun()
                            except Exception as e:
                                st.error(f"重命名失败：{e}")
                    if cancel_rename:
                        st.session_state.edit_category_name = None
                        st.rerun()

            # 删除确认
            if st.session_state.confirm_delete_category == cat:
                st.warning(f"⚠️ 确认删除分类「{cat}」吗？")
                st.info("💡 提示：删除分类后，该分类下的笔记和例题不会被删除，只是分类会变为「未分类」。")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ 确认删除", key=f"confirm_del_cat_{cat}", use_container_width=True):
                        try:
                            for note in note_manager.get_all_notes():
                                if note.get('category') == cat:
                                    note_manager.update_note(note['id'], category='未分类')
                            for example in example_manager.get_all_examples():
                                if example.get('category') == cat:
                                    example_manager.update_example(example['id'], category='未分类')
                            category_manager.delete_category(cat)
                            st.cache_resource.clear()  # ← 清除缓存
                            st.success(f"✅ 分类「{cat}」已删除！")
                            st.session_state.confirm_delete_category = None
                            st.rerun()
                        except Exception as e:
                            st.error(f"删除失败：{e}")
                with c2:
                    if st.button("❌ 取消", key=f"cancel_del_cat_{cat}", use_container_width=True):
                        st.session_state.confirm_delete_category = None
                        st.rerun()

            st.markdown("---")

# ═══════════════════════════════════════════════════════════════
# TAB 4：数据统计
# ═══════════════════════════════════════════════════════════════
elif tab_choice == "📊 数据统计":
    st.header("📊 数据统计")

    all_notes    = note_manager.get_all_notes()
    all_examples = example_manager.get_all_examples()

    st.markdown("### 📈 总览")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-number">{len(all_notes)}</div>
            <div class="stat-label">📝 笔记总数</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg,#f093fb,#f5576c)">
            <div class="stat-number">{len(all_examples)}</div>
            <div class="stat-label">📖 例题总数</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        total_cats = len(category_manager.get_all_categories())
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg,#43e97b,#38f9d7)">
            <div class="stat-number">{total_cats}</div>
            <div class="stat-label">🗂️ 分类总数</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        all_tags = []
        for n in all_notes:
            all_tags.extend(n.get('tags', []))
        st.markdown(f"""
        <div class="stat-box" style="background: linear-gradient(135deg,#fa709a,#fee140)">
            <div class="stat-number">{len(set(all_tags))}</div>
            <div class="stat-label">🏷️ 标签总数</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 📝 笔记分类分布")
        if all_notes:
            cat_counts = Counter(n.get('category', '未分类') for n in all_notes)
            fig_pie = px.pie(
                names=list(cat_counts.keys()),
                values=list(cat_counts.values()),
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.35
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("暂无笔记数据")

    with col_right:
        st.markdown("#### 📖 例题分类分布")
        if all_examples:
            ex_cat_counts = Counter(e.get('category', '未分类') for e in all_examples)
            fig_bar = go.Figure(go.Bar(
                x=list(ex_cat_counts.keys()),
                y=list(ex_cat_counts.values()),
                marker_color='#4caf50',
                text=list(ex_cat_counts.values()),
                textposition='outside'
            ))
            fig_bar.update_layout(
                xaxis_title="分类", yaxis_title="数量",
                margin=dict(t=20, b=20, l=20, r=20),
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("暂无例题数据")

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.markdown("#### 🕐 最近活动时间线")
        activities = []
        for n in all_notes:
            activities.append({
                'time':  n.get('updated_at', n.get('created_at', '')),
                'type':  '📝 笔记',
                'title': n['title']
            })
        for e in all_examples:
            activities.append({
                'time':  e.get('updated_at', e.get('created_at', '')),
                'type':  '📖 例题',
                'title': e['title']
            })
        activities.sort(key=lambda x: x['time'], reverse=True)
        recent = activities[:10]
        if recent:
            for act in recent:
                st.markdown(
                    f"- `{format_datetime(act['time'])}` &nbsp; {act['type']} &nbsp; **{act['title']}**"
                )
        else:
            st.info("暂无活动记录")

    with col_right2:
        st.markdown("#### 🏷️ 标签云")
        if all_tags:
            tag_counts = Counter(all_tags).most_common(30)
            max_count  = tag_counts[0][1] if tag_counts else 1
            tag_html   = ""
            for tag, cnt in tag_counts:
                size = 0.8 + (cnt / max_count) * 1.2
                tag_html += (
                    f'<span style="font-size:{size:.1f}rem; margin:4px; display:inline-block; '
                    f'background:#e3f2fd; color:#1565c0; border-radius:12px; padding:3px 10px;">'
                    f'#{tag} <small>({cnt})</small></span>'
                )
            st.markdown(tag_html, unsafe_allow_html=True)
        else:
            st.info("暂无标签数据")