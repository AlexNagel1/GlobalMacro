#%% packages
from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
import pandas as pd
import numpy as np
from plotnine import ggplot, aes, geom_line, theme, theme_linedraw, element_text, labs
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
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_selectize(id="Strategy", label="Choose Strategies", choices=Strategy_Names_Dict, selected='Total', multiple=True),
            ui.input_date_range(id='date_range', label='Date Range', start=date_range_start, end=date_range_end, ),
            
        ),
        ui.panel_main(
            ui.output_plot("plotTimeseries"),
            
        ),
        
), 

)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def performance_filt():
        date_selected_start = str(input.date_range()[0])
        date_selected_end = str(input.date_range()[1])
        l = Performance_Long.loc[(Performance_Long['Strategy'].isin(list(input.Strategy()))) & (Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)].reset_index(drop=True)
        x = Performance_Long.loc[(Performance_Long['Date_Time']>= date_selected_start) & (Performance_Long['Date_Time']<= date_selected_end)].reset_index(drop=True)
        y =  Performance_Long.loc[(Performance_Long['Strategy'].isin(list(input.Strategy())))].reset_index(drop=True)
        return l


    @output
    @render.plot
    def plotTimeseries():
        g = ggplot(performance_filt(), aes('Date_Time', 'Performance', color='Strategy')) + geom_line() + theme(axis_text_x=element_text(rotation=90, hjust=1)) + labs(x = 'Date', y='Performance Index', title='Global Macro Strategy Performance')
        return g

app = App(app_ui, server)

# %%