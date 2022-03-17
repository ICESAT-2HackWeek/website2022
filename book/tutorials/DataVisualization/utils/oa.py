import pandas as pd
import json
import requests

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
            
    def plotData(self):
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