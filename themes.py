import tkinter as tk
from tkinter import ttk

def set_dynamic_background(root, condition, theme="light"):

    style = ttk.Style()
    condition = condition.lower()

    condition_map = {
        "clear": ["clear", "sunny"],
        "clouds": ["clouds", "few clouds", "scattered clouds", "broken clouds", "overcast clouds"],
        "rain": ["rain", "light rain", "moderate rain", "heavy rain", "freezing rain", "shower rain"],
        "drizzle": ["drizzle", "light drizzle"],
        "thunderstorm": ["thunderstorm", "thunderstorms", "storm"],
        "snow": ["snow", "light snow", "heavy snow", "sleet"],
        "mist": ["mist", "fog", "haze", "smoke", "dust", "sand", "ash", "squall"],
    }

    bg_colors = {
        "clear": "#87CEFA",
        "clouds": "#B0C4DE",
        "rain": "#778899",
        "snow": "#F0F8FF",
        "thunderstorm": "#2F4F4F",
        "drizzle": "#A9A9A9",
        "mist": "#D3D3D3",
        "default": "#ADD8E6",
    }

    dark_colors = {
        "clear": "#1E3A5F",
        "clouds": "#3A4A5A",
        "rain": "#2F3540",
        "snow": "#B0C8D8",
        "thunderstorm": "#0D1111",
        "drizzle": "#2F2F2F",
        "mist": "#4F4F4F",
        "default": "#2A506F",
    }

    light_colors = {
        "clear": "#E0F6FF",
        "clouds": "#E8EEF4",
        "rain": "#D3D6DA",
        "snow": "#FFFFFF",
        "thunderstorm": "#DDE3E3",
        "drizzle": "#E5E5E5",
        "mist": "#F2F2F2",
        "default": "#E3F0FA",
    }

    matched_category = "default"
    for category, keywords in condition_map.items():
        if any(keyword in condition for keyword in keywords):
            matched_category = category
            break

    bg_color = bg_colors.get(matched_category, bg_colors["default"])
    dark_color = dark_colors.get(matched_category, dark_colors["default"])
    light_color = light_colors.get(matched_category, light_colors["default"])

    root.configure(bg=bg_color)

    style.configure(".", background=bg_color)
    style.configure("TFrame", background=bg_color)
    style.configure("TLabel", background=bg_color)
    style.configure("TLabelframe", background=bg_color)
    style.configure("TLabelframe.Label", background=bg_color)
    style.configure("TCombobox", fieldbackground=bg_color)
    style.map("TCombobox", fieldbackground=[('readonly', bg_color)])

    for child in root.winfo_children():
        if isinstance(child, tk.Label) or isinstance(child, tk.Frame):
            try:
                child.configure(bg=bg_color)
            except tk.TclError:
                pass

    return bg_color, dark_color, light_color