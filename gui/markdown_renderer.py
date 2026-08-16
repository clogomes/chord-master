"""Markdown parser and rich-text renderer for CustomTkinter text boxes with table embedding and glossary auto-linking."""
import re
from typing import Callable, Dict, List, Optional, Tuple
import customtkinter as ctk


# Cache for glossary lookup keywords
_GLOSSARY_KEYWORDS_CACHE: Optional[Dict[str, str]] = None


def get_glossary_keywords_map() -> Dict[str, str]:
    """Returns a mapping of normalized glossary terms and aliases to their term_id."""
    global _GLOSSARY_KEYWORDS_CACHE
    if _GLOSSARY_KEYWORDS_CACHE is not None:
        return _GLOSSARY_KEYWORDS_CACHE

    mapping = {}
    try:
        from core.glossary import GLOSSARY_DATABASE
        for term in GLOSSARY_DATABASE:
            # Map canonical ID
            mapping[term.id.replace("_", " ").lower()] = term.id
            
            # Map clean PT term (remove parentheticals)
            clean_pt = re.sub(r"\(.*?\)", "", term.term_pt).strip().lower()
            if len(clean_pt) >= 3:
                mapping[clean_pt] = term.id
            
            # Map clean EN term
            if term.term_en:
                clean_en = re.sub(r"\(.*?\)", "", term.term_en).strip().lower()
                if len(clean_en) >= 3:
                    mapping[clean_en] = term.id
    except Exception:
        pass

    _GLOSSARY_KEYWORDS_CACHE = mapping
    return _GLOSSARY_KEYWORDS_CACHE


def parse_markdown_line_type(line: str) -> str:
    """Classifies a single line of markdown text into its structural token type."""
    stripped = line.strip()
    if not stripped:
        return "empty"
    if stripped.startswith("### "):
        return "h3"
    if stripped.startswith("## "):
        return "h2"
    if stripped.startswith("# "):
        return "h1"
    if stripped in ["---", "***", "___"]:
        return "separator"
    if stripped.startswith("• ") or stripped.startswith("- ") or stripped.startswith("* "):
        return "bullet"
    if stripped.startswith("|") and stripped.endswith("|"):
        if is_table_delimiter(stripped):
            return "table_delimiter"
        return "table_row"
    return "paragraph"


def is_table_delimiter(line: str) -> str:
    """Checks if a table row is a delimiter/alignment row (e.g., '| :--- | :--- |')."""
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return False
    clean = re.sub(r"[|\-:\s]", "", stripped)
    return len(clean) == 0 and "-" in stripped


def parse_table_cells(line: str) -> List[str]:
    """Extracts clean string cell values from a markdown table row."""
    parts = line.strip().split("|")
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def parse_inline_bold(text: str) -> List[Tuple[str, bool]]:
    """Parses a string containing '**bold text**' into a list of tuples (chunk_text, is_bold)."""
    if not text:
        return []

    pattern = r"\*\*(.+?)\*\*"
    chunks: List[Tuple[str, bool]] = []
    last_idx = 0

    for match in re.finditer(pattern, text):
        start, end = match.span()
        if start > last_idx:
            chunks.append((text[last_idx:start], False))
        chunks.append((match.group(1), True))
        last_idx = end

    if last_idx < len(text):
        chunks.append((text[last_idx:], False))

    return chunks


def _split_chunk_with_glossary_terms(
    text: str,
    keywords_map: Dict[str, str]
) -> List[Tuple[str, Optional[str]]]:
    """
    Splits text into chunks of (subtext, matched_term_id_or_none).
    Prioritizes longer keyword matches first.
    """
    if not text or not keywords_map:
        return [(text, None)]

    # Sort keywords by length descending to match longest phrases first
    sorted_keywords = sorted(keywords_map.keys(), key=lambda k: len(k), reverse=True)
    
    # We match keywords as distinct terms / words
    # To avoid regex performance bottlenecks, build regex for keywords with length >= 4
    significant_keywords = [re.escape(k) for k in sorted_keywords if len(k) >= 4]
    if not significant_keywords:
        return [(text, None)]

    pattern = r"\b(" + "|".join(significant_keywords) + r")\b"
    result: List[Tuple[str, Optional[str]]] = []
    last_idx = 0

    for match in re.finditer(pattern, text, flags=re.IGNORECASE):
        start, end = match.span()
        matched_str = match.group(1).lower()
        term_id = keywords_map.get(matched_str)

        if start > last_idx:
            result.append((text[last_idx:start], None))
        
        result.append((text[start:end], term_id))
        last_idx = end

    if last_idx < len(text):
        result.append((text[last_idx:], None))

    return result if result else [(text, None)]


def render_markdown_to_textbox(
    textbox: ctk.CTkTextbox,
    markdown_text: str,
    base_font_size: int = 13,
    header_color: str = "#0F172A",
    text_color: str = "#334155",
    enable_glossary_links: bool = True,
    on_glossary_click: Optional[Callable[[str], None]] = None,
):
    """
    Renders formatted markdown into a CTkTextbox with bold spans, headings,
    bullet lists, divider rules, aligned tables, and auto-linked glossary terms.
    """
    textbox.configure(state="normal")
    textbox.delete("1.0", "end")

    tk_text = getattr(textbox, "_textbox", None)
    if tk_text:
        try:
            tk_text.tag_config("h1", font=("Helvetica", base_font_size + 6, "bold"), spacing1=10, spacing3=6)
            tk_text.tag_config("h2", font=("Helvetica", base_font_size + 4, "bold"), spacing1=8, spacing3=4)
            tk_text.tag_config("h3", font=("Helvetica", base_font_size + 2, "bold"), spacing1=6, spacing3=3)
            tk_text.tag_config("bold", font=("Helvetica", base_font_size, "bold"))
            tk_text.tag_config("normal", font=("Helvetica", base_font_size))
            tk_text.tag_config("bullet", lmargin1=14, lmargin2=28, spacing1=2, spacing3=2)
            tk_text.tag_config("separator", font=("Courier", 10), foreground="#64748B", justify="center")
        except Exception:
            pass

    keywords_map = get_glossary_keywords_map() if enable_glossary_links else {}
    used_glossary_tags = set()

    def handle_gloss_click(term_id: str):
        if on_glossary_click:
            on_glossary_click(term_id)
        else:
            try:
                from gui.components.glossary_modal import show_glossary_term_modal
                show_glossary_term_modal(textbox.winfo_toplevel(), term_id)
            except Exception:
                pass

    def insert_text_with_links(text: str, base_tags: Tuple[str, ...]):
        if not enable_glossary_links or not keywords_map:
            textbox.insert("end", text, base_tags)
            return

        gloss_chunks = _split_chunk_with_glossary_terms(text, keywords_map)
        for subtext, term_id in gloss_chunks:
            if term_id:
                tag_name = f"gloss_{term_id}"
                combined_tags = base_tags + (tag_name,)
                textbox.insert("end", subtext, combined_tags)
                
                if tk_text and tag_name not in used_glossary_tags:
                    used_glossary_tags.add(tag_name)
                    try:
                        tk_text.tag_config(tag_name, foreground="#4F46E5", underline=True)
                        tk_text.tag_bind(tag_name, "<Button-1>", lambda e, tid=term_id: handle_gloss_click(tid))
                        tk_text.tag_bind(tag_name, "<Enter>", lambda e: tk_text.configure(cursor="hand2"))
                        tk_text.tag_bind(tag_name, "<Leave>", lambda e: tk_text.configure(cursor=""))
                    except Exception:
                        pass
            else:
                textbox.insert("end", subtext, base_tags)

    lines = markdown_text.strip().split("\n")
    i = 0
    num_lines = len(lines)

    while i < num_lines:
        raw_line = lines[i]
        line_type = parse_markdown_line_type(raw_line)

        if line_type == "empty":
            textbox.insert("end", "\n")
            i += 1
            continue

        if line_type in ["h1", "h2", "h3"]:
            clean_heading = re.sub(r"^#{1,3}\s*", "", raw_line.strip())
            textbox.insert("end", f"\n{clean_heading}\n", (line_type,))
            i += 1
            continue

        if line_type == "separator":
            sep_line = "─" * 48
            textbox.insert("end", f"\n{sep_line}\n\n", ("separator",))
            i += 1
            continue

        if line_type == "bullet":
            clean_bullet = re.sub(r"^[•\-*]\s*", "", raw_line.strip())
            textbox.insert("end", "• ", ("bullet", "bold"))
            chunks = parse_inline_bold(clean_bullet)
            for chunk_text, is_bold in chunks:
                base_tag = "bold" if is_bold else "normal"
                insert_text_with_links(chunk_text, ("bullet", base_tag))
            textbox.insert("end", "\n")
            i += 1
            continue

        if line_type == "table_row":
            table_lines: List[str] = []
            while i < num_lines and parse_markdown_line_type(lines[i]) in ["table_row", "table_delimiter"]:
                table_lines.append(lines[i])
                i += 1

            _render_embedded_table(textbox, table_lines)
            textbox.insert("end", "\n")
            continue

        # Regular paragraph
        chunks = parse_inline_bold(raw_line)
        for chunk_text, is_bold in chunks:
            base_tag = "bold" if is_bold else "normal"
            insert_text_with_links(chunk_text, (base_tag,))
        textbox.insert("end", "\n")
        i += 1

    textbox.configure(state="disabled")


def _render_embedded_table(textbox: ctk.CTkTextbox, table_lines: List[str]):
    """Embeds an aligned custom grid table inside the CTkTextbox."""
    tk_text = getattr(textbox, "_textbox", None)
    if not tk_text or not table_lines:
        return

    header_cells: List[str] = []
    data_rows: List[List[str]] = []

    for line in table_lines:
        if is_table_delimiter(line):
            continue
        cells = parse_table_cells(line)
        if not header_cells:
            header_cells = cells
        else:
            data_rows.append(cells)

    if not header_cells:
        return

    table_frame = ctk.CTkFrame(
        textbox,
        corner_radius=8,
        fg_color=("#E2E8F0", "#1E293B"),
        border_width=1,
        border_color=("#CBD5E1", "#334155"),
    )

    num_cols = len(header_cells)
    for col_idx in range(num_cols):
        table_frame.grid_columnconfigure(col_idx, weight=1)

    for col_idx, text in enumerate(header_cells):
        clean_text = text.replace("**", "")
        hdr_lbl = ctk.CTkLabel(
            table_frame,
            text=clean_text,
            font=ctk.CTkFont(family="Helvetica", size=12, weight="bold"),
            text_color=("#0F172A", "#F8FAFC"),
            fg_color=("#CBD5E1", "#334155"),
            corner_radius=4,
            padx=8,
            pady=4,
        )
        hdr_lbl.grid(row=0, column=col_idx, padx=2, pady=2, sticky="nsew")

    for row_idx, row_cells in enumerate(data_rows, start=1):
        row_bg = ("#F1F5F9", "#0F172A") if row_idx % 2 == 0 else ("#FFFFFF", "#1E293B")
        for col_idx in range(num_cols):
            cell_val = row_cells[col_idx] if col_idx < len(row_cells) else ""
            clean_val = cell_val.replace("**", "").replace("*", "")
            is_bold = "**" in cell_val or col_idx == 0
            cell_lbl = ctk.CTkLabel(
                table_frame,
                text=clean_val,
                font=ctk.CTkFont(family="Helvetica", size=11, weight="bold" if is_bold else "normal"),
                text_color=("#1E293B", "#E2E8F0"),
                fg_color=row_bg,
                corner_radius=3,
                padx=6,
                pady=3,
                justify="left",
            )
            cell_lbl.grid(row=row_idx, column=col_idx, padx=1, pady=1, sticky="nsew")

    textbox.insert("end", "\n")
    try:
        tk_text.window_create("end", window=table_frame)
    except Exception:
        for line in table_lines:
            textbox.insert("end", f"{line}\n")
    textbox.insert("end", "\n")
