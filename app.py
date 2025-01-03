import streamlit as st
import pandas as pd
import pydeck as pdk
import altair as alt

# Load dataset
@st.cache_data
def load_data(): 
    df = pd.read_csv("data.csv")
    df = df.dropna(subset=["latitude", "longitude"])
    return df

# Load and filter data 
data = load_data()
columns_to_keep = ['latitude', 'longitude', 'city_or_county', 'state', 'date', 'n_killed', 'n_injured']
data = data[columns_to_keep]

st.title("Gun Violence Incidents in the United States")
st.text("This app is a tool to explore gun violence incidents in the United States from 2013 to 2018. The data is sourced from the Gun Violence Archive and includes over 260,000 incidents.")
st.text("The chart is interactive and you can hover over the bars to see the place and date where the incident occurred and the exact number of people injured and killed.")

# Define the PyDeck Layer
data['date'] = pd.to_datetime(data["date"]).dt.strftime("%m/%d/%Y")

layer = pdk.Layer(
    "ScatterplotLayer",
    data=data,
    get_position='[longitude, latitude]',
    get_fill_color='[255, 0, 0, 160]',
    get_radius=500,
    pickable=True,
)

# Define the PyDeck View
view_state = pdk.ViewState(
    latitude=data['latitude'].mean(),
    longitude=data['longitude'].mean(),
    zoom=4,
    pitch=0,
)

# Create PyDeck Deck
deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<div>Shooting at {city_or_county}, {state} on<br>{date}<br>{n_killed} killed, {n_injured} injured</div>"
    }
)

# Display the maps
st.pydeck_chart(deck)

st.divider()

# Show a bar chart of the number injured and killed by state
st.header("Number of Injured and Killed by State")
st.text("The bar chart shows the number of injured and killed by state. The chart is interactive and you can hover over the bars to see the exact number of injured and killed for each state.")

bar_data = data.groupby('state').agg({'n_killed': 'sum', 'n_injured': 'sum'}).reset_index()
bar_data.rename(columns={'state': 'State', 'n_killed': '# Killed', 'n_injured': '# Injured'}, inplace=True)


# Create a stacked bar chart
bar_chart = alt.Chart(bar_data).transform_fold(
    ['# Killed', '# Injured'],
    as_=['Category', 'Count']
).mark_bar().encode(
    x=alt.X('State:O', title='State'),
    y=alt.Y('Count:Q', title='Count'),
    color=alt.Color('Category:N', title='Category'),
    tooltip=['State:N', 'Category:N', 'Count:Q']
).properties(
    width=600,
    height=400
)

st.altair_chart(bar_chart, use_container_width=True)

# Return the top five states with the highest number of injured and killed
bar_data = bar_data.sort_values(by=['# Killed', '# Injured'], ascending=[False, False]).head(5)
st.header("Top 5 States with the Highest Number of Injured and Killed")
st.write("The top five states with the highest number of injured and killed were: California, Texas, Florida, Illinois, and Georgia.")
st.write(bar_data)

# Show raw data
if st.checkbox("Show Raw Data"):
    st.write(data)