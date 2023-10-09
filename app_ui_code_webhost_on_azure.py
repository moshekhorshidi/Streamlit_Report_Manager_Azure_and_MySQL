#dependencies
import streamlit as st
import datetime
import pyodbc as db
import pandas as pd
import time
import requests

# ui function section 

# section 1 on ui

# UI info welcome text seggest by Moshe Khorshidi
st.title("your title doe users on webapp")
st.write("your text to users")
st.write("***Phone:your_phone_number , eMail: your_email_address***, ***LinkedIn:*** [My LinkedIn Profile 👋](your_linkedin_profile_url) ")

# information message to user on test connection on azure database
st.info("Users can be **offline and get un-updated data from azure server**, for better usage test your connection first.")

# test connection on azure database by user 
if st.button("Test Connection To Database Server", key = 1):
    
    try:
        
        conn_setup = check_conn()
        if conn_setup == True:
            progress_text = "Test Connection in progress. Please wait."
            my_bar = st.progress(0, text=progress_text)
            
            for percent_complete in range(100):
                time.sleep(0.05)
                my_bar.progress(percent_complete + 1, text=progress_text)
            my_bar.empty()
            st.success(f"Azure SQL Database session is **active**  :sunglasses: , time established:  **{datetime.datetime.now()}**", icon="✅")
            #cool snow effect not required 
            st.snow()

    except: 
            exception_message = '**Click F5 to reload page and Try to test connection again! Connection not active, user see not updated data (WebApp offline)**'
            st.info(exception_message)
    finally:
        # collect user data from here as user test connection, can implement anyware on app 
        collect_user_data()



# UI info on section 1 of the webapp
st.subheader("Section 1 - Database Exploration")
st.header("Azure Database Tables Exploration", divider='violet')
st.subheader("Select a table you want to explore Raw data on:")

st.write("Click **'See table names button'** to see tables to explore raw data on the database (**user can copy name with 'CTRL C' or 'Copy' action on mobile** )") 

if st.button("See Database tables names", key = 2):

    result = azure_table_names()

    if result.all:
        
        st.write("Table names on Azure datbase")
        st.write(result)
        # create a code snipp for analyst etc.. 
        TableNamesQueryText = """

            ***Azure SQL query snippet:***


                SELECT distinct 
                       t.name as "Table Name",
                       s.name as "Schema Name",
                       s.schema_id as "Schema ID"
                FROM sys.tables t inner join sys.schemas s
	                ON t.schema_id = s.schema_id
                where t.name not in('Customer', 'ErrorLog')
                and s.name = 'SalesLT'
                union 
                select name,
                      'SalesLT',
                       schema_id 
                from sys.views

            """
        st.write(TableNamesQueryText)
        st.button("Close table and code snipp", key = 3)
        
    else:
        
        data_container = st.empty()  # Create an empty container for better ui responde 
        data_container.info("No Data on this table: empty result")     


# see db tables raw data and query tables
#drop down list for user
options = st.selectbox('Choose table name to explore',
                         ('No Table name selected','CustomerInfo', 'ProductModel', 'ProductDescription', 'Product',
                          'ProductCategory', 'Address', 'CustomerAddress', 'SalesOrderDetail',
                          'SalesOrderHeader', 'ProductModelProductDescription'))
option_massege = st.write("Table to query: ", options) 
user_choosen_table = options

if st.button("Run query on table", key = 4): # implemet key = ? for app uniqe value but ui cant present same button and text 
    result = query_builder(user_choosen_table)
    st.write(result)
    if user_choosen_table != 'No Table name selected':
        st.write(f""" 
               
            ***Azure SQL query snippet:***
             
                select * from SalesLT.{user_choosen_table} order by 1 asc
                
                """)  

        st.button("Close table and code snipp", key = 5)
    else:
        st.button("Close user check")

   
# section 2 on ui - sql reports 

st.subheader("Section 2 - Company Database Reports")
st.header("Company Azure Database Reports", divider='violet')

st.subheader("Select your relevant report")
#drop down list for user
reports_options = st.selectbox(' ',
                         ('No report selected','Customer Ranking Report','Sales Person details','Product Revenue Report'
                          ,'Customers Taxes Report'))
reports_massege = st.write("Report Presented: ", reports_options) 
user_choosen_report = reports_options

if st.button("Execute Report"):
    if user_choosen_report == 'Customer Ranking Report':
        result = customer_ranking_report()
        st.write(result)
        # create a code snipp for analyst etc.. 
        query_text = """ 

                ***Azure SQL query snippet:***

            select 

                RANK() over (order by sum(sod.OrderQty) desc) as "Customer Ranking",
                cast(c.customerid as varchar(25)) as "Customer ID",
                c.CompanyName as "Company Name",
                CONCAT(FirstName,' ' ,LastName) as "Full Name",
                case when Title = 'Mr.' then 'M'
                     when Title = 'Ms.' then 'F'
                else null end as "Gender",
                count(soh.salesOrderID) as "Total Orders",
                sum(sod.OrderQty) as "Total Quentity Orderd",
		        round(sum(sod.linetotal),3) as "Total revenue from customer $" 

            from SalesLT.Customer c 
            LEFT JOIN SalesLT.CustomerAddress ca 
                ON c.customerid = ca.customerid
            LEFT JOIN SalesLT.SalesOrderHeader soh
                ON soh.customerid = c.customerid
            LEFT JOIN SalesLT.salesOrderDetail sod
                ON sod.salesOrderID = soh.salesOrderID
            group by c.customerid, Title , CONCAT(FirstName,' ' ,LastName), c.CompanyName
            having count(soh.salesOrderID) > 0 

                     """
        st.write(query_text)
        st.button("close reports")
    elif user_choosen_report == 'Sales Person details': # validate user selection for execution 
         result = Salesperson_info()
         st.write(result)
         st.write("""
                
            ***Azure SQL query snippet:***
                  
                select 	distinct 
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
                  
                    """)
         
         st.button("close reports")

    elif user_choosen_report == 'Product Revenue Report':
        result = Product_Revenue_Report()
        st.write(result)
        query_text = """ 

                ***Azure SQL query snippet:***

    
                    with report as (
                    
                    SELECT distinct
                    pc.name as "Category name",
                    p.name as "Detailed Product name",
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


                    select RANK() over ( order by "Total Revenue From product" desc ) AS "Detailed Product Revenue Rank", 
                              report.* 
                    from report 

                     """
        st.write(query_text)
        st.button("close reports")
    elif user_choosen_report == 'Customers Taxes Report':
        result = Customers_Taxes_Report()
        st.write(result)
        query_text = """ 

                ***Azure SQL query snippet:***

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
        st.write(query_text)
        st.button("Close reports") 

    else:
        # validation on user usage on app
         st.info("""
                 
                **Report not selected**
                 
                User guide check:

                1. Not empty selection or default value - "No report selected"
                2. Check if report was selected properly from list of reports
                3. try to test connection again
                 
                 """)
         st.button("Close user check")
         
         
      
st.subheader("Section 3 - Data Visualization")
st.header("Company Data Visualization", divider='violet')

st.subheader("Select your Vizz and click analyze visual")
#drop down list for user    
vizz_options = st.selectbox(' ',
                         ('No Vizz selected','Top Ranking Customers by Quentity Orderd','Top Ranking Customers by Revenue'))
vizz_massege = st.write("Vizz Presented: ", vizz_options) 
user_choosen_vizz = vizz_options

if st.button("Analyze Visual"):
    if user_choosen_vizz == 'Top Ranking Customers by Quentity Orderd':
        result = top_ranking_report_customers_qty()
        chart_data = result
        st.bar_chart(chart_data,x="Vizz Company Rank", y=["Total Quentity Orderd","Total Orders"])


        vizz_text = "***Note: Analyze top ranked customers by the total orders and quantity of products purchasing***"
        st.info(vizz_text)
        st.button("Close Selected Vizz")

    elif user_choosen_vizz == 'Top Ranking Customers by Revenue': # validate user selection for execution
        result = top_ranking_report_customers_revenue()
        chart_data = result
        st.bar_chart(chart_data,x="Vizz Company Rank", y="($) Total revenue from customer")


        vizz_text = "***Note: Analyze top ranked customers by the revenue inserted to the company***"
        st.info(vizz_text)
        st.button("Close Selected Vizz")
    
    else:
         # validation on user usage on app
         st.info("""
                 
                **Vizz not selected**
                 
                User guide check:

                1. Not empty selection or default value - "No Vizz selected"
                2. Check if report was selected properly from list of reports
                3. try to test connection again
                 
                 """)
         st.button("Close user check")



