#system libraries
import time
start_time = time.time()

import datetime
import zipfile
import shutil
import math
import math
import sys
from importlib import reload
import os
#for matrix computations
import numpy as np
from numpy import ma
np.set_printoptions(threshold=sys.maxsize)
#for image segmentation
from skimage.color import rgb2gray
from skimage.filters import sobel
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
#for downloading Sentinel imagery
from sentinelsat import SentinelAPI
#for working with geospatial data
from osgeo import gdal,ogr, gdalnumeric, osr, gdal_array
#helping classes
import tridy
from tridy import Imagee,Grid
#for plotting
import matplotlib.pyplot as plt
#for curiosity
from scipy.stats import wasserstein_distance
from mpi4py import MPI

#in case of development reimport
del(Imagee,Grid)
reload(tridy)
from tridy import Imagee,Grid


#helping function that creates regular grid from affine transformation parameters
def grid_from_affine_transformation(imagee):
    return Grid((imagee.get_metadata()['affine_transformation'][0],imagee.get_metadata()['affine_transformation'][3]),(imagee.get_metadata()['affine_transformation'][1],imagee.get_metadata()['affine_transformation'][5]),*imagee.get_data().shape)


#helping function that is used to select just segments that have land use homogenity over given percentage
def select_segment_lu(intersecting_features,percentage):
    for i in range(len(intersecting_features)):
        if i==0:
            dictionar=intersecting_features[i]
        else:
            key=list(intersecting_features[i].keys())[0]
            if key in list(dictionar.keys()):
                dictionar[key]=dictionar[key]+intersecting_features[i][key]
            else:
                dictionar[key]=intersecting_features[i][key]
    for key in dictionar.keys():
        if dictionar[key]/np.sum(list(dictionar.values())) >= percentage:
            return key
        else:
            return '0'


#definition of working directory and tiles that are needed
data_folder='/lustre/cray/ws9/6/ws/xeupmara-euxdat/josemu/'
tiles_needed=['33UWS','33UUQ','33UUR','33UUS','33UVP','33UVQ','33UVR','33UVS','33UWQ','33UWR','32UQA','33UXP','33UXQ','33UXR','33UYQ','33UYR']


#opening Czech cadaster shapefile
cadaster = '/lustre/cray/ws9/6/ws/xeupmara-euxdat/josemu/ruian_pos.shp'
driver = ogr.GetDriverByName('ESRI Shapefile')
dataSource = driver.Open(cadaster, 0) 
layer = dataSource.GetLayer()
area_field_index=layer.FindFieldIndex('area',True)
lu_field_index=layer.FindFieldIndex('lu_type',True)


comm = MPI.COMM_WORLD
size = comm.Get_size()
N= len(tiles_needed)
count = int(N / comm.size) 
remainder = N%comm.size    
endloop=0

if comm.rank < remainder:
    start_tile = int(comm.rank * (count + 1))
    stop_tile = int(start_tile + count)

else:
    start_tile = int(comm.rank * count + remainder)
    stop_tile = int(start_tile + (count - 1))


#iterate through all needed tiles

#for tile in tiles_needed:

#print(size)
print("Hello from rank" + str(comm.rank))

for tile_index in range(start_tile,stop_tile+1,1):
    if tile_index == (stop_tile+1):
        endloop=1
    tile=tiles_needed[tile_index]
    print("Procssing tile " + tile)
 
    #open three needed bands
    ds_b2=gdal.Open(data_folder+tile+'/'+[i for i in os.listdir(data_folder+tile) if i.endswith('b2.jp2')][0])
    ds_b4=gdal.Open(data_folder+tile+'/'+[i for i in os.listdir(data_folder+tile) if i.endswith('b4.jp2')][0])
    ds_b8=gdal.Open(data_folder+tile+'/'+[i for i in os.listdir(data_folder+tile) if i.endswith('b8.jp2')][0])
    #creating image metadata dictionary
    metadata_dict={}
    metadata_dict['affine_transformation']=ds_b2.GetGeoTransform()
    if ds_b2.GetRasterBand(1).GetNoDataValue() is not None:
        metadata_dict['nodata']=ds_b2.GetRasterBand(1).GetNoDataValue()
    else:
        metadata_dict['nodata']=0
    if ds_b2.GetProjection() is not None:
        metadata_dict['proj_wkt']=ds_b2.GetProjection()
    else:
        metadata_dict['proj_wkt']='GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
    #create Imagee objects from three needed bands
    im_b2=Imagee(np.array(ds_b2.GetRasterBand(1).ReadAsArray()),metadata_dict)
    im_b4=Imagee(np.array(ds_b4.GetRasterBand(1).ReadAsArray()),metadata_dict)
    im_b8=Imagee(np.array(ds_b8.GetRasterBand(1).ReadAsArray()),metadata_dict)
    #create grid object from affine transformation parameters
    g=grid_from_affine_transformation(im_b2)
    #create iterator that splits the whole image into patches 1000x1000 pixels, iterate through and add all subgrids to the array
    it=g.iterate_grid([1000*10,1000*-10])
    subgrids=[]
    for i in it:
        subgrids.append(i)
    #for patch 1000x1000 pixels in image check if it isn't totally masked anf if yes skip patch
    for subgrid in subgrids:
        if im_b2.get_data()[subgrid[1],subgrid[2]].mask.all():
            continue
        else:
            #create Imagee objects from the data for the given patch for each of the three bands
            im_b2_c=Imagee(im_b2.get_data()[subgrid[1],subgrid[2]],{**metadata_dict,**{'affine_transformation':subgrid[0].get_affinetransformation()}})
            im_b4_c=Imagee(im_b4.get_data()[subgrid[1],subgrid[2]],{**metadata_dict,**{'affine_transformation':subgrid[0].get_affinetransformation()}})
            im_b8_c=Imagee(im_b8.get_data()[subgrid[1],subgrid[2]],{**metadata_dict,**{'affine_transformation':subgrid[0].get_affinetransformation()}})
            #stack the bands
            b_all=np.dstack((im_b4_c.get_data(),im_b8_c.get_data(),im_b2_c.get_data()))
            #run slic segmentation algorithm
            segments_slic = slic(b_all, n_segments=round(math.sqrt(ma.count(im_b2_c.get_data()))*1.5), max_iter=100, compactness=0.5, sigma=1, multichannel=True, convert2lab=True, enforce_connectivity=True, min_size_factor=0.03, max_size_factor=5, slic_zero=True)
            #create Imagee object from identified segments
            segments=Imagee(segments_slic,im_b2_c.get_metadata())
            #combine information about pixel values in bands and in which segment they lie
            c=np.dstack((b_all,segments.get_data()))
            #vectorize segment data
            segments_polygons=gdal_array.OpenNumPyArray(segments.get_data(),binterleave=True )
            segments_polygons.SetGeoTransform(segments.get_metadata()['affine_transformation'])
            segments_polygons.SetProjection(segments.get_metadata()['proj_wkt'])
            srs=osr.SpatialReference()
            srs.ImportFromWkt(segments.get_metadata()['proj_wkt'])
            outDriver=ogr.GetDriverByName('MEMORY')
            outDataSource=outDriver.CreateDataSource('memData')
            outLayer = outDataSource.CreateLayer("data", srs,geom_type=ogr.wkbPolygon)
            pixel_value = ogr.FieldDefn("pixel_value", ogr.OFTInteger)
            outLayer.CreateField(pixel_value)
            gdal.Polygonize( segments_polygons.GetRasterBand(1) , None, outLayer, 0)
            #create empty values matrix where the data about pixel values distribution (histogram) and Y variable(land use class) will be stored
            values_matrix=np.empty((1,151))
            #for each segment find intersecting parcels from cadaster and test if they are more then 80% homogenous (covered more than 80% with the same lu type) and if yes add the their pixel values distribution and land use class to the values matrix
            for poly in range(outLayer.GetFeatureCount()):
                poly=outLayer.GetNextFeature()
                layer.SetSpatialFilter(poly.GetGeometryRef())
                intersecting_features=[]
                for i in range(layer.GetFeatureCount()):
                    feat=layer.GetNextFeature()
                    if (feat.GetGeometryRef()).Intersects(poly.GetGeometryRef()):
                        intersecting_features.append({feat.GetFieldAsString(lu_field_index):feat.GetFieldAsInteger(area_field_index)})
                if len(intersecting_features)==0:
                    continue
                elif select_segment_lu(intersecting_features,0.8)=='0':
                    continue
                else:
                    pixel_values=c[np.where(c[:,:,3]==poly.GetFieldAsInteger(0))]
                    hist1,bins=np.histogram(pixel_values[:,0],50,(0,5000),density=True)
                    hist2,bins=np.histogram(pixel_values[:,1],50,(0,5000),density=True)
                    hist3,bins=np.histogram(pixel_values[:,2],50,(0,5000),density=True)
                    values_matrix=np.vstack((values_matrix,np.append(np.concatenate((hist1,hist2,hist3)),int(select_segment_lu(intersecting_features,0.8)))))
            #if value_matrix is not empty save it in npy format
            if len(values_matrix)>1:
                np.save('values_%s_%s.npy' % (subgrid[0].get_gridorigin()[0],subgrid[0].get_gridorigin()[1]),values_matrix[1:,])
            #delete not needed anymore objects
            del(outDriver,outDataSource,outLayer)
            #rest reading for the layer with cadastral data
            layer.ResetReading()



print("---Execution time %s seconds ---" % (time.time() - start_time))
