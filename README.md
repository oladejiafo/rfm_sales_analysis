
# <p align="center"> SALES ANALYSIS WITH RFM</p>
## <p align="center">RFM Analysis of Sales Data</p>

## About The Dataset
### Context
Sales analytics is the practice of generating insights from sales data, trends, and metrics to set targets and forecast future sales performance. Sales analysis is mining your data to evaluate the performance of your sales team against its goals. It provides insights about the top performing and underperforming products/services, the problems in selling and market opportunities, sales forecasting, and sales activities that generate revenue.

### Data Source:
The data was downloaded from Kaggle, curtesy of [KNIGHT BEARR](https://www.kaggle.com/datasets/knightbearr/sales-product-data).

The project implementation was inspired by [Angelina Frimpong’s](https://www.youtube.com/watch?v=O2hlHzehZb0) YouTube teaching.

### Data Attributes:
*	Order ID - An Order ID is the number system that Amazon uses exclusively to keep track of orders. Each order receives its own Order ID that will not be duplicated. This number can be useful to the seller when attempting to find out certain details about an order such as shipment date or status.
*	Product - The product that have been sold.
*	Quantity Ordered - Ordered Quantity is the total item quantity ordered in the initial order (without any changes).
*	Price Each - The price of each products.
*	Order Date - This is the date the customer is requesting the order be shipped.
*	Purchase Address - The purchase order is prepared by the buyer, often through a purchasing department. The purchase order, or PO, usually includes a PO number, which is useful in matching shipments with purchases; a shipping date; billing address; shipping address; and the request items, quantities and price.

The dataset was a CSV file, which came in 12 files, each representing each month. There were a total of 186,851 records.
 
Here is a peep look at the dataset structure:
![image](https://user-images.githubusercontent.com/69392408/208480939-bdab85b7-c55c-4e61-a279-dd2fc7a53d47.png)


## Objective Of The Analysis
The main objective of this sales analysis is to evaluate a the sales trends to know the strengths and weaknesses of each KPI. 


### Key Questions To Answer:
*	Q: What was the best month for sales? How much was earned that month?
*	Q: What was the best selling product?
*	Q: What City had the highest number of sales? 
*	Q: What products were bought together?
*	Q: Category and percentage of customers bought Recently, Frequently and How much do they buy (RFM)? 

### Data Analytic Tool
For this project, Python, SQL - CTE (via BigQuery platform) and Tableau were used.

##  Data Preparations
The downloaded dataset was merged into 1 file using a python script and named “sales_data.csv”.

The csv file was imported into Google’s cloud-based BigQuery, where SQL was used to inspect and clean the dataset first before analysis began. The following are some of the cleaning done:
*	*Checking the records, there were 545 empty rows. These were removed.*
*	*Duplicates were checked. Since OrderID can possibly be repeated if  different products were bought together, these had to be cheched based on a combination of OrderID, ProductName, Order Date. None was found.*
*	*Finally, Column titles were changed to something easy to work with.*


### Data Cleaning
The SQL codes used to clean these records are:

#### Python Code
```
####merge_data.py####
##Import modules
import pandas as pd
import numpy as np
import os

# let's make a list compression for all the data in the folder
files = [file for file in os.listdir('data/')] 

# let's make a pandas DataFrame
all_data = pd.DataFrame()

# makes a loop for concat the data
for file in files:
    data = pd.read_csv("data/" + file)
    all_data = pd.concat([all_data, data])

# export all data to csv    
all_data.to_csv("data/sales_data.csv", index=False)
```

#### SQL Codes Using BigQuery Platform

```
-- Rename  fields
ALTER TABLE `sales-371417.sales_data.sales` RENAME COLUMN `Order ID` TO OrderID;

ALTER TABLE `sales-371417.sales_data.sales` RENAME COLUMN `Product` TO ProductName;

ALTER TABLE `sales-371417.sales_data.sales` RENAME COLUMN `Quantity Ordered` TO `Qnty_Ordered`;

ALTER TABLE `sales-371417.sales_data.sales` RENAME COLUMN `Price Each` TO `Unit_Price`;

ALTER TABLE `sales-371417.sales_data.sales` RENAME COLUMN `Order Date` TO `Order_Date`;

ALTER TABLE `sales-371417.sales_data.sales` RENAME COLUMN `Purchase Address` TO `Address`;
```

```
-- Inspection
-- -- Total Records 186,851
SELECT * FROM `sales-371417.sales_data.sales`

-- -- CHECK EMPTY ROWS -- 545 empty
SELECT * FROM `sales-371417.sales_data.sales` Where OrderID IS NULL
```


```
-- REMOVE EMPTY Rows
-- Total clean records 185,950
WITH no_empty AS
(
  SELECT * FROM `sales-371417.sales_data.sales` Where OrderID IS NOT NULL AND OrderID != 'Order ID'
)
-- -- Checking but no actual duplicates
SELECT * EXCEPT(row_number) 
FROM (
  SELECT *,ROW_NUMBER() OVER (PARTITION BY OrderID) row_number FROM no_empty ORDER BY OrderId
) WHERE row_number = 2

```

```
-- -- -- Inspect Data More
-- 19 Distinct Product
SELECT distinct ProductName FROM `sales-371417.sales_data.clean_sales`;
-- --178,437 distinct transactions
SELECT distinct OrderID FROM `sales-371417.sales_data.clean_sales`;
-- --140,787 distinct users via addresses
SELECT distinct Address FROM `sales-371417.sales_data.clean_sales`;
-- -- 8 unique states;
SELECT distinct state FROM `sales-371417.sales_data.clean_sales`; 
--- -- 9 unique cities
SELECT distinct city FROM `sales-371417.sales_data.clean_sales`; 
```


## Data Processing & Analysis

### Data Preparations
We need to generate so extra columns to make the data rich. 
These are:
1.	*Unique Identifier (CustomerID)*
2.	*Total Amount Spent*
3.	*Year*
4.	*Month*
5.	*City*
6.	*State*

#### Using SQL CTE
```
With wt_total AS
(
  --Calculate total spent per transaction
  SELECT 
  *,
  (CAST(Qnty_Ordered as INT64) * CAST(Unit_Price as FLOAT64)) as Amt_Spent
  FROM `sales-371417.sales_data.clean_sales` 
),
wt_period AS 
(
  --Extract Date into Month and Year
  SELECT 
  *,
  EXTRACT(YEAR FROM DATE(PARSE_DATE('%m/%d/%y',split(Order_Date, ' ')[offset(0)]))) as Year,
  FORMAT_DATETIME("%B",DATE(PARSE_DATE('%m/%d/%y',split(Order_Date, ' ')[offset(0)]))) as Month 
  FROM wt_total
),
new_t as
(
  --Split Address to City and State
SELECT 
ROW_NUMBER() OVER(ORDER BY (SELECT 1)) AS ID,
*,
split(Address, ',')[offset(0)] as street,
split(Address, ',')[offset(1)] as city,
REVERSE(split(REVERSE(Address),' ')[offset(1)]) as state,
REVERSE(split(REVERSE(Address),' ')[offset(0)]) as ZIP
FROM wt_period
)
select * from new_t;
With wt_total AS
(
  --Calculate total spent per transaction
  SELECT 
  *,
  (CAST(Qnty_Ordered as INT64) * CAST(Unit_Price as FLOAT64)) as Amt_Spent

```

Here is the output:

![image](https://user-images.githubusercontent.com/69392408/208481086-0c580008-a231-46b5-a1ef-a183866bd893.png)


### Data Analysis

Now let get some insights from the data.

#### Insights

```
-- --Best selling Month 
SELECT Month,Year, sum(Amt_Spent) Revenue, count(OrderID) Frequency FROM `sales-371417.sales_data.processed_sales` Group By Month, Year order by Year, Revenue desc;
```
![image](https://user-images.githubusercontent.com/69392408/208481163-b6ed6891-9ad0-4546-b0dc-aa2fe2a78def.png)
 
#### Observation:
December has highest sales, while January has lowest

```
---- Sales per state
SELECT State, SUM(Amt_Spent) Revenue FROM `sales-371417.sales_data.processed_sales` Group By State order by Revenue desc;
```
![image](https://user-images.githubusercontent.com/69392408/208481240-165f3a8e-3ef3-4c4d-a1af-74974d2bfad4.png)
 
#### Observation:
CA – California State has the highest revenue
And San Francisco the highest City.

```
-- --Best selling Product 
SELECT ProductName, sum(Amt_Spent) Revenue FROM `sales-371417.sales_data.processed_sales` Group By ProductName order by Revenue desc;
```
 
![image](https://user-images.githubusercontent.com/69392408/208481299-c497b2ad-8960-449d-962b-acfdea133bbd.png)

#### Observation:
MacbookPro has highest sales, while AAA Batteries has lowest


```
-- -- Operations only in January 2020, and 12 months in 2019 years
SELECT distinct Month FROM `sales-371417.sales_data.processed_sales` Where Year =2019;
```


``` 
-- -- operations only in 2019, 2020 years
SELECT distinct Year FROM `sales-371417.sales_data.processed_sales`; 
```

```
-- Items Bought Together
SELECT a.ProductName AS original_Product, b.ProductName AS bought_with, count(*) as times_bought_together
  FROM `sales-371417.sales_data.processed_sales` AS a
  INNER JOIN `sales-371417.sales_data.processed_sales` AS b ON a.OrderID = b.OrderID
  AND a.ProductName != b.ProductName
 GROUP BY a.ProductName, b.ProductName;
```
![image](https://user-images.githubusercontent.com/69392408/208481388-d50a482e-1bc1-4131-93fb-87c606a0578c.png)


**Next we generate the RFM.**

RFM means Recency, Frequency and Monetary. This used to segment customers according to how recently they still bought products, how frequently the come back, how much they often spend. These will help us know which customers are loyal and those we are loosing.

In this analysis, we have will categorize customers into 5 levels:
*	*Super Customers*
*	*Loyal Customers*
*	*Potential Loyalists*
*	*New Customers and*
*	*Churning Customers*

To achieve this, we need to derive some more columns from our dataset. These are:
*	*Recency*
*	*Frequency*
*	*Monetary*
*	*RFM Scores*
*	*RFM Levels*

#### Using a complex SQL CTE
```
--RFM 
WITH rfm AS
(
  --RFM for best customer
SELECT 
Address, 
sum(Amt_Spent) Monetary,
Avg(Amt_Spent) Avg_Revenue,
count(OrderID) Frequency,
max(PARSE_DATE('%m/%d/%y',split(Order_Date, ' ')[offset(0)])) Last_Order_Date,
(SELECT max(PARSE_DATE('%m/%d/%y',split(Order_Date, ' ')[offset(0)])) FROM `sales-371417.sales_data.processed_sales`) Max_Order_Date,
DATE_DIFF(
  (SELECT max(PARSE_DATE('%m/%d/%y',split(Order_Date, ' ')[offset(0)])) FROM `sales-371417.sales_data.processed_sales`),
  max(PARSE_DATE('%m/%d/%y',split(Order_Date, ' ')[offset(0)])), 
  Day
) Recency
FROM `sales-371417.sales_data.processed_sales` 
Group By Address order by Monetary desc
),
rfm_tile AS
(
-- Group customer patronage into 3
SELECT 
*,
NTILE(3) OVER(ORDER BY rfm.Recency desc) as rfm_rec_tile,
NTILE(3) OVER(ORDER BY rfm.Frequency ) as rfm_freq_tile,
NTILE(3) OVER(ORDER BY rfm.Monetary ) as rfm_mone_tile
from rfm
),
rfm_scores AS
(
  --Create RFM Scores
SELECT 
*, 
(rfm_rec_tile + rfm_freq_tile + rfm_mone_tile) as rfm_val,
CONCAT(CAST(rfm_rec_tile as string) , cast(rfm_freq_tile as String) , cast(rfm_mone_tile as String)) as rfm_score
from rfm_tile
ORDER BY rfm_score desc
),
rfm_levels AS 
(
-- Segment into levels
SELECT distinct Address,
Recency,Frequency,Monetary, rfm_rec_tile, rfm_freq_tile, rfm_mone_tile,
CASE
  WHEN rfm_score IN ('333','332','323','322', '223') THEN 'Super Customers' 
  WHEN rfm_score IN ('221','331','321','233','232','231','222') THEN 'Loyal Customers' 
  WHEN rfm_score IN ('213','212','132','133','123','122') THEN 'Potential Loyalist'
  WHEN rfm_score IN ('313','312','311','211') THEN 'New Customers'  
  ELSE  
  'Churning Customers'
END as rfm_level
FROM rfm_scores
),
final AS 
(
-- -- Generate Unique Customer ID
SELECT ROW_NUMBER() OVER(ORDER BY (SELECT 1)) AS ID, CONCAT('CN',CAST((RAND() * (899999) + 100000) as int))  as CustomerID, * FROM rfm_levels
)
SELECT * FROM final; 
```

#### SQL Output:
![image](https://user-images.githubusercontent.com/69392408/208481469-af2132d1-1241-423a-b3f3-5a7d395443cd.png)


```
-- count per level:
SELECT rfm_level, count(*) as count FROM rfm_levels GROUP BY rfm_level
```
![image](https://user-images.githubusercontent.com/69392408/208481514-9f29794c-0220-4bc1-9f93-6aab220ae964.png)
 

```
-- --Calculate average values for each RFM_Level, and return a size of each segment:
SELECT rfm_level, round(avg(Recency),2) as Recency_Mean, round(avg(Frequency),2) as Frequency_Mean, round(avg(Monetary),2) as Monetary_Mean,  count(*) as count FROM rfm_levels GROUP BY rfm_level order by Frequency_Mean desc

```
![image](https://user-images.githubusercontent.com/69392408/208481572-ceff60e1-9890-4f12-a962-3565a828a651.png)


## Data Visualization

### Sales Dashboard
 ![Sales Dashboard](https://user-images.githubusercontent.com/69392408/208370011-4778a9b1-8d5a-4f5e-b4f5-1b6b7954ee5d.png)


### RFM Dashboard
 ![RFM Dashboard](https://user-images.githubusercontent.com/69392408/208370017-f9f0a9e0-58d8-454b-98fd-e97bfca27cec.png)


[More Visualization on Tableau here](https://public.tableau.com/app/profile/oladeji.afolabi/viz/SalesDataAnalyticsWithRFM/RFMDashboard_1)

![Sales Distributions Over Cities](https://user-images.githubusercontent.com/69392408/208370252-51f71074-9581-4658-8226-71ab0c872ce2.png)

![Sales Distributions Over Months](https://user-images.githubusercontent.com/69392408/208370349-6ec7567d-2b0d-4663-b872-65e36c022730.png)

![Sales Distributions Over Products](https://user-images.githubusercontent.com/69392408/208370348-1004d8c3-46d7-4e1c-934c-a16158cce7d3.png)

![Sales Distributions](https://user-images.githubusercontent.com/69392408/208370361-929c0aa7-e824-4cd5-a584-b60ffb11f90b.png)

![Products Bought Together](https://user-images.githubusercontent.com/69392408/208370474-c51ccc19-217f-4bc5-ba52-9adb66de95bb.png)

 

 

 


 

 


 

