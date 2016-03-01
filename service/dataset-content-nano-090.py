import bson
import pymongo
import json
from bson import ObjectId
from pymongo import MongoClient
import string
import tangelo

# is a value a number or a string? 
# from http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float-in-python

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def run(dbname,tablename):

    
    # Create an empty response object.
    response = {}
    response['data'] = []
    response['header'] = []

    # open a connection and copy the entire database
    connection = MongoClient('localhost', 27017)
    db = connection[dbname]
    dataset_collection = db[tablename]

    # build query for . 
    query = {}
    table = dataset_collection.find(query,{'_id':0})

    # copy but ignore sub-dictionaries

    rows = []
    for thisrow in table:
        row = {}

        # copy all of the regular (non-dictionary) valuws across
        for x in thisrow:
            if not isinstance(thisrow[x],dict):
                row[x] =thisrow[x]

        # now bring over any important, special values which were embedded in dictionaries
        row['dashboard_data_source'] = thisrow['metadata']['dashboard_data_source']
        row['UpdatedAt'] = thisrow['Nanomaterial_JOIN']['UpdatedAt']
        row['DataSource'] = thisrow['Nanomaterial_JOIN']['DataSource']
        row['CuratedBy'] = thisrow['Nanomaterial_JOIN']['CuratedBy']
        row['DataSourceURL'] = thisrow['Nanomaterial_JOIN']['DataSourceURL']
        row['source_pdf'] = 1 if  thisrow['metadata']['dashboard_data_source'] == 'pdf_extraction' else 0 
        row['source_nano_db'] = 1 if thisrow['metadata']['dashboard_data_source'] == 'nano_database' else 0         

        rows.append(row)

    # copy out of the mongodb cursor type to a python list
    for x in rows:
        # many of the attributes we test for are not in all the particles, so fill in the table here using conditional expressions.  The value
        # is passed through if it exists, otherwise it is not. 
        x['Mean Hydrodynamic Diameter'] = x['Mean Hydrodynamic Diameter'] if 'Mean Hydrodynamic Diameter' in x else 0
        x['Molecular Type'] = x['Molecular Type'] if 'Molecular Type' in x else ''
        x['Material Type'] = x['Material Type'] if 'Material Type' in x else ''
        x['Product Name'] = x['Product Name'] if 'Product Name' in x else ''
        x['Mean Hydrodynamic Diameter'] = x['Mean Hydrodynamic Diameter'] if 'Mean Hydrodynamic Diameter' in x else 0
        x['Mean Primary Particle Size'] = x['Mean Primary Particle Size'] if 'Mean Primary Particle Size' in x else 0
        x['Component Molecular Weight'] = x['Component Molecular Weight'] if 'Component Molecular Weight' in x else 0
        x['Molecular Weight'] = x['Molecular Weight'] if 'Molecular Weight' in x else 0
        x['Lambda Max'] = x['Lambda Max'] if 'Lambda Max' in x else 0
        x['Bulk Density'] = x['Bulk Density'] if 'Bulk Density' in x else 0
        x['Primary Particle Size'] = x['Primary Particle Size'] if 'Primary Particle Size' in x else 0
        x['Specific Surface Area'] = x['Specific Surface Area'] if 'Specific Surface Area' in x else 0
        x['Zeta Potential'] = x['Zeta Potential'] if 'Zeta Potential' in x else 0

        x['2D Dimensionality'] = 1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='2D') else 0 
        x['3D Dimensionality'] = 1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='3D') else 0    
#        x['Null Dimensionality'] = 1 if (('Nanoscale Dimensionality' in x) and x['Nanoscale Dimensionality'] =='Null') else 0    
        x['Neutral Polarity']   = 1 if (u'Polarity' in x)  and ((x[u'Polarity'] =='Neutral') or (x[u'Polarity'] =='Neutral ')) else 0  
        x['Positive Polarity']   = 1 if (u'Polarity' in x) and (x[u'Polarity'] =='Positive') else 0  
        x['Negative Polarity']   = 1 if (u'Polarity' in x) and (x[u'Polarity'] =='Negative') else 0  
        #x['Neutral Polarity'] = 1 if x['Polarity'] =='Neutral' else 0
        #x['Positive Polarity'] = 1 if x['Polarity'] =='Potitive' else 0
        #x['Negative Polarity'] = 1 if x['Polarity'] =='Negative' else 0

        x['Metal'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Metal' ) else 0
        x['Metal Oxide'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Metal Oxide') else 0
        x['Polymer'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Polymer') else 0
        x['Carbohydrate'] = 1  if 'Material Type' in x and ( x['Material Type'] ==u'Carbohydrate') else 0
        x['Group Ii-Vi'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Group Ii-Vi' ) else 0
        x['Group Iv - Non C'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Group Iv - Non C' ) else 0
        x['Dendrimer'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Dendrimer' ) else 0
        x['Lipid'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Lipid' ) else 0
        x['Protein'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Protein' ) else 0
        x['Nucleic Acid'] = 1  if 'Material Type' in x and ( x['Material Type'] =='Nucleic Acid' ) else 0

        # look at state (has six different categorical values)
        x['Agglomerated'] = 1  if 'State' in x and ( x['State'] =='Agglomerated' ) else 0
        x['Aggregated'] = 1  if 'State' in x and ( x['State'] =='Aggregated' ) else 0
        x['Aggreg-Agglom'] = 1  if 'State' in x and ( x['State'] =='Aggregated/Agglomerated' ) else 0
        x['Not Aggreg-Agglom'] = 1  if 'State' in x and ( x['State'] =='Not Aggregated/Agglomerated' ) else 0

        # special cleaning for Molecular Identity - usually a string, but at least one number value exists
        x['Molecular Identity'] = str(x['Molecular Identity']) if 'Molecular Identity' in x  else ''

        # special cleaning for 'Purity Of' because it has numeric and character and inconsistent values
        x['Purity99+'] = 1 if ('Purity Of' in x and x['Purity Of']>=99) else 0
        x['UltraPure'] = 1 if 'Purity Of' in x and ((x['Purity Of'] == 'Ultrapure') or (x['Purity Of']=='Ultra Pure')) else 0

        # input database has false/true instead of 0/1 needed for UpSet
        x['IsCrystalline'] = 1 if (x['IsCrystalline']) else 0
        x['Polycrystalline'] = 1 if (x['Polycrystalline']) else 0
        x['SingleCrystal'] = 1 if (x['SingleCrystal']) else 0        
        x['Monoclinic'] = 1 if (x['Monoclinic']) else 0  
      
        # return cleaned tuple
        response['data'].append(x)

    table.rewind()

    # find the column headers
    for col in table[0]:
        if not isinstance(col,dict):
            response['header'].append(col)


    #-------------------------------------------------------------------------
    # now look in the PDF scrapint collection and bring these records in
    #-------------------------------------------------------------------------

    # open a connection and copy the entire database
    dataset_collection = db['pdf_output_processed']

    # build query for Phoenix. focus returns on middle east countries
    query = {};
    table = dataset_collection.find(query,{'_id':0})

    # copy out of the mongodb cursor type to a python list
    for x in table:
        # now add in binary sets.  In each case, the identify of a multi-valued field is tested and turned
        # into an additional binary set attribute
        x['Aromatic'] = 1 if (x['Aromatic']=='yes') else 0
        x['VHQ-R subset'] = 1 if (x['VHQ-R subset']=='yes') else 0
        x['Macrocyclic'] = 1 if (x['Macrocyclic']=='yes') else 0
        x['VHQ-R subset'] = 1 if (x['VHQ-R subset']=='yes') else 0
        x['source_pdf'] = 1 if  x['metadata']['dashboard_data_source'] == 'pdf_extraction' else 0 
        x['source_nano_db'] = 1 if x['metadata']['dashboard_data_source'] == 'nano_database' else 0     
  
        # add the extended row to the dataset returned for analysis
        response['data'].append(x)

    table.rewind()

    # find the column headers
    for col in table[0]:
        response['header'].append(col)
   
   
    print "response:",response
    # convert to string to pass through URL callback
    #tangelo.log(str(response))
    return json.dumps(response)
