#dependencies
import streamlit as st
import datetime
import pyodbc as db
import pandas as pd
import time
import requests


# function define section

# engine conn config, calling conn for db connect and execute
def engine_connect():
    # conn config for connection 
    conn = db.connect(connection_string)
    return conn 

# check connection to server and database on azure or mysql
def check_conn():
    try:      
        db.connect(connection_string) # main connection string as a **global variabele** 
        return True
    except: 
        return False

# get user ip for data collecting app user usage, and monitoring
def get_user_ip():
    try:
        response = requests.get('https://ipinfo.io') # ip source 
        data = response.json()
        ip =  data.get('ip') # get key needed from JSON
        return str(ip)
    except Exception as ex:
        print(f"Error getting IP: {ex}") # exeption for ip get 
        return None

# collect user data and insert the data collected into the database for table named dbo.UserDataCollect on azure sql database
def collect_user_data():

    # db connect     
    conn = engine_connect()
    cursor = conn.cursor()

    # Insert the user's IP address 
    # get user ip 
    get_ip = get_user_ip()
    ip = get_ip

    # Get the generated UserID for the current user
    cursor.execute("SELECT NEWID()")
    get_user_id_from_engine = cursor.fetchone()
    chars_to_replace = "(),"
    user_id_to_str = str(get_user_id_from_engine)
    user_id_clean = ''.join(char for char in user_id_to_str if char not in chars_to_replace)
    
    # get current data for user visit app
    visit_date = datetime.date.today()

    # execute and insert data collected from user to the database
    cursor.execute(f"INSERT INTO dbo.UserDataCollect (UserID,UserIP,VisitDateTime) VALUES ({user_id_clean},'{ip}','{visit_date}')")
    conn.commit()
    #test user_ip collect
    #cursor.execute(f"INSERT INTO dbo.UserDataCollect (UserIP) values ()")
    #conn.commit()
    conn.close()



# getting all table names from azure sql database 
def azure_table_names():

# Create a database connection
    conn = engine_connect()

# SQL query code
    query = """ SELECT distinct t.name as "Table Name",
                s.name as "Schema Name",
                s.schema_id as "Schema ID"
                FROM sys.tables t inner join sys.schemas s
                ON t.schema_id = s.schema_id
                where t.name not in('Customer', 'ErrorLog')
                and s.name = 'SalesLT'
                union 
                select name, 'SalesLT' , schema_id 
                from sys.views v
                where v.object_id = 1314103722
                
                
            """

# Read and Fatch data
    query_data_read = pd.read_sql(query,conn)
    data = pd.DataFrame(query_data_read)

    return data

# user query execution from list of tables in database 
def query_builder(table):
    
    # Create a cursor object
    conn = engine_connect()

    try: 

        query = f""" select * from SalesLT.{table} order by 1 asc"""
        query_data_read = pd.read_sql(query,conn)
        data = pd.DataFrame(query_data_read)
        
        return data

    # validation on user usage on app
    except:
        
        st.info("""
                  User guide check: 
                  1. Not empty selection or default value - "No Table name selected"
                  2. Check if table was selected properly from list of tables
                  3. try to test connection again """)
        st.info(""" **Tables Names to copy:** CustomerInfo, ProductModel, ProductDescription, Product,
         ProductCategory, Address, CustomerAddress, SalesOrderDetail, SalesOrderHeader, ProductModelProductDescription""")
        
        return ""

# report for app
def customer_ranking_report():

    # Create a database connection
    conn = engine_connect()

    # SQL query code
    query = """

            select 
                cast(RANK() over (order by sum(sod.OrderQty) desc) as varchar(3) ) as "Customer Ranking",
                cast(c.customerid as varchar(25)) as "Customer ID",
                c.CompanyName as "Company Name",
                CONCAT(FirstName,' ' ,LastName) as "Full Name",
                case when Title = 'Mr.' then 'M'
                        when Title = 'Ms.' then 'F'
                    else null end as "Gender",
                    count(soh.salesOrderID) as "Total Orders",
                    sum(sod.OrderQty) as "Total Quentity Orderd",
                    round(sum(sod.linetotal),3) as "($) Total revenue from customer"
                    
            from SalesLT.Customer c 
            left join SalesLT.CustomerAddress ca 
                on c.customerid = ca.customerid
            left join SalesLT.SalesOrderHeader soh
                on soh.customerid = c.customerid
            left join SalesLT.salesOrderDetail sod
            ON sod.salesOrderID = soh.salesOrderID
            group by c.customerid, Title , CONCAT(FirstName,' ' ,LastName), c.CompanyName
            having count(soh.salesOrderID) > 0 

            """
    
    # Read and Fatch data
    query_data_read = pd.read_sql(query,conn)
    data = pd.DataFrame(query_data_read)

    return data

# report for app
def top_ranking_report_customers_qty():

    # Create a database connection
    conn = engine_connect()

    # SQL query code
    query = """

                      with report as(
  select          
                concat('(',cast(RANK() over (order by sum(sod.OrderQty) desc) as varchar(3) ), ')', ' ', c.CompanyName) as "Vizz Company Rank",
                cast(RANK() over (order by sum(sod.OrderQty) desc) as varchar(3)) as "Customer Ranking", 
                cast(c.customerid as varchar(25)) as "Customer ID",
                c.CompanyName as "Company Name",
                CONCAT(FirstName,' ' ,LastName) as "Full Name",
                case when Title = 'Mr.' then 'M'
                        when Title = 'Ms.' then 'F'
                    else null end as "Gender",
                    count(soh.salesOrderID) as "Total Orders",
                    sum(sod.OrderQty) as "Total Quentity Orderd",
                    round(sum(sod.linetotal),3) as "($) Total revenue from customer"
                    
            from SalesLT.Customer c 
            left join SalesLT.CustomerAddress ca 
                on c.customerid = ca.customerid
            left join SalesLT.SalesOrderHeader soh
                on soh.customerid = c.customerid
            left join SalesLT.salesOrderDetail sod
            ON sod.salesOrderID = soh.salesOrderID
            group by c.customerid, Title , CONCAT(FirstName,' ' ,LastName), c.CompanyName
            having count(soh.salesOrderID) > 0)

            select 
                   *
            from report 
            where "Customer Ranking" <10
            
            
            
            """
    
    # Read and Fatch data
    query_data_read = pd.read_sql(query,conn)
    data = pd.DataFrame(query_data_read)

    return data

# report for app
def top_ranking_report_customers_revenue():

    # Create a database connection
    conn = engine_connect()

    # SQL query code
    query = """

                      with report as(
  select          
                concat('(',cast(RANK() over (order by sum(sod.linetotal) desc) as varchar(3) ), ')', ' ', c.CompanyName) as "Vizz Company Rank",
                cast(RANK() over (order by sum(sod.linetotal) desc) as varchar(3)) as "Customer Ranking", 
                cast(c.customerid as varchar(25)) as "Customer ID",
                c.CompanyName as "Company Name",
                CONCAT(FirstName,' ' ,LastName) as "Full Name",
                case when Title = 'Mr.' then 'M'
                        when Title = 'Ms.' then 'F'
                    else null end as "Gender",
                    count(soh.salesOrderID) as "Total Orders",
                    sum(sod.OrderQty) as "Total Quentity Orderd",
                    round(sum(sod.linetotal),3) as "($) Total revenue from customer"
                    
            from SalesLT.Customer c 
            left join SalesLT.CustomerAddress ca 
                on c.customerid = ca.customerid
            left join SalesLT.SalesOrderHeader soh
                on soh.customerid = c.customerid
            left join SalesLT.salesOrderDetail sod
            ON sod.salesOrderID = soh.salesOrderID
            group by c.customerid, Title , CONCAT(FirstName,' ' ,LastName), c.CompanyName
            having count(soh.salesOrderID) > 0)

            select 
                   *
            from report 
            where "Customer Ranking" <10
            
            
            
            """
    
    # Read and Fatch data
    query_data_read = pd.read_sql(query,conn)
    data = pd.DataFrame(query_data_read)

    return data


# report for app
def Salesperson_info():

    # Create a database connection
    conn = engine_connect()

    # SQL query code
    query = """
                    

                    select  distinct 
                            rank() over (order by sum(totaldue) desc) as "Salesperson Ranking",
                            trim(' 1 2 3 4 5 6 7 8 9 0 ' from trim('\ ' from trim('adventure-works' FROM cust.salesperson))) as "Sales Person",
                            count(distinct cust.customerid) as "Total Customers Sale",
                            sum(totaldue) as "Total Revenue from Salesperson",
                            lag(sum(totaldue)) over (order by sum(totaldue) desc) - sum(totaldue) as "Salesperson Difference", 
                            round((lag(sum(totaldue)) over (order by sum(totaldue) desc) - sum(totaldue))*100.0/
                            lag(sum(totaldue)) over (order by sum(totaldue) desc),3) as " (%) Gap Percentage"
                    from SalesLT.Customer cust
                    inner join SalesLT.SalesOrderHeader sod 
                        on cust.customerid = sod.customerid
                    group by trim(' 1 2 3 4 5 6 7 8 9 0 ' from trim('\ ' from trim('adventure-works' FROM cust.salesperson)))

"""

# Read and Fatch data
    query_data_read = pd.read_sql(query,conn)
    data = pd.DataFrame(query_data_read)

    return data

# report for app
def Product_Revenue_Report():

    # Create a database connection
    conn = engine_connect()

    # SQL query code
    query = """
                    
                    with report as (
                    SELECT distinct
                    pc.name as "Category Name",
                    p.name as "Detailed Product Name",
                    listprice as "Product Price",
                    sum(orderqty) over ( partition by pc.name, p.name, listprice order by pc.name ) as "total qty orderd",
                    sum(TotalDue) over ( partition by pc.name, p.name, listprice order by pc.name ) as "($) Total Revenue From product"
                    FROM [SalesLT].[Product] as p
                    inner join [SalesLT].[ProductCategory] as pc
                           on p.ProductCategoryid = pc.ProductCategoryid
                    inner join [SalesLT].ProductModel as pm
                           on pm.ProductModelid = p.ProductModelid
                    inner join [SalesLT].ProductModelProductDescription as pmp
                           on pmp.ProductModelid = p.ProductModelid
                    inner join [SalesLT].SalesOrderDetail as sod
                           on sod.productid = p.productid
                    inner join [SalesLT].SalesOrderHeader soh  
                           on soh.salesorderid = sod.salesorderid ) 


                    select RANK() over ( order by "($) Total Revenue From product" desc ) AS "Detailed Product Revenue Rank", 
                              report.* 
                    from report 
                   

            """

# Read and Fatch data
    query_data_read = pd.read_sql(query,conn)
    data = pd.DataFrame(query_data_read)

    return data
    
# report for app
def Customers_Taxes_Report():

    # Create a database connection
    conn = engine_connect()

    # SQL query code
    query = """
                    

                    with Tax_Info as (

                        SELECT distinct
                        cast(sod.SalesOrderID as varchar(25) ) as "Sales Order ID",
                        c.CompanyName as "Company Name",
                        concat(c.firstname, ' ', c.lastname) as "Full Name",
                        TaxAmt as "Taxes Amount",
                        Freight as "Freight Amount",
                        sum(sod.OrderQty) over (partition by sod.SalesOrderID  order by sod.SalesOrderID ) as "Total Order Quentity"
                        FROM [SalesLT].[Product] as p
                        inner join [SalesLT].SalesOrderDetail as sod
                               on sod.productid = p.productid
                        inner join [SalesLT].SalesOrderHeader soh  
                               on soh.salesorderid = sod.salesorderid
                        inner join [SalesLT].customer c 
                                  on c.customerid = soh.customerid
                        ) 

                        select rank() over(order by "Taxes Amount" desc) as "Tax Ranking For Customer", Tax_Info.*
                        from Tax_Info 

"""

# Read and Fatch data
    query_data_read = pd.read_sql(query,conn)
    data = pd.DataFrame(query_data_read)

    return data