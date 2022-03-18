import os
import ee
import geemap
import json
import requests
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from datetime import datetime
from datetime import timedelta
import rasterio as rio
from rasterio import plot
from rasterio import warp

try:
    ee.Initialize()
except: 
    ee.Authenticate()
    ee.Initialize()

class dataCollector:
    def __init__(self, beam=None, oaurl=None, track=None, date=None, latlims=None, lonlims=None, verbose=False):
        if (beam is None) or ((oaurl is None) and (None in [track, date, latlims, lonlims])):
            raise Exception('''Please specify a beam and 
            - either: an OpenAltimetry API url, 
            - or: a track, date, latitude limits and longitude limits.''')
        else:
            if oaurl is not None:
                url = oaurl
                tofind = '&beamName='
                ids = url.find(tofind)
                while ids>-1:
                    url = url.replace(url[ids:ids+len(tofind)+4],'')
                    ids = url.find(tofind)
                iprod = url.find('/atl')
                url = url.replace(url[iprod:iprod+6],'/atlXX')
                url += tofind + beam + '&client=jupyter'

                idate = url.find('date=') + len('date=')
                date = url[idate:idate+10]
                itrack = url.find('trackId=') + len('trackId=')
                trackend = url[itrack:].find('&')
                track = int(url[itrack:itrack+trackend])
                bb = []
                for s in ['minx=', 'maxx=', 'miny=', 'maxy=']:
                    ids = url.find(s) + len(s)
                    ide = url[ids:].find('&')
                    bb.append(float(url[ids:ids+ide]))
                lonlims = bb[:2]
                latlims = bb[2:]
            elif None not in [track, date, latlims, lonlims]:
                url = 'https://openaltimetry.org/data/api/icesat2/atlXX?'
                url += 'date={date}&minx={minx}&miny={miny}&maxx={maxx}&maxy={maxy}&trackId={track}&beamName={beam}'.format(
                        date=date,minx=lonlims[0],miny=latlims[0],maxx=lonlims[1],maxy=latlims[1],track=track,beam=beam)
                url += '&outputFormat=json&client=jupyter'
            
            self.url = url
            self.date = date
            self.track = track
            self.beam = beam
            self.latlims = latlims
            self.lonlims = lonlims
            if verbose:
                print('OpenAltimetry API URL:', self.url)
                print('Date:', self.date)
                print('Track:', self.track)
                print('Beam:', self.beam)
                print('Latitude limits:', self.latlims)
                print('Longitude limits:', self.lonlims)
            
    def requestData(self, verbose=False): 
        if verbose:
            print('---> requesting ATL03 data...',end='')
        product = 'atl03'
        request_url = self.url.replace('atlXX',product)
        data = requests.get(request_url).json()
        lat, lon, h, confs = [], [], [], []
        for beam in data:
            for confidence in beam['series']:
                for p in confidence['data']:
                    confs.append(confidence['name'])
                    lat.append(p[0])
                    lon.append(p[1])
                    h.append(p[2])
        self.atl03 = pd.DataFrame(list(zip(lat,lon,h,confs)), columns = ['lat','lon','h','conf'])
        if verbose:
            print(' Done.')
            
            print('---> requesting ATL06 data...',end='')
        product = 'atl06'
        request_url = self.url.replace('atlXX',product)
        data = requests.get(request_url).json()
        self.atl06 = pd.DataFrame(data['series'][0]['lat_lon_elev'], columns = ['lat','lon','h'])
        if verbose:
            print(' Done.')
            
            print('---> requesting ATL08 data...',end='')
        product = 'atl08'
        request_url = self.url.replace('atlXX',product)
        data = requests.get(request_url).json()
        self.atl08 = pd.DataFrame(data['series'][0]['lat_lon_elev_canopy'], columns = ['lat','lon','h','canopy'])
        if verbose:
            print(' Done.')
    
    ################################################################################################ 
    def plotData(self,ax=None,title='some Data I found on OpenAltimetry'):

        # get data if not already there
        if 'atl03' not in vars(self).keys(): 
            print('Data has not yet been requested from OpenAltimetry yet. Doing this now.')
            self.requestData(verbose=True)

        axes_not_specified = True if ax == None else False

        # create the figure and axis
        if axes_not_specified:
            fig, ax = plt.subplots(figsize=[10,6])
        atl03 = ax.scatter(self.atl03.lat, self.atl03.h, s=2, color='black', alpha=0.2, label='ATL03')
        atl06, = ax.plot(self.atl06.lat, self.atl06.h, label='ATL06')
        atl08, = ax.plot(self.atl08.lat, self.atl08.h, label='ATL08', linestyle='--')

        heights = self.atl03.h[self.atl03.conf != 'Noise']
        y_min1 = np.min(heights)
        y_max1 = np.max(heights)
        maxprods = np.nanmax((self.atl06.h.max(), self.atl08.h.max()))
        minprods = np.nanmin((self.atl06.h.min(), self.atl08.h.min()))
        hrange = maxprods - minprods
        y_min2 = minprods - hrange * 0.5
        y_max2 = maxprods + hrange * 0.5
        y_min = np.nanmin((y_min1, y_min2))
        y_max = np.nanmax((y_max1, y_max2))

        x_min = self.atl08.lat.min()
        x_max = self.atl08.lat.max()

        ax.set_xlim((x_min, x_max))
        ax.set_ylim((y_min, y_max))

        # label the axes
        ax.set_title(title)
        ax.set_xlabel('latitude')
        ax.set_ylabel('elevation in meters')

        # add a legend
        ax.legend(loc='lower right')

        # add some text to provide info on what is plotted
        info = 'ICESat-2 track {track:d}-{beam:s} on {date:s}\n({lon:.4f}E, {lat:.4f}N)'.format(track=self.track, 
                                                                                                beam=self.beam, 
                                                                                                date=self.date, 
                                                                                                lon=np.mean(self.lonlims), 
                                                                                                lat=np.mean(self.latlims))
        infotext = ax.text(0.03, 0.03, info,
                           horizontalalignment='left', 
                           verticalalignment='bottom', 
                           transform=ax.transAxes,
                           fontsize=7,
                           bbox=dict(edgecolor=None, facecolor='white', alpha=0.9, linewidth=0))

        if axes_not_specified:
            fig.tight_layout()
            return fig
        else:
            return ax

    ################################################################################################        
    def plotData_hv(self):
        import holoviews as hv
        from holoviews import opts
        hv.extension('bokeh', 'matplotlib')
        
        confdict = {'Noise': -1.0, 'Buffer': 0.0, 'Low': 1.0, 'Medium': 2.0, 'High': 3.0}
        self.atl03['conf_num'] = [confdict[x] for x in self.atl03.conf]
        self.atl08['canopy_h'] = self.atl08.h + self.atl08.canopy
        atl03scat = hv.Scatter(self.atl03, 'lat', vdims=['h', 'conf_num'], label='ATL03')\
                    .opts(color='conf_num', alpha=1, cmap='dimgray_r')
        atl06line = hv.Curve(self.atl06, 'lat', 'h', label='ATL06')\
                    .opts(color='r', alpha=0.5, line_width=3)
        atl08line = hv.Curve(self.atl08, 'lat', 'h', label='ATL08')\
                    .opts(color='b', alpha=1, line_width=1)
        atl08scat = hv.Scatter(self.atl08, 'lat', 'canopy_h', label='ATL08 Canopy')
        atl08scat = atl08scat.opts(alpha=1, color='g', size=4)
        hrange = self.atl06.h.max() - self.atl06.h.min()
        overlay = (atl03scat * atl06line * atl08line * atl08scat).opts(
            height=500, 
            width=800,
            xlabel='latitude', 
            ylabel='elevation', 
            title='ICESat-2 track %d %s on %s' % (self.track,self.beam.upper(),self.date),
            legend_position='bottom_right',
            ylim=(self.atl06.h.min()-hrange, self.atl06.h.max()+hrange),
            xlim=(self.atl06.lat.min(), self.atl06.lat.max())
        )
        return overlay
    
    ################################################################################################
    def makeGEEmap(self, days_buffer=25):

        # get data if not already there
        if 'atl03' not in vars(self).keys(): 
            print('Data has not yet been requested from OpenAltimetry yet. Doing this now.')
            self.requestData(verbose=True)

        def dist_latlon2meters(lat1, lon1, lat2, lon2):
            # returns the distance between two lat/lon coordinate points along the earth's surface in meters
            R = 6371000
            def deg2rad(deg):
                return deg * (np.pi/180)
            dlat = deg2rad(lat2-lat1)
            dlon = deg2rad(lon2-lon1)
            a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(deg2rad(lat1)) * np.cos(deg2rad(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            return R * c

        lat1, lat2 = self.atl08.lat[0], self.atl08.lat.iloc[-1]
        lon1, lon2 = self.atl08.lon[0], self.atl08.lon.iloc[-1]
        center_lat = (lat1 + lat2) / 2
        center_lon = (lon1 + lon2) / 2
        ground_track_length = dist_latlon2meters(lat1, lon1, lat2, lon2)
        print('The ground track is %d meters long.' % np.round(ground_track_length))

        collection_name1 = 'COPERNICUS/S2_SR'  # Sentinel-2 earth engine collection 
        # https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR

        collection_name2 = 'LANDSAT/LC08/C01/T2'  # Landsat 8 earth engine collection 
        # https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C01_T2
        # Note: Landsat 8 ingestion into Earth Engine seems to not have reached Antarctica yet, so using raw scenes...

        # the point of interest (center of the track) as an Earth Engine Geometry
        point_of_interest = ee.Geometry.Point(center_lon, center_lat)

        def query_scenes(self, days_buffer):
            # get the dates
            datetime_requested = datetime.strptime(self.date, '%Y-%m-%d')
            search_start = (datetime_requested - timedelta(days=days_buffer)).strftime('%Y-%m-%d')
            search_end = (datetime_requested + timedelta(days=days_buffer)).strftime('%Y-%m-%d')
            print('Search for imagery from {start:s} to {end:s}.'.format(start=search_start, end=search_end))

            # the collection to query: 
            # 1) merge Landsat 8 and Sentinel-2 collections
            # 2) filter by acquisition date
            # 3) filter by the point of interest
            # 4) sort by acquisition date
            collection = ee.ImageCollection(collection_name1) \
                .merge(ee.ImageCollection(collection_name2)) \
                .filterDate(search_start, search_end) \
                .filterBounds(point_of_interest) \
                .sort('system:time_start') 

            info = collection.getInfo()
            n_imgs = len(info['features'])
            print('--> Number of scenes found within +/- %d days of ICESat-2 overpass: %d' % (days_buffer, n_imgs))

            return (collection, info, n_imgs)

        # query collection for initial days_buffer
        collection, info, n_imgs = query_scenes(self, days_buffer)

        # if query returns more than 20 images, try to narrow it down
        tries = 0
        while (n_imgs > 20) & (tries<5): 
            print('----> This is too many. Narrowing it down...')
            days_buffer = np.round(days_buffer * 15 / n_imgs)
            collection, info, n_imgs = query_scenes(self, days_buffer)
            n_imgs = len(info['features'])
            tries += 1

        # if query returns no images, then return
        if n_imgs < 1: 
            print('NO SCENES FOUND. Try to widen your search by including more dates.')
            return

        # region of interest around the ground track (use this area to scale visualization factors)
        buffer_around_center_meters = ground_track_length/2
        region_of_interest = point_of_interest.buffer(buffer_around_center_meters)

        # make an earth engine feature collection from the ground track so we can show it on the map
        ground_track_coordinates = list(zip(self.atl08.lon, self.atl08.lat))
        ground_track_projection = 'EPSG:4326' # <-- this specifies that our data longitude/latitude in degrees [https://epsg.io/4326]
        gtx_feature = ee.FeatureCollection(ee.Geometry.LineString(coords=ground_track_coordinates,
                                                                  proj=ground_track_projection,
                                                                  geodesic=True))

        Map = geemap.Map(center=(40, -100), zoom=4)
        Map.add_basemap('HYBRID')

        for i, feature in enumerate(info['features']):

            # get the relevant info
            thisDate = datetime.fromtimestamp(feature['properties']['system:time_start']/1e3)
            dtstr = thisDate.strftime('%Y-%m-%d')
            dt = (thisDate - datetime.strptime(self.date, '%Y-%m-%d')).days
            ID = feature['id']
            rel = 'before' if dt<0 else 'after'
            print('%02d: %s (%3d days %s ICESat-2 overpass): %s' % (i, dtstr, np.abs(dt), rel, ID))

            # get image by id, and normalize rgb range
            image_id = feature['id']
            thisScene = ee.Image(image_id)
            rgb = thisScene.select('B4', 'B3', 'B2')
            rgbmax = rgb.reduce(ee.Reducer.max()).reduceRegion(reducer=ee.Reducer.max(), geometry=region_of_interest, bestEffort=True, maxPixels=1e6)
            rgbmin = rgb.reduce(ee.Reducer.min()).reduceRegion(reducer=ee.Reducer.min(), geometry=region_of_interest, bestEffort=True, maxPixels=1e6)
            rgb = rgb.unitScale(ee.Number(rgbmin.get('min')), ee.Number(rgbmax.get('max'))).clamp(0.0, 1.0)

            # if the image is Landsat 8, then pan-sharpen the image
            if 'LANDSAT' in ID: 
                pan = thisScene.select('B8').unitScale(ee.Number(rgbmin.get('min')), ee.Number(rgbmax.get('max'))).clamp(0.0, 1.0)
                huesat = rgb.rgbToHsv().select('hue', 'saturation')
                rgb = ee.Image.cat(huesat, pan).hsvToRgb().clamp(0.0, 1.0)

            # make the image uint8
            rgb = rgb.multiply(255).uint8()

            # add to map (only show the first layer, then can toggle others on in map)
            show_layer = True if i==0 else False
            Map.addLayer(rgb, name='%02d: %d days, %s'%(i,dt,ID), shown=show_layer)

        # show ground track on map, and center on our region of interest
        Map.addLayer(gtx_feature, {'color': 'red'}, 'ground track')
        Map.centerObject(region_of_interest,zoom=11)

        return Map
    
    ################################################################################################
    def plotDataAndMap(self, scene_id, crs='EPSG:3857', title='ICESat-2 Data'):

        from utils.curve_intersect import intersection

        # get data if not already there
        if 'atl03' not in vars(self).keys(): 
            print('Data has not yet been requested from OpenAltimetry yet. Doing this now.')
            self.requestData(verbose=True)

        # plot the ICESat-2 data
        fig = plt.figure(figsize=[12,5])
        ax_data = fig.add_subplot(122)
        self.plotData(ax_data, title=title)

        # get the image and plot
        ax_img = fig.add_subplot(121)

        def dist_latlon2meters(lat1, lon1, lat2, lon2):
            # returns the distance between two lat/lon coordinate points along the earth's surface in meters
            R = 6371000
            def deg2rad(deg):
                return deg * (np.pi/180)
            dlat = deg2rad(lat2-lat1)
            dlon = deg2rad(lon2-lon1)
            a = np.sin(dlat/2) * np.sin(dlat/2) + np.cos(deg2rad(lat1)) * np.cos(deg2rad(lat2)) * np.sin(dlon/2) * np.sin(dlon/2)
            c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
            return R * c

        lat1, lat2 = self.atl08.lat[0], self.atl08.lat.iloc[-1]
        lon1, lon2 = self.atl08.lon[0], self.atl08.lon.iloc[-1]
        center_lat = (lat1 + lat2) / 2
        center_lon = (lon1 + lon2) / 2
        ground_track_length = dist_latlon2meters(lat1, lon1, lat2, lon2)

        # the point of interest (center of the track) as an Earth Engine Geometry
        point_of_interest = ee.Geometry.Point(center_lon, center_lat)

        # region of interest around the ground track (use this area to scale visualization factors)
        buffer_around_center_meters = ground_track_length*0.52
        region_of_interest = point_of_interest.buffer(buffer_around_center_meters)

        thisScene = ee.Image(scene_id)
        info = thisScene.getInfo()

        # get the relevant info
        thisDate = datetime.fromtimestamp(info['properties']['system:time_start']/1e3)
        dtstr = thisDate.strftime('%Y-%m-%d')

        download_folder = 'downloads/'
        download_filename = '%s%s-8bitRGB.tif' % (download_folder, scene_id.replace('/', '-'))

        if os.path.exists(download_filename):
            print('This file already exists, not downloading again: %s' % download_filename)
        else:
            # get image by id, and normalize rgb range
            rgb = thisScene.select('B4', 'B3', 'B2')
            rgbmax = rgb.reduce(ee.Reducer.max()).reduceRegion(reducer=ee.Reducer.max(), geometry=region_of_interest, bestEffort=True, maxPixels=1e6)
            rgbmin = rgb.reduce(ee.Reducer.min()).reduceRegion(reducer=ee.Reducer.min(), geometry=region_of_interest, bestEffort=True, maxPixels=1e6)
            rgb = rgb.unitScale(ee.Number(rgbmin.get('min')), ee.Number(rgbmax.get('max'))).clamp(0.0, 1.0)

            # if the image is Landsat 8, then pan-sharpen the image
            if 'LANDSAT' in scene_id: 
                pan = thisScene.select('B8').unitScale(ee.Number(rgbmin.get('min')), ee.Number(rgbmax.get('max'))).clamp(0.0, 1.0)
                huesat = rgb.rgbToHsv().select('hue', 'saturation')
                rgb = ee.Image.cat(huesat, pan).hsvToRgb().clamp(0.0, 1.0)

            # make the image uint8
            rgb = rgb.multiply(255).uint8()

            rgb_info = rgb.getInfo()
            downloadURL = rgb.getDownloadUrl({'name': 'mySatelliteImage',
                                          'crs': crs,
                                          'scale': rgb_info['bands'][0]['crs_transform'][0],
                                          'region': region_of_interest,
                                          'filePerBand': False,
                                          'format': 'GEO_TIFF'})

            response = requests.get(downloadURL)

            if not os.path.exists(download_folder): os.makedirs(download_folder)
            with open(download_filename, 'wb') as fd:
                fd.write(response.content)

            print('Downloaded %s' % download_filename)

        img = rio.open(download_filename)
        plot.show(img, ax=ax_img)

        # get the graticule right
        latlon_bbox = warp.transform(img.crs, {'init': 'epsg:4326'}, 
                                     [img.bounds[i] for i in [0,2,2,0,0]], 
                                     [img.bounds[i] for i in [1,1,3,3,1]])
        min_lat = np.min(latlon_bbox[1])
        max_lat = np.max(latlon_bbox[1])
        min_lon = np.min(latlon_bbox[0])
        max_lon = np.max(latlon_bbox[0])
        latdiff = max_lat-min_lat
        londiff = max_lon-min_lon
        diffs = np.array([0.0001, 0.0002, 0.00025, 0.0004, 0.0005,
                          0.001, 0.002, 0.0025, 0.004, 0.005, 
                          0.01, 0.02, 0.025, 0.04, 0.05, 0.1, 0.2, 0.25, 0.4, 0.5, 1, 2])
        latstep = np.min(diffs[diffs>latdiff/8])
        lonstep = np.min(diffs[diffs>londiff/8])
        minlat = np.floor(min_lat/latstep)*latstep
        maxlat = np.ceil(max_lat/latstep)*latstep
        minlon = np.floor(min_lon/lonstep)*lonstep
        maxlon = np.ceil(max_lon/lonstep)*lonstep

        # plot meridians and parallels
        xl = (img.bounds.left, img.bounds.right)
        yl = (img.bounds.bottom, img.bounds.top)
        meridians = np.arange(minlon,maxlon, step=lonstep)
        parallels = np.arange(minlat,maxlat, step=latstep)
        latseq = np.linspace(minlat,maxlat,200)
        lonseq = np.linspace(minlon,maxlon,200)
        gridcol = 'k'
        gridls = ':'
        gridlw = 0.5
        topline = [[xl[0],xl[1]],[yl[1],yl[1]]]
        bottomline = [[xl[0],xl[1]],[yl[0],yl[0]]]
        leftline = [[xl[0],xl[0]],[yl[0],yl[1]]]
        rightline = [[xl[1],xl[1]],[yl[0],yl[1]]]
        for me in meridians:
            gr_trans = warp.transform({'init': 'epsg:4326'},img.crs,me*np.ones_like(latseq),latseq)
            intx,inty = intersection(leftline[0], leftline[1], gr_trans[0], gr_trans[1])
            deglab = '%.10g°E' % me if me >= 0 else '%.10g°W' % -me
            if len(intx) > 0:
                intx = intx[0]
                inty = inty[0]
                ax_img.text(intx, inty, deglab, fontsize=6, color='gray',verticalalignment='center',horizontalalignment='right',
                        rotation='vertical')
            intx,inty = intersection(bottomline[0], bottomline[1], gr_trans[0], gr_trans[1])
            if len(intx) > 0:
                intx = intx[0]
                inty = inty[0]
                ax_img.text(intx, inty, deglab, fontsize=6, color='gray',verticalalignment='top',horizontalalignment='center',
                        rotation='vertical')
            thislw = gridlw
            ax_img.plot(gr_trans[0],gr_trans[1],c=gridcol,ls=gridls,lw=thislw,alpha=0.5)
        for pa in parallels:
            gr_trans = warp.transform({'init': 'epsg:4326'},img.crs,lonseq,pa*np.ones_like(lonseq))
            thislw = gridlw
            deglab = '%.10g°N' % pa if pa >= 0 else '%.10g°S' % -pa
            intx,inty = intersection(topline[0], topline[1], gr_trans[0], gr_trans[1])
            if len(intx) > 0:
                intx = intx[0]
                inty = inty[0]
                ax_img.text(intx, inty, deglab, fontsize=6, color='gray',verticalalignment='bottom',horizontalalignment='center')
            intx,inty = intersection(rightline[0], rightline[1], gr_trans[0], gr_trans[1])
            if len(intx) > 0:
                intx = intx[0]
                inty = inty[0]
                ax_img.text(intx, inty, deglab, fontsize=6, color='gray',verticalalignment='center',horizontalalignment='left')
            ax_img.plot(gr_trans[0],gr_trans[1],c=gridcol,ls=gridls,lw=thislw,alpha=0.5)

        ax_img.text(0.99, 0.01, scene_id, fontsize=6, color='k',verticalalignment='bottom',horizontalalignment='right',transform=ax_img.transAxes)
        ax_img.set_xlim(xl)
        ax_img.set_ylim(yl)

        # plot the ground track
        gtx_x, gtx_y = warp.transform(src_crs='epsg:4326', dst_crs=img.crs, xs=self.atl08.lon, ys=self.atl08.lat)
        ax_img.plot(gtx_x, gtx_y, color='red', linestyle='-')
        ax_img.axis('off')

        lengths_scalebar = np.array([0.1, 0.2, 0.3, 0.5, 1, 2, 3, 5, 10, 20, 30, 50, 100, 200, 500, 1000])
        ratios = lengths_scalebar / (0.9*ground_track_length/1000)
        lengths_scalebar = lengths_scalebar[ratios < 1]
        length_scalebar = lengths_scalebar[-1]
        xl = ax_data.get_xlim()
        yl = ax_data.get_ylim()
        mid_lat = np.mean(xl)
        len_lat = (xl[1]-xl[0]) * (length_scalebar / ground_track_length*1000)
        h_scale = yl[0] + 0.93 * (yl[1]-yl[0])
        ax_data.arrow(mid_lat-0.5*len_lat,h_scale,len_lat,0,#head_width=3, head_length=5, 
                 fc='k', ec='k',lw=1,ls='-',length_includes_head=True,snap=True)
        ax_data.text(mid_lat, h_scale, '%.10g km' % (length_scalebar),va='bottom',ha='center')

        fig.tight_layout()
        
        plots_folder = 'plots/'
        if not os.path.exists(plots_folder): os.makedirs(plots_folder)
        plot_filename = '%s%s-8bitRGB-plot.jpg' % (plots_folder, scene_id.replace('/', '-'))
        fig.savefig(plot_filename,dpi=600)
        print('Saved plot to: %s' % plot_filename)

        return fig