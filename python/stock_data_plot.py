import pandas as pd
import numpy as np

# import argparse

from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, LinearInterpolator
from bokeh.models.widgets import Select, TextInput  #, RadioButtonGroup
from bokeh.models.widgets import TableColumn, DataTable, RangeSlider
from bokeh.io import curdoc  # , output_notebook

from column_name_conversions import heb_to_eng_names, eng_to_heb_names
#~ useful guide at:
#~ http://bokeh.pydata.org/en/latest/docs/user_guide/interaction/widgets.html


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
stocks_data['color'] = np.where(stocks_data['% תשואה 3 חודשים אחרונים'] > 0, 'royalblue', 'grey')
stocks_data['alpha'] = np.where(stocks_data['% תשואה 3 חודשים אחרונים'] > 0, 0.6, 0.4)

# Create Input controls
company_name = TextInput(
    title="Company name contains (hit ENTER whe done)")
x_axis = Select(title="X Axis", options=stocks_data_columns_wo_name, 
                value=stocks_data_columns_wo_name[0])
y_axis = Select(title="Y Axis", options=stocks_data_columns_wo_name, 
                value=stocks_data_columns_wo_name[1])



range_slider_market_cap = RangeSlider(
    start=stocks_data['שווי שוק'].min(), 
    end=stocks_data['שווי שוק'].max(), 
    range=(stocks_data['שווי שוק'].min(),
           stocks_data['שווי שוק'].max()), 
    step=10.0, 
    title='Market Capitalization')


range_slider_net_profit_margin = RangeSlider(
    start=stocks_data['רווח נקי למכירות'].min(), 
    end=stocks_data['רווח נקי למכירות'].max(), 
    range=(stocks_data['רווח נקי למכירות'].min(),
           stocks_data['רווח נקי למכירות'].max()), 
    step=0.01, 
    title='Net profit margin')









#~ x_axis_type_button = RadioButtonGroup(
        #~ labels=['linear', 'log'], active=0)

# create size linear interpolator
size_mapper = LinearInterpolator(
    x=[np.log10(stocks_data['שווי שוק'].min()),
       np.log10(stocks_data['שווי שוק'].max())],
    y=[5, 30])

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(
    data={**dict(x=[], y=[], color=[], 
          title=[], alpha=[]),
          **{var: [] for var in stocks_data_columns}
         }
)



# adding data table
data_table_columns = [TableColumn(field=column_name, title=column_name)
                      for column_name in stocks_data_columns]

data_table = DataTable(
    source=source, 
    columns=data_table_columns,
    width=1500, height=400)




tools = 'pan,wheel_zoom,xbox_select,reset'

hover = HoverTool(tooltips=[
    ('Name', '@stock_name'),
    ('Market Cap (thousands)', '@stock_market_cap'),
    ('Beta', '@stock_beta'),
])


p = figure(plot_height=600, plot_width=700, title='', 
           #~ x_axis_type=['linear', 'log'][x_axis_type_button.active], 
           # linear, log
           toolbar_location='right', 
           tools=[hover, 
                  'pan', 'wheel_zoom', 'box_select', 
                  'box_zoom', 'reset'])

p.circle(x='x', y='y',
         source=source, 
         size={'field': 'stock_market_cap_log',
               'transform': size_mapper}, 
         color='color', selection_color="orange", 
         line_color=None, fill_alpha='alpha')


def select_stocks():
    # get values from controls
    company_name_val = company_name.value.strip()
    min_market_cap, max_market_cap = range_slider_market_cap.range
    min_net_profit_margin, max_net_profit_margin = \
        range_slider_net_profit_margin.range
    
    selected = stocks_data[
        (stocks_data['שווי שוק'].between(
            min_market_cap, max_market_cap, inclusive=True)) &
        (stocks_data['רווח נקי למכירות'].between(
            min_net_profit_margin, max_net_profit_margin, inclusive=True))
#         (movies.Reviews >= reviews.value) &
#         (movies.Year <= max_year.value) &
#         (movies.Oscars >= oscars.value)
    ]
    
    if (company_name_val != ""):
        selected = selected[selected.index.str.contains(company_name_val)==True]
    return selected


def update():
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
        alpha=df["alpha"],
        stock_name=df.index,
        stock_market_cap=df['שווי שוק'],
        stock_market_cap_log=np.log10(df['שווי שוק']),
        stock_beta=df['בטא']),
    **{var: df[var] for var in stocks_data_columns}
    }

# controls = [reviews, boxoffice, genre, min_year, max_year, oscars, director, company_name, x_axis, y_axis]
controls = [company_name, 
            x_axis, y_axis, 
            range_slider_market_cap, 
            range_slider_net_profit_margin]

for control in controls:
    if hasattr(control, 'value'):
        control.on_change('value', lambda attr, old, new: update())
    # RangeSliders do not have a 'value' attr
    if hasattr(control, 'range'):
        control.on_change('range', lambda attr, old, new: update())
    #~ if hasattr(control, 'active'):
        #~ control.on_change('active', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'fixed', 'scale_width', 'stretch_both'

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
#     [desc],
    [inputs, p],
    [data_table]
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Stocks by Yarden: Awesome Great Job Well Done!"

