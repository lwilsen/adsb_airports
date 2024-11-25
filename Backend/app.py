from fastapi import FastAPI, Request
import pickle
from utils import cellToBbox, make_dfs
import os
from sentinelhub import SHConfig
from sentinelhub import (
    CRS,
    BBox,
    bbox_to_dimensions,
)

'''SENTINAL SETUP'''

CLIENT_ID = '139dda82-905a-4f6c-8aaa-3a6635c5216c'
CLIENT_SECRET = os.environ.get("SENTINAL_API_KEY")

config = SHConfig()

config.sh_client_id = CLIENT_ID
config.sh_client_secret = CLIENT_SECRET
config.save("my-profile")
    
'''Unpickling data sets'''
# Should try to access data sets through sqlite3

with open('gdf_all_res.pkl','rb') as f: #resolution = 10
    gdf = pickle.load(f)

'''Fast API'''

app = FastAPI()

@app.post("/map")
async def handle_request(request : Request):
    try:
        data = await request.json()

        if "Distance" in data.get('data'):

            params = data.get('data')
            
            DISTANCE = params["Distance"]
            RESOLUTION = params["Resolution"]
            SIGNIFICANCE = params["Resolution"]
# 
            h3_df, h3_gdf, geojson_obj_h3_gdf = make_dfs(DISTANCE, RESOLUTION, SIGNIFICANCE, Geom_DF = gdf)
            h3_df = h3_df.to_json(orient = "records")
            h3_gdf = h3_gdf.to_json()

            return {"h3_df": h3_df, "h3_gdf":h3_gdf, "geojson_obj_h3_gdf":geojson_obj_h3_gdf}
        
        elif "x_adjust" in data.get('data'):
            box_params = data.get("data")

            x_adjust = box_params["x_adjust"]
            y_adjust = box_params["y_adjust"]
            cell_id = box_params["cell_id"]
            tampa_box_cords = cellToBbox(cell_id,
                                 x_adjust = x_adjust, 
                                 y_adjust = y_adjust)
            tampa_res = 1
            tampa_bbox = BBox(bbox = tampa_box_cords, crs=CRS.WGS84)
            tampa_size = bbox_to_dimensions(tampa_bbox, resolution=tampa_res)
            
            box_coords_string = (f"Box coordinates: {tampa_box_cords}")

            if max(tampa_size) != 2500:
                new_res = max(tampa_size) / 2500
                tampa_bbox = BBox(bbox = tampa_box_cords, crs=CRS.WGS84)
                tampa_size = bbox_to_dimensions(tampa_bbox, resolution=new_res)
                new_res_string = (f"New Image shape at {new_res} m resolution: {tampa_size} pixels")

            evalscript_true_color = """
                //VERSION=3

                function setup() {
                    return {
                        input: [{
                            bands: ["B02", "B03", "B04"]
                        }],
                        output: {
                            bands: 3
                        }
                    };
                }

                function evaluatePixel(sample) {
                    return [sample.B04, sample.B03, sample.B02];
                }
            """
            print(type(tampa_bbox))
            print(type(tampa_size))
            for_st = {"evalscript_true_color":evalscript_true_color, 
                      "tampa_bbox":tampa_bbox, 
                      "tampa_size": tampa_size,
                      "bcords_str":box_coords_string,
                      "nw_rs_str":new_res_string}

            return(for_st)
    
    except Exception as e:
        
        return {"Error during map making": str(e), "data":data}
