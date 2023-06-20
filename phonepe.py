import streamlit as st
import json
import os
import pandas as pd
import mysql.connector
import requests
import folium
from streamlit_folium import folium_static
import plotly.express as px
import re


# This is to direct the path to get the data as states
path = r"C:\Users\shrib\PycharmProjects\pulse\data\aggregated\transaction\country\india\state"
Agg_state_list = os.listdir(path)

clm = {'State': [], 'Year': [], 'Quater': [], 'Transacion_type': [], 'Transacion_count': [], 'Transacion_amount': []}

for i in Agg_state_list:
    p_i = path + "\\" + i + "\\"
    Agg_yr = os.listdir(p_i)
    for j in Agg_yr:
        p_j = p_i + j + "\\"
        Agg_yr_list = os.listdir(p_j)
        for k in Agg_yr_list:
            p_k = p_j + k
            Data = open(p_k, 'r')
            D = json.load(Data)
            for z in D['data']['transactionData']:
                Name = z['name']
                count = z['paymentInstruments'][0]['count']
                amount = z['paymentInstruments'][0]['amount']
                clm['Transacion_type'].append(Name)
                clm['Transacion_count'].append(count)
                clm['Transacion_amount'].append(amount)
                clm['State'].append(i)
                clm['Year'].append(j)
                clm['Quater'].append(int(k.strip('.json')))

# Successfully created a dataframe
df = pd.DataFrame(clm)

# Establish a connection to the MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="phonepe"
)

# Create a cursor object to execute SQL queries
cursor = connection.cursor()

# Check if the table already exists
check_query = "SELECT COUNT(*) FROM data"
cursor.execute(check_query)
row_count = cursor.fetchone()[0]

if row_count == 0:
    # Create the table
    table_schema = '''
    CREATE TABLE IF NOT EXISTS data (
        State VARCHAR(255),
        Year INT,
        Quater INT,
        Transacion_type VARCHAR(255),
        Transacion_count INT,
        Transacion_amount FLOAT
    )
    '''
    cursor.execute(table_schema)

    # Insert the data into the table
    data = df.values.tolist()
    insert_query = "INSERT INTO data (State, Year, Quater, Transacion_type, Transacion_count, Transacion_amount) VALUES (%s, %s, %s, %s, %s, %s)"
    cursor.executemany(insert_query, data)
    connection.commit()

# Fetch the data from the MySQL database
select_query = "SELECT * FROM data"
cursor.execute(select_query)
data = cursor.fetchall()

# Create a DataFrame from the fetched data
df = pd.DataFrame(data, columns=['State', 'Year', 'Quater', 'Transacion_type', 'Transacion_count', 'Transacion_amount'])

# Close the cursor and the database connection
cursor.close()
connection.close()

# Combine Year and Quater columns and add "Q" prefix
df["Quarter_label"] = "Q" + df["Quater"].astype(str) + " " + df["Year"].astype(str)

# Set the page title
st.set_page_config(page_title="Explore Insights on Online Transactions Across India")

# Add Title
st.markdown("# Phonepe Pulse | The Beat of Progress")

# Add the filter dropdown for quarters
selected_quarter = st.selectbox("Select Quarter", df["Quarter_label"].unique())

# Filter the data based on the selected quarter
filtered_df = df[df["Quarter_label"] == selected_quarter]

# Calculate the required statistics
transaction_count = filtered_df["Transacion_count"].sum()
total_payment_value = filtered_df["Transacion_amount"].sum()
average_transaction_value = round(sum(filtered_df["Transacion_amount"]) / sum(filtered_df["Transacion_count"]), 2)

# Aggregate the data by state and calculate the total count
state_counts = filtered_df.groupby('State')['Transacion_count'].sum().reset_index()


# Add the first small space with transaction facts
st.markdown("<h2>Transaction</h2>", unsafe_allow_html=True)
st.markdown(f"<h4>All Phonepe Transactions Count: {transaction_count}</h4>", unsafe_allow_html=True)
st.markdown(f"<h4>Total Payment Value (Rs.): {total_payment_value}</h4>", unsafe_allow_html=True)
st.markdown(f"<h4>Average Transaction Value (Rs.): {average_transaction_value}</h4>", unsafe_allow_html=True)


# Replace '-' with spaces in the state names of the DataFrame
filtered_df['State'] = filtered_df['State'].apply(lambda x: re.sub(r'-', ' ', x))

# Download the GeoJSON file and save it locally
url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

with requests.get(url) as r:
    with open('india_states.geojson', 'wb') as f:
        f.write(r.content)

# Load the GeoJSON file and modify state names to lowercase with '-' replaced by spaces
with open('india_states.geojson') as f:
    geojson_data = json.load(f)
    for feature in geojson_data['features']:
        state_name = feature['properties']['ST_NM']
        state_name = re.sub(r'-', ' ', state_name.lower())
        feature['properties']['ST_NM'] = state_name


# Create a base map centered around India for count
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

st.markdown("<h2>Transaction Count Map</h2>", unsafe_allow_html=True)

# Add the choropleth layer with the color mapping and legend
folium.Choropleth(
    geo_data=geojson_data,
    name='choropleth',
    data=filtered_df,
    columns=['State', 'Transacion_count'],
    key_on='feature.properties.ST_NM',
    fill_color='YlOrBr',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Transaction Count',
).add_to(m)

# Display the map in Streamlit
folium_static(m)

# Create a base map centered around India for amount
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

st.markdown("<h2>Transaction Amount Map</h2>", unsafe_allow_html=True)

# Add the choropleth layer with the color mapping and legend
folium.Choropleth(
    geo_data=geojson_data,
    name='choropleth',
    data=filtered_df,
    columns=['State', 'Transacion_amount'],
    key_on='feature.properties.ST_NM',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Transaction Amount',
).add_to(m)

# Display the map in Streamlit
folium_static(m)

# Add the second small space with categories and their values
st.markdown("## Categories")
categories = df["Transacion_type"].unique()
for category in categories:
    category_total = filtered_df.loc[filtered_df["Transacion_type"] == category, "Transacion_amount"].sum()
    st.write(category, f"Rs. {category_total}")

# Calculate the category totals
category_totals = filtered_df.groupby("Transacion_type")["Transacion_amount"].sum()

# Create a pie chart using Plotly Express
fig = px.pie(category_totals, values="Transacion_amount", names=category_totals.index)

# Set the chart title
fig.update_layout(title="Transaction Category")

# Display the chart using Streamlit
st.plotly_chart(fig)

# Add the third small space with top 10 states
st.markdown("## Top 10 States")
top_10_states = filtered_df.groupby("State")["Transacion_amount"].sum().nlargest(10)
for i, (state, amount) in enumerate(top_10_states.items(), start=1):
    st.write(f"{i}. {state}: Rs. {amount} ")

# Get the top 10 states and their transaction amounts
top_10_states = filtered_df.groupby("State")["Transacion_amount"].sum().nlargest(10).reset_index()

# Create a bar chart using Plotly Express
fig = px.bar(top_10_states, x="State", y="Transacion_amount", color="State", title="Top 10 States by Transaction Amount")

# Set the x-axis label
fig.update_xaxes(title="State")

# Set the y-axis label
fig.update_yaxes(title="Transaction Amount")

# Display the chart using Streamlit
st.plotly_chart(fig)

# Calculate the transaction amount by Quarter_label
transaction_amount_by_quarter = df.groupby("Quarter_label")["Transacion_amount"].sum().reset_index()

# Sort the Quarter_label in ascending order
sorted_quarters = sorted(filtered_df["Quarter_label"].unique())

# Create a bar chart using Plotly Express with sorted x-axis labels
fig = px.bar(transaction_amount_by_quarter, x="Quarter_label", y="Transacion_amount", title="Transaction Amount by Quarter",
             category_orders={"Quarter_label": sorted_quarters})

# Set the x-axis label
fig.update_xaxes(title="Quarter")

# Set the y-axis label
fig.update_yaxes(title="Transaction Amount")

# Adjust the spacing between bars
fig.update_layout(bargap=0.1)

# Display the chart using Streamlit
st.plotly_chart(fig)
