########################################################################################################
#Purpose: Clones a web map and replaces some layers if specified in the code. Other layers remain in the
#application.
#Date Created: 4-27-22
#Author: Paul McCord
########################################################################################################


from arcgis.gis import GIS
from arcgis.mapping import WebMap
import json

"""
The below cloning process has encountered several problems:
1) A primary and significant obstacle is that to "swizzle" layers when cloning, the itemID is needed witin the
dictionary object. However, in this situation all layers (source and target) are actually sublayers under a 
parent layer (e.g., wHydrants, wMains, etc under the WaterDistribution feature layer). As a result, all sub-
layers have the same itemID as their parent.

2) I tried to simply force the clone_items() function to work. In my item mapping dictionary, I used the top-
level feature layer itemIDs (ie, {old Sanitary Network: new Sanitary Network, old Water Network: new
 Water Network, old Storm Network: new Storm Network}). I also removed all layers from Oak Co, SEMCOG, etc.
 (in other words, all layers not owned by AH AGO). When doing this, the script ran to completion, but the
 swizzle process (item mapping) only mapped some layer correctly.

#*Ideas to try:
#*1) Try to get the clone to work by cloning to the OHM AGO and then cloning back to the AH AGO.
#*2) Use the Python API and try to substitute in the URL for the new layer by navigating through the JSON <-- TRY THIS FIRST

#?The map that is used to develop a cloning solution is called Test_Start_Clone_Map (583f0bb89b3440809dd43abf2cb308f7).
#?This map is located in the Utility Viewer folder.
#?The map has several sub-layers from the Water, Sanitary, and Storm feature layers.
#?Below the corresponding new layers are listed as these are the layers that I attempt to replace the existing layers with.
"""


def inspect_map_lyrs(web_map):
    """
    Prints the layer name and item ID for every layer in the map

    Args: Web Map that is being cloned

    Returns: Does not return an object or value    
    """
    print(f"{'Layer Name':<33}{'Item ID'}\n" f"{'-'*28:<30}{'-'*37}")
    for layer in web_map.layers:
        layer_dict = dict(layer).keys()
        name = layer.title
        if "url" not in layer_dict:
            url = "No Item URL"
            
        else:
            url = layer.url
        print(f"{name[:30]:33} {url}")

def map_layers():
    """
    Creates a dictionary of key, value pairs where the key is the URL of the Existing Operational Layer in the web map and the value is the
    URL of the layer that will replace the Existing Operational Layer.

    The service URLs are stored in a separate text file to save space.

    Args: None

    Output: Dictionary of key, value pairs for Web Map urls
    """

    #layer ids are mapped by hand as automation isn't possible without knowing layer names
    #*Below are the URLs of the existing operational layers that will be replaced as well as the URLs of the layers that will be substituted into the map:
    #*Fire Hydrant: Existing- https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/Water_Utility/FeatureServer/5; Replacing - https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/WaterDistributionSystem_viewing_866f1c7920b543ebb8f17f1de64a0882/FeatureServer/501007
    #*wFitting: Existing- https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/Water_Utility/FeatureServer/4; Replacing - https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/WaterDistributionSystem_viewing_866f1c7920b543ebb8f17f1de64a0882/FeatureServer/510020
    #*wServiceLine: Existing- https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/Water_Utility/FeatureServer/10; Replacing - https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/WaterDistributionSystem_viewing_866f1c7920b543ebb8f17f1de64a0882/FeatureServer/515002
    #*wMain: Existing- https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/Water_Utility/FeatureServer/8; Replacing - https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/WaterDistributionSystem_viewing_866f1c7920b543ebb8f17f1de64a0882/FeatureServer/515001
    #*ssManhole: Existing- https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/Sewer_Utility/FeatureServer/5; Replacing - https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/SewerSystem_viewing_a8e714c76ab5468e81e3dce56428383f/FeatureServer/900209
    #*ssGravityMain: Existing- https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/Sewer_Utility/FeatureServer/10; Replacing - https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/SewerSystem_viewing_a8e714c76ab5468e81e3dce56428383f/FeatureServer/315001
    #*swManhole: Existing- https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/Storm_Utility/FeatureServer/6; Replacing - https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/StormwaterSystem_viewing_612c8866150f4165ba732201a9233209/FeatureServer/900208
    #*swGravityMain: Existing- https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/Storm_Utility/FeatureServer/10; Replacing - https://services5.arcgis.com/fkLHZg2ojpDnVAod/arcgis/rest/services/StormwaterSystem_viewing_612c8866150f4165ba732201a9233209/FeatureServer/415004
    #wm_lyr_mapping = {'7b7f532717f942e18f6057f7bdf49603': 'fc4be67509b244a2afd896fa6a71ea2a', <- Used as part of previous cloning test... keep for now
    #                'c63d28416085496ab879c9f220512f6f': '4b47eb2f4e464409baf912b7a8c10ec6',  <- Used as part of previous cloning test... keep for now
    #                '552267e9927644db9182557e55fd2069': 'aba51f1fb4584b6689b99b347c22651f'}  <- Used as part of previous cloning test... keep for now
    wm_lyr_mapping = {}
    file_path = r"C:\Users\pmccord\Scripts\Python\CloningContent\AuburnHills\files\layer_mapping.txt"
    with open(file_path) as fle:
        for line in fle:
            key, value = line.strip().split(None, 1)
            wm_lyr_mapping[key] = value.strip()

    return wm_lyr_mapping


def replace_layers(web_map, lyr_dict):
    """
    Replaces the specified existing operational layer URL with the URL to the new layer

    Args: Web Map where layers will be replaced. Item "mapping" dictionary specifying existing (within web map) and replacing (layer to be
    substituted into web map) layers.

    Output: Finalized web map with appropriate layers replaced. 
    """
    for layer in web_map.layers:
        for key, value in lyr_dict.items():
            if layer['url'] == key:
                layer['url'] = layer['url'].replace(key, value)
                #gis.update_properties(web_map.layers)
    web_map.update()
            


if __name__ == "__main__":

    #log into AH AGO
    gis = GIS(url="https://auburnhills.maps.arcgis.com/", profile="auburnhills_ago")

    #get content to be cloned
    web_map_item = gis.content.get("81dc0ea72aab4dc59bac874e4afdc33a")
    web_map_lyr_replace = WebMap(web_map_item)

    inspect_map_lyrs(web_map_lyr_replace)
    wm_lyr_mapping = map_layers()
    replace_layers(web_map_lyr_replace, wm_lyr_mapping)

    """
    try:
        gis.content.clone_items([map_to_clone_item], "Utility Viewer", copy_data=False, item_mapping=wm_dict)
    except:
        print("error occurred")
    """
    




