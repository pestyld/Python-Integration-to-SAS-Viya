import swat

## Personal module to connect to CAS. Will not work in other environments
from casConnect import connect_to_cas 

## Connect to the CAS server
conn = connect_to_cas()

## Load the data source file into memory
conn.loadTable(path = 'warranty_demo.parquet', caslib = 'casuser',   ## Specify the data source file and caslib location
               casOut = {'name':'warranty_demo',                     ## Specify the output CAS table information
                         'caslib':'casuser',
                         'replace':True})

## Reference the CAS table
castbl = conn.CASTable('WARRANTY_DEMO', caslib = 'casuser')


##
## Rename and columns from the original table
##

## Get a list of the current raw column names
df = castbl.columnInfo()['ColumnInfo']
castableColumnNames = df.loc[:,'Column'].to_list()

## Specify the name of the new columns
newColumnNames = [
            'campaign_type','selling_dealer','vehicle_class','platform','trim_level','make','model_year','customer_country','engine_model',
            'vehicle_assembly_plant','repairing_division','repairing_state_province','repairing_region','repairing_country','repairing_dealer',
            'primary_labor_group','primary_labor_description','total_claim_count','claim_repair_start_date','claim_repair_end_date','claim_processed_date',
            'claim_submitted_date','primary_labor_code','defect_key','primary_labor_group_code','primary_replaced__material_id',
            'primary_replaced_material_group_code','warranty_claim_id','usage_value','gross_claim_amount','gross_labor_amount','gross_material_amount',
            'gross_other_amount','product_unit_id','product_model','product_unit_assembly_date','service_year_date','ship_date','ship_year','defect_code',
            'latitude','longitude'
]

## Create a to select the specific the current column name, and the name to rename it to.
renameColumns = []
for i in range(len(castableColumnNames)):
    colToRename = {'name' : castableColumnNames[i], 'rename' : newColumnNames[i]}
    renameColumns.append(colToRename)

## List of columns to drop
dropColumns = ['defect_code','repairing_division','usage_value','campaign_type','customer_country','ship_year',
               'product_unit_assembly_date','primary_replaced_material_group_code','primary_labor_group_code',
               'selling_dealer','vehicle_class','ship_date', 'total_claim_count']

## Rename and drop columns
castbl.alterTable(columns = renameColumns, 
                  drop = dropColumns)

# ## Restructure column order
# newColumnOrder = ['warranty_claim_id', 'make', 'product_model', 'model_year', 'platform', 'trim_level', 'engine_model','vehicle_assembly_plant',
#                   'primary_labor_group', 'primary_labor_description', 'primary_labor_code', 'defect_key','primary_replaced__material_id', 'gross_claim_amount', 
#                   'gross_labor_amount', 'gross_material_amount', 'gross_other_amount','product_unit_id', 'repairing_state_province', 'repairing_region', 
#                   'repairing_country', 'repairing_dealer', 'latitude', 'longitude', 'claim_repair_start_date', 'claim_repair_end_date', 'claim_processed_date', 
#                   'claim_submitted_date','service_year_date']
# castbl.alterTable(columnOrder = newColumnOrder)


##
## Prepare the final CAS table
##

## Create new columns and name the new table warranty_final
(castbl
 .eval("days_to_repair = claim_repair_end_date - claim_repair_start_date", inplace = False)
 .eval("days_to_process_claim = claim_processed_date - claim_submitted_date", inplace = False)
 .eval("primary_labor_item = scan(primary_labor_description,1,'–:-','r')", inplace = False)
 .eval("car_serviced = ifc(service_year_date = ., 'Not Serviced', 'Serviced')", inplace = False)
 .eval("car_id = catx(' ',model_year, make, product_model, platform)", inplace = False)
 .copyTable(casout = {'name':'warranty_final', 'caslib':'casuser', 'replace':True})
)


## Reference the new CAS table
finalTbl = conn.CASTable('WARRANTY_FINAL', caslib = 'casuser')

##
## Add column labels
##

## Create a dictionary with the column name and the label
addLabelsToColumns = [{'name':colname, 'label':colname.replace('_',' ').title().replace('Id','ID')} for colname in finalTbl.columns.to_list()]

## Apply the new labels
finalTbl.alterTable(columns = addLabelsToColumns)

##
## Save the CAS table as a data source file
##
finalTbl.save(name='warranty_final.sashdat', caslib = 'casuser', replace = True)

## Drop the current reporting table
conn.dropTable('warranty_final', caslib = 'casuser', quiet = True)

##
## Terminate the CAS connection
##
conn.terminate()