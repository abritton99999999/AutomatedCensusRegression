# AutomatedCensusRegression
How to use the Automated Census Collection and Regression System:
Thank you for using this project. This code comes in several distinct parts, which this overview will walk you though to eliminate as many headaches as possible. To use this project, you will need the following:
1.	A google drive account, and
2.	Access to ArcGIS Pro
I hope you enjoy!
Austin Ray Britton
Google Earth Engine Instructions:
Access to the code: https://code.earthengine.google.com/dfc5bcd049d8344e0b61376cdf1d0323
Using this code, you will be met with a small UI on the bottom left. Click “Choose Input Building”, and select a location in which you wish to analyze. As a default this location will become the center of a 5 km square. After selection a red dot will appear, and the “Calculate” button will be able to be pressed. If you wish to change your location, simply click “Choose Input Building” again, and choose on the map.

Once you click “Calculate”, the code will do several things. The first thing you will notice is that several layers have been added to the map, although the only one visible is a true color image of the 5 km square. The other layers are:
Tree Raster – A manually calculated TIF of tree locations, using the true color image.
CensusBlockGroupSquare – A shapefile of the census block group outlines.
CensusBlockSquare – A shapefile of the census block outlines.
RoadNetwork – A map of all the roads within the 5 km square
Buildings – A shapefile of all building shapes within the 5 km square
Each of these layers comes with accompanying data, some of which we will utilize in ArcGIS. You will notice in the top right that the tab “Tasks” has be lit up, and is populated with several files. For each of these tasks you will have to hit “Run” twice. These files will take time to download [15-20 minutes], and will be saved in your google drive under the folder “Project Outputs”. It’s important to note that this time estimate will vary, as the speed is dependent on Google’s servers, and is not quick at the best of times.
Once all of the files are finished, you can go to google drive and download the folder to your local computer. Once the folder is downloaded, export all files to uncompress the folder, but it’s recommended to keep all of the files in the same folder.
Make a note of the folder it’s saved in, as well as the entire path of the files, minus the drive that it’s saved on. For example, my files are saved in:
“/Users/Username/Downloads/Project Outputs/”
It’s important to note the use of the forward slash, as well as the slash at the beginning and end of the path. This ensures that the ArcGIS code can find your files with ease.

ArcGIS Instructions:
Link to Python Code:
When you first load ArcGIS, you will be under the default ArcGIS environment and packages, unless you have modified this before. In order to run this project successfully, you will need to install the following packages: skicit-learn and statsmodels.
To do this requires a few steps. First, under the left hand menu, select “Package Manager”. Then, next to the “Active Environment” text you will see what environment you currently have selected. Select the gear next to this. This will allow you to see what environments you have created. Hover over the default environment, and select the “Clone Environment”. Name this whatever you choose, and wait for the clone process to finish. 
After the new clone as been created, select the gear again, and change your active environment to the new environment. You will have to restart ArcGIS for this change to take effect.
Once your new environment is active, go back to the “Package Manager” tab, and select “Add Packages” from the top. Search for the two modules above, and wait as each module and their dependents are installed. You may have to restart ArcGIS after these downloads for them to take effect.
Now that your environment is set up, you can run the rest of the project. 
Create a new project, and once it is loaded, go to the “Insert” tab, and under projects, select “New Notebook”. Once this is loaded, paste in the code from the accompanying python file. Once you run this file, it will walk you through the several steps and options you can take!

Options within the Code:
Upon running the program you will be met with three options and a quit button. Typing the corresponding number or typing in the choice will select that option. 
Set up Regression: This will take your downloaded files, load in census data, and set up the project for any regression done. This process will take 15-20 minutes, depending on how fast the census data downloads. This API has variable speed.  This process will ask for the location of your files that you noted earlier.
After this has run, it will return you to the main menu.
Choose and Run Regression: This menu will allow you to modify the independent variables, the dependent variable, the VIF cutoff, the correlation coefficient cutoff, and the P-value cutoff. It will also allow you to run the regression when you are satisfied with your choice.
	Independent Variables: The variables present are separated into three categories, “Infrastructure”, “Population, and “Total”. The variables present are listed below:
		Infrastructure – Default choice. Variables are:
1.	SchoolDistance_NEAR_DIST – Distance from the nearest school
2.	Difference_from_Average_Area – the average area of all buildings minus the area of each building
3.	Highwaydist – The distance from the nearest highway. This includes both interstates and US highways.
4.	RoadDist – The distance from the nearest road, +1
5.	TreeGridCode – The average percentage of tree cover for a given census block.
6.	Dist_Lat – The median latitude of all buildings minus the latitude of a given house.
7.	Dist_Lon – The median longitude of all buildings minus the longitude of a given house.
8.	Apartment – An identifier if a building is an apartment or not. Apartments are 1, Single family homes are 0.
Population – Variables related to census data. While several census categories are not included, such as those who reported being of more than one race, the percentages were calculated by assuming these were the only categories, summing the available number of persons, and dividing by the sum. Variables are:
1.	White alone – Percentage of block that are only this race.
2.	Black or African American alone – Percentage of block that are only this race.
3.	American Indian and Alaska Native alone – Percentage of block that are only this race.
4.	Asian alone– Percentage of block that are only this race.
5.	Native Hawaiian and Other Pacific Islander alone – Percentage of block that are only this race.
6.	Hispanic or Latino – Percentage of block that are only this ethnicity. As opposed to race data, this percentage was calculated by summing those saying they are this ethnicity and saying they are not, and dividing.
7.	PMale – Percentage of block that are male. Note for the census only male and female are reported, and as a result this percentage does not include those who do not identify as male or female.
8.	MedianAge – Median age of census block
9.	EstTotalPop – Total population estimate in each census block.
Total – Both sets of variables combined. Note that running the regression using this choice will extend the time for the operations, as described below.

	Dependent Variables: The dependent variable will be an income bracket, and, besides the default of “Median Income”, is shown as a percentage of the population within a block group that are within that census group.
	VIF Cutoff: Default 10. This cutoff will determine the VIF at which variables are discarded above before a regression is run. A lower number constitutes a higher standard, and will result in more variables being removed.
	Correlation Coefficient Cutoff: Default .6. This cutoff determines the max correlation coefficient allowed between any two variables. The program will calculate this coefficient for each combination of independent variables. It will then eliminate the variable with the most coefficients above this cutoff, and repeat until there are no variables above this cutoff. This operation will be much longer for the “Total” selection of variables, and many more calculations are required. A lower number constitutes a higher standard, and will result in more variables being removed.
	P-Value Cutoff: This cutoff will determine the level of significance required in a final regression. The regression will remove variables as described below until all remaining variables are below this cutoff. A smaller number constitutes a higher standard, and will result in more variables being removed.
	Run Regression: This runs the regression. It will first run the correlation coefficient matrices, followed by the VIF test, followed by an OLS regression. The program will calculate the OLS regression, and remove the variable with the highest P-value. It will continue this process until all variables are below the specified P-Value Cutoff. Afte reaching this point it will output a printed summary, save that summary to a summary.txt file, and create a global variable that has all the summary information in it.

Update Map: This selection will take the summary variable as output from the regression, and add each remaining significant variable to a new layer titled “FinalOutputs”. It also includes two new variables, “Prediction”, and “DistanceFromPrediction”, which use the summary to calculate a prediction of each building’s median income, and then calculates the amount of error, respectively. 

