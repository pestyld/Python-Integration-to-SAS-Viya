## DESCRIPTION: The following functions create two demo tables in the casuser caslib


####################################################
## Create a products table with n number of rows  ##
####################################################
def createProducts(connection,nRows):

## DATA Step code to create the demo table
    createOrdersData='''
data casuser.products;
   length Product varchar(10) DiscountCode varchar(10) Return varchar(3);
   call streaminit(99);
    do i=1 to {};
    *StoreID*;
        StoreID=int(rand('CHISQ', 20));

    *Country*;
        *rand_Countries=rand("table",);

    *product*;
        array products_groups[4] varchar(10) _temporary_ ("Sweatshirt","Pants","Shirts","Hats");   
        rand_Products=rand("table",.2,.3,.4,.1);
        Product=products_groups[rand_Products];

    *product price*;
    array products_price[4] _temporary_ (10.99,8.99,7.99,4.99);
        Price=products_price[rand_Products];
  
    *product cost*;
    array products_cost[4] _temporary_ (1.99,1.49,1.99,.99);      
        Cost=products_cost[rand_Products];
    
    *quantity*;
        Quantity=ceil(rand('BINOM', 0.75, 10));
    
    *return*;
    rand_return=rand('uniform',0,1);
        if (product="Sweatshirt" and rand_return<.02) then Return="Yes";
        else if (product="Pants" and rand_return<.05) then Return="Yes";
        else if (product="Shirts" and rand_return<.08) then Return="Yes";
        else if (product="Hats" and rand_return<.01) then Return="Yes";
        else Return="";

    *discount code*;
    rand_discountValue=rand("table",.3,.15,.25,.09,.01,.15,.05);
    rand_discountApplied=rand('uniform',0,1);
    array products_discounts[7] varchar(10) _temporary_ ("TC10","BB20","TENOFF","EMP50","FMDISCOUNT","SPC","FREEDEAL");  
    if rand_DiscountAPplied <.20 then DiscountCode=products_discounts[rand_discountValue];
        else DiscountCode="";

     output;
       
    end;
    
    drop i rand:;
run;
'''.format(nRows)

## Execute the data step
    connection.runCode(code=createOrdersData)

## Print the results of the create table
    result = connection.tableInfo(caslib="casuser", name="products")["TableInfo"].loc[:,["Name","Rows"]]
    rows=result.loc[0,"Rows"]
    tblName=result.loc[0,"Name"]
    print("The {} table has been created with {:,} rows in the CASUSER caslib".format(tblName,rows))

## Specify the input table information
    inputTbl=dict(name="products", caslib="casuser")

## Specify the name of the data source file and caslib to write to
    outFileName="products.csv"
    outFileCaslib="casuser"

## Save the in-memory table as a physical file
    connection.save(table=inputTbl, name=outFileName, caslib=outFileCaslib, replace=True)

## Drop the in-memory table
    connection.dropTable(name="products", caslib="casuser")

## Function complete
    print("NOTE: File {} created successfully with {:,} rows.".format(outFileName,rows))




####################################################
## Create a discount lookup table in CAS          ##
####################################################
def createDiscountData(connection):
    createDiscountData='''
data casuser.discount_dim; 
    length Code varchar(10);
    retain i 0;
    do Code="TC10","BB20","TENOFF","EMP50","FMDISCOUNT","SPC","FREEDEAL";
        i+1;
        array products_discounts[7] _temporary_ (10,20,10,50,25,35,100); 
        DiscountValue=products_discounts[i];
        array disc_desc[7] varchar(65) _temporary_ ("TV Commercial Deal for 10% off",
                                                    "TV Commercial Deal for 20% off",
                                                    "First Time Customer Order 10% Discount",
                                                    "Employee 50% Discount",
                                                    "FM Credit Card 25% Discount",
                                                    "Holiday Special 35% Discount",
                                                    "Free Discount. Use Occasionally for Customer Service"); 
        Description=disc_desc[i];
        output;
    end; 
    drop i;
run;
'''

## Execute the data step
    connection.runCode(code=createDiscountData, single="YES")

## Print the results of the create table
    result = connection.tableInfo(caslib="casuser", name="discount_dim")["TableInfo"].loc[:,["Name","Rows"]]
    rows=result.loc[0,"Rows"]
    tblName=result.loc[0,"Name"]
    print("The {} table has been created with {:,} rows in the CASUSER caslib".format(tblName,rows))

## Specify the input table information
    inputTbl=dict(name="discount_dim", caslib="casuser")

    ## Specify the name of the data source file and caslib to write to
    outFileName="discount_dim.sashdat"
    outFileCaslib="casuser"

## Save the in-memory table as a physical file
    connection.save(table=inputTbl,
        name=outFileName, caslib=outFileCaslib, replace=True)

    connection.dropTable(name="discount_dim", caslib="casuser")
    
## Function complete
    print("NOTE: File {} created successfully with {:,} rows.".format(outFileName,rows))