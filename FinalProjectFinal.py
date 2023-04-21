import os
import sys
import subprocess
import pkg_resources
import time
import warnings
warnings.filterwarnings("ignore")
from arcgis.gis import GIS
import datetime as dt
import zipfile
import numpy as np
from arcpy.sa import *    
import arcpy
import pandas as pd
import glob
import requests
import io
from statsmodels.stats.outliers_influence import variance_inflation_factor
from IPython.display import display, clear_output
import statsmodels.api as sm


def data_setup(Residential):
    #Attempt at Adding dummy variables 
    #You will need to install skicit-learn and statsmodels and set your environment before forest regression
    #Creation of Dummy Variables
    #Distance from Average House
    Residential["Shape"] = Residential['Shape'].str.replace('(','')
    Residential["Shape"] = Residential['Shape'].str.replace(')','')
    Coords = Residential["Shape"].str.split(",",expand = True)
    Residential["Lats"] = Coords[Coords.columns[1]].astype(float)
    Residential["Lons"] = Coords[Coords.columns[0]].astype(float)
    MeanLon = Residential["Lons"].astype(float).mean()
    MeanLat = Residential["Lats"].astype(float).mean()
    #Use distance from center houses and connect 
    Residential["Dist_Lat"] = Residential["Lats"] - MeanLat
    Residential["Dist_Lon"] = Residential["Lons"] - MeanLon
    #Delete Female %
    #Residential = Residential.drop(["PFemale"],axis = 1)

    #Resident > 1 = Apartment
    Residential["Apartment"] = 0
    Residential["SingleHome"] = 0
    Residential.loc[Residential["House"] >1,"Apartment"] = 1
    Residential.loc[Residential["House"] == 1,"SingleHome"] = 1
    return(Residential)

def regression(ChosenVar):
    clear_output(wait=False)
    time.sleep(.3)
    while True:
        try:
            Residential = pd.read_csv("Residential.csv", index_col = 0)
            Residential = data_setup(Residential)
        except:
            print("Please input the folder that the data is in...")
            print("This should look similar to: /Users/USERNAME/Downloads/FolderWithData/")
            lyrTest = input()
            os.chdir(lyrTest)
            Residential = pd.read_csv("Residential.csv", index_col = 0)
            Residential = data_setup(Residential)

        menu = {}
        currentoptions = {}
        menu['1']="Dependant Variable    *" 
        menu['2']="Independant Variables *"
        menu['3']="P-Value Cutoff        *"
        menu['4']="VIF Test Cutoff       *"
        menu['5']="Correlation Cutoff    *"
        menu['6']="Run Regression       "
        menu['7']="Return to Menu       " 
        while True: 
            print("There are several regression options for you to make:")
            print("Name                    * Current Selection")
            print("*******************************************")
            currentoptions['1'] = ChosenVar[0]
            currentoptions['2'] = ChosenVar[1]
            currentoptions['3'] = ChosenVar[2]
            currentoptions['4'] = ChosenVar[3]
            currentoptions['5'] = ChosenVar[4]
            currentoptions['6'] = '*'
            currentoptions['7'] = '*'
            options = menu.keys()
            #options.sort()
            for entry in options: 
                print(entry, menu[entry], currentoptions[entry])
            print("*******************************************")
            select2=input("Please Select Var:  ")
           
            if (select2 == '1') or (select2==menu['1']):
                while True:
                    clear_output(wait=False)
                    time.sleep(.3)
                    print("What would you like to set the Dependant Variable to:")
                    menu2 = {}
                    menu2['1']= Residential.columns[24]
                    x=2
                    for value in Residential.columns[27:]:
                        menu2[x] = value
                        x+=1
                    options = menu2.keys()
                    for entry in options: 
                        print(entry, menu2[entry])
                    select3 = input("Please Select Variable:   ")
                    if select3 == '1':
                        ChosenVar[0] = Residential.columns[22]
                        clear_output(wait=False)
                        time.sleep(.3)
                        break
                    else:
                        try:
                            intselect = int(select3)
                            ChosenVar[0] = Residential.columns[25+intselect]
                            currentoptions['1'] = ChosenVar[0]
                            clear_output(wait=False)
                            time.sleep(.3)
                            break
                        except:
                            clear_output(wait=False)
                            time.sleep(.3)
                            print("Sorry, that column doesnt exist, try again!")
            elif select2 =="7" or (select2==menu['6']):
                clear_output(wait=False)
                time.sleep(.3)
                return(ChosenVar,Residential,0)

            elif select2 =='2' or (select2==menu['2']):
                clear_output(wait=False)
                time.sleep(.3)
                while True:
                    print("What would you like to set the Independant Variables to:")
                    menu4 = {}
                    menu4['1'] = "Infrastructure Variables"
                    menu4['2'] = "Population Variables"
                    menu4['3'] = "All Available Variables"
                    options = menu4.keys()
                    for entry in options: 
                        print(entry, menu4[entry])
                    selection = input("Please Select:")
                    if selection in menu4.keys():
                        ChosenVar[1] = menu4[selection]
                        clear_output(wait=False)
                        time.sleep(.3)
                        break
                    elif selection == menu4['1'] or selection == menu4['2'] or selection == menu4['3']:
                        ChosenVar[1] = selection
                        clear_output(wait=False)
                        time.sleep(.3)
                        break
                    else:
                        clear_output(wait=False)
                        time.sleep(.3)
                        "Not found in list, please try again"
            elif select2 =='3' or (select2==menu['3']):
                clear_output(wait=False)
                time.sleep(.3)
                while True:
                    print("What would you like to set the P Value Cutoff to:")
                    print("This cutoff ultimately determines the statistical cutoff for the regression. A smaller number will result in more statistically significant results.")
                    menu4 = {}
                    menu4['1'] = ".01"
                    menu4['2'] = ".05"
                    menu4['3'] = ".1"
                    options = menu4.keys()
                    for entry in options: 
                        print(entry, menu4[entry])
                    selection = input("Please Select:")
                    if selection in menu4.keys():
                        ChosenVar[2] = menu4[selection]
                        clear_output(wait=False)
                        time.sleep(.3)
                        break
                    elif selection == menu4['1'] or selection == menu4['2'] or selection == menu4['3']:
                        ChosenVar[2] = selection
                        clear_output(wait=False)
                        time.sleep(.3)
                        break
                    else:
                        clear_output(wait=False)
                        time.sleep(.3)
                        "Not found in list, please try again"
            elif select2 =='4' or (select2==menu['4']):
                clear_output(wait=False)
                time.sleep(.3)
                while True:
                    print("What would you like to set the VIF Cutoff to:")
                    print("This cutoff will determine the correlation between every variable, and eliminate variables that are too closely linked. A lower number is stricter, while a higher number could result in numerical issues")
                    menu4 = {}
                    menu4['1'] = "1"
                    menu4['2'] = "5"
                    menu4['3'] = "10"
                    options = menu4.keys()
                    for entry in options: 
                        print(entry, menu4[entry])
                    selection = input("Please Select:")
                    if selection in menu4.keys():
                        ChosenVar[3] = menu4[selection]
                        clear_output(wait=False)
                        time.sleep(.3)
                        break
                    elif selection == menu4['1'] or selection == menu4['2'] or selection == menu4['3']:
                        ChosenVar[3] = selection
                        clear_output(wait=False)
                        time.sleep(.3)
                        break
                    else:
                        clear_output(wait=False)
                        time.sleep(.3)
                        "Not found in list, please try again"
            elif select2 =='6' or (select2==menu['4']):
                #RUN REGRESSION
                summary,Residential = run_regression(ChosenVar,Residential)
                print("*********************************************************")
                print("This summary has been saved as the variable 'summary', as well as saved as the file 'summary.txt'")
                print("*********************************************************")
                selection = input("Press Enter to Return to the Main Menu")
                return(ChosenVar,Residential,summary)
            elif select2 =='5' or (select2==menu['5']):
                clear_output(wait=False)
                time.sleep(.3)
                while True:
                    print("What would you like to set the Correlation Cutoff to:")
                    print("When first subsetting the data, this is the cutoff that helps slim down any potential issues between datasets. A lower cutoff could result in numerical issues")
                    menu4 = {}
                    menu4['1'] = ".2"
                    menu4['2'] = ".4"
                    menu4['3'] = ".6"
                    options = menu4.keys()
                    for entry in options: 
                        print(entry, menu4[entry])
                    selection = input("Please Select:")
                    if selection in menu4.keys():
                        ChosenVar[4] = menu4[selection]
                        clear_output(wait=False)
                        time.sleep(.3)
                        break
                    elif selection == menu4['1'] or selection == menu4['2'] or selection == menu4['3']:
                        ChosenVar[4] = selection
                        clear_output(wait=False)
                        time.sleep(.3)
                        break
                    else:
                        clear_output(wait=False)
                        time.sleep(.3)
                        "Not found in list, please try again"
            else:
                clear_output(wait=False)
                time.sleep(.3)
                "Not found in list, please try again"
                
def run_regression(ChosenVars,Residential):
    #ChosenVar = ["Median Income","Infrastructure Variables",'.01','10','.6']
    ys = ChosenVars[0]
    XName = ChosenVars[1]
    PValue = ChosenVars[2]
    VIFcutoff = ChosenVars[3]
    CorrCutoff = ChosenVars[4]
    Combined = Residential[:]

    Infrastructure = [2,5,6,7,20,44,45,46]
    RGB = [13,14,15,16,17,18,21,23,25]
    Total = [2,5,6,7,13,14,15,16,17,18,20,21,23,25,44,45,46]
    outputTOTAL = [Residential.columns[val] for val in Total]
    outputIN = [Residential.columns[val] for val in Infrastructure]
    outputRGB = [Residential.columns[val] for val in RGB]
    if XName == "Infrastructure Variables":
        Xs = outputIN
    elif XName == "Population Variables":
        Xs = outputRGB
    else:
        Xs = outputTOTAL
    new_x = Xs[:]
    for column in range(0,len(Xs)):
        for columntwo in range(column,len(Xs)):
            Combined[(Xs[column] + " x " +Xs[columntwo])] = Combined[Xs[column]] * Combined[Xs[columntwo]]
            new_x.append((Xs[column] + " x " +Xs[columntwo]))
    NewCombined = Combined[new_x]
    CorrMat = NewCombined.corr()
    listofcols = CorrMat.columns
    listofcols = pd.DataFrame([0]*len(listofcols),index=listofcols,columns=["Count"])
    for column in CorrMat.columns:
        for colo in range(0,len(CorrMat[column])):
            val = CorrMat.loc[column,CorrMat.index[colo]]
            if val > float(CorrCutoff) and val <1:
                listofcols.loc[column,"Count"] +=1
                listofcols.loc[CorrMat.index[colo],"Count"] +=1
    while max(listofcols["Count"] > 0):
        listofcols = listofcols.sort_values(by = "Count",ascending = False)
        NewCombined = NewCombined.drop(listofcols.index[0],axis=1)
        CorrMat = NewCombined.corr()
        listofcols = CorrMat.columns
        listofcols = pd.DataFrame([0]*len(listofcols),index=listofcols,columns=["Count"])
        for column in CorrMat.columns:
            for colo in range(0,len(CorrMat[column])):
                val = CorrMat.loc[column,CorrMat.index[colo]]
                if val > float(CorrCutoff) and val <1:
                    listofcols.loc[column,"Count"] +=1
                    listofcols.loc[CorrMat.index[colo],"Count"] +=1
    NewCombined["Constant"] = 1

    #VIF Test
    vif_data = pd.DataFrame()
    FullColumns = NewCombined.columns
    vif_data["feature"] = FullColumns
    NewCombined = NewCombined.dropna()
    # calculating VIF for each feature
    vif_data["VIF"] = [variance_inflation_factor(NewCombined, i)
                              for i in range(len(NewCombined.columns))]
    for value in list(vif_data[vif_data["VIF"] > float(VIFcutoff)]["feature"].values):
        if value != "Constant":
            NewCombined = NewCombined.drop(value,axis=1)
    vif_data = vif_data.sort_values(by = "VIF")
    NewCombinedTwo = NewCombined.dropna()

    FinalColumns = NewCombinedTwo.columns.values.tolist()
    y= Residential[ys]
    y=y[NewCombinedTwo.index]
    results3 = Next_Step(NewCombinedTwo,FinalColumns,y)
    while max(results3.pvalues) > float(PValue):# or len(FinalColumns)  > 10:
        VAL = np.where(results3.pvalues.isna())[0]
        VAL.sort()
        VAL = VAL[::-1]
        for val in VAL:
            FinalColumns.remove(FinalColumns[val])
        FinalColumns.remove(FinalColumns[(np.where(results3.pvalues == max(results3.pvalues))[0][0])])
        results3 = Next_Step(NewCombinedTwo,FinalColumns,y)
    clear_output(wait=False)
    time.sleep(.3)
    print(results3.summary())
    with open('summary.txt', 'w') as fh:
        fh.write(results3.summary().as_text())
    return(results3, Residential)

def Next_Step(NewCombinedTwo,FinalColumns,y):
    x = NewCombinedTwo[FinalColumns]
    results = sm.OLS(y, x).fit()
    return(results)

def arcgis_table_to_df(in_fc, input_fields=None, query=""):
    """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    input fields using an arcpy.da.SearchCursor.
    :param - in_fc - input feature class or table to convert
    :param - input_fields - fields to input to a da search cursor for retrieval
    :param - query - sql query to grab appropriate values
    :returns - pandas.DataFrame"""
    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    if input_fields:
        final_fields = [OIDFieldName] + input_fields
    else:
        final_fields = [field.name for field in arcpy.ListFields(in_fc)]
    data = [row for row in arcpy.da.SearchCursor(in_fc,final_fields,where_clause=query)]
    fc_dataframe = pd.DataFrame(data,columns=final_fields)
    fc_dataframe = fc_dataframe.set_index(OIDFieldName,drop=True)
    return(fc_dataframe)
    
def setup():
    print("This setup will allow the script to connect with the data you have downloaded from Google Earth Engine. The time varies, but can take between 15-30 minutes, depending on the area.")
    print("Please input the folder that the data is in...")
    print("This should look similar to: /Users/USERNAME/Downloads/FolderWithData/")
    lyrTest = input()
    os.chdir(lyrTest)
    #Rest of Code for Running

    timeZero = time.time()
    #Download Data from Online
    gis = GIS("pro") #connect to GIS
    #Check if Output files exist:

    Files = glob.glob('*.shp') #collect SHP files
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    aprxMap = aprx.listMaps("Map")[-1]
    for layer in aprxMap.listLayers():
        arcpy.management.Delete(layer)
    for layer in aprxMap.listTables():
        arcpy.management.Delete(layer)
    #lyr = aprxMap.addDataFromPath(lyrTest+Files[0])
    print("Loading Files")
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    for file in Files:
        #print(file)
        if file != "Public Schools.shp":
            arcpy.MakeFeatureLayer_management(lyrTest+file,file[:-4]) #Load and name files
    #USE THIS BLOCK TO LOAD IN ALL LAYERS 
    #print("Initial analysis")
    for layer in aprxMap.listLayers(): #Expand this to name all SHP files, but so far does the necessary ones
        layer.visible = False
        if layer.longName =="MapofBuildings":
            MapofBuildings = layer 
        if layer.longName == "RoadNetwork":
            RoadNetwork = layer
    Highways = arcpy.management.SelectLayerByAttribute("RoadNetwork", 'NEW_SELECTION', "mtfcc = 'S1100'")
    AllHighways = arcpy.management.SelectLayerByAttribute(Highways, 'ADD_TO_SELECTION', "mtfcc = 'S1200'") #Selects both interstates and old US routes as "highways",might seperate 
    arcpy.management.CopyFeatures(AllHighways, 'Highways')
    arcpy.SelectLayerByAttribute_management("RoadNetwork", "CLEAR_SELECTION")
    arcpy.management.CalculateGeometryAttributes("MapofBuildings", [["Area","AREA_GEODESIC"]],"","SQUARE_METERS")
    arcpy.analysis.GenerateNearTable(MapofBuildings, Highways, "HighwayCloseness",method='GEODESIC')

    #MapofBuildings.symbology = sym
    print("Downloading Supplementary Analysis Files") #This code loads in a public datast of all public schools, very handy but annoying to import
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    folder_path ='/Users/britt/Downloads/Project Outputs2/Project Outputs/' #Change this later
    num_items = 1
    items = gis.content.get('87376bdb0cb3490cbda39935626f6604') 
    Testing = items.export("Test2","Shapefile")
    Testing.download(folder_path) #downloads to same folder as other shapefiles, extracts and imports
    print("Unzipping")
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    with zipfile.ZipFile(folder_path+"Test2.zip", 'r') as zip_ref:
        zip_ref.extractall(folder_path)

    PublicSchools = arcpy.MakeFeatureLayer_management("PublicSchools.shp","PublicSchools")
    arcpy.analysis.GenerateNearTable(MapofBuildings, PublicSchools, "SchoolDistance",method='GEODESIC')
    arcpy.management.AddJoin(MapofBuildings, 'FID', 'SchoolDistance', 'IN_FID') #Create another near table and update symbology
    #print("Modifying Data...")
    #Remove School Polygons from buildings
        #Select via distance from school, remove
    NonSchools = arcpy.management.SelectLayerByAttribute("MapofBuildings", 'NEW_SELECTION','SchoolDistance.NEAR_DIST > 10')
    NonSchools = arcpy.management.CopyFeatures(NonSchools, 'BuildingsNoSchools')
    arcpy.management.Delete("MapofBuildings")

    #Calculate Area of Buildings
    NonSchools2 = arcpy.management.SelectLayerByAttribute("BuildingsNoSchools", 'NEW_SELECTION','MapofBuildings_Area > 60')
    NonSchools2 = arcpy.management.CopyFeatures(NonSchools2, 'BuildingsNoSmall')
    arcpy.SelectLayerByAttribute_management("BuildingsNoSchools", "CLEAR_SELECTION")
    arcpy.management.Delete("BuildingsNoSchools")

    #Find Num Buildings Per Block
    arcpy.analysis.SpatialJoin('CensusBlockSquare', "BuildingsNoSmall", 'BuildingsPerCB')
    arcpy.management.Delete("CensusBlockSquare")

    #find average area, stdev of ALL buildings
    stat_fields = [['Area', 'Mean'], ['Area','STD']]

    arcpy.analysis.Statistics("BuildingsNoSmall", "BuildingStats", stat_fields)
    Stats = arcpy.SearchCursor("BuildingStats")
    for row in Stats:
        STD = row.getValue('STD_MapofBuildings_Area')
        MEAN = row.getValue('MEAN_MapofBuildings_Area')
    Obsv_Vis = arcpy.AddField_management("BuildingsNoSmall", "DifAvg", "FLOAT")

    #Calculate distance from Mean - should draw out larger buildings, apartments and industry
    arcpy.CalculateField_management ("BuildingsNoSmall", 'DifAvg',"!MapofBuildings_Area!-{}".format(MEAN))
    #CLEAR UP SOME FIELDS
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    aprxMap = aprx.listMaps("Map")[-1]
    for layer in aprxMap.listLayers():
        layer.visible = False
        if layer.longName == "Highways":
            arcpy.DeleteField_management("Highways",["rttyp","fullname","linearid"])
        if layer.longName == "MapofBuildings":
            arcpy.DeleteField_management("MapofBuildings",["MapofBuildings.release","MapofBuildings.capture_da"])
        if layer.longName == "BuildingsPerCB":
            arcpy.DeleteField_management("BuildingsPerCB",["TRACTCE20",'MTFCC20', 'COUNTYFP20', 'INTPTLAT20', 'BLOCKCE20', 'UACE20', 'STATEFP20', 'NAME20', 'UR20', 'INTPTLON20','FUNCSTAT20','UATYPE20'])
        if layer.longName == "CensusBlockGroupSquare":
            arcpy.DeleteField_management("CensusBlockGroupSquare",['BLKGRPCE', 'INTPTLON', 'TRACTCE', 'MTFCC', 'STATEFP', 'INTPTLAT', 'FUNCSTAT', 'COUNTYFP','NAMELSAD'])

    #Import all tif files
    Files = glob.glob('*.tif') #collect SHP files
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    aprxMap = aprx.listMaps("Map")[-1]
    print("Loading Raster Files")
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    Name = "Raster"
    x = 1
    Temp3 = [0]*len(Files)
    for file in Files:
        Temp = arcpy.management.MakeRasterLayer(lyrTest+file,Name+str(x))
        Temp3[x-1] = Name+str(x)
        x+=1
    #COMBINE
    arcpy.management.MosaicToNewRaster(Temp3, lyrTest,"Testing2","","","",1,"BLEND","FIRST")
    for layer in aprxMap.listLayers():
        layer.visible = False
        if layer.longName == "Testing2":
            TreeRaster2 = Raster(layer.longName)*1000
            TreeRaster2 = arcpy.sa.ZonalStatistics("BuildingsPerCB","Join_Count",TreeRaster2)
            arcpy.management.Delete("NewRast")
            TreeRaster2 = Int(TreeRaster2)
            arcpy.conversion.RasterToPolygon(TreeRaster2, "TreeRaster")
            arcpy.management.Delete(layer)
    x=1
    for file in Files:
        arcpy.management.Delete(Name+str(x))
        x+=1
    arcpy.management.Delete("Testing2")
    for layer in aprxMap.listLayers():
        if layer.longName =="TreeRaster2":
            arcpy.management.Delete(layer)
        layer.visible = False
        #if layer.longName =="Build"

    #Connect Distance from Road and Building Size - Try and draw out Businesses vs Housing
    #Generate Near Table of buildings to roads
    arcpy.analysis.GenerateNearTable("BuildingsNoSmall", "RoadNetwork", "RoadDistance",method='GEODESIC')

    #Add 1 to all
    arcpy.AddField_management("RoadDistance", "Modifier", "FLOAT")
    arcpy.CalculateField_management ("RoadDistance", 'Modifier',"!NEAR_DIST!+{}".format(1))

    #Generate Near Table within BuildingsNoSmall - BuildingsPerCB to connect GEOID20 to each building
    arcpy.analysis.GenerateNearTable("BuildingsNoSmall", "BuildingsPerCB", "GEOIDConn",method='GEODESIC')

    #Generate Near Table within BuildingsNoSmall - CensusBlockGroupSquare to connect GEOID to each building
    arcpy.analysis.GenerateNearTable("BuildingsNoSmall", "CensusBlockGroupSquare", "GEOIDConn_GROUP",method='GEODESIC')

    arcpy.analysis.SummarizeWithin("BuildingsPerCB",'TreeRaster',"BlocksTrees","KEEP_ALL",[["gridcode","MEAN"]])#Export to Table

    
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    aprxMap = aprx.listMaps("Map")[-1]
    for layer in aprxMap.listLayers():
        layer.visible = False
        if layer.longName == "BuildingsNoSmall":
            Buildings = arcgis_table_to_df(layer)
        elif layer.longName == "BlocksTrees":
            CBlock = arcgis_table_to_df(layer)
        elif layer.longName == "CensusBlockGroupSquare":
            CGroup = arcgis_table_to_df(layer)
    for layer in aprxMap.listTables():
        if layer.longName =="HighwayCloseness":
            HighwayCloseness = arcgis_table_to_df(layer)
            HighwayCloseness = HighwayCloseness["NEAR_DIST"]
            Buildings = Buildings.merge(HighwayCloseness,left_index=True,right_index=True)
        if layer.longName =="RoadDistance":
            RoadDistance = arcgis_table_to_df(layer)
            RoadDistance = RoadDistance["Modifier"]
            Buildings = Buildings.merge(RoadDistance,left_index=True,right_index=True)
        if layer.longName =="GEOIDConn":
            GEOIDConn = arcgis_table_to_df(layer)
            GEOIDConn = GEOIDConn[["NEAR_DIST","NEAR_FID"]]
            Buildings = Buildings.merge(GEOIDConn,left_index=True,right_index=True)
        if layer.longName =="GEOIDConn_GROUP":
            GEOIDConn_GROUP = arcgis_table_to_df(layer)
            GEOIDConn_GROUP = GEOIDConn_GROUP[["NEAR_DIST","NEAR_FID"]]        
            Buildings = Buildings.merge(GEOIDConn_GROUP,left_index=True,right_index=True)



    #GENERATE BUILDING MODIFIER

    GEOID20s = CBlock["GEOID20"].drop_duplicates()
    GEOIDs_short= GEOID20s.str[:-4]
    NEWGEOS = GEOIDs_short.drop_duplicates()

    TEST = pd.DataFrame([])
    IMPORTDATA2 = pd.DataFrame([])
    print("Grabbing Census Data...")
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    GEOID20s = CBlock["GEOID20"].drop_duplicates()
    GEOIDs_short= GEOID20s.str[:-4]
    NEWGEOS = GEOIDs_short.drop_duplicates()
    STATECOUNTIES = []
    for geo in NEWGEOS:
        if geo[0:5] not in STATECOUNTIES:
            STATECOUNTIES.append(geo[0:5])
    TEST = pd.DataFrame([])
    IMPORTDATA2 = pd.DataFrame([])
    IMPORTDATA = pd.DataFrame([])
    for GEOID in STATECOUNTIES:
        query_url = 'https://api.census.gov/data/2020/dec/pl?get=H1_002N,H1_002N,P1_003N,P1_004N,P1_005N,P1_006N,P1_007N,P2_002N,P2_003N&for=block:*&in=state:'+str(GEOID[0:2])+'&in=county:'+str(GEOID[2:5])+'&in=tract:*&key=02f4845b752341af1ea0eb002636816107968ccb'
        DATTEST = (pd.read_csv(query_url))
        IMPORTDATA = IMPORTDATA.append(DATTEST) 
    for row in range(0,IMPORTDATA.shape[0]):
        rowdat = IMPORTDATA.iloc[row]
        rowdat["state"] =str(GEOID[0:2])
        rowdat["county"] =str(GEOID[2:5])
        #rowdat["tract"] = str(GEOID[5:11])
        tractval = str(rowdat["tract"])
        while len(tractval) < 6:
            tractval = "0"+tractval
        rowdat["tract"] = tractval
        IMPORTDATA.iloc[row] = rowdat
    IMPORTDATA["GEOID20"] = IMPORTDATA["state"].astype(str)+IMPORTDATA["county"].astype(str)+IMPORTDATA["tract"].astype(str)+IMPORTDATA["block]"].str[:-1]#[DATTEST.columns[1]]#.str.split("[")
    #IMPORTDATA = IMPORTDATA[IMPORTDATA.columns[1:(len(IMPORTDATA.columns)-6)].values]
    #IMPORTDATA2 = IMPORTDATA2.append(IMPORTDATA)
    #print(IMPORTDATA2.shape)
    IMPORTDATA = IMPORTDATA.reset_index().drop(["index"],axis=1)
    for row in range(0,IMPORTDATA.shape[0]):
        if (IMPORTDATA.loc[row,"GEOID20"][-1]) == "]":
            IMPORTDATA.loc[row,"GEOID20"] = IMPORTDATA.loc[row,"GEOID20"][:-1]
        if (IMPORTDATA.loc[row,"GEOID20"][-1]) == "]":
            IMPORTDATA.loc[row,"GEOID20"] = IMPORTDATA.loc[row,"GEOID20"][:-1]
    Final = pd.merge(CBlock, IMPORTDATA, on='GEOID20')
    Final["Pwater"] = Final["AWATER20"]/(Final["ALAND20"]+Final["AWATER20"])
    Final["PLand"] = Final["ALAND20"]/(Final["ALAND20"]+Final["AWATER20"])
    Final = Final.drop(["AWATER20","ALAND20"],axis=1)

    for GEOID in NEWGEOS:
        query_url = 'https://api.census.gov/data/2020/dec/pl?get=H1_002N,H1_002N,P1_003N,P1_004N,P1_005N,P1_006N,P1_007N,P2_002N,P2_003N&for=block:*&in=state:'+str(GEOID[0:2])+'&in=county:'+str(GEOID[2:5])+'&in=tract:'+str(GEOID[5:11])+'&key=02f4845b752341af1ea0eb002636816107968ccb'
        DATTEST = (pd.read_csv(query_url))
        for row in range(0,DATTEST.shape[0]):
            rowdat = DATTEST.iloc[row]
            rowdat["state"] =str(GEOID[0:2])
            rowdat["county"] =str(GEOID[2:5])
            rowdat["tract"] = str(GEOID[5:11])
            DATTEST.iloc[row] = rowdat
        DATTEST["GEOID20"] = DATTEST["state"].astype(str)+DATTEST["county"].astype(str)+DATTEST["tract"].astype(str)+DATTEST["block]"].str[:-1]#[DATTEST.columns[1]]#.str.split("[")
        IMPORTDATA = DATTEST[DATTEST.columns[1:(len(DATTEST.columns)-6)].values]
        IMPORTDATA["GEOID20"] = DATTEST["GEOID20"]
        IMPORTDATA2 = IMPORTDATA2.append(IMPORTDATA)
        #print(IMPORTDATA2.shape)
    IMPORTDATA2 = IMPORTDATA2.reset_index().drop(["index"],axis=1)
    for row in range(0,IMPORTDATA2.shape[0]):
        if (IMPORTDATA2.loc[row,"GEOID20"][-1]) == "]":
            IMPORTDATA2.loc[row,"GEOID20"] = IMPORTDATA2.loc[row,"GEOID20"][:-1]
        if (IMPORTDATA2.loc[row,"GEOID20"][-1]) == "]":
            IMPORTDATA2.loc[row,"GEOID20"] = IMPORTDATA2.loc[row,"GEOID20"][:-1]
    Final = pd.merge(CBlock, IMPORTDATA2, on='GEOID20')
    Final["Pwater"] = Final["AWATER20"]/(Final["ALAND20"]+Final["AWATER20"])
    Final["PLand"] = Final["ALAND20"]/(Final["ALAND20"]+Final["AWATER20"])
    Final = Final.drop(["AWATER20","ALAND20"],axis=1)

    Buildings = Buildings.drop(["SchoolDistance_NEAR_FID","SchoolDistance_IN_FID","SchoolDistance_OBJECTID","MapofBuildings_Test","MapofBuildings_capture_da","MapofBuildings_geometry_t","MapofBuildings_release"],axis=1)
    Buildings = Buildings.rename(columns={"NEAR_DIST_x":"HighwaydistMAYBE","NEAR_DIST_y":"GEOIDConn.NEAR_DIST","NEAR_FID_x":"GEOIDConn.NEAR_FID","NEAR_DIST":"GEOIDConn_GROUP.NEAR_DIST","NEAR_FID_y":"GEOIDConn_GROUP.NEAR_FID"})

    #Need to pull remaining census data on 

    #HOUSE IDENTIFICATION
    CombinedBuildings = Buildings[Buildings['GEOIDConn.NEAR_DIST'] ==0]
    CombinedBuildings["House"] = 0
    totalcensus = 0
    totalcaught = 0
    print("Identifying Houses")
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    for row in range(0,Final.shape[0]):
        #print(row)
        y=0
        joincount, censuscount = (Final.iloc[row][["Join_Count","H1_002N"]])
        if (joincount !=0):
            if censuscount == 0:
                CombinedBuildings.loc[CombinedBuildings["GEOIDConn.NEAR_FID"]==row+1,"House"]=-1
            elif (censuscount !=0):
                if joincount == censuscount:
                    CombinedBuildings.loc[CombinedBuildings["GEOIDConn.NEAR_FID"]==row+1,"House"] =1
                    y = censuscount
                elif joincount > censuscount:
                    Test = CombinedBuildings[CombinedBuildings["GEOIDConn.NEAR_FID"] == row+1]["MapofBuildings_AREA"]
                    #print(len(Test))
                    Test2 = Test
                    x=0
                    y=0
                    Test2 = Test2[Test2 <=300]
                    Test2 = Test2.sort_values(ascending=False)
                    Test3 = Test2
                    while censuscount -y >0 and len(Test3) >0:
                        CombinedBuildings.loc[Test2.index[x],"House"] =1
                        Test3 = Test3.drop([Test2.index[x]],axis=0)
                        x+=1
                        y+=1
                    for index in range(0,len(Test3)):
                        CombinedBuildings.loc[Test2.index[x],"House"] =-1
                    #print(joincount,x,y,censuscount)
                    if censuscount -y >0:
                        Savey = y
                        #print(censuscount-y)
                        Test2 = Test[Test >300].sort_values(ascending=True)
                        x=0
                        while censuscount -y >0 and len(Test2)>x:
                            CombinedBuildings.loc[Test2.index[x],"House"] =1
                            x+=1
                            y+=1
                            if len(Test2) ==x and censuscount -y >0:
                                z = 0
                                Math = 0
                                for building in range(0,len(Test2)):
                                    Math = int(np.floor((censuscount-Savey-Math)/(len(Test2)-z)))
                                    #print(Math)
                                    CombinedBuildings.loc[Test2.index[building],"House"] = Math
                elif joincount < censuscount:
                    Test = CombinedBuildings[CombinedBuildings["GEOIDConn.NEAR_FID"] == row+1]["MapofBuildings_AREA"]
                    #print(len(Test))
                    Test2 = Test
                    x=0
                    y=0
                    Test2 = Test2[Test2 <=300]
                    Test2 = Test2.sort_values(ascending=False)
                    Test3 = Test2
                    while censuscount -y >0 and len(Test3) >0:
                        CombinedBuildings.loc[Test2.index[x],"House"] =1
                        Test3 = Test3.drop([Test2.index[x]],axis=0)
                        x+=1
                        y+=1
                    for index in range(0,len(Test3)):
                        CombinedBuildings.loc[Test2.index[x],"House"] =-1
                    #print(joincount,x,y,censuscount)
                    if censuscount -y >0:
                        Savey = y
                        #print(censuscount-y)
                        Test2 = Test[Test >300].sort_values(ascending=False)
                        CombinedBuildings.loc[Test2.index[Test2 > 4000],"House"] = -1
                        y+=len(Test2.index[Test2>4000])
                        Test2 = Test2.drop(Test2.index[Test2 > 4000], axis=0)
                        Test3 = Test2
                        for value in range(0,len(Test2)):
                            if Test2[Test2.index[value]] > 1000:
                                if CombinedBuildings.loc[Test2.index[value],"Modifier"] >30:
                                    Test3 = Test3.drop(Test2.index[value], axis=0)
                                    y+=1
                        x=0
                        Test2 = Test3
                        while censuscount -y >0 and len(Test2)>x:
                            CombinedBuildings.loc[Test2.index[x],"House"] =1
                            x+=1
                            y+=1
                            if len(Test2) ==x and censuscount -y >0:
                                z = 0
                                Math = 0
                                for building in range(0,len(Test2)):
                                    Math = int(np.floor((censuscount-Savey-Math)/(len(Test2)-z)))
                                    #print(Math)
                                    CombinedBuildings.loc[Test2.index[building],"House"] = Math

    print('Done identifying houses!')
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    Residential = CombinedBuildings[CombinedBuildings["House"] >= 1]
    NonResidential = CombinedBuildings[CombinedBuildings["House"] < 1]

    CensusLayers = ["White alone","Black or African American alone","American Indian and Alaska Native alone","Asian alone","Native Hawaiian and Other Pacific Islander alone","Hispanic or Latino","Not Hispanic or Latino"]
    for layer in CensusLayers:
        Residential[layer] = 0
    for row in range(0,Residential.shape[0]):
        ID = Residential.loc[Residential.index[row],"GEOIDConn.NEAR_FID"]
        FinRow = Final.iloc[ID-1]
        TotalPop = FinRow["P2_002N"] + FinRow["P2_003N"]
        #By single race - Note, does not include the several other categories for race included in the census, and as a default race percentages will not sum to 1
        Residential.loc[Residential.index[row],"White alone"] = FinRow["P1_003N"]/TotalPop
        Residential.loc[Residential.index[row],"Black or African American alone"] = FinRow["P1_004N"]/TotalPop
        Residential.loc[Residential.index[row],"American Indian and Alaska Native alone"] = FinRow["P1_005N"]/TotalPop
        Residential.loc[Residential.index[row],"Asian alone"] = FinRow["P1_006N"]/TotalPop
        Residential.loc[Residential.index[row],"Native Hawaiian and Other Pacific Islander alone"] = FinRow["P1_007N"]/TotalPop
        #Hispanic/Not
        Residential.loc[Residential.index[row],"Hispanic or Latino"] = FinRow["P2_002N"]/TotalPop
        Residential.loc[Residential.index[row],"Not Hispanic or Latino"] = FinRow["P2_003N"]/TotalPop
        #Also Trees
        Residential.loc[Residential.index[row],"TreeGridCode"] = FinRow["mean_gridcode"]
    NEWGEOS = CGroup["GEOID"].drop_duplicates()
    GEOID20s = CGroup["GEOID"].drop_duplicates()
    GEOIDs_short= GEOID20s.str[:-1]
    NEWGEOS = GEOIDs_short.drop_duplicates()

    TEST = pd.DataFrame([])
    IMPORTDATA2 = pd.DataFrame([])
    print("Census Data part 2")
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    count = 0

    for GEOID in GEOID20s:
        query_url = 'https://api.census.gov/data/2021/acs/acs5?get=NAME,B02001_001E,B01001_002E,B01001_026E,B01002_001E&for=block%20group:*&in=state:'+str(GEOID[0:2])+'&in=county:'+str(GEOID[2:5])+'&in=tract:'+str(GEOID[5:11])+'&key=02f4845b752341af1ea0eb002636816107968ccb'
        DATTEST = (pd.read_csv(query_url))
        for row in range(0,DATTEST.shape[0]):
            rowdat = DATTEST.iloc[row]
            rowdat["state"] =str(GEOID[0:2])
            rowdat["county"] =str(GEOID[2:5])
            rowdat["tract"] = str(GEOID[5:11])
            try:
                if "]" in rowdat["block group]"]:
                    rowdat["block group]"] = rowdat["block group]"].split("]")[0]
            except:
                if "]" in rowdat["Unnamed: 9"]:
                    rowdat["block group]"] = rowdat["Unnamed: 9"].split("]")[0]
            DATTEST.iloc[row] = rowdat
        DATTEST["GEOID"] = DATTEST["state"].astype(str)+DATTEST["county"].astype(str)+DATTEST["tract"].astype(str)+DATTEST["block group]"].astype(str)#.str[:-1]
        IMPORTDATA = DATTEST[DATTEST.columns[1:(len(DATTEST.columns)-5)].values]
        IMPORTDATA["GEOID"] = DATTEST["GEOID"]
        IMPORTDATA2 = IMPORTDATA2.append(IMPORTDATA)
    CENSUSSEXDATA = IMPORTDATA2.reset_index().drop(["index"],axis=1)
    CENSUSSEXDATA = CENSUSSEXDATA.drop_duplicates().reset_index().drop(["index"], axis=1)
    CENSUSSEXDATA = CENSUSSEXDATA.rename(columns = {"B02001_001E":"Total","B01001_002E":"Male","B01001_026E":"Female","B01002_001E":"MedianAge"})

    #Need second half of census - Income primarily
    print("Census part 3")
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    NEWGEOS = CGroup["GEOID"].drop_duplicates()
    GEOID20s = CGroup["GEOID"].drop_duplicates()
    GEOIDs_short= GEOID20s.str[:5]
    FINALGEOs = GEOIDs_short.drop_duplicates()
    IMPORTDATA2 = pd.DataFrame([])
    for geo in FINALGEOs:
        query_url = 'https://api.census.gov/data/2021/acs/acs5?get=NAME,B19013_001E,B19001_001E,B19001_002E,B19001_003E,B19001_004E,B19001_005E,B19001_006E,B19001_007E,B19001_008E,B19001_009E,B19001_010E,B19001_011E,B19001_012E,B19001_013E,B19001_014E,B19001_015E,B19001_016E,B19001_017E&for=block%20group:*&in=state:'+str(geo[0:2])+'&in=county:'+str(geo[2:5])+'&key=02f4845b752341af1ea0eb002636816107968ccb'
        DATTEST = (pd.read_csv(query_url))
        for row in range(0,DATTEST.shape[0]):
            rowdat = DATTEST.iloc[row]
            if "]" in rowdat["block group]"]:
                rowdat["block group]"] = rowdat["block group]"][:-1]
            rowdat["tract"] = str(rowdat["tract"])
            while (len(rowdat["tract"]) <6):
                rowdat["tract"] = "0"+rowdat["tract"]
                #print(rowdat["tract"])
            DATTEST.iloc[row] = rowdat
        DATTEST["GEOID"] = DATTEST["state"].astype(str)+DATTEST["county"].astype(str)+DATTEST["tract"].astype(str)+DATTEST["block group]"].astype(str)
        IMPORTDATA = DATTEST[DATTEST.columns[1:(len(DATTEST.columns)-5)].values]
        IMPORTDATA["GEOID"] = DATTEST["GEOID"]
        IMPORTDATA2 = IMPORTDATA2.append(IMPORTDATA)

    CENSUSINCOMEDATA = IMPORTDATA2.reset_index().drop(["level_0","level_1"],axis=1)
    CENSUSINCOMEDATA = CENSUSINCOMEDATA.rename(columns = {
        "B19013_001E":"MedianIncome",
        "B19001_002E":"Less than $10,000",
        "B19001_003E":"$10,000 to $14,999",
        "B19001_004E":"$15,000 to $19,999",
        "B19001_005E":"$20,000 to $24,999",
        "B19001_006E":"$25,000 to $29,999",
        "B19001_007E":"$30,000 to $34,999",
        "B19001_008E":"$35,000 to $39,999",
        "B19001_009E":"$40,000 to $44,999",
        "B19001_010E":"$45,000 to $49,999",
        "B19001_011E":"$50,000 to $59,999",
        "B19001_012E":"$60,000 to $74,999",
        "B19001_013E":"$75,000 to $99,999",
        "B19001_014E":"$100,000 to $124,999",
        "B19001_015E":"$125,000 to $149,999",
        "B19001_001E":"EstTotalPop",
        "B19001_016E":"$150,000 to $199,999",
        "B19001_017E":"$200,000 or more"})
    #Rename Columns:

    print("Connecting Census Data, please hold")
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    Newrows = ["PMale","PFemale","MedianAge"]
    Residential[Newrows] = 0
    Newrows = CENSUSINCOMEDATA.columns[:-1].values
    Residential[Newrows] = 0
    for row in range(0,Residential.shape[0]):
        ##Rowind ##
        ID = Residential.at[Residential.index[row],"GEOIDConn_GROUP.NEAR_FID"]
        FinRow = CGroup.iloc[ID]
        ID2 = FinRow["GEOID"]
        incomerow = CENSUSINCOMEDATA[CENSUSINCOMEDATA["GEOID"]==ID2]
        incomerow = incomerow[incomerow.columns[1:-2]]
        sexrow  = CENSUSSEXDATA[CENSUSSEXDATA["GEOID"]==ID2]
        try:
            Residential.at[Residential.index[row],"PMale"] = float(sexrow["Male"])/float(sexrow["Total"])
            Residential.at[Residential.index[row],"PFemale"] = float(sexrow["Female"])/float(sexrow["Total"])
            Residential.at[Residential.index[row],"MedianAge"] = float(sexrow["MedianAge"])
        except:
            Residential.loc[Residential.index[row],"PMale"] = float(sexrow["Female"])/float(sexrow["Male"])
            Residential.loc[Residential.index[row],"PFemale"] = float(sexrow["MedianAge"])/float(sexrow["Male"])
            Residential.loc[Residential.index[row],"MedianAge"] = "NA"
        for value in incomerow:
            try:
                Residential.at[Residential.index[row],value] = float(incomerow[value])
            except Exception as e:
                Residential.loc[Residential.index[row],value] = "NA"

    if "level_2" in Residential.columns:
        Residential = Residential.drop(["level_2"],axis=1)
    Newrows = CENSUSINCOMEDATA.columns[1:-1].values
    for row in Newrows:
        Residential = Residential[Residential[row] != "NA"]
        Residential = Residential[Residential[row] != -666666666]
        Residential[row] = Residential[row].astype(float)

        Cols = Residential.columns[26:-1]
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    for row in range(0,Residential.shape[0]):
        try:
            POP   = float(Residential.at[Residential.index[row],"EstTotalPop"])
            for col in Cols:
                if POP != 0:
                    Residential.at[Residential.index[row],col] = int(Residential.at[Residential.index[row],col])/POP  
        except Exception as e:
            pass #Not good coding practice, but we're just skipping block groups that have no population, which is what we want to do anyways
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    Residential = Residential.drop(["state"],axis=1)
    Residential.to_csv("Residential.csv")
    for fc in arcpy.ListFeatureClasses():
        if fc == "BuildingsNoSmall":
            x=1
            arcpy.AddField_management(fc, "HouseIdent", "FLOAT")
            with arcpy.da.UpdateCursor(fc, "HouseIdent") as cursor:
                ResLoc = 0
                if "OBJECTID" in Residential.columns:
                    ObjectIDs = Residential["OBJECTID"]
                    for row in cursor:
                        if ResLoc < len(ObjectIDs) and x == ObjectIDs[ResLoc]:
                            row[0] = Residential.loc[ResLoc,"House"]
                            ResLoc +=1
                        cursor.updateRow(row)
                        x+=1
                else:
                    for row in cursor:
                        if x in Residential.index:
                            row[0] = Residential.loc[x,"House"]
                            cursor.updateRow(row)
                        x+=1
            for fieldval in Residential.columns[12:]:
                x=1
                ResLoc = 0
                field = "_".join("_".join("_".join("_".join("_".join(fieldval.split(" ")).split("$")).split(",")).split(")")).split("("))
                arcpy.AddField_management(fc, field, "FLOAT")
                with arcpy.da.UpdateCursor(fc, field) as cursor:
                        try:
                            ObjectIDs = Residential["OBJECTID"]
                        except:
                            ObjectIDs = Residential.index
                        for row in cursor:
                            if ResLoc < len(ObjectIDs) and x == ObjectIDs[ResLoc]:
                                val = Residential.loc[x,fieldval]
                                if val != "NA":
                                    row[0] = Residential.loc[x,fieldval]
                                    ResLoc +=1
                            cursor.updateRow(row)
                            x+=1
    ResidentialPoly = arcpy.management.SelectLayerByAttribute("BuildingsNoSmall", 'NEW_SELECTION', '"HouseIdent" > 0')
    arcpy.management.CopyFeatures(ResidentialPoly, 'ResidentialBuildings')
    arcpy.SelectLayerByAttribute_management("BuildingsNoSmall", "CLEAR_SELECTION")
    print("Done!")
    timenow = time.time()
    print("Time Elapsed: " +str(timenow - timeZero))
    Residential.to_csv("Residential.csv")
    
    #Converting Local Vars to Global
    l = list(locals().items())
    return(l)
    for val in l:
        print(val)
        if lyrTest in val:
            print(val)
            globals().update(val)
    return(Residential)
def mapping(summary,Residential):
    clear_output(wait=False)
    time.sleep(.3)
    print("Unfortunately, I was unable to find time to automate map updating depending on the variable you choose. Instead, this function updates your map, specifically the Final Outputs layer, to have all of the variables in a given summary")
    print("It also adds a new variable, 'Prediction', which uses the summary to plot the predicted median income of each residential building")
    PARAMS = list(summary.params.index.values)
    Residential["Constant"] = 1
    for fc in arcpy.ListFeatureClasses():
        if fc == "ResidentialBuildings":
            for param in PARAMS:
                x=1
                #print(param)
                splits = param.split(" x ")
                if len(splits) >1:
                    Residential[param] = Residential[splits[0]] * Residential[splits[1]]
                    arcpy.AddField_management(fc, str(splits[0]+"x"+splits[1]), "FLOAT")
                    ResLoc = 0
                    with arcpy.da.UpdateCursor(fc,str(splits[0]+"x"+splits[1])) as cursor:
                            try:
                                ObjectIDs = Residential["OBJECTID"]
                            except:
                                ObjectIDs = Residential.index
                            for row in cursor:
                                if ResLoc < len(ObjectIDs) and x == ObjectIDs[ResLoc]:
                                    val = Residential.loc[x,param]
                                    if val != "NA":
                                        row[0] = Residential.loc[x,param]
                                        ResLoc +=1
                                    else:
                                        print(x,param)
                                cursor.updateRow(row)
                                x+=1
                else:
                    Residential[param] = Residential[splits[0]]
                    arcpy.AddField_management(fc, str(param), "FLOAT")
                    ResLoc = 0
                    with arcpy.da.UpdateCursor(fc,str(param)) as cursor:
                            try:
                                ObjectIDs = Residential["OBJECTID"]
                            except:
                                ObjectIDs = Residential.index
                            for row in cursor:
                                if ResLoc < len(ObjectIDs) and x == ObjectIDs[ResLoc]:
                                    val = Residential.loc[x,param]
                                    if val != "NA":
                                        row[0] = Residential.loc[x,param]
                                        ResLoc +=1
                                    else:
                                        print(val)
                                cursor.updateRow(row)
                                x+=1
            Residential["Predict"] = summary.predict()
            x = 1
            #Residential[param] = Residential[splits[0]]
            arcpy.AddField_management(fc, "Predict", "FLOAT")
            ResLoc = 0
            with arcpy.da.UpdateCursor(fc,"Predict") as cursor:
                    try:
                        ObjectIDs = Residential["OBJECTID"]
                    except:
                        ObjectIDs = Residential.index
                    for row in cursor:
                        if ResLoc < len(ObjectIDs) and x == ObjectIDs[ResLoc]:
                            val = Residential.loc[x,"Predict"]
                            if val != "NA":
                                row[0] = Residential.loc[x,"Predict"]
                                ResLoc +=1
                            else:
                                print(val)
                        cursor.updateRow(row)
                        x+=1
            Residential["PredictionDifference"] = summary.predict() - Residential["MedianIncome"]
            x = 1
            #print("PredictionDifference")
            #Residential[param] = Residential[splits[0]]
            arcpy.AddField_management(fc, "PredictionDifference", "FLOAT")
            ResLoc = 0
            with arcpy.da.UpdateCursor(fc,"PredictionDifference") as cursor:
                    try:
                        ObjectIDs = Residential["OBJECTID"]
                    except:
                        ObjectIDs = Residential.index
                    for row in cursor:
                        if ResLoc < len(ObjectIDs) and x == ObjectIDs[ResLoc]:
                            val = Residential.loc[x,"PredictionDifference"]
                            if val != "NA":
                                row[0] = Residential.loc[x,"PredictionDifference"]
                                ResLoc +=1
                            else:
                                print(val)
                        cursor.updateRow(row)
                        x+=1
            arcpy.management.CopyFeatures(fc, 'FinalOutputs')
            arcpy.management.Delete("MapofBuildings")
            print("The layer 'Final Outputs' has been updated!")
    return(Residential,summary)
#Main#
menu = {}
menu['1']="Set Up Regression" 
menu['2']="Choose and Run Regression"
menu['3']="Update Map"
menu['4']="Exit"
ChosenVar = ["MedianIncome","Infrastructure Variables",'.01','10','.6']

while True: 
    options = menu.keys()
    #options.sort()
    print("**************************************")
    for entry in options: 
        print(entry, menu[entry])
    print("**************************************")
    selection=input("Please Select:  ")
    
    if selection =='1' or selection==menu['1']: 
        print("Setting up Analysis")
        Residential = setup()
        #Need to rename vars for final regressions
    elif selection == '2'or selection==menu['2']: 
        print("Running Regression")
        ChosenVar,Residential,summary = regression(ChosenVar)
        clear_output(wait=False)
        time.sleep(.3)
        #Setup regression choices
    elif selection == '3'or selection==menu['3']:
        print("Updating Map") 
        Residential,summary = mapping(summary, Residential)
        #Allow for choice of var
    elif selection =='4':
        break
    else: 
        print("Unknown Option Selected!") 
        break
#NEed to make "How to" file as welll