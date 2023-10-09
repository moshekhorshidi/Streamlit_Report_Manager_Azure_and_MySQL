import mysql.connector
import json 
import streamlit as st
import pandas as pd 


# Connect to the MySQL database
conn = mysql.connector.connect(
    host="your_host_cards_local_or_server",
    user="your_user_name",
    password="your_password",
    database="sakila"
)

st.title("Welcome to Moshe Khorshidi Sakila Database Query and reports UI :sunglasses:")
st.write("Streamlit application.")
st.header("Pay report:", divider='rainbow')
st.subheader(" The query that build the report: ")

def pay_report_data():

# Create a cursor object
    cursor = conn.cursor()

# Execute a SQL query
    cursor.execute("""select concat(cust.first_name, ' ', cust.last_name) as "Full Name", 
		            CAST(cust.customer_id as SIGNED) as "Customer ID", sum(amount) as "Total Pay" 
                    from sakila.customer cust inner join sakila.payment pay
	                    on cust.customer_id = pay.customer_id
                    group by 1,2
                    """)

# Fetch the results
    pay_report_data_query_columns_names = [col[0] for col in cursor.description]
    pay_report_data_query_rows = cursor.fetchall()
    data_q1 = pd.DataFrame(pay_report_data_query_rows, columns = pay_report_data_query_columns_names)
 

    # Close cursor and connection
    cursor.close()
    conn.close()

    return data_q1


#defines columns names for query
#colomns_names = ["Customer full name", "Customer ID", "Total Pay"]
#This code defines the UI of the application

# Rest of your Streamlit app code goes here


Q1_text = '''  
            
        ***MySQL Code Snip:***

        SELECT concat(cust.first_name, ' ', cust.last_name) as "Full Name",
		       CAST(cust.customer_id as SIGNED) as "Customer ID",
               sum(amount) as "Total Pay" 
    FROM sakila.customer cust INNER JOIN sakila.payment pay
	    ON cust.customer_id = pay.customer_id
    GROUP BY 1,2
          
          '''

if st.button("Query 1 - Code Snip"):
     st.markdown(Q1_text)
     st.button("Close Code Snipp")


if st.button("See Report"):

    result = pay_report_data()
    
    
    if result.empty:

        data_container = st.empty()  # Create an empty container
        data_container.write("No Data on this report:")     
    
    else:
        
        st.write("pay report data.")
        st.write(result)
        st.button("Close Report")

#Next report --------------------------------------------------------------------------

st.header("Actor ranking report:", divider='rainbow')
st.subheader("The query that build the report:")


Q2_text = '''  

            ***MySQL Code Snip:***

                SELECT s.actor_id,
                       concat(ac.first_name, ' ', ac.last_name) as full_name,
                       count(distinct s.film_id) as total_films,
                       rank() over(order by count(distinct s.film_id) desc ) as rank_actor
                FROM sakila.film_actor s inner join sakila.actor a
                    on a.actor_id = s.actor_id
                inner join sakila.film f
                    on f.film_id = s.film_id
                inner join actor ac 
                    on ac.actor_id = s.actor_id
                group by 1,2 
                        
          '''

if st.button("Query 2 - Code Snip"):
     st.markdown(Q2_text)
     st.button("Close Code Snipp")
    

def Actor_ranking_report():

# Create a cursor object
    cursor = conn.cursor()

# Execute a SQL query
    cursor.execute("""SELECT    s.actor_id,
                                concat(ac.first_name, ' ', ac.last_name) as full_name, 
                                #title,
                                count(distinct s.film_id) as total_films,
                                rank() over(order by count(distinct s.film_id) desc ) as rank_actor
                        FROM sakila.film_actor s inner join sakila.actor a
                            on a.actor_id = s.actor_id
                        inner join sakila.film f
                            on f.film_id = s.film_id
                            inner join actor ac 
                            on ac.actor_id = s.actor_id
                            group by 1,2""")

# Fetch the results
    Actor_ranking_report_query_columns_names = [col[0] for col in cursor.description]
    Actor_ranking_report_query_rows = cursor.fetchall()
    data_q2 = pd.DataFrame(Actor_ranking_report_query_rows, columns = Actor_ranking_report_query_columns_names)
 

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return data_q2


if st.button("Actor Ranking Report"):

    result = Actor_ranking_report()
    
    
    if result.empty:

        data_container = st.empty()  # Create an empty container
        data_container.write("No Data on this report:")     
    
    else:
        
        st.write("Actor Ranking Report.")
        st.write(result)
        st.button("Close Report")

# Next query ------------------------------------------------------------

st.header("Most Unrental Movies Per Store report:", divider='rainbow')
st.subheader("The query that build the report:")


Q3_text =   '''

            ***MySQL Code Snip:***
            
                with my_stores as 
                
                (

                select s.store_id , title,  
                       i.film_id, count(i.film_id) over (partition by s.store_id, title) as Total_copies
                from `sakila`.`inventory` i left join  `sakila`.`store` s
                    on s.store_id = i.store_id
                inner join `sakila`.`film` f
                    on i.film_id = f.film_id

                ) , max_value_count as 
                    
                    (
            
                         select store_id, max(Total_copies) as max_copies_movie 
                         from my_stores
                         group by 1
                        
                    )

                select my_stores.store_id , title , count(film_id) as total
                from my_stores inner join max_value_count
                    on my_stores.store_id = max_value_count.store_id
                where Total_copies = max_copies_movie
                group by 1,2 
                       
                                 
            '''

if st.button("Query 3 - Code Snip"):
     st.markdown(Q3_text)
     st.button("Close Code Snipp")
    

def most_unrental_movies_per_Store_report():

# Create a cursor object
    cursor = conn.cursor()

# Execute a SQL query
    cursor.execute("""with my_stores as (

select s.store_id , title,  i.film_id, count(i.film_id) over (partition by s.store_id, title) as Total_copies
from `sakila`.`inventory` i left join  `sakila`.`store` s
	on s.store_id = i.store_id
inner join `sakila`.`film` f
	on i.film_id = f.film_id
    
    ) , max_value_count as (
    
    select store_id, max(Total_copies) as max_copies_movie 
	from my_stores
    group by 1
    
    )

select my_stores.store_id , title , count(film_id) as total
from my_stores inner join max_value_count
	on my_stores.store_id = max_value_count.store_id
where Total_copies = max_copies_movie
group by 1,2
""")

# Fetch the results
    most_unrental_movies_per_Store_report_query_columns_names = [col[0] for col in cursor.description]
    most_unrental_movies_per_Store_report_query_rows = cursor.fetchall()
    data_q3 = pd.DataFrame(most_unrental_movies_per_Store_report_query_rows, columns = most_unrental_movies_per_Store_report_query_columns_names)
 

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return data_q3


if st.button("Most Unrental Movies Per Store"):

    result = most_unrental_movies_per_Store_report()
    
    
    if result.empty:

        data_container = st.empty()  # Create an empty container
        data_container.write("No Data on this report:")     
    
    else:
        
        st.write("Most Unrental Movies Per Store.")
        st.write(result)
        st.button("Close Report")


#-----------------------------------------

st.write("Testing")

#-----------------------------------------


def table_names():

# Create a cursor object
    cursor = conn.cursor()

# Execute a SQL query
    cursor.execute(""" SELECT TABLE_NAME, TABLE_SCHEMA FROM information_schema.tables where TABLE_SCHEMA = 'sakila' """)

# Fetch the results
    information_schema_table_columns_names = [col[0] for col in cursor.description]
    information_schema_table_data = cursor.fetchall()
    table_names_data = pd.DataFrame(information_schema_table_data, columns = information_schema_table_columns_names)
 

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return table_names_data

def query_builder():


    cursor = conn.cursor()
    # Get a list of all table names in the database
    tables = cursor.execute(""" SELECT TABLE_NAME, TABLE_SCHEMA FROM information_schema.tables where TABLE_SCHEMA = 'sakila' """)
    table_names = [table[0] for table in tables]

    # Create a dropdown list button for the table name
    table_name = st.selectbox('Select a table:', table_names)

    # Create a button for selecting the `*` symbol for all columns
    select_all_columns = st.button('Select all columns')

    # If the 'Select all columns' button is clicked, add the `*` symbol to the query
    if select_all_columns:
        cursor.execute(f"""select * from {table_name}""")  
    else:
        # Get a list of all column names in the selected table
        columns = cursor.execute("""select * from actor""")
        column_names = [column[0] for column in columns]

    # Close the database connection
    conn.close()

    return results

table_name = st.selectbox('Select a table:', test_table_names())
select_all_columns = st.button('See Data Table')


