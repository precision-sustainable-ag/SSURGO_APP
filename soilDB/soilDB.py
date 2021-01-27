import requests
import json
import xmltodict
import pprint
import pandas as pd

lat = "39.0321"
lon = "-76.8740"
lonLat = lon + " " + lat
url="https://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx"
#headers = {'content-type': 'application/soap+xml'}
headers = {'content-type': 'text/xml'}
body = """<?xml version="1.0" encoding="utf-8"?>
          <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:sdm="http://SDMDataAccess.nrcs.usda.gov/Tabular/SDMTabularService.asmx">
   <soap:Header/>
   <soap:Body>
      <sdm:RunQuery>
         <sdm:Query>SELECT co.cokey as cokey, ch.chkey as chkey, comppct_r as prcent, slope_r, slope_h as slope, hzname, hzdept_r as depth, awc_r as awc, 
                    claytotal_r as clay, silttotal_r as silt, sandtotal_r as sand, om_r as OM, dbthirdbar_r as dbthirdbar, wthirdbar_r as th33, 
                    (dbthirdbar_r-wthirdbar_r)/100 as bd FROM sacatalog sc
                    FULL OUTER JOIN legend lg  ON sc.areasymbol=lg.areasymbol
                    FULL OUTER JOIN mapunit mu ON lg.lkey=mu.lkey
                    FULL OUTER JOIN component co ON mu.mukey=co.mukey
                    FULL OUTER JOIN chorizon ch ON co.cokey=ch.cokey
                    FULL OUTER JOIN chtexturegrp ctg ON ch.chkey=ctg.chkey
                    FULL OUTER JOIN chtexture ct ON ctg.chtgkey=ct.chtgkey
                    FULL OUTER JOIN copmgrp pmg ON co.cokey=pmg.cokey
                    FULL OUTER JOIN corestrictions rt ON co.cokey=rt.cokey
                    WHERE mu.mukey IN (SELECT * from SDA_Get_Mukey_from_intersection_with_WktWgs84('point(""" + lonLat + """)')) order by co.cokey, ch.chkey, prcent, depth
        </sdm:Query>
      </sdm:RunQuery>
   </soap:Body>
</soap:Envelope>"""

response = requests.post(url,data=body,headers=headers)
print("###############################################\n")
# Put query results in dictionary format
my_dict = xmltodict.parse(response.content)

# Convert from dictionary to dataframe format
soil_df = pd.DataFrame.from_dict(my_dict['soap:Envelope']['soap:Body']['RunQueryResponse']['RunQueryResult']['diffgr:diffgram']['NewDataSet']['Table'])

# Drop columns where all values are None or NaN
soil_df = soil_df.dropna(axis=1, how='all')
soil_df = soil_df[soil_df.chkey.notnull()]

# Drop unecessary columns
soil_df = soil_df.drop(['@diffgr:id', '@msdata:rowOrder', '@diffgr:hasChanges'], axis=1)

# Drop duplicate rows
soil_df = soil_df.drop_duplicates()

# Convert prcent and depth column from object to float
soil_df['prcent'] = soil_df['prcent'].astype(float)
soil_df['depth'] = soil_df['depth'].astype(float)

# Select rows with max prcent
soil_df = soil_df[soil_df.prcent == soil_df.prcent.max()]

# Sort rows by depth
soil_df = soil_df.sort_values(by=['depth'])

print(soil_df)
