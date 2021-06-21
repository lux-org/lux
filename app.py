import html

import pandas as pd
import panel as pn
import lux

pn.extension(sizing_mode="stretch_width")

df = pd.read_csv("https://raw.githubusercontent.com/lux-org/lux-datasets/master/data/hpi.csv")

def save_as_iframe(df, style="width:100%;height:100%", frameborder="0"):
    html_content = df.save_as_html(output=True)
    html_content = html.escape(html_content)
    return f"""<iframe srcdoc="{html_content}" style={style} frameborder="{frameborder}"
"allowfullscreen></iframe>"""

lux_iframe_report = save_as_iframe(df)

# Can display in notebook
lux_panel = pn.pane.HTML(lux_iframe_report, height=425)

# Can display as app with panel serve
pn.template.FastListTemplate(site="💡 Lux and Panel", title="Analysis of Happy Planet Index Dataset", main=[lux_panel]).servable();