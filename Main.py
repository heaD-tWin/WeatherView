"""
Weather View - A weather dashboard using OpenWeatherMap API.
Author: Dan White
"""

import tkinter as tk
from ui_components import build_ui, handle_search, start_auto_refresh, focus_search_entry
from geolocation import get_user_city
from favourites import  load_favourites
from utils import on_save_favourite, update_fav_button
    
def on_select_favourite(ui, unit_var):
    selected_city = ui["favourites_dropdown"].get()
    if selected_city:
        ui["search_entry"].delete(0, tk.END)
        ui["search_entry"].insert(0, selected_city)
        handle_search(ui, unit_var)
        update_fav_button(ui)

def main():
    root = tk.Tk()
    root.withdraw()

    unit_var = tk.StringVar(value="metric")
    ui = build_ui(root, unit_var)
    start_auto_refresh(ui, unit_var)
    user_city = get_user_city()

    if user_city:
        ui["search_entry"].delete(0, tk.END)
        ui["search_entry"].insert(0, user_city)
        handle_search(ui, unit_var)
        update_fav_button(ui)

    favourites = load_favourites()
    ui["favourites_dropdown"]["values"] = favourites
    ui["save_button"].config(command=lambda: on_save_favourite(ui))
    ui["favourites_dropdown"].bind("<<ComboboxSelected>>", lambda _: on_select_favourite(ui, unit_var)) 
    update_fav_button(ui)
    ui["root"].after(100, lambda: focus_search_entry(ui))

    root.deiconify()
    root.mainloop()

if __name__ == "__main__":
    main()
