# Importing Libraries
import dash
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go

import pandas as pd
from bs4 import BeautifulSoup
import requests 
import lxml


external_stylesheets = ['assets/style.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets, update_title='Loading...', title = 'CompEcom!')

fig = go.Figure(data = go.Table())

app.layout = html.Div(
    [
        html.Div(style = {'color' : '#ffffff', 'backgroundColor': '#98151b', 'padding-top': '20px', 'padding-bottom': '20px'},
        children = [
            html.Img(src=app.get_asset_url('CompEcom1.png')), 
            html.H1(id='header', children = 'CompEcom!'),
            html.H2(id='sub-header', children ='Compare prices & get surprises...')]),
        
        html.Div(
        children = [
            dcc.Input(id ='my-input', type ='text', placeholder = 'Enter the product name', value = ''),
            html.Button('Submit', id= 'button', n_clicks = 0),

            dcc.Dropdown(
                id = 'my-dropdown',
                options = [
                    {'label': 'All Websites', 'value': 'AFS'},
                    {'label': 'Amazon vs Flipkart', 'value': 'AF'},
                    {'label': 'Flipkart vs Snapdeal', 'value': 'FS'},
                    {'label': 'Amazon vs Snapdeal', 'value': 'AS'},  
                    {'label': 'Amazon', 'value': 'Amazon'},
                    {'label': 'Flipkart', 'value': 'Flipkart'},
                    {'label': 'Snapdeal', 'value': 'Snapdeal'}

                ],
                value = 'AF',
                searchable = False,
                clearable=False,
                multi = False,
                placeholder = 'Select which website prices you want to compare',               
            )

        ]),
    
        dcc.Graph(id='graph-output', figure = fig)
    ]
)

@app.callback(
    Output('graph-output', 'figure'),
    [Input('button', 'n_clicks'), Input('my-dropdown','value')], 
    [State('my-input', 'value')]
)

def update_graph(n_clicks, val_chosen, data):
    if len(data) != 0:
        user_input = data 

        headers = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36', 
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
            'Accept-Language' : 'en-US,en;q=0.5',
            'Accept-Encoding' : 'gzip', 
            'DNT' : '1', # Do Not Track Request Header 
            'Connection' : 'close'
        }

        # ---------------------------------------- A - AMAZON / F - FLIPKART / S - SNAPDEAL ------------------------------------------- #

        A_URL = 'https://www.amazon.in/s?k='+user_input+'&ref=nb_sb_noss_2' 

        F_URL = 'https://www.flipkart.com/search?q='+user_input

        S_URL = 'https://www.snapdeal.com/search?keyword='+user_input

        page_a = requests.get(A_URL, headers = headers ) # Fetching above Url's using request library.
        page_f = requests.get(F_URL, headers = headers )
        page_s = requests.get(S_URL, headers = headers )

        soup_a = BeautifulSoup(page_a.content, 'lxml') # "Parsing" the content of the page using lxml over html for better speed.
        soup_f = BeautifulSoup(page_f.content, 'lxml')
        soup_s = BeautifulSoup(page_s.content, 'lxml')

        # AMAZON-INDIA ------------------------------------------------------

        a_inner_title = soup_a.select('span.a-size-base-plus.a-color-base.a-text-normal') #Grocery & other products(Eg:maggi)
        a_inner_title1 = soup_a.select('span.a-size-medium.a-color-base.a-text-normal') #Electronics(Eg:Iphone)
        a_title = []

        if a_inner_title1 == []:
            for a_t in a_inner_title:
                a_title.append(a_t.text)
        else:
            for a_t1 in a_inner_title1:
                a_title.append(a_t1.text)


        a_inner_price = soup_a.select('span.a-price-whole')

        a_price = []
        for a_p in a_inner_price:
            a_price.append('₹'+a_p.text)


        ## FLIPKART ---------------------------------------------------------

        f_inner_link = soup_f.select('div._1UoZlX a._31qSD5') #Electronics
        f_inner_link1 = soup_f.select('div._3liAhj a.Zhf2z-') #Groceries
        f_inner_link2 = soup_f.select('div.IIdQZO._1SSAGr a._3dqZjq') #Other items - eg. watches

        f_link = []

        if f_inner_link1 == [] and f_inner_link2 == []:
            for f_l in f_inner_link:
                f_l = f_l.get('href')
                f_link.append('http://www.flipkart.com'+f_l)

        elif f_inner_link == [] and f_inner_link2 == []:
            for f_l1 in f_inner_link1:
                f_l1 = f_l1.get('href')
                f_link.append('http://www.flipkart.com'+f_l1)
                
        else:
            for f_l2 in f_inner_link2:
                f_l2 = f_l2.get('href')
                f_link.append('http://www.flipkart.com'+f_l2)

        f_final_link = f_link[:16]  
        f_final_title = []

        for f_URL2 in f_final_link:
            f_page2 = requests.get(f_URL2, headers = headers)
            f_soup2 = BeautifulSoup(f_page2.content, 'lxml')
            f_inner_title = f_soup2.select('span._35KyD6') #selecting title

            f_title=[]
            for f_t in f_inner_title:
                f_title.append(f_t.text)
            for f_tt in f_title:
                f_tt = f_tt.strip()
                f_final_title.append(f_tt)

            

        f_inner_price = soup_f.select('div._1HmYoV._35HD7C div._1vC4OE')

        f_price = []
        for p in f_inner_price:
            f_price.append(p.text)


        ## SNAPDEAL -------------------------------------------------------------

        s_inner_title = soup_s.select('p.product-title ') # Same class is used for every product

        s_title = []
        for s_t in s_inner_title:
            s_title.append(s_t.text)

        s_inner_price = soup_s.select('div.lfloat.marR10 span.lfloat.product-price') 

        s_price = []
        for s_p in s_inner_price:
            s_price.append(s_p.text)


        ## Creating Data-Frames --------------------------------------------------

        a_table1 = pd.DataFrame(a_title, columns = ['Amazon'])

        a_table2 = pd.DataFrame(a_price, columns = ['A_Price'])

        f_table1 = pd.DataFrame(f_final_title, columns = ['Flipkart'])

        f_table2 = pd.DataFrame(f_price, columns = ['F_Price'])

        s_table1 = pd.DataFrame(s_title, columns = ['Snapdeal'])

        s_table2 = pd.DataFrame(s_price, columns = ['S_Price'])

        frame = [a_table1, a_table2, f_table1, f_table2, s_table1, s_table2]

        ## Concatenating Data-Frames --------------------------------------------

        result = pd.concat(frame, axis=1, sort=True)
        final_result = result[:16]
        
        df = final_result

        df["S_Price"] = df["S_Price"].str.replace('Rs.  ','₹')

        if val_chosen == 'Amazon':
            fig = go.Figure(data = [go.Table(
                columnorder = [1, 2],
                columnwidth= [200, 100],
                
                header = dict(values = list(df.columns)[:2], fill_color='#98151b',align='center', font=dict(color='white', size=15)),
                cells  = dict(values = [df.Amazon, df.A_Price], fill_color='#e6e6e6', align = 'left', font=dict(color='black', size=12)))])
            fig.update_layout(height = 550)
            return fig
        elif val_chosen == 'Flipkart':
            fig = go.Figure(data = [go.Table(
                columnorder = [1, 2],
                columnwidth= [200, 100],

                header = dict(values = list(df.columns)[2:4], fill_color='#98151b',align='center', font=dict(color='white', size=15)),
                cells  = dict(values = [df.Flipkart, df.F_Price], fill_color='#e6e6e6', align = 'left', font=dict(color='black', size=12)))])
            fig.update_layout(height = 550)
            return fig
        elif val_chosen == 'Snapdeal':
            fig = go.Figure(data = [go.Table(
                columnorder = [1, 2],
                columnwidth= [200, 100],

                header = dict(values = list(df.columns)[4:], fill_color='#98151b',align='center', font=dict(color='white', size=15)),
                cells  = dict(values = [df.Snapdeal, df.S_Price], fill_color='#e6e6e6', align = 'left', font=dict(color='black', size=12)))])
            fig.update_layout(height = 550)
            return fig
        elif val_chosen == 'AF':
            fig = go.Figure(data = [go.Table(
                columnorder = [1, 2, 3, 4],
                columnwidth= [200, 100, 200, 100],

                header = dict(values = list(df.columns)[:4], fill_color='#98151b',align='center', font=dict(color='white', size=15)),
                cells  = dict(values = [df.Amazon, df.A_Price, df.Flipkart, df.F_Price], fill_color='#e6e6e6', align = 'left', font=dict(color='black', size=12)))])
            fig.update_layout(height = 550)
            return fig
        elif val_chosen == 'FS':
            fig = go.Figure(data = [go.Table(
                columnorder = [1, 2, 3, 4],
                columnwidth= [200, 100, 200, 100],

                header = dict(values = list(df.columns)[2:6], fill_color='#98151b',align='center', font=dict(color='white', size=15)),
                cells  = dict(values = [df.Flipkart, df.F_Price, df.Snapdeal, df.S_Price], fill_color='#e6e6e6', align = 'left', font=dict(color='black', size=12)))])
            fig.update_layout(height = 550)
            return fig
        elif val_chosen == 'AS':
            fig = go.Figure(data = [go.Table(
                columnorder = [1, 2, 3, 4],
                columnwidth= [200, 100, 200, 100],

                header = dict(values = (df.columns)[[0,1,4,5]], fill_color='#98151b',align='center', font=dict(color='white', size=15)),
                cells  = dict(values = [df.Amazon, df.A_Price, df.Snapdeal, df.S_Price], fill_color='#e6e6e6', align = 'left', font=dict(color='black', size=12)))])
            fig.update_layout(height = 550)
            return fig
        elif val_chosen == 'AFS':
            fig = go.Figure(data = [go.Table(
                columnorder = [1, 2, 3, 4, 5, 6],
                columnwidth= [200, 100, 200, 100, 200, 100],

                header = dict(values = list(df.columns), fill_color='#98151b',align='center', font=dict(color='white', size=15)),
                cells  = dict(values = [df.Amazon, df.A_Price, df.Flipkart, df.F_Price, df.Snapdeal, df.S_Price], fill_color='#e6e6e6', align = 'left', font=dict(color='black', size=12)))])
            fig.update_layout(height = 550)
            return fig
        elif len(val_chosen) == 0:
            raise dash.exceptions.PreventUpdate
        
    else:
        raise dash.exceptions.PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)