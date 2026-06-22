import pandas as pd
import streamlit as st
import plotly_express as px
import matplotlib
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_option_menu import option_menu
import warnings
import requests
import io
import sys 
sys.modules['warnings'] = warnings
st.set_page_config(
    page_title="Dashboard",
    page_icon=":bar_chart:",
    layout="wide"
)
#option menu code
selected = option_menu(
    menu_title=None,
    options=["Home", "Customers", "Marketing", "Graphs"],
    icons=["house", "people", "megaphone", "bar-chart"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#1a1c29"},
        "icon": {"color": "#00d9ff", "font-size": "18px"},
        "nav-link": {
            "font-size": "14px",
            "text-align": "center",
            "margin": "0px",
            "color": "white",
            "--hover-color": "#2a2d3e",
        },
        "nav-link-selected": {"background-color": "#2a2d3e"},
    },
)

    

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet"/>
""", unsafe_allow_html=True)
        
def download_csv(pub_url):
    response = requests.get(pub_url)
    return pd.read_csv(io.StringIO(response.content.decode("utf-8")))
@st.cache_data
def excel_store():
    orders_dt = download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQ6RYGTdLCVG45nqXIeXW0zfH0T3f1OivuPbDa2VhiommrcY2ePm5eWydX-RTmF4ljukwOdmSFl-MLU/pub?output=csv")
    dt1= download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRuLO8Q7E5zWP7z0NUekrDFBi1ulSlDqmGwTmbYc01dIsdDWRkw7Cwju9_stOAzDLNVqSNZtS8aoLet/pub?gid=2120930077&single=true&output=csv")
    dt2= download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSXfYlGKn67nOgmfCG4_8YCQjFuWEEJZyyDRDCJWt1ImXLXKBYnEnVTotK0pvzn0p9cGcy1jLfiNooA/pub?gid=1070054059&single=true&output=csv")
    dt3= download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vSE8cE8cBYFRGLNeZUPTlrHMMbDKgS0R74nggBoCvXA5534Sbp9Q2ByWx1Rgh-fF_FbwT_csICYnOPI/pub?gid=691192464&single=true&output=csv")
    dt4= download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRbH86QK79o2zl9csB3_aH0L1db4lWc7OeikHs0AeBsstUGNlOw8zP4npAaObKRv9e7548zKk8f91Qd/pub?gid=1570935170&single=true&output=csv")
    dt_e= download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vRYELTw4obFZKW7M7hMK7P3WySKBEjam5kb8PUYtmNsNcqx2-NiEGYN4EJUI3PeOoM2WUzmUxRBCdO4/pub?gid=1076665978&single=true&output=csv")
    
    order_items_dt=pd.concat([dt1, dt2, dt3, dt4], ignore_index= True)
  

    products_dt = download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQqRDfmfmUQGG0irIAn_ZkhC_iKiRCsMzLVl_s_2Wa0R7ULD6D3TGmKksyYlb1sTbHnYkAn5Pk-6DMg/pub?output=csv")
    dt= pd.merge(
        orders_dt,
        order_items_dt,
        on= "order_id",
        how= "left")
    
    df= pd.merge(
            products_dt,
            dt,
            on ="product_id",
            how= "left"
        )
    df= df[['product_id', 'product_name',
                'category', 'subcategory', 'brand',
        'cost_price', 'selling_price', 
        'profit_margin_pct', 'order_id', 'order_date', 
        'order_status', 'sales_channel', 'region', 
        'quantity', 'net_sales', 'profit']]




    return df

@st.cache_data
def store_2(df):
    df= excel_store()
    def format_number(num):
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)
    
    df["order_status"] = df["order_status"].str.strip().str.lower()
    total_sales= (df[df["order_status"]=="delivered"]["net_sales"]).sum()
    total_profit= (df[df["order_status"]=="delivered"]["profit"]).sum()
    gross_profit_margin= round(total_profit*100/total_sales) if total_sales else 0
    delivered_orders = len(df[df["order_status"] == "delivered"]) 
    profit_per_category=(
         df.groupby(by= df["category"])[["net_sales"]].sum().reset_index()
    )
    profit_per_category = profit_per_category[
        profit_per_category["net_sales"] / profit_per_category["net_sales"].sum() > 0.01
    ]
    profit_per_category["mark"]=  profit_per_category["net_sales"].apply(format_number) 
    #Sales per year
    df["order_date"]= pd.to_datetime(df["order_date"])
    df["year"]= df["order_date"].dt.year
    
    max_year= df["year"].max()
    min_year= df["year"].min()
    sales_per_year=(
        df.groupby(by=df["year"])[["net_sales"]]
        .sum()
        .reset_index()
    )
    min_sales= sales_per_year["net_sales"].min()
    max_sales= sales_per_year["net_sales"].max()
    sales_per_region=(
        df.groupby(by= df["region"])[["net_sales"]]
        .sum()
        .reset_index()
    )
    sales_per_region["mark"]= sales_per_region["net_sales"].apply(format_number)
    #product count
    unique_products= df["product_id"].nunique()
    dt_pivot= df.groupby(by= ["region", "year"])[["order_id"]].count().unstack()
    dt_pivot.columns.name= None
    dt_pivot.columns= dt_pivot.columns.droplevel(0).astype(int)
    dt_pivot_norm= dt_pivot.div(dt_pivot.max(axis= 1), axis= 0)
    ##RETURNED, DELIVERRED GOODS COUNT
   
    del_counts= df.groupby(by= ["order_status"])[["order_id"]].count().reset_index()
    df_comb = df.groupby(by=["year"]).agg(
    completed=("order_status", lambda x: (x == "delivered").sum()),
    returned=("order_status", lambda x: (x == "returned").sum())  
).reset_index()
    
    return (
        total_sales,
        total_profit,
        gross_profit_margin,
        delivered_orders,
        profit_per_category,
        sales_per_region,
        sales_per_year,
        unique_products,
        max_year,
        min_year,
        min_sales,
        max_sales,
        dt_pivot_norm,
        del_counts,
        df_comb
    )
    #st.title(":bar_chart: Sales Dashboard")

    # Color and font
@st.cache_data
def show_home():
    df= excel_store()
    (
        total_sales,
        total_profit,
        gross_profit_margin,
        delivered_orders,
        profit_per_category,
        sales_per_region,
        sales_per_year,
        unique_products,
        max_year,
        min_year,
        max_sales,
        min_sales,
        dt_pivot_norm,
        del_counts,
        df_comb
    ) = store_2(df)
    def format_number(num):
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)
    col1, col2 = st.columns([1, 10], vertical_alignment= "center")
    with col1:
            st.image("data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20xmlns%3Axlink%3D%22http%3A%2F%2Fwww.w3.org%2F1999%2Fxlink%22%20width%3D%22603%22%20height%3D%22182%22%20style%3D%22fill%3A%23221f1f%22%3E%3Cpath%20d%3D%22M374.006%20142.184c-35%2025.797-85.729%2039.561-129.406%2039.561-61.242%200-116.376-22.651-158.087-60.325-3.278-2.962-.341-7%203.591-4.693%2045.015%2026.191%20100.673%2041.947%20158.166%2041.947%2038.775%200%2081.43-8.022%20120.65-24.67%205.925-2.516%2010.88%203.88%205.086%208.18%22%20style%3D%22fill%3A%23f90%22%2F%3E%3Cpath%20d%3D%22M388.557%20125.536c-4.457-5.715-29.573-2.7-40.846-1.363-3.434.42-3.959-2.57-.865-4.719%2020.003-14.078%2052.827-10.015%2056.654-5.296%203.828%204.745-.996%2037.648-19.793%2053.352-2.884%202.411-5.637%201.127-4.352-2.072%204.22-10.539%2013.685-34.16%209.202-39.902%22%20style%3D%22fill%3A%23f90%22%2F%3E%3Cpath%20d%3D%22M348.497%2020.066V6.381c0-2.071%201.573-3.46%203.461-3.46h61.269c1.966%200%203.54%201.415%203.54%203.46V18.1c-.027%201.966-1.679%204.535-4.615%208.599l-31.749%2045.329c11.798-.289%2024.25%201.468%2034.947%207.498%202.412%201.363%203.068%203.356%203.251%205.322V99.45c0%201.992-2.202%204.325-4.509%203.12-18.85-9.884-43.887-10.96-64.73.104-2.123%201.154-4.351-1.153-4.351-3.146V85.661c0-2.229.026-6.03%202.254-9.412L384.047%2023.5h-32.01c-1.967%200-3.54-1.39-3.54-3.434M124.999%20105.454h-18.64c-1.783-.13-3.199-1.468-3.33-3.172V6.617c0-1.914%201.6-3.435%203.592-3.435h17.382c1.809.079%203.25%201.468%203.382%203.199v12.505h.34c4.536-12.086%2013.056-17.722%2024.54-17.722%2011.666%200%2018.954%205.636%2024.198%2017.722%204.509-12.086%2014.76-17.722%2025.744-17.722%207.813%200%2016.36%203.224%2021.577%2010.46%205.899%208.049%204.693%2019.741%204.693%2029.992l-.026%2060.378c0%201.913-1.6%203.46-3.592%203.46h-18.614c-1.862-.13-3.356-1.625-3.356-3.46V51.29c0-4.037.367-14.104-.524-17.932-1.39-6.423-5.558-8.232-10.959-8.232-4.51%200-9.228%203.015-11.142%207.839s-1.73%2012.898-1.73%2018.325v50.704c0%201.913-1.6%203.46-3.592%203.46h-18.614c-1.888-.13-3.356-1.625-3.356-3.46l-.026-50.704c0-10.67%201.757-26.374-11.483-26.374-13.397%200-12.872%2015.31-12.872%2026.374v50.704c0%201.913-1.6%203.46-3.592%203.46M469.514%201.164c27.66%200%2042.629%2023.752%2042.629%2053.954%200%2029.18-16.543%2052.329-42.629%2052.329-27.16%200-41.947-23.753-41.947-53.352%200-29.782%2014.97-52.931%2041.947-52.931m.158%2019.531c-13.738%200-14.603%2018.719-14.603%2030.386%200%2011.692-.184%2036.65%2014.445%2036.65%2014.446%200%2015.128-20.134%2015.128-32.403%200-8.075-.341-17.723-2.78-25.378-2.097-6.66-6.265-9.255-12.19-9.255M548.008%20105.454h-18.562c-1.861-.13-3.356-1.625-3.356-3.46l-.026-95.692c.157-1.756%201.704-3.12%203.592-3.12h17.277c1.625.079%202.962%201.18%203.33%202.674v14.63h.34c5.217-13.083%2012.532-19.322%2025.404-19.322%208.363%200%2016.517%203.015%2021.76%2011.273%204.877%207.655%204.877%2020.528%204.877%2029.782v60.22c-.21%201.678-1.757%203.015-3.592%203.015h-18.693c-1.704-.13-3.12-1.39-3.303-3.015V50.478c0-10.461%201.206-25.772-11.667-25.772-4.535%200-8.704%203.042-10.775%207.656-2.621%205.846-2.962%2011.666-2.962%2018.116v51.516c-.026%201.913-1.652%203.46-3.644%203.46%22%2F%3E%3Cuse%20xlink%3Ahref%3D%22%23a%22%20transform%3D%22translate(244.367)%22%2F%3E%3Cpath%20id%3D%22a%22%20d%3D%22M55.288%2059.758v-4.037c-13.475%200-27.71%202.884-27.71%2018.771%200%208.049%204.168%2013.502%2011.325%2013.502%205.243%200%209.936-3.225%2012.898-8.468%203.67-6.45%203.487-12.506%203.487-19.768m18.798%2045.434c-1.232%201.101-3.015%201.18-4.405.446-6.187-5.139-7.288-7.524-10.696-12.427-10.225%2010.434-17.46%2013.554-30.726%2013.554-15.678%200-27.895-9.674-27.895-29.048%200-15.127%208.206-25.43%2019.872-30.464%2010.12-4.457%2024.25-5.244%2035.052-6.476v-2.412c0-4.43.341-9.674-2.254-13.501-2.281-3.435-6.633-4.85-10.46-4.85-7.106%200-13.45%203.644-14.997%2011.194-.315%201.678-1.547%203.33-3.225%203.408l-18.09-1.94c-1.52-.34-3.198-1.573-2.778-3.906C7.652%206.853%2027.446.246%2045.169.246c9.07%200%2020.92%202.412%2028.078%209.28%209.07%208.469%208.206%2019.768%208.206%2032.064v29.048c0%208.73%203.618%2012.558%207.026%2017.277%201.206%201.678%201.468%203.697-.053%204.955-3.801%203.172-10.565%209.071-14.288%2012.375z%22%2F%3E%3C%2Fsvg%3E%0A", width=100)
    with col2:
            st.markdown("""
                <h1 style="color: #ff4500; font-family: Courier New, monospace; 
                        font-size:30px">
                    AMAZON SALES PERFORMANCE DASHBOARD
                </h1>
            """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
            [data-testid="stMetric"] {
                background-color: #0E0D0B;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 20px;
            }
            [data-testid="stMetricLabel"] {
                color: #F4F2F1;
                font-size: 16px;
            }
            [data-testid="stMetricValue"] {
                color: #F4F2F1;
                font-size: 28px;
            }
        </style>
    """, unsafe_allow_html=True)
    
   
       

    left_column,middle_column, right_column, far_right, far= st.columns(5)
   
    with left_column:
        st.metric(label="💰 Total Sales $", value=format_number(total_sales))
            
    with middle_column:
        st.metric(label="📈 Profit $", value=format_number(total_profit))
    
    with right_column:
        st.metric(label= "Gross Profit Margin", value=f"{gross_profit_margin}%")
    with far_right:
        st.metric(label="Total Orders", value=format_number(delivered_orders) )
    with far:
        st.metric(label= "Total Products", value= format_number(unique_products))
    # Filter out tiny slices before plotting
    

    cat_chart =px.bar(
        
        y= profit_per_category["category"],
        x=profit_per_category["net_sales"],
        title= "<b>Sales by Category</b>",
        orientation= "h",
        #text=  profit_per_category["mark"],
        color_discrete_sequence= ["#CE03A2"]
    )
    

    
    cat_chart.update_layout(
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        xaxis= dict(
            showgrid= False,
            title= None
            
        ),
        yaxis= dict(
          tickfont= dict(size= 10),
          showgrid= False,
          title= None,
          ),
        plot_bgcolor= "rgba(0, 0, 0, 0)",
        showlegend= False,
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font_color="white",
        title_font_color="#752F05" 
    )
    

    
    #sales by region
    
    region_sales_bar= px.bar(
        sales_per_region,
        y= "net_sales",
        x= "region",
        text= "mark",
        #orientation="h",
        title= "<b> Sales per Region</b>",
        color_discrete_sequence=["#672AF4"]
        
        
    )

    region_sales_bar.update_layout(
        height= 230,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        font_color="white",
        title_font_color="#752F05" ,
        xaxis= dict(
            tickfont= dict(size= 8),
            title=None),
        yaxis= dict(
          title= None,
          showgrid= False,
          showticklabels= False))
    region_sales_bar.update_traces(
        textposition= "outside")
    
    #sales Per year line graph
    yearly_sales_bar= px.area(
        sales_per_year,
        x= "year",
        y="net_sales",
        markers= True,
        title= "<b> Yearly Sales Over Time</b>",
        color_discrete_sequence= ["#AB4A0E"],
    )
    
    
    yearly_sales_bar.update_layout(
        height= 230,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        xaxis= dict(
            tickvals= list(range(int(min_year), int(max_year)+1)),
            range= [int(min_year)-0.5, int(max_year)+0.5],
            showgrid= False,
            title= None,
            dtick= 1,
        ),
        yaxis= dict(
            range= [min_sales*0.98, max_sales*1.02],
            showgrid= False,
            showticklabels= False,
            title= None),
       title_font_color= "#AB4A0E"
    )
    yearly_sales_bar.update_traces(
        line= dict(
            shape= "spline",
            color="#AB4A0E"),
        fillpattern= dict(
                shape= "/",
                fgcolor= "#AB4A0E",
                bgcolor= "rgba(0, 0, 0, 0)"
            )
    )
    yearly_sales_bar.update_xaxes(
    tickmode='linear',  
    dtick=1               
)

    orders_heat= px.imshow(
        dt_pivot_norm,
        color_continuous_scale= "Oranges",
        title= "Order Concentration by Region & Year"
    )
    orders_heat.update_layout(
        height= 180,
        title_font_color= "#AB4A0E",
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        xaxis= dict(
            title= None
        ),
        yaxis= dict(
            title= None
        )
    )
     

    status_pie= go.Figure(go.Pie(
        labels= del_counts["order_status"],
        values= del_counts["order_id"],
        hole= 0.8,
        textinfo= "none",
        domain= dict(x= [0.1, 0.7], y= [0.1, 0.7])
    ))
    status_pie.update_layout(
        height= 250,
        margin= dict(t= 40, b= 10, l= 10, r= 10),
        legend= dict(orientation= "h", y= -0.1)
    )
    #further  order status analysis
    ret_ag_del = px.bar(
    df_comb,
    x="year",
    y=["completed", "returned"],
    title="Completed Vs Returned orders over time",
    barmode="group",
    color_discrete_map={
        "completed": "#3a9ad9",
        "returned": "#e8622a"
    }
)
    ret_ag_del.update_layout(
        height= 180,
        title_font_color= "#ff4500")
    left, right, far_right= st.columns([2, 1.5, 1.5])
    with left:
      with st.container(border= True):
        st.plotly_chart(yearly_sales_bar)
      with st.container(border= True):
        st.plotly_chart(orders_heat)
    with far_right:
      with st.container(border= True):
        st.plotly_chart(cat_chart)
    with right:
        with st.container(border= True):
          st.plotly_chart(region_sales_bar)
        with st.container(border= True):
            st.plotly_chart(ret_ag_del)
   

    
    
    
    
 #customer insights
@st.cache_data
def xcl_store():
    df = download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQQbLvfnKB3WMaw98GueEScb0B6n4SXhw5dTNDq6-1zoojhUFChiDfli1nBc6TOJzHM55Rkrrqbq9Bi/pub?output=csv")
    dt = download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vQtKWIUDlK2HnqIONRKaz9AL50T0iIXnVHL5Uo3z6dHvlfRFPpqCCyWZcbaEbYVu8zBll85mvd9imAF/pub?output=csv")
    
    customers_dt= pd.merge(
            df,
            dt,
            on=("customer_id"),
            how= "left"
        )
    customers_dt["full_name"]= customers_dt["first_name"]+" "+customers_dt["last_name"]
    customers_dt= customers_dt[["customer_id", "full_name", "gender", "loyalty_tier",
                                    "age", "city", "country", "signup_date", "customer_segment", 
                                    "churn_probability",
                                    "customer_lifetime_value", "ticket_date", "resolution_days", "satisfaction_score"]]
        
    return customers_dt
@st.cache_data
def load_data(customers_dt):
    def format_number(num):
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)
    
    customers_dt= xcl_store()
    satisfaction_rating = round(customers_dt["satisfaction_score"].mean())
    churn_rate= round(
        (customers_dt["churn_probability"].sum())*100/len(customers_dt["churn_probability"]))
    total_customers=(
        customers_dt["customer_id"].nunique())
    
    unique_customers= customers_dt.drop_duplicates(subset="customer_id" )
    
    tier_counts= unique_customers["loyalty_tier"].value_counts()
    #amount per tier
    avg_clv=customers_dt.groupby(
    by="customer_id")[["customer_lifetime_value"]].first()
    avg_clv=round(avg_clv.mean().iloc[0])
    avg_clv= format_number(avg_clv)
    spend_per_tier=(
    customers_dt.groupby(
        by=customers_dt["loyalty_tier"])[["customer_lifetime_value"]].sum().reset_index()
        )
    #Gnder distribution
  
    #customer segment distribution analysis
    segment_counts= unique_customers["customer_segment"].value_counts()
    mark= segment_counts.apply(format_number).values
    segment_spend= (
      customers_dt.groupby(
        by= customers_dt["customer_segment"])[["customer_lifetime_value"]]
      .sum()
      .round(2)
      .sort_values(by= "customer_lifetime_value", ascending= True)
      .reset_index()
    )
    segment_spend["label"]= segment_spend["customer_lifetime_value"].apply(format_number)
    man_count=(unique_customers["gender"]=="Male").sum()
    woman_count= (unique_customers["gender"]=="Female").sum()
    male_pct = round(man_count*100/total_customers, 1)
    female_pct = round(woman_count *100/total_customers, 1)
    other= round(100-male_pct-female_pct, 1)
    #Age analysis
    # Age analysis
    bins = [18, 25, 35, 45, 55, 65, 100]
    labels = ["18-25", "26-35", "36-45", "46-55", "56-65", "66+"]

   
    customers_dt["age_group"] = pd.cut(customers_dt["age"], bins=bins,
                                        labels=labels, right=True)
    unique_customers= customers_dt.drop_duplicates(subset="customer_id" )
    age_group_count = unique_customers["age_group"].value_counts()
        
    country_dist_dt = (
    unique_customers["country"]
    .value_counts(normalize=True)  # returns proportions
    .mul(100)                      # convert to percentage
    .round(2)                      # round to 2 decimal places
    .reset_index()
)

    country_dist_dt.columns = ["Country", "Percentage"]
    total_customers= format_number(total_customers)
    
    return (
           satisfaction_rating,
           churn_rate,
           total_customers,
           tier_counts,
           spend_per_tier,
           avg_clv,
           country_dist_dt,
           male_pct,
           female_pct,
           other,
           age_group_count,
           segment_counts,
           segment_spend,
           mark

    )
@st.cache_data                                                       
def show_customers():
    
    customers_dt= xcl_store()
    (
           satisfaction_rating,
           churn_rate,
           total_customers,
           tier_counts,
           spend_per_tier,
           avg_clv,
           country_dist_dt,
           male_pct,
           female_pct,
           other,
           age_group_count,
           segment_counts,
           segment_spend,
           mark


    )= load_data(customers_dt)

    st.markdown("""
                <h1 style="color: #20b2aa; font-family: Courier New, monospace; 
                        font-size:36px">
                    Customer Insight✨
                </h1>
            """, unsafe_allow_html=True)   


    col, col2,left, right= st.columns(4)

    rating_stars = '<span class="material-symbols-outlined">star_rate</span>' * satisfaction_rating
    
    with left:
        st.markdown(f"""
            <div style="background-color:#20b2aa; padding:10px; border-radius:6px;">
                <p style="color:black; font-size:16px; margin-bottom:4px;">Satisfaction Rating</p>
                <p style="font-size:30px; font-weight:bold; margin-bottom:4px;">
                    {satisfaction_rating} <span style="color:#ff4500; margin:0;">{rating_stars}</span>
                    </p>
            </div>
        """, unsafe_allow_html=True)
    with col2:
         st.markdown(f"""
            <div style="background-color:#20b2aa; padding:10px; border-radius:6px;">
                <p style="color:black; font-size:16px; margin-bottom:4px;">Average C-L-V</p>
                <p style="font-size:30px; font-weight:bold; margin-bottom:4px;">{avg_clv}💲 </p>
            </div>
        """, unsafe_allow_html=True)
                                                        
    with right:
        st.markdown(f"""
            <div style="background-color:#20b2aa; padding:10px; border-radius:6px;">
                <p style="color:black; font-size:16px; margin-bottom:4px;">Churn Rate</p>
                <p style="font-size:30px; font-weight:bold; margin-bottom:4px;">{churn_rate} %</p>
            </div>
        """, unsafe_allow_html=True)
    #total_customers
    
    with col:
        st.markdown(f"""
            <div style="background-color:#20b2aa; padding:10px; border-radius:6px;">
                <p style="color:black; font-size:16px; margin-bottom:4px;">Total customers</p>
                <p style="font-size:30px; font-weight:bold; margin-bottom:4px;">{total_customers}👥 </p>
            </div>
        """, unsafe_allow_html=True)


    segment_counts_bar= px.bar(
      x= segment_counts.index,
      y= segment_counts.values,
      text= mark,
      title="<b> Sgement Population</b>",
      color_discrete_sequence= ["#4D82D1"]
    )
    segment_counts_bar.update_traces(
      textposition= "outside")
    segment_counts_bar.update_layout(
      yaxis= dict(
        title= None,
        showgrid= False,
        showticklabels= False
      ),
      xaxis= dict(
        title= None)
    )

    segment_spend_bar= px.bar(
     segment_spend,
     x= "customer_segment",
     y= "customer_lifetime_value",
     text= "label",
     title= "<b>Segment Spending</b>",
     color_discrete_sequence= ["#49D498"])
    segment_spend_bar.update_traces(
      textposition= "outside")

  
    segment_spend_bar.update_layout(
      yaxis= dict(
        title= None,
        showgrid= False,
        showticklabels= False
      ),
      xaxis= dict(
        title= None)
    )
    st.markdown("#")
    lef, righ= st.columns(2)
    with lef:
      with st.container(border= True):
          st.plotly_chart(segment_counts_bar)
    with righ:
      with st.container(border= True):
         st.plotly_chart(segment_spend_bar)
    lef, rig, middle= st.columns(3)
  
    #tier counts
    
    #pie for tier distribution
    pie_tier=go.Figure(go.Pie(
        labels= tier_counts.index,
        values=tier_counts.values,
        hole= 0.7,
        textinfo= "label",
        textposition= "outside"
    
    )
    )
    pie_tier.update_traces(
        outsidetextfont= dict(size= 12),
        domain= dict(x=[0.1, 0.9], y=[0.1, 0.9])
    )
    pie_tier.update_layout(
    
        showlegend= False
    )
    pie_tier.update_layout(

        uniformtext_minsize=10,
        uniformtext_mode='hide',
        plot_bgcolor= "rgba(0, 0, 0, 0)",
        
        showlegend= False,
        title= "<b>Customers Distribution on Tier</b>",
        
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font_color="white",
        title_font_color="#4D60D1"
    )
    age_group_count_pie= go.Figure(go.Pie(
        labels= age_group_count.index,
        values=age_group_count.values,
        hole= 0.7,
        textinfo= "label+percent",
        textposition="outside"

    ))
    age_group_count_pie.update_traces(
         outsidetextfont=dict(size= 12),
         domain= dict(x=[0.1, 0.9], y=[0.1, 0.9])
    )

    age_group_count_pie.update_layout(

        uniformtext_minsize=10,
        uniformtext_mode='hide',
        plot_bgcolor= "rgba(0, 0, 0, 0)",
        
        showlegend= False,
        title= "<b>Age Groups</b>",
        
        paper_bgcolor="rgba(0, 0, 0, 0)",
        font_color="white",
        title_font_color="#4D60D1"
    )

    #bar
    tier_bar=px.bar(
        spend_per_tier,
        x="customer_lifetime_value",
        y= "loyalty_tier",
        orientation="h",
        title= "<b> Spend on Different Tiers📊</b>",
        color_discrete_sequence= ["#58BDC6"]
        )
    tier_bar.update_layout(
        title_font_color= "#4D60D1",
        showlegend= False,
        xaxis= dict(
        showticklabels= False,
        title= None,),
        yaxis=dict(title= "Customer Tier",
        showticklabels= True,
        )
    )
    with rig:
       with st.container(border= True):
           st.plotly_chart(tier_bar, use_container_width= True)
    with lef:
        with st.container(border= True):
            st.plotly_chart(pie_tier, use_container_width= True)
    with middle:
       with st.container(border= True):
          st.plotly_chart(age_group_count_pie, use_container_width= True)
    
    st.markdown(f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <div style="
        background-color: #20b2aa;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        width: 100%;
        box-sizing: border-box;
    ">
        <p style="color:white; font-size:16px; margin-bottom:16px;">Gender Distribution</p>
        <div style="display:flex; justify-content:space-around; align-items:center;">
            <div style="text-align:center;">
                <i class="fas fa-person" style="font-size:64px; color:#000000;"></i>
                <p style="color:white; font-size:22px; font-weight:bold; margin:8px 0 0 0;">{male_pct}%</p>
                <p style="color:white; font-size:14px; margin:0;">Male</p>
            </div>
            <div style="text-align:center;">
                <i class="fas fa-person-dress" style="font-size:64px; color:#f48fb1;"></i>
                <p style="color:white; font-size:22px; font-weight:bold; margin:8px 0 0 0;">{female_pct}%</p>
                <p style="color:white; font-size:14px; margin:0;">Female</p>
            </div>
            <div style="text-align:center;">
                <i class="fas fa-genderless" style="font-size:64px; color:#023020;"></i>
                <p style="color:white; font-size:22px; font-weight:bold; margin:8px 0 0 0;">{other}%</p>
                <p style="color:white; font-size:14px; margin:0;">Other/prefer not to say</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)


    st.markdown("### Customers by country")

    # Map country name to ISO 2-letter code (for flagcdn.com)
    flag_map = {
        "USA": "us",
        "Kenya": "ke",
        "UK": "gb",
        "India": "in",
        "South Africa": "za",
        "China": "cn",
        "Canada": "ca",
        "Nigeria": "ng",
        "Tanzania": "tz",
        "Uganda": "ug",
        "Germany": "de",
        "France": "fr",
        "Australia": "au",
    }

    cols_per_row = 5
    cols = st.columns(cols_per_row)

    for i, row in enumerate(country_dist_dt.itertuples()):
        country = row.Country        
        percentage = row.Percentage  
        code = flag_map.get(country, "un")  # 'un' = UN flag as fallback
        flag_url = f"https://flagcdn.com/64x48/{code}.png"

        with cols[i % cols_per_row]:
            st.markdown(f"""
                <div style="
                    background-color: #20b2aa;
                    border-radius: 10px;
                    padding: 12px 16px;
                    margin-bottom: 10px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                ">
                    <div>
                        <p style="font-weight:bold; font-size:16px; margin:0; color:white;">{country}</p>
                        <p style="font-size:14px; color:white; margin:0;">{percentage:.1f}%</p>
                    </div>
                    <img src="{flag_url}" width="48" height="36" style="border-radius:4px;">
                </div>
            """, unsafe_allow_html=True)
        
    
    st.dataframe(customers_dt.head(100))
if selected== "Home":
    show_home()
elif selected== "Customers":
     show_customers()

        
        
            
        
              
              




    
    
