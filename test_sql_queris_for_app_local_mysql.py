import database_connection_mysql as db
import pandas as pd
import streamlit as st 

def pay_report():

# Create a cursor object
    conn = db.conn
    cursor = conn.cursor()

# Execute a SQL query
    cursor.execute("""select concat(cust.first_name, ' ', cust.last_name) as "Full Name", 
		            CAST(cust.customer_id as SIGNED) as "Customer ID", cast(sum(amount) as float) as "Total Pay" 
                    from sakila.customer cust inner join sakila.payment pay
	                    on cust.customer_id = pay.customer_id
                    group by 1,2
                    limit 1 
                    """)

# Fetch the results
    pay_report_data_query_columns_names = [col[0] for col in cursor.description]
    pay_report_data_query_rows = cursor.fetchall()
    data = pd.DataFrame(pay_report_data_query_rows, columns = pay_report_data_query_columns_names)

 

    # Close the cursor and connection
    cursor.close()
    #conn.close()

    return data


def Actor_ranking_report():

# Create a cursor object
    conn = db.conn
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
    data = pd.DataFrame(Actor_ranking_report_query_rows, columns = Actor_ranking_report_query_columns_names)
 

    # Close the cursor and connection
    cursor.close()
    #conn.close()

    return data


def most_unrental_movies_per_Store_report():

# Create a cursor object
    conn = db.conn
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
    data = pd.DataFrame(most_unrental_movies_per_Store_report_query_rows, columns = most_unrental_movies_per_Store_report_query_columns_names)
 

    # Close the cursor and connection
    cursor.close()
    #conn.close()

    return data


def sakila_table_names():

# Create a cursor object
    conn = db.conn
    cursor = conn.cursor()

# Execute a SQL query
    cursor.execute(""" SELECT TABLE_NAME, TABLE_SCHEMA as DB_TABLE_SCHEMA FROM information_schema.tables where TABLE_SCHEMA = 'sakila' """)

# Fetch the results
    information_schema_table_columns_names = [col[0] for col in cursor.description]
    information_schema_table_data = cursor.fetchall()
    data = pd.DataFrame(information_schema_table_data, columns = information_schema_table_columns_names)
    

    # Close the cursor and connection
    cursor.close()

    return data


def query_builder(table):
    
    # Create a cursor object
    conn = db.conn
    cursor = conn.cursor()
    
    try: 

        cursor.execute(f""" select * from {table} order by 1 asc""")
        table_columns_names = [col[0] for col in cursor.description]
        table_data = cursor.fetchall()
        data = pd.DataFrame(table_data, columns = table_columns_names)
        
        return data

    except:
        
        st.subheader("""Need to insert a not empty/currect table name, or check if the table in the list of tables""")
        st.write(""" **Tables Names to copy:** actor, actor_info, address, category,
         city, country, customer, customer_list, film, film_actor, film_category,
         film_list, film_text, inventory, language, nicer_but_slower_film_list, payment,
         rental, sales_by_film_category, sales_by_store, staff, staff_list, store """)

    cursor.close()

        

    

def pay_report_chart():

# Create a cursor object
    conn = db.conn
    cursor = conn.cursor()

# Execute a SQL query
    data_for_chart = pay_report()
 

    # Close the cursor and connection
    cursor.close()
    #conn.close()

    return data_for_chart



res = pay_report()
print(res)