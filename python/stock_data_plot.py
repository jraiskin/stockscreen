import pandas as pd
import numpy as np

# import argparse

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.models.widgets import Select, TextInput, RadioButtonGroup
from bokeh.models.widgets import TableColumn, DataTable, RangeSlider
from bokeh.io import curdoc  # , output_notebook

from column_name_conversions import heb_to_eng_names, eng_to_heb_names

# import stock data from CSV
stocks_data_fname_lastest = '../assets/stocks_raw_data_latest.csv'

stocks_data = pd.read_csv(
    stocks_data_fname_lastest, 
    sep=';', 
    na_values='NaN', 
    header=0,
    index_col=0,
    encoding='UTF-8')

stocks_data_columns = sorted(list(stocks_data.columns))
stocks_data_columns_wo_name = stocks_data_columns
stocks_data_columns = ['שם חברה'] + stocks_data_columns

stocks_data['שם חברה'] = stocks_data.index

# Create Input controls
company_name = TextInput(
    title="Company name contains (hit ENTER whe done)")
x_axis = Select(title="X Axis", options=stocks_data_columns_wo_name, 
                value=stocks_data_columns_wo_name[0])
y_axis = Select(title="Y Axis", options=stocks_data_columns_wo_name, 
                value=stocks_data_columns_wo_name[1])

X_AXIS_TYPE = Select(title="X_AXIS_TYPE", options=['linear', 'log'], 
                value=['linear', 'log'][0])


market_cap_range_slider = RangeSlider(
    start=stocks_data['שווי שוק'].min(), 
    end=stocks_data['שווי שוק'].max(), 
    range=(stocks_data['שווי שוק'].min(), stocks_data['שווי שוק'].max()), 
    step=.1, 
    #~ call_callbacks = select_stocks,
    title="Market Capitalization")




x_axis_type_button = RadioButtonGroup(
        labels=['linear', 'log'], active=0)



stocks_data['color'] = np.where(stocks_data['% תשואה 3 חודשים אחרונים'] > 0, 'orange', 'grey')
stocks_data['alpha'] = np.where(stocks_data['% תשואה 3 חודשים אחרונים'] > 0, 0.9, 0.25)

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(
    data={**dict(x=[], y=[], color=[], 
          title=[], alpha=[]),
          **{var: [] for var in stocks_data_columns}
         }
)

tools = 'pan,wheel_zoom,xbox_select,reset'

hover = HoverTool(tooltips=[
    ('Name', '@stock_name'),
    ('Market Cap (thousands)', '@stock_market_cap'),
    ('Beta', '@stock_beta'),
])

def create_figure():
    global p
    p = figure(plot_height=600, plot_width=700, title='', 
               #~ x_axis_type=['linear', 'log'][x_axis_type_button.active], 
               x_axis_type=X_AXIS_TYPE.value,
               # linear, log
               toolbar_location='right', 
               tools=[hover, 
                      'pan', 'wheel_zoom', 'box_select', 
                      'box_zoom', 'reset'])

    p.circle(x='x', y='y',
             source=source, 
             size=7, color='color', selection_color="orange", 
             line_color=None, fill_alpha='alpha')
    
    return p


data_table_columns = [TableColumn(field=column_name, title=column_name)
                      for column_name in stocks_data_columns]

#~ data_table_columns = [TableColumn(field='דיבידנט למניה', title='דיבידנט למניה'), 
                      #~ TableColumn(field='הון עצמי למאזן', title='הון עצמי למאזן')]

data_table = DataTable(
    source=source, 
    columns=data_table_columns,
    width=1500, height=400)

def select_stocks():
    # get values from controls
    company_name_val = company_name.value.strip()
    min_market_cap, max_market_cap = market_cap_range_slider.range
    
    selected = stocks_data[
        stocks_data['שווי שוק'].between(
            min_market_cap, max_market_cap, inclusive=True)
#         (movies.Reviews >= reviews.value) &
#         (movies.BoxOffice >= (boxoffice.value * 1e6)) &
#         (movies.Year >= min_year.value) &
#         (movies.Year <= max_year.value) &
#         (movies.Oscars >= oscars.value)
    ]
    
#     if (genre_val != "All"):
#         selected = selected[selected.Genre.str.contains(genre_val)==True]
#     if (director_val != ""):
#         selected = selected[selected.Director.str.contains(director_val)==True]
    if (company_name_val != ""):
        selected = selected[selected.index.str.contains(company_name_val)==True]
    return selected


def update(p):
    df = select_stocks()
#     x_name = axis_map[x_axis.value]
#     y_name = axis_map[y_axis.value]
    x_name = x_axis.value
    y_name = y_axis.value

    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = y_axis.value
    p.title.text = "Plotting {} stocks".format(len(df))
    source.data = {**dict(
        x=df[x_name],
        y=df[y_name],
        color=df["color"],
#         title=df["Title"],
#         year=df["Year"],
#         revenue=df["revenue"],
        alpha=df["alpha"],
        stock_name=df.index,
        stock_market_cap=df['שווי שוק'],
        stock_beta=df['בטא']),
    **{var: df[var] for var in stocks_data_columns}
    }

# controls = [reviews, boxoffice, genre, min_year, max_year, oscars, director, company_name, x_axis, y_axis]
controls = [company_name, x_axis, x_axis_type_button,
            y_axis, X_AXIS_TYPE,
            market_cap_range_slider]

for control in controls:
    if hasattr(control, 'value'):
        control.on_change('value', lambda attr, old, new: update(p))
    # RangeSliders do not have a 'value' attr
    if hasattr(control, 'range'):
        control.on_change('range', lambda attr, old, new: update(p))
    if hasattr(control, 'active'):
        control.on_change('active', lambda attr, old, new: update(p))

sizing_mode = 'fixed'  # 'fixed', 'scale_width' also looks nice with this example

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
#     [desc],
    [inputs, create_figure()],
    [data_table]
], sizing_mode=sizing_mode)

update(p)  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Stocks by Yarden: Awesome Great Job Well Done!"

