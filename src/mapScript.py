import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pandas as pd
import os.path


# Initialize folium map over Berlin
map = folium.Map(location=[52.520008, 13.404954], tiles="OpenStreetMap", 
zoom_start=11, height="92%", prefer_canvas=True)


# Add Berlin Border Layer
# style1 = {'fillColor': '#228B22', 'lineColor': '#228B22'}
folium.GeoJson('./src/berlin_border.geojson'#, style_function=lambda x:style1
                # ,tooltip=None
                ).add_to(map)


# Add a title
title_html =    """
                <h5 align=”center”; margin-bottom=0px; padding-bottom=0px; style=”font-size:20px”><b>Berlin RepairCafé Map</b></h3>
                <h5 align=”center”; margin-top=0px; padding-top=0px; style=”font-size:14px”>Klick auf Positionsmarker zeigt Details an</h3>
                """
map.get_root().html.add_child(folium.Element(title_html))
map


# Read in Repair Cafe maps data
mapdata_dir = "./resources/mapdata/"
mapdatajson_files = [mapdata_dir + pos_json for pos_json in os.listdir(mapdata_dir) if pos_json.endswith('.json')]

cafes_df = pd.DataFrame()

for file in mapdatajson_files:
    data = pd.read_json(file, orient=str)#, lines=True)
    link = data['link']#.find('!3d')
    
    pos_lat = link.str.split('!3d')
    pos_lon = link.str.split('!4d')
    
    for i in range(0, len(pos_lon)):
        pos_lon[i] = pos_lon[i][1].partition('!')[0]
        pos_lat[i] = pos_lat[i][1].partition('!')[0]


    data['longitude'] = pos_lon
    data['latitude'] = pos_lat
    cafes_df = cafes_df.append(data, ignore_index = True)

cafes = gpd.GeoDataFrame(cafes_df, geometry=gpd.points_from_xy(cafes_df.longitude, cafes_df.latitude, crs=4326)).drop_duplicates()


# Create a marker for each cafe location. Format popup
marker_cluster = MarkerCluster().add_to(map)

for index, row in cafes.iterrows():
    html = f"""{row['title']}<br>
        <br>
        <strong>Adresse:</strong> {row['address']}<br>
        <br>
            """
    if row['phone'] != "":
        html = html + f"""<strong>Telefon:</strong> {row['phone']}<br>"""
    if row['website'] != "":
        html = html + f"""<br>Mehr Informationen zum Repair-Café gibt es auf der <a href={row['website']} target=”_blank”>Website</a><br>"""
    if row['categories'] != "":
        html = html + f"""<br>{row['categories']}<br>"""

    iframe = folium.IFrame(html,
                        width=200,
                        height=200)
    popup = folium.Popup(iframe,
                        max_width=400)
    folium.Marker(location=[row["latitude"], row["longitude"]],
                                            radius=10,
                                            color="#3186cc",
                                            fill=True,
                                            fill_color="#3186cc",
                                            popup=popup).add_to(marker_cluster)


# Update Map
map


# Save map
map.save("./index.html")