# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 12:39:25 2024
#download photos from arcgis layer
@author: smcnamara
"""

#download photos from arcgis layer
import os, shutil
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
import pandas as pd
from PIL import Image

#adjust these parameters as needed
access_projectID = "Ft_Douglas"
projectID = "Ft_Douglas"
AGOL_user = "hchung_HGLGIS"
password = "digitalfieldnotes1"

#get survey feature ID from arcgis website
#find feature layer (not form!) from https://hglgis.maps.arcgis.com/home/content.html?view=table&sortOrder=desc&sortField=modified&folder=all#content
#click on the feature layer and on the right under details is the ID.  Can also see the ID in the url    
survey_item_ID="e43a5882db0d4191b8ece1ed7f1cba62"

def get_GEOdir():
    #get working directory
    curDir = os.getcwd()
    #find DGM directory
    GEOdir = curDir[:curDir.lower().find('geodata')+7]
    return GEOdir

gis = GIS("https://www.arcgis.com",AGOL_user, password)
#print('logged on')

# item = gis.content.get(survey_item_ID)
# feature_layer = item.layers[0]  # Assuming it's the first layer

survey_by_id = gis.content.get(survey_item_ID)
layer0 = survey_by_id.layers[0]
exportLayer = FeatureLayerCollection.fromitem(survey_by_id)

GEOdir = get_GEOdir()

for layer in exportLayer.layers:
    # Query all features
    #update if trying to download by day, test dataset doesn't have that info
    features = layer.query(where = "1=1", return_geometry=True)
    coordinates = [(feature.geometry['x'], feature.geometry['y']) for feature in features]
    print(exportLayer.properties.spatialReference)
    
    # Prepare lists to store data
    data = []
    photo_names = []
    
    # Iterate through features
    for feature in features:
        # Extract attributes
        att = feature.attributes
        #store attributes to a csv, including location data
        
        
        #download photos for this feature
        for photonum in range(len(layer0.attachments.get_list(oid=att['OBJECTID']))):
            photoID = layer0.attachments.get_list(oid=att['OBJECTID'])[photonum]['id']
            photoName = layer0.attachments.get_list(oid=att['OBJECTID'])[photonum]['name']
            photo_path_orig = os.path.join(GEOdir, "03_RawData","photo_download")
            #if photoName already exists, delete it
            if os.path.exists(os.path.join(GEOdir, "03_RawData","photo_download",photoName)):
                os.remove(os.path.join(GEOdir,"03_RawData","photo_download",photoName))
            layer0.attachments.download(oid=att['OBJECTID'],attachment_id=photoID,save_path = photo_path_orig)
            #rename photo to something more useful, but not much more unless the original feature layer captures more info
            newPhotoName=''
            # Open the image
            with Image.open(os.path.join(photo_path_orig,photoName)) as image1:
                #get exif info
                exif1 = image1._getexif()
                #tag for date taken is 36867
                #if this tag doesn't exist, just name with the photoID
                if 36867 in exif1:
                    dateTaken = exif1[36867]
                    #remove "/" and ":" from dateTaken string
                    dateTaken=dateTaken.replace("/","")
                    dateTaken=dateTaken.replace(":","")
                    dateTaken=dateTaken.replace(" ","_")
                    newPhotoName = "photo"+str(photoID+1)+"_"+dateTaken+".jpg"
                else:
                    newPhotoName = "photo"+str(photoID+1)+".jpg"
                                            
            #confirm photo does not already exist 
            #if it does, skip
            if not os.path.exists(os.path.join(GEOdir,"03_RawData","photo_download","renamed",newPhotoName)):
                shutil.move(os.path.join(GEOdir, "03_RawData","photo_download",photoName),os.path.join(GEOdir,"03_RawData","photo_download","renamed",newPhotoName))
            else:
                #delete the original photo, since the download function will not overwrite
                os.remove(os.path.join(GEOdir,"03_RawData","photo_download",photoName))
    
    
    # Convert the result to a pandas DataFrame
    df = features.sdf
    # Save DataFrame to CSV
    csv_path = os.path.join(GEOdir, "03_RawData", "feature_layer_data.csv")
    df.to_csv(csv_path, index=False)
    
    print(f"CSV file with photo names saved at: {csv_path}")
