import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests

# Title and description
st.title("Customize Your Smoothie :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for the name on the order
name_on_order = st.text_input('Name on Smoothie')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.experimental_connection("snowflake")
session = cnx.session()
fruit_options = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark DataFrame to Pandas DataFrame
pd_df = fruit_options.to_pandas()

# Display fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')

        st.subheader(f'{fruit_chosen} Nutrition Information')
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen.lower()}")
        
        if fruityvice_response.status_code == 200:
            fv_df = pd.json_normalize(fruityvice_response.json())
            st.dataframe(data=fv_df, use_container_width=True)
        else:
            st.write("Nutrition information not available for", fruit_chosen)

    # SQL statement for inserting the order
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered', icon="✅")
