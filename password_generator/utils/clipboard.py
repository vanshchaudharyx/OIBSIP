"""
Clipboard integration utility.
Works cross-platform using tkinter or pyperclip as fallback.
"""


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard.
    Returns True on success, False on failure.
    """
    # Try tkinter first (no extra deps)
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        # Note: clipboard is cleared when root is destroyed
        # We keep root alive briefly; GUI app manages its own root
        root.after(3000, root.destroy)
        root.mainloop()
        return True
    except Exception:
        pass

    # Fallback: pyperclip
    try:
        import pyperclip  # type: ignore
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    return False


def copy_to_clipboard_via_widget(text: str, widget) -> bool:
    """
    Copy text using an existing tkinter widget's clipboard.
    Use this inside a running tkinter app.
    """
    try:
        widget.clipboard_clear()
        widget.clipboard_append(text)
        widget.update()
        return True
    except Exception:
        return False