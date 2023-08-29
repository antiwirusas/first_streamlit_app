import streamlit as st
import pandas as pd
import requests
import snowflake.connector
from urllib.error import URLError

st.title('My Parents New Healthy Diner')
st.header('Breakfast Favorites')
st.text('🥣   Omega 3 a 8ueberry Oatmeal')
st.text('🥗   Kale, Spinach & Rocket Smoothie')
st.text('🐔   Hard-Boiled Free-Range Egg')
st.text('🥑🍞 Avocado Toast')

st.header('🍌🥭 Build Your Own Fruit Smoothie 🥝🍇')

my_fruit_list = pd.read_csv("https://uni-lab-files.s3.us-west-2.amazonaws.com/dabw/fruit_macros.txt")
my_fruit_list = my_fruit_list.set_index('Fruit')
fruits_selected = st.multiselect("Pick some fruits:", list(my_fruit_list.index), ['Avocado','Strawberries'])
fruits_to_show = my_fruit_list.loc[fruits_selected]
st.dataframe(fruits_to_show)

def get_fruityvice_data(this_fruit_choice):
    fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + this_fruit_choice)
    fruityvice_normalized = pd.json_normalize(fruityvice_response.json())
    return fruityvice_normalized

st.header("Fruityvice Fruit Advice!")
try:
    fruit_choice = st.text_input('What fruit would you like information about?')
    if not fruit_choice:
        st.error("Please select a fruit to get information.")
    else:
        back_from_function = get_fruityvice_data(fruit_choice)
        st.dataframe(back_from_function)
except URLError as e:
    st.error(f"Failed to fetch data from the Fruityvice API: {e}")

# Now let's address the snowflake database interactions

# Connect to Snowflake once
my_cnx = snowflake.connector.connect(**st.secrets["snowflake"])

def get_fruit_load_list():
    with my_cnx.cursor() as my_cur:
        my_cur.execute("SELECT * from fruit_load_list")
        return my_cur.fetchall()

def insert_row_snowflake(new_fruit):
    with my_cnx.cursor() as my_cur:
        # Use parameterized query to avoid SQL injection
        my_cur.execute("insert into fruit_load_list values (%s)", (new_fruit,))
        return 'Thanks for adding ' + new_fruit

st.header("The fruit load list contains:")

if st.button('Get Fruit Load List'):
    my_data_rows = get_fruit_load_list()
    st.dataframe(my_data_rows)

add_my_fruit = st.text_input('What fruit would you like to add?')

if st.button('Add a Fruit to the List'):
    back_from_function = insert_row_snowflake(add_my_fruit)
    st.text(back_from_function)

st.stop()
my_cnx.close()  # Close the Snowflake connection
