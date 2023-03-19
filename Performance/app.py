#%% packages
from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
import pandas as pd
import jinja2 as jn
import numpy as np
from plotnine import ggplot, aes, geom_line, geom_smooth, coord_cartesian, labs, scale_color_discrete, theme_bw, coord_cartesian, theme, element_rect, element_line, element_text, annotate, geom_vline, scale_color_manual
import seaborn as sns
from pathlib import Path
#%% data prep
Performance_Data = pd.read_csv(Path(__file__).parent / 'Performance.csv')

Performance_Data['Date_Time'] = pd.to_datetime(Performance_Data['Date'], format="%d/%m/%Y")
Performance_Data.drop(axis=1, columns=['Date'], inplace=True)  # Date column not required anymore

#%% set up input values
Performance_Long = Performance_Data.melt(id_vars='Date_Time', value_name='Performance', var_name='Strategy').reset_index(drop=True)

date_range_start = np.min(Performance_Long['Date_Time'])
date_range_end = np.max(Performance_Long['Date_Time'])

#%%
# languages.info()
# languages.describe()

#%% values for dropdown field
Strategy_Names = Performance_Long['Strategy'].unique()
Strategy_Names_Dict = {l:l for l in Strategy_Names}

#%% app
app_ui = ui.page_fluid(
    ui.panel_title('Global Macro Performance Review'),
    ui.row(
        ui.column(4,
            ui.input_selectize(id="Strategy", label="Choose Strategies", choices=Strategy_Names_Dict, selected='Total', multiple=True),
            ui.input_date_range(id='date_range', label='Date Range', start=date_range_start, end=date_range_end,),
            ui.input_radio_buttons(id="rb", label="Style Correlation", choices={"a": "Correlation On", "b":"Correlation Off"}, selected="a")    
        ),
        ui.column(7,
            ui.output_plot("plotTimeseries")),
        ui.column(1,)
        ),
    ui.row(
        ui.column(4,),
        ui.column(7, ui.output_table("Stat_table", style="text-align:center;")),
        ui.column(1,)
    ),
    ui.row(
        ui.column(4),
        ui.column(7, ui.output_table("Corr_table", style="text-align:center;")),
        ui.column(1,)
    )   
) 

#%%
def server(input: Inputs, output: Outputs, session: Session):
    # Preparation of Chart
    @reactive.Calc
    def performance_filt():
        date_selected_start = str(input.date_range()[0])
        date_selected_end = str(input.date_range()[1])
        l = Performance_Long.loc[(Performance_Long['Strategy'].isin(list(input.Strategy()))) & (Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)].reset_index(drop=True)
        return l

    # Calculation for Stats Table
    @reactive.Calc
    def stat_table():
        date_selected_start = str(input.date_range()[0])
        date_selected_end = str(input.date_range()[1])
        
        # Filter for selection and choose column "Performance"
        data_Total = Performance_Long.loc[(Performance_Long['Strategy'] == "Total") & (Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)]["Performance"].reset_index(drop=True)
        data_Tactical = Performance_Long.loc[(Performance_Long['Strategy'] == "Tactical") & (Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)]["Performance"].reset_index(drop=True)
        data_Momentum = Performance_Long.loc[(Performance_Long['Strategy'] == "Momentum") & (Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)]["Performance"].reset_index(drop=True)
        data_Fundamental = Performance_Long.loc[(Performance_Long['Strategy'] == "Fundamental") & (Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)]["Performance"].reset_index(drop=True)
        
        # Calculate Performance over period
        k = len(data_Total)-1
        #m = int(date_selected_start)
        #print(m)
        perf_Total = (data_Total[k] / data_Total[0]) -1
        perf_Total_ann = (data_Total[k] / data_Total[0]) ** (250/k) -1
        perf_Total_f = "{:.2%}".format(perf_Total)
        perf_Total_ann_f = "{:.2%}".format(perf_Total_ann)
   
        perf_Tactical = (data_Tactical[k] / data_Tactical[0]) -1
        perf_Tactical_ann = (data_Tactical[k] / data_Tactical[0])  ** (250/k) -1
        perf_Tactical_f = "{:.2%}".format(perf_Tactical)
        perf_Tactical_ann_f = "{:.2%}".format(perf_Tactical_ann)
        
        perf_Momentum = (data_Momentum[k] / data_Momentum[0]) -1
        perf_Momentum_ann = (data_Momentum[k] / data_Momentum[0])  **(250/k) -1
        perf_Momentum_f = "{:.2%}".format(perf_Momentum)
        perf_Momentum_ann_f = "{:.2%}".format(perf_Momentum_ann)
        
        perf_Fundamental = (data_Fundamental[k] / data_Fundamental[0]) -1
        perf_Fundamental_ann = (data_Fundamental[k] / data_Fundamental[0])  ** (250/k) -1
        perf_Fundamental_f = "{:.2%}".format(perf_Fundamental)
        perf_Fundamental_ann_f = "{:.2%}".format(perf_Fundamental_ann)

        #Calculate Volatility over period
        returns_Total = data_Total.pct_change()
        stdev_Total = returns_Total.std() * np.sqrt(250)
        stdev_Total_f = "%.2f%%" % (stdev_Total*100)
        returns_Fundamental = data_Fundamental.pct_change()
        stdev_Fundamental = returns_Fundamental.std() * np.sqrt(250)
        stdev_Fundamental_f = "%.2f%%" % (stdev_Fundamental*100)
        returns_Momentum = data_Momentum.pct_change()
        stdev_Momentum = returns_Momentum.std() * np.sqrt(250)
        stdev_Momentum_f = "%.2f%%" % (stdev_Momentum*100)
        returns_Tactical = data_Tactical.pct_change()
        stdev_Tactical = returns_Tactical.std() * np.sqrt(250)
        stdev_Tactical_f = "%.2f%%" % (stdev_Tactical*100)

        #Calculate IR over period
        ir_Total = perf_Total_ann / stdev_Total
        ir_Total_f = "%.2f" % (ir_Total)
        ir_Fundamental = perf_Fundamental_ann / stdev_Tactical
        ir_Fundamental_f = "%.2f" % (ir_Fundamental)
        ir_Momentum = perf_Momentum_ann / stdev_Momentum
        ir_Momentum_f = "%.2f" % (ir_Momentum)
        ir_Tactical = perf_Tactical_ann / stdev_Tactical
        ir_Tactical_f = "%.2f" % (ir_Tactical)
                
        table = pd.DataFrame({'Strategy': ['Total', 'Fundamental', 'Momentum', "Tactical"], 'Performance': [perf_Total_f, perf_Fundamental_f, perf_Momentum_f, perf_Tactical_f], 'Performance (ann)': [perf_Total_ann_f, perf_Fundamental_ann_f, perf_Momentum_ann_f, perf_Tactical_ann_f], 'Volatility': [stdev_Total_f, stdev_Fundamental_f, stdev_Momentum_f, stdev_Tactical_f], "IR": [ir_Total_f,ir_Fundamental_f,ir_Momentum_f,ir_Tactical_f]})
        
        tab = table.loc[(table['Strategy'].isin(list(input.Strategy())))]
        return tab
    
    # Calculation for Stats Table
    @reactive.Calc
    def corr_table():
        #Calculate Correlations
        date_selected_start = str(input.date_range()[0])
        date_selected_end = str(input.date_range()[1])
        
        data_Tactical = Performance_Long.loc[(Performance_Long['Strategy'] == "Tactical") & (Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)]["Performance"].reset_index(drop=True)
        data_Momentum = Performance_Long.loc[(Performance_Long['Strategy'] == "Momentum") & (Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)]["Performance"].reset_index(drop=True)
        data_Fundamental = Performance_Long.loc[(Performance_Long['Strategy'] == "Fundamental") & (Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)]["Performance"].reset_index(drop=True)
        
        returns_Fundamental = data_Fundamental.pct_change()
        returns_Tactical = data_Tactical.pct_change()
        returns_Momentum = data_Momentum.pct_change()

        corr_Momentum_Tactical = "{:.2}".format(returns_Momentum.corr(returns_Tactical))
        corr_Momentum_Fundamental = "{:.2}".format(returns_Momentum.corr(returns_Fundamental))
        corr_Tactical_Fundamental = "{:.2}".format(returns_Tactical.corr(returns_Fundamental))

        corr_tab = pd.DataFrame({'Correlation': ['Fundamental', 'Momentum', "Tactical"], 'Fundamental': [1,corr_Momentum_Fundamental , corr_Tactical_Fundamental], 'Momentum': ["", 1, corr_Momentum_Tactical], 'Tactical': ["", "", 1]})

        return corr_tab


    # Output
    @output
    @render.plot
    def plotTimeseries():
        g = ggplot(performance_filt(), aes('Date_Time', 'Performance', color="Strategy")) + geom_line() + theme(plot_background=element_rect(fill='white'), panel_background=element_rect(fill='white'), rect=element_rect(color='black', size=1, fill='#fff'), axis_text_x=element_text(rotation=90, hjust=1), panel_grid_major_y=element_line(color="grey"), legend_position="right", legend_margin=(20)) + labs(x = 'Date', y='Performance Index', title='Global Macro Strategy Performance') + coord_cartesian(ylim=[98,103])
        return g
    
    @output
    @render.table
    def Stat_table():
        stats = stat_table()
        return stats
    
    @output
    @render.table
    def Corr_table():
        if input.rb() == "a":
            corr = corr_table()
        else:
            corr = pd.DataFrame()
        return corr
    
app = App(app_ui, server)

# %%