
import tkinter as tk
from tkinter import ttk
import os
import sys
from datetime import datetime, timezone
from PIL import Image, ImageTk
from weather_api import get_weather_by_city, get_forecast_by_city, get_detailed_forecast_by_city
from themes import set_dynamic_background
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from graph_forecast import create_forecast_figure
from utils import update_fav_button

def handle_search(ui, unit_var):
    city = ui["search_entry"].get()
    unit = unit_var.get()
    ui["status_label"].config(text="Loading...", foreground="black")
    ui["status_label"].update_idletasks()
    ui["search_button"].config(state="disabled")

    error_type = None

    try:
        #---Current Weather---
        result = get_weather_by_city(city, unit)
        if "error" in result:
            if "Location" in result["error"]:
                ui["city_label"].config(text="City: Not found", foreground="red")
                error_type = "Bad Location"
            else:
                error_type = "Network Not Found"
                ui["city_label"].config(text="No Network", foreground="red")
            ui["temp_label"].config(text="Temperature: —")
            ui["condition_label"].config(text="Condition: —")
            ui["humidity_label"].config(text="Humidity: —")
            ui["wind_label"].config(text="Wind Speed: —")
            ui["icon_label"].config(image="")
            icon_code = "error"
        else:
            unit_symbol = "°C" if unit == "metric" else "°F"
            ui["city_label"].config(text=f"{result['city']}", foreground="black")
            ui["temp_label"].config(text=f"Temperature: {result['temperature']}{unit_symbol}")
            ui["condition_label"].config(text=f"Condition: {result['condition']}")
            ui["humidity_label"].config(text=f"Humidity: {result['humidity']}%")
            ui["wind_label"].config(text=f"Wind Speed: {result['wind_speed']} m/s")
            ui["time_label"].config(text=f"{result['day']} {result['date']} {result['time']}")
            bg, border, light = set_dynamic_background(ui["root"], result["condition"])

            icon_code = result.get("icon")
        if icon_code:
            photo = load_weather_icon(icon_code, size=(150, 150))
            if photo:
                ui["icon_label"].config(image=photo)
                ui["icon_label"].image = photo
            else:
                ui["icon_label"].config(image="")
        else:
            ui["icon_label"].config(image="")
        
        #---Forecast---
        container = ui["forecast_cards_container"]
        for widget in container.winfo_children():
                widget.destroy()

        if "error" not in result:
            forecast = get_forecast_by_city(city, unit)
        
            if isinstance(forecast, dict) and "error" in forecast:
                error_type = "Could not get Forecast"
            else:
                forecast_icons = []
                for i, day in enumerate(forecast):
                    card = tk.Frame(
                        container,
                        relief="flat",
                        highlightbackground=border,
                        highlightthickness=1,
                        bg=bg,
                        width=150,
                        height=155
                    )
                    card.pack_propagate(False)
                    card.grid(row=0, column=i, padx=5, pady=5)

                    try:
                        date_obj = datetime.datetime.strptime(day["date"], "%Y-%m-%d")
                        day_name = date_obj.strftime("%A")
                        ttk.Label(card, text=day_name, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=5)
                        ttk.Label(card, text=day["date"], font=("Segoe UI", 10)).pack(anchor="w", padx=5)
                    except Exception as e:
                        ttk.Label(card, text=day["date"], font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=5)

                    try:
                        icon_code = day['icon']
                        icon_path = resource_path(os.path.join("weather_icons", f"{icon_code}.png"))
                        img = Image.open(icon_path).resize((60, 60), Image.LANCZOS)
                        icon_img = ImageTk.PhotoImage(img)
                        forecast_icons.append(icon_img)
                        icon_label = ttk.Label(card, image=icon_img)
                        icon_label.image = icon_img
                        icon_label.pack(pady=5)
                    except Exception as e:
                        ttk.Label(card, text="(icon)").pack(pady=5)
                        icon_img = ImageTk.PhotoImage(img)
                        forecast_icons.append(icon_img)
                        icon_label = ttk.Label(card, image=icon_img)
                        icon_label.image = icon_img
                        icon_label.pack(pady=5)
                    except Exception as e:
                        ttk.Label(card, text="(icon)").pack(side="left", padx=5)

                    try:
                        temp_text = f"{day["min_temp"]}/{day["max_temp"]}{unit_symbol}"
                        ttk.Label(card, text=temp_text, font=("Segoe UI", 10, "bold")).pack(anchor="center", pady=(5, 0))
                    except Exception as e:
                        ttk.Label(card, text=day["temperature"], font=("Segoe UI", 10, "bold")).pack(anchor="w")
    except Exception as e:
        pass    #Exception handled in 'Update UI' block
    
    #---Detailed Forecast---
    if "error" not in result and "error" not in forecast:
        try:
            detailed_forecast = get_detailed_forecast_by_city(city, unit,)
    
            if isinstance(detailed_forecast, list) and detailed_forecast:
                fig = create_forecast_figure(detailed_forecast, city, bg, border, light, unit)
                embed_chart(ui, fig)
        except Exception as e:
            error_type = "Could not graph Forecast"
            for widget in ui["chart_frame"].winfo_children():
                widget.destroy()
    else:
        for widget in ui["chart_frame"].winfo_children():
            widget.destroy()
    
    #---Update UI---
    try:
        set_dynamic_background(ui["root"], result["condition"])
        ui["save_button"].config(state="enabled")
        ui["unit_toggle_button"].config(state="enabled")
        ui["status_label"].config(text="")
    except Exception as e:
        ui["status_label"].config(text=error_type, foreground="red")
        ui["save_button"].config(state="disabled")
        ui["unit_toggle_button"].config(state="disabled")

    ui["search_button"].config(state="normal")
    reset_auto_refresh(ui, unit_var)

    update_fav_button(ui)
    ui["search_entry_highlighted"] = False


def build_ui(parent, unit_var):
    def toggle_units():
        current = unit_var.get()
        new_unit = "imperial" if current == "metric" else "metric"
        unit_var.set(new_unit)
        handle_search(ui_refs, unit_var)

    #---MAIN WINDOW---
    parent.title("Weather View")
    parent.geometry("820x620+100+50")
    parent.resizable(False, False)

    try:
        icon_path = resource_path(os.path.join("weather_icons", f"{icon_code}.png"))
        icon_image = Image.open(icon_path)
        icon_photo = ImageTk.PhotoImage(icon_image)
        parent.iconphoto(False, icon_photo)
    except Exception as e:
        pass

    #---FRAME: Current Weather---
    current_weather_frame = tk.Frame(parent)
    current_weather_frame.pack(padx=10, fill="x")
    current_weather_frame.configure(height=180)
    current_weather_frame.pack_propagate(False)

    weather_content_frame = ttk.Frame(current_weather_frame)
    weather_content_frame.pack(fill="x", padx=(3,10), pady=0)

    icon_label = ttk.Label(weather_content_frame)
    icon_label.pack(side="left", padx=(0, 10), pady=(10,0))

    weather_text_frame = ttk.Frame(weather_content_frame)
    weather_text_frame.pack(side="left", fill="x")

    temp_label = ttk.Label(weather_text_frame, text="Temperature: ", font=("Segoe UI", 12))
    temp_label.pack(anchor="w", pady=4)

    condition_label = ttk.Label(weather_text_frame, text="Condition: ", font=("Segoe UI", 12))
    condition_label.pack(anchor="w", pady=4)

    humidity_label = ttk.Label(weather_text_frame, text="Humidity: ", font=("Segoe UI", 12))
    humidity_label.pack(anchor="w", pady=4)

    wind_label = ttk.Label(weather_text_frame, text="Wind Speed: ", font=("Segoe UI", 12))
    wind_label.pack(anchor="w", pady=4)

    #---FRAME: Search---
    search_area_frame = ttk.Frame(weather_content_frame)
    search_area_frame.pack(side="right", fill="x", pady=(0,0))

    city_label = ttk.Label(search_area_frame, text="City: ", font=("Segoe UI", 18, "bold"))
    city_label.pack(anchor="w", padx=20)

    time_label = ttk.Label(search_area_frame, text="Time: ", font=("Segoe UI", 12))
    time_label.pack(anchor="w", padx=20, pady=(2,0))

    search_frame = ttk.Frame(search_area_frame, padding=10)
    search_frame.pack(fill='x')

    search_entry = ttk.Entry(search_frame, width=30)
    search_entry.pack(side='left', padx=(0, 10))

    def select_all(event):
        if not ui_refs["search_entry_highlighted"]:
            event.widget.after(1, lambda: event.widget.select_range(0, tk.END))
            ui_refs["search_entry_highlighted"] = True

    search_entry.bind("<FocusIn>", select_all)
    search_entry.bind("<Button-1>", select_all)
    
    search_entry.bind("<Return>", lambda event: handle_search(ui_refs, unit_var))

    search_button = ttk.Button(search_frame, text="Search", command=lambda: handle_search(ui_refs, unit_var))
    search_button.pack(side='left')

    status_label = ttk.Label(search_frame, text="", foreground="red")
    status_label.pack(side='left', padx=(10, 10))

    save_frame = ttk.Frame(search_area_frame, padding=0 )
    save_frame.pack(fill='x')

    favourites_var = tk.StringVar()
    favourites_dropdown = ttk.Combobox(save_frame, textvariable=favourites_var, state="readonly", width=22)
    favourites_dropdown.pack(side="left", padx=(10, 0))

    save_button = ttk.Button(save_frame, text="Save to Favourites", width=22)
    save_button.pack(side="left", padx=(10, 0))

    unit_toggle_button = ttk.Button(save_frame, text="°C / °F", command=toggle_units)
    unit_toggle_button.pack(side='right', padx=5)

    #---FRAME: Forecast Cards---
    forecast_frame = tk.Frame(parent)
    forecast_frame.pack(padx=10, fill="x")
    forecast_frame.configure(height=160)
    forecast_frame.pack_propagate(False)

    forecast_cards_container = ttk.Frame(forecast_frame)
    forecast_cards_container.pack(fill="x")

    #---FRAME: Forecast Chart---
    chart_frame = tk.Frame(parent, height=255, width=780)
    chart_frame.pack_propagate(False)
    chart_frame.pack(pady=(5, 10), anchor="n")

    ui_refs = {
        "root": parent,
        "current_weather_frame": current_weather_frame,
        "search_entry": search_entry,
        "search_button": search_button,
        "status_label" : status_label,
        "save_button" : save_button,
        "favourites_dropdown" : favourites_dropdown,
        "city_label": city_label,
        "temp_label": temp_label,
        "condition_label": condition_label,
        "humidity_label": humidity_label,
        "wind_label": wind_label,
        "time_label": time_label,
        "icon_label": icon_label,
        "forecast_cards_container": forecast_cards_container,
        "unit_toggle_button": unit_toggle_button,
        "chart_frame": chart_frame
    }

    return ui_refs

def start_auto_refresh(ui, unit_var, interval_ms=900000):
    def refresh():
        handle_search(ui, unit_var)
        ui["auto_refresh_id"] = ui["root"].after(interval_ms, refresh)
    ui["auto_refresh_id"] = ui["root"].after(interval_ms, refresh)

def reset_auto_refresh(ui, unit_var, interval_ms=900000):
    if "auto_refresh_id" in ui:
        ui["root"].after_cancel(ui["auto_refresh_id"])
    start_auto_refresh(ui, unit_var, interval_ms)

def load_weather_icon(icon_code, size=(150, 150)):
    try:
        icon_path = resource_path(os.path.join("weather_icons", f"{icon_code}.png"))
        if not os.path.exists(icon_path):
            icon_path = os.path.join("weather_icons", "default.png")
        image = Image.open(icon_path).resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as e:
        return None

def embed_chart(ui, fig, retry_delay=50, max_attempts=20, attempt=0):

    frame = ui["chart_frame"]

    if frame.winfo_ismapped() and frame.winfo_width() > 1:
        for widget in frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=False, pady=(5, 10))

    elif attempt < max_attempts:
        frame.after(retry_delay, lambda: embed_chart(ui, fig, retry_delay, max_attempts, attempt + 1))

def focus_search_entry(ui_refs):
    ui_refs["root"].focus_force()
    ui_refs["search_entry"].focus()
    ui_refs["search_entry"].selection_range(0, tk.END)
    ui_refs["search_entry_highlighted"] = False

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

