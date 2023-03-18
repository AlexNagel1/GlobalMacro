#%% Import 
from shiny import Inputs, Outputs, Session, App, render, ui, reactive
import pandas as pd
import numpy as np
from pathlib import Path
from plotnine import ggplot, aes, geom_line, theme, element_text, labs


#%% Data

Performance_Data = pd.read_csv(Path(__file__).parent /'Performance.csv')
Performance_Data["DateTime"] = pd.to_datetime(Performance_Data["Date"])
Performance_Data.drop(axis=1, columns=["Date"], inplace=True)
Performance_Long = Performance_Data.melt(id_vars='DateTime', value_name='Performance', var_name='Strategy').reset_index(drop=True)

Date_Range_Start = np.min(Performance_Long["DateTime"])
Date_Range_End = np.max(Performance_Long["DateTime"])

Strategy_Names = Performance_Long["Strategy"].unique()
#Strategy_Names_List = list(Strategy_Names)
Strategy_Names_Dict = {s:s for s in Strategy_Names}

#%% Inputs for Plot
app_ui = ui.page_fluid(
    ui.panel_title("Global Macro Track Record"),
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.input_selectize(id="Strategy", label="Strategies", choices=Strategy_Names_Dict, selected=("Total"), multiple=True ),
            ui.input_date_range(id="Date_Range", label="Date Range", start=Date_Range_Start, end=Date_Range_End,),
        ),
        ui.panel_main(
            ui.output_text_verbatim("txt"),
            #ui.output_plot("Plot_Performance"),
        ),
    ),
)

def server(input, output, session):
    #@input
    #def Chart_Inputs():
    #    Chart_Input = Performance_Data
    #    return Chart_Input
    
    @output
    @render.plot
    def Performance_Plot():
        Date_Start = str(input.Date_Range()[0])
        Date_End = str(input.Date_Range()[1])
        Performance_Filt = Performance_Long.loc[(Performance_Long['Strategy'].isin(list(input.Strategy()))) & (Performance_Long['DateTime']>= Date_Start) & (Performance_Long['DateTime']<= Date_End)].reset_index(drop=True)
        Perf_Chart = ggplot(data=Performance_Filt)
        return Perf_Chart

#def server(input: Inputs, output: Outputs, session: Session):
    #%% plot
    #@input
    #@reactive.Calc
    
    #def Performance_Filter():
    #    Date_Start = str(input.Date_Range()[0])
    #    Date_End = str(input.Date_Range()[1])
    #    Performance_Filt = Performance_Long.loc[(Performance_Long['Strategy'].isin(list(input.Strategy()))) & (Performance_Long['DateTime']>= Date_Start) & (Performance_Long['DateTime']<= Date_End)].reset_index(drop=True)
    #    return Performance_Filt

    #@output
    #@render.text
    #def txt():
        return "Test"
    #def plotPerformance():
    #    g = ggplot(Performance_Filter())
    #    #g = ggplot(Performance_Filter()) + aes(x = 'DateTime', y='Performance Index', color='Strategies') + geom_line() + theme(axis_text_x=element_text(rotation=90, hjust=1)) + labs(x ='Date', y='Performance Index', title='Global Macro Performance Track Record')
    #    return g

app = App(app_ui, server)

# %%
