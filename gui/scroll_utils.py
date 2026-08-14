"""Utilities for smooth cross-platform mouse wheel scrolling on CTkScrollableFrame."""
import sys
import customtkinter as ctk


def bind_mousewheel(scrollable_frame: ctk.CTkScrollableFrame):
    """
    Recursively attaches cross-platform mousewheel events (<MouseWheel>, <Button-4>, <Button-5>)
    to a CTkScrollableFrame, its internal canvas, and all its children widgets.
    """
    if not isinstance(scrollable_frame, ctk.CTkScrollableFrame):
        return

    canvas = getattr(scrollable_frame, "_parent_canvas", None)
    if canvas is None:
        return

    is_macos = sys.platform == "darwin"
    is_windows = sys.platform.startswith("win")

    def _on_mousewheel(event):
        try:
            if not canvas.winfo_exists():
                return
            if is_macos:
                # macOS delta is small integer (+1 / -1)
                delta = -1 * int(event.delta) if event.delta else 0
                if delta == 0 and event.delta:
                    delta = -1 if event.delta > 0 else 1
                canvas.yview_scroll(delta, "units")
            elif is_windows:
                # Windows delta is +/- 120 per notch
                delta = int(-1 * (event.delta / 120)) if event.delta else 0
                canvas.yview_scroll(delta, "units")
            else:
                # Fallback
                delta = -1 if event.delta > 0 else 1
                canvas.yview_scroll(delta, "units")
        except Exception:
            pass

    def _on_linux_scroll_up(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(-1, "units")
        except Exception:
            pass

    def _on_linux_scroll_down(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(1, "units")
        except Exception:
            pass

    def _bind_widget_recursively(widget):
        try:
            # Bind mousewheel to the widget
            widget.bind("<MouseWheel>", _on_mousewheel, add="+")
            widget.bind("<Button-4>", _on_linux_scroll_up, add="+")
            widget.bind("<Button-5>", _on_linux_scroll_down, add="+")

            # When mouse enters a container, bind its children in case they were added dynamically
            widget.bind(
                "<Enter>",
                lambda e, w=widget: _bind_subchildren(w),
                add="+"
            )
        except Exception:
            pass

        for child in widget.winfo_children():
            _bind_widget_recursively(child)

    def _bind_subchildren(parent_widget):
        try:
            for child in parent_widget.winfo_children():
                try:
                    child.bind("<MouseWheel>", _on_mousewheel, add="+")
                    child.bind("<Button-4>", _on_linux_scroll_up, add="+")
                    child.bind("<Button-5>", _on_linux_scroll_down, add="+")
                except Exception:
                    pass
        except Exception:
            pass

    # Initial binding pass
    _bind_widget_recursively(scrollable_frame)
    if canvas:
        _bind_widget_recursively(canvas)
