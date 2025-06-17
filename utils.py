from favourites import save_favourite, load_favourites

def on_save_favourite(ui):
    city = ui["search_entry"].get().strip().title()
    favourites = load_favourites()
    if city and city not in favourites:
        favourites.append(city)
        save_favourite(city)
        ui["favourites_dropdown"]["values"] = favourites
    update_fav_button(ui)

def update_fav_button(ui):
    city = ui["search_entry"].get().strip().title()
    favourites = load_favourites()
    if city in favourites:
        ui["save_button"].config(
            text="Remove from Favourites",
            command=lambda: on_remove_favourite(ui)
        )
        ui["favourites_dropdown"].set(city)      
    else:
        ui["save_button"].config(
            text="Save to Favourites",
            command=lambda: on_save_favourite(ui)
        )
        ui["favourites_dropdown"].set("")
    favourites = load_favourites()

def on_remove_favourite(ui):
    city = ui["search_entry"].get().strip().title()
    favourites = load_favourites()
    if city in favourites:
        favourites.remove(city)
        save_favourite(city)
        ui["favourites_dropdown"]["values"] = favourites
        update_fav_button(ui)

