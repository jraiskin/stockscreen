import pandas as pd
import numpy as np

#~ from os.path import dirname, join

# import argparse

#~ from bokeh import events
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, HoverTool, LinearInterpolator  # , CustomJS
from bokeh.models.widgets import Select, TextInput  # , Button, RadioButtonGroup, Toggle
from bokeh.models.widgets import TableColumn, DataTable, RangeSlider  #, PreText
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

## range sliders ##
## multiples ##
range_slider_pe_mult = RangeSlider(
    start=stocks_data['מכפיל רווח'].min(), 
    end=stocks_data['מכפיל רווח'].max(), 
    range=(stocks_data['מכפיל רווח'].min(),
           stocks_data['מכפיל רווח'].max()), 
    step=0.1, 
    title='Price/ Earnings (PE multiple)')

range_slider_price_bv_mult = RangeSlider(
    start=stocks_data['מכפיל הון'].min(), 
    end=stocks_data['מכפיל הון'].max(), 
    range=(stocks_data['מכפיל הון'].min(),
           stocks_data['מכפיל הון'].max()), 
    step=0.1, 
    title='Price / BV (Capital multiple)')

range_slider_price_cf_mult = RangeSlider(
    start=stocks_data['מכפיל תזרים'].min(), 
    end=stocks_data['מכפיל תזרים'].max(), 
    range=(stocks_data['מכפיל תזרים'].min(),
           stocks_data['מכפיל תזרים'].max()), 
    step=0.1, 
    title='Price / Cashflow')

range_slider_price_revenues_mult = RangeSlider(
    start=stocks_data['מכפיל מכירות'].min(), 
    end=stocks_data['מכפיל מכירות'].max(), 
    range=(stocks_data['מכפיל מכירות'].min(),
           stocks_data['מכפיל מכירות'].max()), 
    step=0.1, 
    title='Price / Revenues')

## financial stability, leverage and liquidity ratios ##
range_slider_market_cap = RangeSlider(
    start=stocks_data['שווי שוק'].min(), 
    end=stocks_data['שווי שוק'].max(), 
    range=(stocks_data['שווי שוק'].min(),
           stocks_data['שווי שוק'].max()), 
    step=10.0, 
    title='Market Capitalization')

range_slider_capital_assets_ratio = RangeSlider(
    start=stocks_data['הון עצמי למאזן'].min(), 
    end=stocks_data['הון עצמי למאזן'].max(), 
    range=(stocks_data['הון עצמי למאזן'].min(),
           stocks_data['הון עצמי למאזן'].max()), 
    step=0.05, 
    title='Capital BV / assets')

range_slider_current_ratio = RangeSlider(
    start=stocks_data['יחס שוטף'].min(), 
    end=stocks_data['יחס שוטף'].max(), 
    range=(stocks_data['יחס שוטף'].min(),
           stocks_data['יחס שוטף'].max()), 
    step=0.5, 
    title='Current Ratio (Current Assets / Current Liabilities)')

## returns and profitability ##
range_slider_net_profit_margin = RangeSlider(
    start=stocks_data['רווח נקי למכירות'].min(), 
    end=stocks_data['רווח נקי למכירות'].max(), 
    range=(stocks_data['רווח נקי למכירות'].min(),
           stocks_data['רווח נקי למכירות'].max()), 
    step=0.01, 
    title='Net profit margin')

range_slider_returns_this_month = RangeSlider(
    start=stocks_data['% תשואה מתחילת החודש'].min(), 
    end=stocks_data['% תשואה מתחילת החודש'].max(), 
    range=(stocks_data['% תשואה מתחילת החודש'].min(),
           stocks_data['% תשואה מתחילת החודש'].max()), 
    step=0.01, 
    title='Returns this month')


#~ button_save = Button(label="Download Table as CSV", 
                     #~ button_type="success")

#~ x_axis_type_button = RadioButtonGroup(
        #~ labels=['linear', 'log'], active=0)

#~ button_update = Button(label="Update", button_type="success")

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
    #~ fit_columns=True,
    width=1800, height=400,
    #~ sizing_mode='scale_width',
    )

hover = HoverTool(tooltips=[
    ('Name', '@stock_name'),
    ('Market Cap (thousands)', '@stock_market_cap'),
    ('Beta', '@stock_beta'),
])

p = figure(plot_height=600, plot_width=700, title='', 
       #~ x_axis_type=['linear', 'log'][x_axis_type_button.active], 
       x_axis_type='linear', 
       #~ toolbar_location='right', 
       toolbar_location='above', 
       tools=[hover, 
              'pan', 'wheel_zoom', 'box_select', 
              'box_zoom', 'reset'],
       active_scroll='wheel_zoom',
       )
#~ p.toolbar.active_scroll = wheel_zoom
p.circle(x='x', y='y',
         source=source, 
         size={'field': 'stock_market_cap_log',
               'transform': size_mapper}, 
         color='color', selection_color='orange', 
         line_color=None, fill_alpha='alpha')
    

def select_stocks():
    # get values from controls
    company_name_val = company_name.value.strip()
    min_net_profit_margin, max_net_profit_margin = \
        range_slider_net_profit_margin.range
    min_pe_mult, max_pe_mult = range_slider_pe_mult.range
    min_price_bv_mult, max_price_bv_mult = \
        range_slider_price_bv_mult.range
    min_price_cf_mult, max_price_cf_mult = \
        range_slider_price_cf_mult.range
    min_price_revenues_mult, max_price_revenues_mult = \
        range_slider_price_revenues_mult.range
    min_market_cap, max_market_cap = range_slider_market_cap.range
    min_capital_assets_ratio, max_capital_assets_ratio = \
        range_slider_capital_assets_ratio.range
    min_current_ratio, max_current_ratio = \
        range_slider_current_ratio.range
    min_returns_this_month, max_returns_this_month = \
        range_slider_returns_this_month.range
    
    selected = stocks_data[
        (stocks_data['שווי שוק'].between(
            min_market_cap, max_market_cap, inclusive=True)) &
        (stocks_data['רווח נקי למכירות'].between(
            min_net_profit_margin, max_net_profit_margin, inclusive=True)) & 
        (stocks_data['מכפיל רווח'].between(
            min_pe_mult, max_pe_mult, inclusive=True)) & 
        (stocks_data['מכפיל הון'].between(
            min_price_bv_mult, max_price_bv_mult, inclusive=True)) & 
        (stocks_data['מכפיל תזרים'].between(
            min_price_cf_mult, max_price_cf_mult, inclusive=True)) & 
        (stocks_data['מכפיל מכירות'].between(
            min_price_revenues_mult, max_price_revenues_mult, inclusive=True)) & 
        (stocks_data['הון עצמי למאזן'].between(
            min_capital_assets_ratio, max_capital_assets_ratio, inclusive=True)) & 
        (stocks_data['יחס שוטף'].between(
            min_current_ratio, max_current_ratio, inclusive=True)) & 
        (stocks_data['% תשואה מתחילת החודש'].between(
            min_returns_this_month, max_returns_this_month, inclusive=True))
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

controls = [company_name, 
            y_axis, 
            x_axis, 
            range_slider_pe_mult,
            range_slider_price_bv_mult,
            range_slider_price_cf_mult,
            range_slider_price_revenues_mult,
            range_slider_market_cap,
            range_slider_capital_assets_ratio,
            range_slider_current_ratio,
            range_slider_net_profit_margin,
            range_slider_returns_this_month
            ]


#~ def toggleCallback(attr):
    #~ # Get the layout object added to the documents root
    #~ l = curdoc().get_model_by_name('mainLayout')
    #~ listOfSubLayouts = l.children

    #~ # Either add or remove the second graph
    #~ if  toggle.active == False:
        #~ plotToRemove = curdoc().get_model_by_name('plot2')
        #~ listOfSubLayouts.remove(plotToRemove)

    #~ if toggle.active == True:
        #~ if not curdoc().get_model_by_name('plot2'):
            #~ p2 = figure(name='plot2')
            #~ plotToAdd = p2
            #~ p2.line(x,y2)
            #~ # print('Remade plot 2')
        #~ else:
            #~ plotToAdd = curdoc().get_model_by_name('plot2')
        #~ listOfSubLayouts.append(plotToAdd)


for control in controls:
    if hasattr(control, 'value'):
        control.on_change('value', lambda attr, old, new: update())
    # RangeSliders do not have a 'value' attr
    if hasattr(control, 'range'):
        control.on_change('range', lambda attr, old, new: update())
# action on button click
#~ button_update.on_click(lambda: print(str(x_axis_type_button.active)))
#~ x_axis_type_button.on_change(lambda: print('CLICK!'))

#~ button_save.callback = CustomJS(
    #~ args=dict(source=source),
    #~ code="""
    #~ var data = source.data;
    #~ var filetext = 'שם מניה,שווי שוק\n';
    #~ for (i=0, i < data['שם מניה'].length, i++) {
        #~ var currRow = [data['שם מניה'][i].toString(),
                       #~ // data['שווי שוק'][i].toString(),
                       #~ data['שווי שוק'][i].toString().concat('\n')];

        #~ var joined = currRow.join();
        #~ filetext = filetext.concat(joined);
    #~ }

    #~ var filename = 'data_result.csv';
    #~ var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });

    #~ //addresses IE
    #~ if (navigator.msSaveBlob) {
        #~ navigator.msSaveBlob(blob, filename);
    #~ }

    #~ else {
        #~ var link = document.createElement("a");
        #~ link = document.createElement('a')
        #~ link.href = URL.createObjectURL(blob);
        #~ link.download = filename
        #~ link.target = "_blank";
        #~ link.style.visibility = 'hidden';
        #~ link.dispatchEvent(new MouseEvent('click'))
    #~ }
#~ """)

sizing_mode = 'stretch_both'  # 'fixed', 'scale_width', 'stretch_both'

inputs = widgetbox(*controls, 
                   #~ sizing_mode=sizing_mode
                   )


main_layout = layout(
    [[inputs, p],
     [data_table]],
    sizing_mode=sizing_mode,
    #~ sizing_mode='stretch_both',
    responsive=True,
    )

update()  # initial load of the data

curdoc().add_root(main_layout)
curdoc().title = "Stocks by Yarden: Awesome Great Job Well Done!"

