import streamlit as st
import test_sql_queris_for_app_local_mysql as sqa
import test_database_connection_mysql as db
import pandas as pd
import numpy as np

# Create three columns for open source if needed
#col1, col2, col3, col4 = st.columns(4)

st.title("Welcome to Moshe Khorshidi Sakila Database Query and reports UI :sunglasses:")
st.write("Streamlit application by Moshe Khorshidi.")

st.subheader("Section 1 - Database Exploration")
st.header("Sakilla Database Tables Exploration:", divider='rainbow')
st.subheader("Select the table you want to see and explore the data: ")

st.write("click to see tables names on database (**copy name with 'CTRL C'** )") 
if st.button("Table names"):
    result = sqa.sakila_table_names()
    st.write(result)

    st.button("close")

# see db tables raw data and query tables
table_name = st.text_input('Insert table name: ')


if st.button("Run query on table"):
    result = sqa.query_builder(table_name)
    st.write(result)
    st.button("close")


st.divider()

st.subheader("Section 2 - Database Reports")
st.header("Pay report:", divider='rainbow')
st.subheader(" The query that build the report: ")




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

if st.button("See bar_chart"):
    chart_data = sqa.pay_report_chart()
    st.bar_chart(chart_data, x = 'Full Name', y = 'Total Pay')
    st.button("Close Bar Chart")


if st.button("See Report"):

    result = sqa.pay_report()

    if result.empty:

        data_container = st.empty()  # Create an empty container
        data_container.write("No Data on this report:")     
    
    else:
        
        st.write("pay report data.")
        st.write(result)
        st.button("Close Report")

# Next query ----------------------------------------- Next query 

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


if st.button("Actor Ranking Report"):

    result = sqa.Actor_ranking_report()
    
    if result.empty:

        data_container = st.empty()  # Create an empty container
        data_container.write("No Data on this report:")     
    
    else:
        
        st.write("Actor Ranking Report.")
        st.write(result)
        st.button("Close Report")


# Next query ----------------------------------------- Next query 

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

if st.button("Most Unrental Movies Per Store"):

    result = sqa.most_unrental_movies_per_Store_report()
    
    
    if result.empty:

        data_container = st.empty()  # Create an empty container
        data_container.write("No Data on this report:")     
    
    else:
        
        st.write("Most Unrental Movies Per Store.")
        st.write(result)
        st.button("Close Report")
    


    


