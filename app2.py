import pandas as pd
import streamlit as st
import plotly_express as px
import matplotlib
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
import warnings
import requests
import io
import sys 
sys.modules['warnings'] = warnings
#option menu code
st.set_page_config(page_title= "Sales Dashbord",
                    page_icon= ":bar_chart:",
                    layout= "wide")

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

    
def download_csv(pub_url):
    response = requests.get(pub_url)
    return pd.read_csv(io.StringIO(response.content.decode("utf-8")))
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined" rel="stylesheet"/>
""", unsafe_allow_html=True)
        

@st.cache_data
def excel_store():
    orders_dt = download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vTM0OV17ARTPBIFMnQC-DmYIZMcQ5pvGVuHVuXFcT_lsUG1PNfe5aDj12s9Zva3ebAUWasIGPeTNAUp/pub?output=csv")
    order_items_dt = download_csv("https://docs.google.com/spreadsheets/d/e/2PACX-1vTneMnypJ7M-1okZDOjTWCnIoxF6NmVVrFsa2zlLbkjLlu3axFqtkdHTc1Q-mTigQU7X6A4tqZvkkeX/pub?output=csv")
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
    #Sales per year
    df["order_date"]= pd.to_datetime(df["order_date"])
    df["year"]= df["order_date"].dt.year
    sales_per_year=(
        df.groupby(by=df["year"])[["net_sales"]]
        .sum()
        .reset_index()
    )
    sales_per_region=(
        df.groupby(by= df["region"])[["net_sales"]]
        .sum()
        .reset_index()
    )
    #product count
    unique_products= df["product_id"].nunique()
    
         
    return (
        total_sales,
        total_profit,
        gross_profit_margin,
        delivered_orders,
        profit_per_category,
        sales_per_region,
        sales_per_year,
        unique_products
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
        unique_products
    ) = store_2(df)
    def format_number(num):
        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"
        elif num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num/1_000:.1f}K"
        return str(num)
    st.markdown("""
        <h1 style="color: #20b2aa; font-family: Courier New, monospace; 
                font-size:36px">
            📊 Sales Dashboard
        </h1>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        <style>
            [data-testid="stMetric"] {
                background-color: #1e1e2e;
                border: 1px solid #333;
                border-radius: 10px;
                padding: 20px;
            }
            [data-testid="stMetricLabel"] {
                color: #aaaaaa;
                font-size: 16px;
            }
            [data-testid="stMetricValue"] {
                color: #20b2aa;
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
        st.metric(label= "Total Producs", value= format_number(unique_products))
    # Filter out tiny slices before plotting
    

    cat_chart =px.bar(
        
        y= profit_per_category["category"],
        x=profit_per_category["net_sales"],
        title= "<b>Sales by Category</b>",
        orientation= "h",
        color_discrete_sequence= ["#AB4A0E"]
    )
    


    cat_chart.update_layout(
        xaxis= dict(
            showgrid= False
            
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
        x= "net_sales",
        y= "region",
        orientation="h",
        title= "<b> Sales per Region</b>",
        color_discrete_sequence=["#AB4A0E"]
        
        
    )

    region_sales_bar.update_layout(
        font_color="white",
        title_font_color="#752F05" ,
        xaxis= dict(
            title= "Sales"

        )
        
    )
    
    #sales Per year line graph
    yearly_sales_bar= px.line(
        sales_per_year,
        x= "year",
        y="net_sales",
        markers= True,
        title= "<b> Yearly Sales Over Time</b>",
        color_discrete_sequence= ["#AB4A0E"],
    )
    yearly_sales_bar.update_traces(
        line_shape= "spline"
    )
    yearly_sales_bar.update_layout(
        xaxis= dict(
            range= [2020, 2024],
            showgrid= False,
            dtick= 1,
        ),
        yaxis= dict(
            showgrid= False,
            showticklabels= False,
            title= None),
       title_font_color= "#AB4A0E"
    )
    yearly_sales_bar.update_xaxes(
    tickmode='linear',  
    dtick=1               
)
    
    left, right, far_right= st.columns(3)
    with left:
      with st.container(border= True):
        st.plotly_chart(yearly_sales_bar)
    with right:
      with st.container(border= True):
        st.plotly_chart(cat_chart)
    with far_right:
       with st.container(border= True):
          st.plotly_chart(region_sales_bar)
      
    st.dataframe(df.head(101))

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
           age_group_count

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
           age_group_count


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
        title_font_color="green"
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
        title_font_color="green"
    )

    #bar
    tier_bar=px.bar(
        spend_per_tier,
        x="customer_lifetime_value",
        y= "loyalty_tier",
        orientation="h",
        title= "<b> Spend on Different Tiers📊</b>",
        color_discrete_sequence= ["#ff0026"]
        )
    tier_bar.update_layout(
        title_font_color= "green",
        showlegend= False,
        xaxis= dict(
        showticklabels= False,
        title= None,),
        yaxis=dict(title= "Customer Tier",
        showticklabels= True,
        )
    )
    with rig:
     st.plotly_chart(tier_bar, use_container_width= True)
    with lef:
      st.plotly_chart(pie_tier, use_container_width= True)
    with middle:
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

        
        
            
        
              
              




    
    
