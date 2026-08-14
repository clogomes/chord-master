"""
ChordMaster Design System & Theme Tokens.

Standardizes typography, color harmony, visual hierarchy, and UI building blocks
across all screens and interactive components in ChordMaster.
"""

from typing import Tuple, Union, Optional
import customtkinter as ctk

# ============================================================================
# 1. TYPOGRAPHY SCALES
# ============================================================================
# Note: Body text must never be smaller than 14px for high legibility.
# Headers: 22-26px bold. Section titles: 16-18px bold. Badges/Captions: 12px.

FONT_FAMILY: str = "Helvetica"
FONT_MONO_FAMILY: str = "Courier"

FONT_HERO: Tuple[str, int, str] = ("Helvetica", 32, "bold")
FONT_TITLE: Tuple[str, int, str] = ("Helvetica", 24, "bold")
FONT_SECTION: Tuple[str, int, str] = ("Helvetica", 18, "bold")
FONT_SUBTITLE: Tuple[str, int, str] = ("Helvetica", 16, "bold")
FONT_BODY: Tuple[str, int] = ("Helvetica", 14)
FONT_BODY_BOLD: Tuple[str, int, str] = ("Helvetica", 14, "bold")
FONT_SMALL: Tuple[str, int] = ("Helvetica", 12)
FONT_SMALL_BOLD: Tuple[str, int, str] = ("Helvetica", 12, "bold")
FONT_BADGE: Tuple[str, int, str] = ("Helvetica", 12, "bold")
FONT_MONO: Tuple[str, int, str] = ("Courier", 14, "bold")
FONT_MONO_BODY: Tuple[str, int] = ("Courier", 14)


def get_font(
    spec: Union[Tuple, str],
    size: Optional[int] = None,
    weight: Optional[str] = None
) -> ctk.CTkFont:
    """
    Factory helper to instantiate a CTkFont instance from a tuple or custom specs.

    Example:
        `label = ctk.CTkLabel(frame, text="Title", font=get_font(FONT_TITLE))`
    """
    if isinstance(spec, tuple):
        family = spec[0]
        f_size = spec[1] if size is None else size
        f_weight = spec[2] if len(spec) > 2 and weight is None else (weight or "normal")
        return ctk.CTkFont(family=family, size=f_size, weight=f_weight)
    elif isinstance(spec, str):
        return ctk.CTkFont(family=spec, size=size or 14, weight=weight or "normal")
    return ctk.CTkFont()


# ============================================================================
# 2. COLOR PALETTE TOKENS (LIGHT_MODE, DARK_MODE)
# ============================================================================
# Modern slate base palette with purpose-driven accents:
# - Indigo: Primary brand actions & navigation
# - Emerald: Success, correct answers, in-tune status, mastered progress
# - Sky: Theory concepts, informational banners, chords & scales
# - Amber: Attention, sharp notes, ear training interval prompts
# - Crimson: Flat notes, errors, danger/reset actions
# - Purple: Tetrads, advanced harmonic extensions, score badges

# Surface & Structural Colors
COLOR_BG: Tuple[str, str] = ("#F8FAFC", "#0B0F19")           # Main background
COLOR_SURFACE: Tuple[str, str] = ("#FFFFFF", "#111827")      # Card / container surface
COLOR_SURFACE_SECONDARY: Tuple[str, str] = ("#F1F5F9", "#1F2937")  # Inner card / row highlight
COLOR_SURFACE_HOVER: Tuple[str, str] = ("#E2E8F0", "#374151")      # Hovered row / item
COLOR_BORDER: Tuple[str, str] = ("#E2E8F0", "#374151")       # Clean 1px border
COLOR_BORDER_SUBTLE: Tuple[str, str] = ("#CBD5E1", "#1F2937") # Subtle border separator

# Primary Brand (Royal Indigo)
COLOR_PRIMARY: str = "#4F46E5"
COLOR_PRIMARY_HOVER: str = "#4338CA"
COLOR_PRIMARY_BG: Tuple[str, str] = ("#EEF2FF", "#1E1B4B")
COLOR_PRIMARY_BORDER: Tuple[str, str] = ("#C7D2FE", "#3730A3")

# Success / Progress / In-Tune (Emerald)
COLOR_SUCCESS: str = "#10B981"
COLOR_SUCCESS_HOVER: str = "#059669"
COLOR_SUCCESS_DARK: str = "#064E3B"
COLOR_SUCCESS_BG: Tuple[str, str] = ("#ECFDF5", "#064E3B")
COLOR_SUCCESS_BORDER: Tuple[str, str] = ("#A7F3D0", "#047857")

# Accent Colors
# Theory & Notes (Sky Blue)
COLOR_ACCENT_SKY: str = "#0284C7"
COLOR_ACCENT_SKY_HOVER: str = "#0369A1"
COLOR_SKY_BG: Tuple[str, str] = ("#E0F2FE", "#082F49")
COLOR_SKY_BORDER: Tuple[str, str] = ("#BAE6FD", "#075985")

# Tuning & Attention (Amber)
COLOR_ACCENT_AMBER: str = "#F59E0B"
COLOR_ACCENT_AMBER_HOVER: str = "#D97706"
COLOR_AMBER_BG: Tuple[str, str] = ("#FEF3C7", "#78350F")
COLOR_AMBER_BORDER: Tuple[str, str] = ("#FDE68A", "#B45309")

# Error / Flat Notes / Reset (Crimson)
COLOR_ACCENT_CRIMSON: str = "#EF4444"
COLOR_ACCENT_CRIMSON_HOVER: str = "#DC2626"
COLOR_CRIMSON_BG: Tuple[str, str] = ("#FEE2E2", "#7F1D1D")
COLOR_CRIMSON_BORDER: Tuple[str, str] = ("#FECACA", "#991B1B")

# Tetrads & Advanced Harmony (Purple)
COLOR_ACCENT_PURPLE: str = "#8B5CF6"
COLOR_ACCENT_PURPLE_HOVER: str = "#7C3AED"
COLOR_PURPLE_BG: Tuple[str, str] = ("#F3E8FF", "#3B0764")
COLOR_PURPLE_BORDER: Tuple[str, str] = ("#DDD6FE", "#6D28D9")

# Text Hierarchy
COLOR_TEXT_PRIMARY: Tuple[str, str] = ("#0F172A", "#F9FAFB")  # Slate 900 / Slate 50
COLOR_TEXT_MUTED: Tuple[str, str] = ("#64748B", "#94A3B8")    # Slate 500 / Slate 400
COLOR_TEXT_SUBTLE: Tuple[str, str] = ("#94A3B8", "#6B7280")   # Slate 400 / Slate 500
COLOR_TEXT_INVERSE: Tuple[str, str] = ("#FFFFFF", "#FFFFFF")  # Crisp white on solid badges


# ============================================================================
# 3. SPACING & GEOMETRY TOKENS
# ============================================================================
PAD_XS: int = 4
PAD_SM: int = 8
PAD_MD: int = 16
PAD_LG: int = 24
PAD_XL: int = 32

RADIUS_SM: int = 6
RADIUS_MD: int = 10
RADIUS_LG: int = 14
RADIUS_FULL: int = 999

BORDER_WIDTH: int = 1


# ============================================================================
# 4. COMPONENT BUILDER HELPERS
# ============================================================================

def create_card_frame(
    master,
    corner_radius: int = RADIUS_MD,
    fg_color: Tuple[str, str] = COLOR_SURFACE,
    border_color: Tuple[str, str] = COLOR_BORDER,
    border_width: int = BORDER_WIDTH,
    **kwargs
) -> ctk.CTkFrame:
    """
    Creates a styled card container matching ChordMaster design tokens.
    """
    return ctk.CTkFrame(
        master,
        corner_radius=corner_radius,
        fg_color=fg_color,
        border_color=border_color,
        border_width=border_width,
        **kwargs
    )


def create_header(
    master,
    title: str,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
    padx: int = PAD_LG,
    pady: Tuple[int, int] = (PAD_LG, PAD_MD)
) -> ctk.CTkFrame:
    """
    Creates a standardized header banner with bold title and muted subtitle.
    """
    header_frame = ctk.CTkFrame(master, fg_color="transparent")
    header_frame.pack(fill="x", padx=padx, pady=pady)

    display_title = f"{icon} {title}" if icon else title
    title_label = ctk.CTkLabel(
        header_frame,
        text=display_title,
        font=get_font(FONT_TITLE),
        text_color=COLOR_TEXT_PRIMARY,
    )
    title_label.pack(anchor="w")

    if subtitle:
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text=subtitle,
            font=get_font(FONT_BODY),
            text_color=COLOR_TEXT_MUTED,
        )
        subtitle_label.pack(anchor="w", pady=(PAD_XS, 0))

    return header_frame


def create_badge(
    master,
    text: str,
    bg_color: Union[str, Tuple[str, str]] = COLOR_PRIMARY_BG,
    text_color: Union[str, Tuple[str, str]] = COLOR_PRIMARY,
    corner_radius: int = RADIUS_SM,
    padx: int = PAD_SM,
    pady: int = PAD_XS,
    **kwargs
) -> ctk.CTkLabel:
    """
    Creates a compact badge / tag for categories, difficulty, or status indicators.
    """
    return ctk.CTkLabel(
        master,
        text=text,
        font=get_font(FONT_BADGE),
        fg_color=bg_color,
        text_color=text_color,
        corner_radius=corner_radius,
        padx=padx,
        pady=pady,
        **kwargs
    )
