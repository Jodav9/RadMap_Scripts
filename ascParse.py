import arcpy,csv

table =r'/home/john_davis/Downloads/srtm_12_05.asc'
outfile = r'/home/john_davis/Desktop/ascTable.txt'

#--first lets make a list of all of the fields in the table
fields = arcpy.ListFields(table)
field_names = [field.name for field in fields]

with open(outfile,'wb') as f:
    dw = csv.DictWriter(f,field_names)
    #--write all field names to the output file
    dw.writeheader()

    #--now we make the search cursor that will iterate through the rows of the table
    with arcpy.da.SearchCursor(table,field_names) as cursor:
        for row in cursor:
            dw.writerow(dict(zip(field_names,row)))