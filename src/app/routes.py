from __future__ import print_function
from app import app
import json
import sys
import numpy as np
from app.analytics.c import DB_Storage, OLU_Feature,  Imagee
from flask import request,  send_file
from io import BytesIO

np.set_printoptions(threshold=sys.maxsize)

#initialize db storage of OLU features
raster_file='/home/dima/Documents/data/eu_dem_wv_3857.tif' # add correct file_location
dbs=DB_Storage({'dbname':'gis','user':'postgres','host':'localhost','port':'5432','password':'postgres'}) # change to correct connection string
dbs.connect()

@app.route('/get_fields_geometry', methods=['GET'])
def get_params_of_get_fields_geometry():
    bbox = str(request.args.get('bbox'))
    return get_fields_geometry(bbox)
def get_fields_geometry(bbox):
    r=dbs.read_olu_features('elu_austria','at30810',bbox)
    return json.dumps(r)
    
@app.route('/get_field_statistics', methods=['GET'])
def get_params_of_get_field_statistics():
    id = int(request.args.get('id'))
    return get_field_statistics(id)
def get_field_statistics(id, onfly=False):
    if onfly==False:
        r=dbs.read_field_statistic(id)
        return json.dumps(r.json())
    else:
        return print('this time onfly generation is not supported .')
'''
@app.route('/get_field_raster', methods=['GET'])
def get_params_of_get_field_raster():
    id = int(request.args.get('id'))
    kind = str(request.args.get('kind'))
    output = str(request.args.get('output'))
    return get_field_raster(id, kind, output)
def get_field_raster(id,kind, output, onfly=False):
    if onfly==False:
        if  output=='image':
            image=dbs.read_raster(id, kind)
            buffer = BytesIO()
            buffer.write(image)
            buffer.seek(0)
            return send_file(image,attachment_filename="image.tif", as_attachment=True)
        elif output=='wms':
            wms=dbs.read_field.generate_wms(id, kind)
            return wms
        else:
            return print('this output type is not supported .')
    else:
        return print('this time onfly generation is not supported .')'''
    
