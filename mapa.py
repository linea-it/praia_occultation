from mpl_toolkits.basemap import Basemap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os
import astropy.units as u
from astropy.time import Time, TimeDelta
from astropy.coordinates import SkyCoord, EarthLocation, Angle, FK5
from multiprocessing import Pool


################################################################################################################################

#### Atualizacao 11/12/2018

################################################################################################################################

def xy2latlon(y, z, loncen, latcen):
    r = 6370997.0
    y = y - r
    z = z - r
    loncen = loncen*u.deg
    latcen = latcen*u.deg
    x_temp = r*r-y*y-z*z
    a = np.where(x_temp >= 0.0)
    x = np.repeat(np.nan, len(x_temp))
    x[a] = np.sqrt(x_temp[a])
    x1 = y1 = z1 = np.zeros(len(x))
    x1 = np.cos(loncen)*np.cos(latcen)*x - np.sin(loncen)*y - np.cos(loncen)*np.sin(latcen)*z
    y1 = np.sin(loncen)*np.cos(latcen)*x + np.cos(loncen)*y - np.sin(loncen)*np.sin(latcen)*z
    z1 = np.sin(latcen)*x + np.cos(latcen)*z
    lat = np.arctan(z1/np.sqrt(x1*x1+y1*y1)).to(u.deg).value
    lon = np.arctan2(y1,x1).to(u.deg).value
    if type(x) is np.ndarray:
        a = np.isnan(x)
        lon[a] = 1e+31
        lat[a] = 1e+31
    elif np.isnan(x):
        lon = 1e+31
        lat = 1e+31
    return lon, lat
    
################################################################################################################################
    
def latlon2xy(site, center):
#    r = 6370997.0
    x1 = np.cos(center.lat)*np.cos(center.lon)*site.x.value + np.cos(center.lat)*np.sin(center.lon)*site.y.value + np.sin(center.lat)*site.z.value
    y1 = - np.sin(center.lon)*site.x.value + np.cos(center.lon)*site.y.value
    z1 = - np.sin(center.lat)*np.cos(center.lon)*site.x.value - np.sin(center.lat)*np.sin(center.lon)*site.y.value + np.cos(center.lat)*site.z.value
#    y1 = y1*1000.0+r
#    z1 = z1*1000.0+r
    if type(x1.value) is np.ndarray:
        a = np.where(x1 < 0.0)
        y1[a] = 1e+31
        z1[a] = 1e+31
    elif x1 < 0.0:
        y1 = 1e+31
        z1 = y1
    return y1, z1
    
################################################################################################################################

def report(predic, sitearq, step=0.1, **kwargs):
#################### Lendo arquivo ###################################
    try:
        dados = np.loadtxt(predic, skiprows=41, usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 18, 19, 20, 21, 22, 25, 26, 28, 29), \
            dtype={'names': ('dia', 'mes', 'ano', 'hor', 'min', 'sec', 'afh', 'afm', 'afs', 'ded', 'dem', 'des', 'ca', 'pa', 'vel', 'delta', 'mR', 'mK', 'long', 'ora', 'ode'), 
            'formats': ('S30', 'S30', 'S30','S30', 'S30', 'S30','S20', 'S20', 'S20','S20', 'S20', 'S20', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8')}, ndmin=1)
    except:
        raise IOError('{} is not in PRAIA format'.format(arquivo))
################## lendo coordenadas #################
    coor = dados['afh']
    for i in ['afm', 'afs', 'ded', 'dem', 'des']:
        coor = np.core.defchararray.add(coor, ' ')
        coor = np.core.defchararray.add(coor, dados[i])
    stars = SkyCoord(coor, frame='icrs', unit=(u.hourangle, u.degree))
################### lendo tempo ########################
    tim=dados['ano']
    len_iso = ['-', '-', ' ', ':',':']
    arr = ['mes', 'dia', 'hor', 'min', 'sec']
    for i in np.arange(len(arr)):
        tim = np.core.defchararray.add(tim, len_iso[i]) 
        tim = np.core.defchararray.add(tim, dados[arr[i]])
    tim = np.char.array(tim) + '000'
    datas = Time(tim, format='iso', scale='utc')
############### definindo parametros #############
    ca = dados['ca']*u.arcsec
    posa = dados['pa']*u.deg
    vel = dados['vel']*(u.km/u.s)
    dist = dados['delta']*u.AU
    ob_off_ra = dados['ora']*u.mas
    ob_off_de = dados['ode']*u.mas
    magR = dados['mR']
    magK = dados['mK']
    longi = dados['long']
    datas.delta_ut1_utc = 0
    
    for elem in np.arange(len(stars)):
        print('Occ {}'.format(datas[elem].iso))
########## aplica offsets ######
        off_ra = 0.0*u.mas
        off_de = 0.0*u.mas
        ob_ra = 0.0*u.mas
        ob_de = 0.0*u.mas
        if 'off_o' in kwargs.keys():
            off_ra = off_ra + kwargs['off_o'][0]*u.mas
            off_de = off_de + kwargs['off_o'][1]*u.mas
            ob_ra = ob_off_ra[elem] + kwargs['off_o'][0]*u.mas
            ob_de = ob_off_de[elem] + kwargs['off_o'][1]*u.mas
        st_off_ra = st_off_de = 0.0*u.mas
        if 'off_s' in kwargs.keys():
            off_ra = off_ra - kwargs['off_s'][0]*u.mas
            off_de = off_de - kwargs['off_s'][1]*u.mas
            st_off_ra = kwargs['off_s'][0]*u.mas
            st_off_de = kwargs['off_s'][1]*u.mas
        dca = off_ra*np.sin(posa[elem]) + off_de*np.cos(posa[elem])
        dt = ((off_ra*np.cos(posa[elem]) - off_de*np.sin(posa[elem])).to(u.rad)*dist[elem].to(u.km)/np.absolute(vel[elem])).value*u.s
        ca1 = ca[elem] + dca
        data = datas[elem] + dt
        
    ########### calcula caminho ##################
        vec = np.arange(0, int(8000/(np.absolute(vel[elem].value))), step)
        vec = np.sort(np.concatenate((vec,-vec[1:]), axis=0))
        pa = Angle(posa[elem])
        pa.wrap_at('180d', inplace=True)
        if pa > 90*u.deg:
            paplus = pa - 180*u.deg
        elif pa < -90*u.deg:
            paplus = pa + 180*u.deg
        else:
            paplus = pa
        deltatime = vec*u.s
        datas1 = data + TimeDelta(deltatime)
        datas1.delta_ut1_utc = 0
        longg = stars[elem].ra - datas1.sidereal_time('mean', 'greenwich')
        centers = EarthLocation(longg, stars[elem].dec, height=0.0*u.m)

        dista = (dist[elem].to(u.m)*np.sin(ca1))
        ax = dista*np.sin(pa) + (deltatime*vel[elem])*np.cos(paplus)
        by = dista*np.cos(pa) - (deltatime*vel[elem])*np.sin(paplus)
            
        sites = np.loadtxt(sitearq, ndmin=1,  dtype={'names': ('lat', 'lon', 'alt', 'nome', 'offx', 'offy', 'color'), 'formats': ('f8', 'f8', 'f8', 'S30',  'f8', 'f8', 'S30')}, delimiter=',')
        sss = EarthLocation(sites['lon']*u.deg,sites['lat']*u.deg)
        
        for i in np.arange(len(sss)):
            xxx,yyy = latlon2xy(sss[i], centers)
            ddd = np.sqrt((ax.value-xxx)**2+(by.value-yyy)**2)
            mii = np.argmin(ddd)
            xxxx = ax.value-xxx
            yyyy = by.value-yyy
            if ddd[mii]/1000.0 < 7000:
                cinst = 'Central Instant: {}\n    Central distance: {:.0f} km'.format(datas1[mii].iso.split()[1], ddd[mii]/1000.0)
            else:
                cinst = 'Not able to observe'
            vv = np.sqrt((xxxx[mii+1]-xxxx[mii])**2 + (yyyy[mii+1]-yyyy[mii])**2)/(1000.0*step)
            dur = ''
            if 'diam' in kwargs.keys():
                dur = 'Duration: Out of the shadow\n'
                if ddd[mii]/1000.0 < kwargs['diam']/2.0:
                    rr = np.sqrt((kwargs['diam']/2.0)**2 - (ddd[mii]/1000.0)**2)
                    w = (rr*2.0)/vv
                    dur = 'Duration: {:.1f} s\n'.format(w)
                
            print('  Site: {}\n    {}\n    {}'.format(sites[i]['nome'].strip(), cinst, dur))


################################################################################################################################

def delta_mag(mp,ms, show=True):
    dm = mp - ms + 2.5*np.log10(np.power(10, (ms - mp)/2.5)+1)
    fr = np.power(10,-dm/2.5)
    if show == True:
        print('Delta Magnitude = {:-5.2f}'.format(dm))
        print('Flux Ratio = {:5.3f}'.format(fr))
        return
    return dm, fr
    
################################################################################################################################

def geramapa(obj, diam, *args, **kwargs):
    print("######################## Gera Mapas ########################")
    print("Gerando mapas para Objeto [ %s ] Diametro [ %s ]" % (obj, diam))
##### Default values ###########################################
    mapstyle = 1
    resolution = 'l'
    fmt='png'
    dpi=100
    step=1
    sitearq=''
    country=''
    mapsize=[46.0, 38.0]
    erro=None
    ring=None
    atm=None
    cpoints=60
    limits=None
    meridians=30
    parallels=30
    nscale=1
    cscale=1
    sscale=1
    pscale=1

#############################################
    if not type(obj) == str:
        raise TypeError('obj keyword must be a string')

    if not type(diam) in [int,float]:
        raise TypeError('diam keyword must be a number')
    diam = diam*u.km

#################### Lendo arquivo ###################################
    if args:
        arquivo = args[0]
    elif 'file' in kwargs.keys():
        arquivo = kwargs['file']
    if os.path.isfile(arquivo) == False:
        raise IOError('File {} not found'.format(arquivo))
    try:
        print("Lendo tabela de predicao. [ %s ]" % arquivo)

        dados = np.loadtxt(arquivo, skiprows=41, usecols=(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 18, 19, 20, 21, 22, 25, 26, 28, 29), \
            dtype={'names': ('dia', 'mes', 'ano', 'hor', 'min', 'sec', 'afh', 'afm', 'afs', 'ded', 'dem', 'des', 'ca', 'pa', 'vel', 'delta', 'mR', 'mK', 'long', 'ora', 'ode'), 
            'formats': ('S30', 'S30', 'S30','S30', 'S30', 'S30','S20', 'S20', 'S20','S20', 'S20', 'S20', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8')}, ndmin=1)

        print("Predicoes: [ %s ] " % dados.size)
    except:
        raise IOError('{} is not in PRAIA format'.format(arquivo))
################## lendo coordenadas #################
    print("-------------- Lendo Coordendas --------------")

    coor = np.char.array(dados['afh'], unicode=True)
    for i in ['afm', 'afs', 'ded', 'dem', 'des']:
        coor = np.core.defchararray.add(coor, ' ')
        coor = np.core.defchararray.add(coor, np.char.array(dados[i], unicode=True))
    stars = SkyCoord(coor, frame='icrs', unit=(u.hourangle, u.degree))

    print("Stars:")
    print(stars)

################### lendo tempo ########################
    print("-------------- Lendo Tempo --------------")

    tim=np.char.array(dados['ano'], unicode=True)
    len_iso = ['-', '-', ' ', ':',':']
    arr = ['mes', 'dia', 'hor', 'min', 'sec']
    for i in np.arange(len(arr)):
        tim = np.core.defchararray.add(tim, len_iso[i]) 
        tim = np.core.defchararray.add(tim, np.char.array(dados[arr[i]], unicode=True))
    tim = np.char.array(tim) + '000'
    datas = Time(tim, format='iso', scale='utc')

    print("Datas:")
    print(datas)    
############### definindo parametros #############

    print("-------------- Definindo Parametros --------------")

    ca = dados['ca']*u.arcsec
    posa = dados['pa']*u.deg
    vel = dados['vel']*(u.km/u.s)
    dist = dados['delta']*u.AU
    ob_off_ra = dados['ora']*u.mas
    ob_off_de = dados['ode']*u.mas
    magR = dados['mR']
    magK = dados['mK']
    longi = dados['long']
    datas.delta_ut1_utc = 0
        
    if 'mapstyle' in kwargs.keys():
        mapstyle = kwargs['mapstyle']
    if not type(mapstyle) == int:
        raise TypeError('mapstyle keyword must be an integer')

    print("mapstyle: %s" % mapstyle)

    if 'resolution' in kwargs.keys():
        resolution = kwargs['resolution']
    if resolution not in ['c', 'l', 'i', 'h', 'f']:
        raise TypeError('resolution keyword must be one of these: [c, l, i, h, f]')
    
    print("resolution: %s" % resolution)

    if 'fmt' in kwargs.keys():
        fmt = kwargs['fmt']
    if not type(fmt) == str:
        raise TypeError('fmt keyword must be a string')
    
    print("fmt: %s" % fmt)
    
    if 'dpi' in kwargs.keys():
        dpi = kwargs['dpi']
    if not type(dpi) == int:
        raise TypeError('dpi keyword must be an integer')
        
    print("dpi: %s" % dpi)

    if 'step' in kwargs.keys():
        step = kwargs['step']
    if not type(step) in [int,float]:
        raise TypeError('step keyword must be a number')

    print("step: %s" % step)

    if 'sitearq' in kwargs.keys():
        sitearq = kwargs['sitearq']
    if not type(sitearq) == str:
        raise TypeError('sitearq keyword must be a string')
        
    print("sitearq: %s" % sitearq)

    if 'country' in kwargs.keys():
        country = kwargs['country']
    if not type(country) == str:
        raise TypeError('country keyword must be a string')

    print("country: %s" % country)

    if 'mapsize' in kwargs.keys():
        mapsize = kwargs['mapsize']
    if not type(mapsize) == list:
        raise TypeError('mapsize keyword must be a list with 2 numbers')
    mapsize = mapsize*u.cm
        
    print("mapsize: %s" % mapsize)

    if 'erro' in kwargs.keys():
        erro = kwargs['erro']
    if not type(erro) in [int,float,type(None)]:
        raise TypeError('erro keyword must be a number')
        
    print("erro: %s" % erro)

    if 'ring' in kwargs.keys():
        ring = kwargs['ring']
    if not type(ring) in [int,float,type(None)]:
        raise TypeError('ring keyword must be a number')
        
    print("ring: %s" % ring)

    if 'atm' in kwargs.keys():
        atm = kwargs['atm']
    if not type(atm) in [int,float,type(None)]:
        raise TypeError('atm keyword must be a number')
    
    print("atm: %s" % atm)

    if 'cpoints' in kwargs.keys():
        cpoints = kwargs['cpoints']
    if not type(cpoints) in [int]:
        raise TypeError('cpoints keyword must be an integer')
        
    print("cpoints: %s" % cpoints)

    if 'limits' in kwargs.keys():
        maplats = False
        limits = kwargs['limits']
        if type(limits[0]) == float:
            maplats = True
        
    print("limits: %s" % limits)

    if ('meridians' in kwargs.keys()) and (type(kwargs['meridians']) in [int,float]):
        meridians = kwargs['meridians']

    print("meridians: %s" % meridians)

    if ('parallels' in kwargs.keys()) and (type(kwargs['parallels']) in [int,float]):
        parallels = kwargs['parallels']
        
    print("parallels: %s" % parallels)

    if ('nscale' in kwargs.keys()) and (type(kwargs['nscale']) in [int,float]):
        nscale = kwargs['nscale']
        
    print("nscale: %s" % nscale)

    if ('sscale' in kwargs.keys()) and (type(kwargs['sscale']) in [int,float]):
        sscale = kwargs['sscale']
        
    print("sscale: %s" % sscale)

    if ('cscale' in kwargs.keys()) and (type(kwargs['cscale']) in [int,float]):
        cscale = kwargs['cscale']
        
    print("cscale: %s" % cscale)

    if ('pscale' in kwargs.keys()) and (type(kwargs['pscale']) in [int,float]):
        pscale = kwargs['pscale']

    print("pscale: %s" % pscale)
##############################################################################################################################################################        
#### Define funcao que computa e gera o mapa para cada predicao ##############################################################################################
##############################################################################################################################################################
    def compute(elem):
        print("============== Gerando o mapa para a predicao ==============")
        print("Predicao: [ %s ] Star RA: [ %s ] Dec: [ %s ]" %(elem, stars[elem].ra, stars[elem].dec))

        r = 6370997.0
        
        print("r: %s" % r)

########## aplica offsets ######
        print("-------------- Aplica Offsets --------------")

        off_ra = 0.0*u.mas
        off_de = 0.0*u.mas
        ob_ra = 0.0*u.mas
        ob_de = 0.0*u.mas
        if 'off_o' in kwargs.keys():
            off_ra = off_ra + kwargs['off_o'][0]*u.mas
            off_de = off_de + kwargs['off_o'][1]*u.mas
            ob_ra = ob_off_ra[elem] + kwargs['off_o'][0]*u.mas
            ob_de = ob_off_de[elem] + kwargs['off_o'][1]*u.mas
        st_off_ra = st_off_de = 0.0*u.mas
        if 'off_s' in kwargs.keys():
            off_ra = off_ra - kwargs['off_s'][0]*u.mas
            off_de = off_de - kwargs['off_s'][1]*u.mas
            st_off_ra = kwargs['off_s'][0]*u.mas
            st_off_de = kwargs['off_s'][1]*u.mas
        dca = off_ra*np.sin(posa[elem]) + off_de*np.cos(posa[elem])
        dt = ((off_ra*np.cos(posa[elem]) - off_de*np.sin(posa[elem])).to(u.rad)*dist[elem].to(u.km)/np.absolute(vel[elem])).value*u.s
        ca1 = ca[elem] + dca
        data = datas[elem] + dt
        
        print("off_ra: %s" % off_ra)
        print("off_de: %s" % off_de)
        print("ob_ra: %s" % ob_ra)
        print("ob_de: %s" % ob_de)
        print("st_off_ra: %s" % st_off_ra)
        print("dca: %s" % dca)
        print("dt: %s" % dt)
        print("ca1: %s" % ca1)
        print("data: %s" % data)

##### define parametros do mapa #####

        print("-------------- define parametros do mapa --------------")

        lon = stars[elem].ra - data.sidereal_time('mean', 'greenwich')
        center_map = EarthLocation(lon, stars[elem].dec)
        centert = True
        if 'centermap' in kwargs.keys():
            if not type(kwargs['centermap']) == EarthLocation:
                raise TypeError('centermap must be an Astropy EarthLocation Object')
            center_map = kwargs['centermap']
            centert = False
        fig = plt.figure(figsize=(mapsize[0].to(u.imperial.inch).value, mapsize[1].to(u.imperial.inch).value))
        if not limits:
            m = Basemap(projection='ortho',lat_0=center_map.lat.value,lon_0=center_map.lon.value,resolution=resolution)
        elif np.array(limits).shape == (3,):
            if maplats:
                m = Basemap(projection='ortho',lat_0=center_map.lat.value,lon_0=center_map.lon.value,resolution=resolution)
                cx, cy = m(limits[1], limits[0])
                limits[0] = (cx - r)/1000.0
                limits[1] = (cy - r)/1000.0
            if np.any(np.absolute(limits[0:2]) > r):
                raise ValueError('Value for limits out of range (not in the map)')
            if mapsize[1] < mapsize[0]:
                ly = (limits[1]*u.km).to(u.m).value - r/limits[2]
                uy = (limits[1]*u.km).to(u.m).value + r/limits[2]
                lx = (limits[0]*u.km).to(u.m).value - (r/limits[2])*(mapsize[0]/mapsize[1])
                ux = (limits[0]*u.km).to(u.m).value + (r/limits[2])*(mapsize[0]/mapsize[1])
            else:
                lx = (limits[0]*u.km).to(u.m).value - r/limits[2]
                ux = (limits[0]*u.km).to(u.m).value + r/limits[2]
                ly = (limits[1]*u.km).to(u.m).value - (r/limits[2])*(mapsize[1]/mapsize[0])
                uy = (limits[1]*u.km).to(u.m).value + (r/limits[2])*(mapsize[1]/mapsize[0])
            m = Basemap(projection='ortho',lat_0=center_map.lat.value,lon_0=center_map.lon.value,resolution=resolution,llcrnrx=lx,llcrnry=ly,urcrnrx=ux,urcrnry=uy, area_thresh=2000)
            axf = fig.add_axes([-0.001,-0.001,1.002,1.002])
            axf.set_rasterization_zorder(1)
        else:
            raise ValueError('limits keyword must be an array with 3 elements: [centerx, centery, zoom]')
        if mapstyle == 1:
            m.drawmapboundary(fill_color='0.9')
            m.fillcontinents(color='1.0',lake_color='0.9')
            ptcolor= 'red'
            lncolor= 'blue'
            ercolor= 'blue'
            rncolor= 'blue'
            atcolor= 'blue'
            outcolor= 'red'
        elif mapstyle == 2:
            m.drawmapboundary(fill_color='aqua')
            m.fillcontinents(color='coral',lake_color='aqua')
            ptcolor= 'red'
            lncolor= 'blue'
            ercolor= 'red'
            rncolor= 'black'
            atcolor= 'black'
            outcolor= 'red'
        elif mapstyle == 3:
            m.shadedrelief()
            ptcolor= 'red'
            lncolor= 'blue'
            ercolor= 'red'
            rncolor= 'black'
            atcolor= 'black'
            outcolor= 'red'
        elif mapstyle == 4:
            m.bluemarble()
            ptcolor= 'red'
            lncolor= 'red'
            ercolor= 'red'
            rncolor= 'black'
            atcolor= 'black'
            outcolor= 'red'
        elif mapstyle == 5:
            m.etopo()
            ptcolor= 'red'
            lncolor= 'red'
            ercolor= 'red'
            rncolor= 'black'
            atcolor= 'black'
            outcolor= 'red'

        m.drawcoastlines(linewidth=0.5)  ## desenha as linhas da costa
        m.drawcountries(linewidth=0.5)  ## desenha os paises
        if 'states' in kwargs.keys():
            m.drawstates(linewidth=0.5)    ## Desenha os estados
        m.drawmeridians(np.arange(0,360,meridians))  ## desenha os meridianos
        m.drawparallels(np.arange(-90,90,parallels))  ## desenha os paralelos
        m.drawmapboundary()  ## desenha o contorno do mapa
        m.nightshade(data.datetime, alpha=0.25, zorder=1.2)  ## desenha a sombra da noite

        if 'ptcolor' in kwargs.keys():
            ptcolor = kwargs['ptcolor']
        if 'lncolor' in kwargs.keys():
            lncolor = kwargs['lncolor']
        if 'ercolor' in kwargs.keys():
            ercolor = kwargs['ercolor']
        if 'rncolor' in kwargs.keys():
            rncolor = kwargs['rncolor']
        if 'atcolor' in kwargs.keys():
            atcolor = kwargs['atcolor']
        if 'outcolor' in kwargs.keys():
            outcolor = kwargs['outcolor']

########### calcula caminho ##################
        print("-------------- calcula caminho --------------")

        vec = np.arange(0, int(8000/(np.absolute(vel[elem].value))), step)
        vec = np.sort(np.concatenate((vec,-vec[1:]), axis=0))
        pa = Angle(posa[elem])
        pa.wrap_at('180d', inplace=True)
        if pa > 90*u.deg:
            paplus = pa - 180*u.deg
        elif pa < -90*u.deg:
            paplus = pa + 180*u.deg
        else:
            paplus = pa
        deltatime = vec*u.s
        datas1 = data + TimeDelta(deltatime)
        datas1.delta_ut1_utc = 0
        longg = stars[elem].ra - datas1.sidereal_time('mean', 'greenwich')
        centers = EarthLocation(longg, stars[elem].dec, height=0.0*u.m)

        a = r*u.m
        b = r*u.m
        dista = (dist[elem].to(u.km)*ca1.to(u.rad)).value*u.km
        ax = a + dista*np.sin(pa) + (deltatime*vel[elem])*np.cos(paplus)
        by = b + dista*np.cos(pa) - (deltatime*vel[elem])*np.sin(paplus)
        ax2 = ax - (diam/2.0)*np.sin(paplus)
        by2 = by - (diam/2.0)*np.cos(paplus)
        ax3 = ax + (diam/2.0)*np.sin(paplus)
        by3 = by + (diam/2.0)*np.cos(paplus)

        lon1, lat1 = xy2latlon(ax2.value, by2.value, centers.lon.value, centers.lat.value)
        j = np.where(lon1 < 1e+30)
        xs, ys = m(lon1[j], lat1[j])
        xs = [i for i in xs if i < 1e+30]
        ys = [i for i in ys if i < 1e+30]
        m.plot(xs, ys, color=lncolor)
        if centert:
            j = np.where(lon1 > 1e+30)
            m.plot(ax2[j].value, by2[j].value, color=outcolor, clip_on=False, zorder=-0.2)

        lon2, lat2 = xy2latlon(ax3.value, by3.value, centers.lon.value, centers.lat.value)
        j = np.where(lon2 < 1e+30)
        xt, yt = m(lon2[j], lat2[j])
        xt = [i for i in xt if i < 1e+30]
        yt = [i for i in yt if i < 1e+30]
        m.plot(xt, yt, color=lncolor)
        if centert:
            j = np.where(lon2 > 1e+30)
            m.plot(ax3[j].value, by3[j].value, color=outcolor, clip_on=False, zorder=-0.2)

##### plot erro #####
        if erro:
            err = erro*u.mas
            errd = (dist[elem].to(u.km)*err.to(u.rad)).value*u.km
            ax2 = ax - errd*np.sin(paplus) - (diam/2.0)*np.sin(paplus)
            by2 = by - errd*np.cos(paplus) - (diam/2.0)*np.cos(paplus)
            ax3 = ax + errd*np.sin(paplus) + (diam/2.0)*np.sin(paplus)
            by3 = by + errd*np.cos(paplus) + (diam/2.0)*np.cos(paplus)
            lon1, lat1 = xy2latlon(ax2.value, by2.value, centers.lon.value, centers.lat.value)
            j = np.where(lon1 < 1e+30)
            xs, ys = m(lon1[j], lat1[j])
            xs = [i for i in xs if i < 1e+30]
            ys = [i for i in ys if i < 1e+30]
            m.plot(xs, ys, '--', color=ercolor)

            lon2, lat2 = xy2latlon(ax3.value, by3.value, centers.lon.value, centers.lat.value)
            j = np.where(lon2 < 1e+30)
            xt, yt = m(lon2[j], lat2[j])
            xt = [i for i in xt if i < 1e+30]
            yt = [i for i in yt if i < 1e+30]
            m.plot(xt, yt, '--', color=ercolor)

##### plot ring ##### 
        if ring:
            rng = ring*u.km
            ax2 = ax - rng*np.sin(paplus)
            by2 = by - rng*np.cos(paplus)
            ax3 = ax + rng*np.sin(paplus)
            by3 = by + rng*np.cos(paplus)
            lon1, lat1 = xy2latlon(ax2.value, by2.value, centers.lon.value, centers.lat.value)
            j = np.where(lon1 < 1e+30)
            xs, ys = m(lon1[j], lat1[j])
            xs = [i for i in xs if i < 1e+30]
            ys = [i for i in ys if i < 1e+30]
            m.plot(xs, ys, '--', color=rncolor)

            lon2, lat2 = xy2latlon(ax3.value, by3.value, centers.lon.value, centers.lat.value)
            j = np.where(lon2 < 1e+30)
            xt, yt = m(lon2[j], lat2[j])
            xt = [i for i in xt if i < 1e+30]
            yt = [i for i in yt if i < 1e+30]
            m.plot(xt, yt, '--', color=rncolor)

##### plot atm #####
        if atm:
            atmo = atm*u.km
            ax2 = ax - atmo*np.sin(paplus)
            by2 = by - atmo*np.cos(paplus)
            ax3 = ax + atmo*np.sin(paplus)
            by3 = by + atmo*np.cos(paplus)
            lon1, lat1 = xy2latlon(ax2.value, by2.value, centers.lon.value, centers.lat.value)
            j = np.where(lon1 < 1e+30)
            xs, ys = m(lon1[j], lat1[j])
            xs = [i for i in xs if i < 1e+30]
            ys = [i for i in ys if i < 1e+30]
            m.plot(xs, ys, color=atcolor)

            lon2, lat2 = xy2latlon(ax3.value, by3.value, centers.lon.value, centers.lat.value)
            j = np.where(lon2 < 1e+30)
            xt, yt = m(lon2[j], lat2[j])
            xt = [i for i in xt if i < 1e+30]
            yt = [i for i in yt if i < 1e+30]
            m.plot(xt, yt, '--', color=atcolor)

##### plot clat #####
        vec = np.arange(0, int(8000/(np.absolute(vel[elem].value))), cpoints)
        deltatime = np.sort(np.concatenate((vec,-vec[1:]), axis=0))*u.s
        axc = a + dista*np.sin(pa) + (deltatime*vel[elem])*np.cos(paplus)
        byc = b + dista*np.cos(pa) - (deltatime*vel[elem])*np.sin(paplus)
        if centert:
            m.plot(axc.value, byc.value, 'o', color=ptcolor, clip_on=False, markersize=mapsize[0].value*pscale*8.0/46.0, zorder=-0.2) 
        
        datas2 = data + TimeDelta(deltatime)
        datas2.delta_ut1_utc = 0
        lon3 = stars[elem].ra - datas2.sidereal_time('mean', 'greenwich')
        clon1, clat1 = xy2latlon(axc.value, byc.value, lon3.value, stars[elem].dec.value)
        j = np.where(clon1 < 1e+30)
        xc, yc = m(clon1[j], clat1[j])
        xc = [i for i in xc if i < 1e+30]
        yc = [i for i in yc if i < 1e+30]
        m.plot(xc, yc, 'o', color=ptcolor, clip_on=False, markersize=mapsize[0].value*pscale*8.0/46.0)

#        xc, yc = m(lon.value, stars[elem].dec.value)
        if centert:
            m.plot(a + dista*np.sin(pa), b + dista*np.cos(pa), 'o', color=ptcolor, clip_on=False, markersize=mapsize[0].value*pscale*24.0/46.0)

######## Define o titulo e o label da saida #########
        title = 'Object        Diam   Tmax   dots <> ra_off_obj_de  ra_of_star_de\n{:10s} {:4.0f} km  {:5.1f}s  {:02d} s <>{:+6.1f} {:+6.1f}  {:+6.1f} {:+6.1f} \n'\
    .format(obj, diam.value, (diam/np.absolute(vel[elem])).value, cpoints, ob_ra.value, ob_de.value, st_off_ra.value, st_off_de.value)
        labelx = '\n year-m-d    h:m:s UT     ra__dec__J2000__candidate    C/A    P/A    vel   Delta   G*  long\n\
{}  {:02d} {:02d} {:07.4f} {:+03d} {:02d} {:06.3f} {:6.3f} {:6.2f} {:6.2f}  {:5.2f} {:5.1f}  {:3.0f}'.format(data.iso,
int(stars[elem].ra.hms.h), int(stars[elem].ra.hms.m), stars[elem].ra.hms.s, int(stars[elem].dec.dms.d), np.absolute(int(stars[elem].dec.dms.m)), np.absolute(stars[elem].dec.dms.s),
            ca1.value, posa[elem].value, vel[elem].value, dist[elem].value, magR[elem], longi[elem])

########### plota seta de direcao ##################
        print("--------- plota seta de direcao ---------")
        print("Limits: %s" % limits)
        if not limits:
            print(a+5500000*u.m,b-5500000*u.m, np.sin(paplus+90*u.deg)*np.sign(vel[elem]), np.cos(paplus+90*u.deg)*np.sign(vel[elem]))

            tmp_sin = np.sin(paplus+90*u.deg)*np.sign(vel[elem])
            tmp_cos = np.cos(paplus+90*u.deg)*np.sign(vel[elem])
            # plt.quiver(11870997,870997, 0.84395364, 0.53641612, width=0.005)
            plt.quiver(a+5500000*u.m,b-5500000*u.m, tmp_sin.value, tmp_cos.value, width=0.005)

            # plt.quiver(a+5500000*u.m,b-5500000*u.m, np.sin(paplus+90*u.deg)*np.sign(vel[elem]), np.cos(paplus+90*u.deg)*np.sign(vel[elem]), width=0.005)
        else:
            plt.quiver(a.value + lx + (ux-lx)*0.9,b.value + ly + (uy-ly)*0.1, np.sin(paplus+90*u.deg)*np.sign(vel[elem]), np.cos(paplus+90*u.deg)*np.sign(vel[elem]), width=0.005, zorder = 1.3)

####### imprime os nomes dos paises #####
        print("--------- imprime os nomes dos paises ---------")
        if os.path.isfile(country) == True:
            paises = np.loadtxt(country, dtype={'names': ('nome', 'lat', 'lon'), 'formats': ('S30', 'f8', 'f8')}, delimiter=',', ndmin=1)
            xpt,ypt = m(paises['lon'], paises['lat'])
            for i in np.arange(len(xpt)):
                plt.text(xpt[i],ypt[i],np.char.strip(paises['nome'][i]), weight='bold', color='grey', fontsize=30*cscale)

####### imprime os sitios ##############
        print("--------- imprime os sitios ---------")
        if os.path.isfile(sitearq) == True:
            sites = np.loadtxt(sitearq, ndmin=1,  dtype={'names': ('lat', 'lon', 'alt', 'nome', 'offx', 'offy', 'color'), 'formats': ('f8', 'f8', 'f8', 'S30',  'f8', 'f8', 'S30')}, delimiter=',')

            print(sites)

            xpt,ypt = m(sites['lon'],sites['lat'])
            sss = EarthLocation(sites['lon']*u.deg,sites['lat']*u.deg,sites['alt']*u.km)
            for i in np.arange(len(xpt)):
                m.plot(xpt[i],ypt[i],'o', markersize=mapsize[0].value*sscale*10.0/46.0, color=sites['color'][i].strip().decode('utf-8'))
                plt.text(xpt[i] + sites['offx'][i]*1000,ypt[i]+sites['offy'][i]*1000, sites['nome'][i].strip().decode('utf-8'), weight='bold', fontsize=25*nscale)

####### finaliza a plotagem do mapa#####
        print("--------- finaliza a plotagem do mapa ---------")

        plt.title(title, fontsize=mapsize[0].value*25/46, fontproperties='FreeMono', weight='bold')

        plt.xlabel(labelx, fontsize=mapsize[0].value*21/46, fontproperties='FreeMono', weight='bold')
        if 'nameimg' in kwargs.keys():
            nameimg = kwargs['nameimg']
        else:
            nameimg = '{}_{}'.format(obj, data.isot)

        print("nameimg: %s" % nameimg)
        print("fmt: %s" % fmt)
        print("dpi: %s" % dpi)

        plt.savefig('{}.{}'.format(nameimg, fmt), format=fmt, dpi=dpi)

        print('Gerado: {}.{}'.format(nameimg, fmt))
        plt.clf()
        plt.close()
        
    
####### roda todos as predicoes #####
    vals = np.arange(len(stars))
    if 'n' in kwargs.keys():
        vals = np.array(kwargs['n'], ndmin=1)
    if vals.max() >= len(stars):
        raise IndexError('values {} out of range for table with {} predictions'.format(vals[np.where(vals >= len(stars))],len(stars)))
    if ('process' in kwargs.keys()) and (type(kwargs['process']) == int):
        p = Pool(kwargs['process'])
        p.map(compute, vals)
    else:
        for i in vals:
            compute(i)
        