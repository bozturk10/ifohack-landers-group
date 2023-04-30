# ReadMe, Shimmer4382

## Feature Extraction
For the features we used data from the following two sources: 
1. Census 
2. OSM 

There are in essence three groups of variables that we extracted from these: 
1. Census Data 
   1. First, we averaged the census data across neighborhoods 
   2. Additionally, we created segreagtion measures based on 
      - age 
      - marital status 
      - nationality 
      These measures were computed by taking the so-called interaction measure. They were computed at the neighborhood level. 
2. OSM 
   3. Our third group of features stem from the OSM data. In this case, we exctracted all available amenitinies in a neighborhood and dropped those that were overwhelmingly missing.

### Clarification note
We additionally tried to get more features which didn't make it to the end model due to time constrains. Therefore, while inspecting the code you might notice we didn't make use of (parts) of the following files: `segregation.ipynb`, `connectedness_neighbourhoods.ipynb`. 

The first file also includes additional seggregation measures for...
- regligion,
- building year, and
- building size

The second intended to compute the walking distance from a centroid of a neighborhood to any possible stop of public transportation as a form of connectedness. 

## Model 
