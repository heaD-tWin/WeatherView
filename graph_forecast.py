import datetime
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure
from matplotlib import rcParams


rcParams['toolbar'] = 'None'

def create_forecast_figure(forecast_data, city_name, bg_color, border, light, unit):
    datetimes = [datetime.datetime.strptime(entry["datetime"], "%Y-%m-%d %H:%M:%S") for entry in forecast_data]
    temps = [entry["temperature"] for entry in forecast_data]

    fig = Figure(figsize=(7.8, 2.4), dpi=100)
    ax = fig.add_subplot(111)

    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(light)
    for spine in ax.spines.values():
        spine.set_edgecolor(border)

    ax.plot(datetimes, temps, marker='o', linestyle='-', color=border)
    # This line is changed to use a simple 'C'
    unit_symbol = "C" if unit == "metric" else "F"
    ax.set_title(f"5-Day Temperature Forecast for {city_name.title()} ({unit_symbol})")
    ax.grid(True)

    ax.xaxis.set_major_formatter(DateFormatter('%a %H:%M'))
    ax.tick_params(axis='x', labelrotation=15)

    for label in ax.get_xticklabels():
        label.set_fontsize(8)

    fig.tight_layout(pad=2)
    fig.subplots_adjust(bottom=0.15)
    fig.texts.clear()
    fig.subplots_adjust(left=0.05) 

    return fig

