# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para mejortorrent
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os, sys
from channelselector import get_thumbnail_path

from core import logger
from core import config
from core import scrapertools
from core import jsontools
from core.item import Item
from servers import servertools
from core.tmdb import Tmdb

__category__ = "A"
__type__ = "generic"
__title__ = "Mejor Torrent"
__channel__ = "mejortorrent"
__language__ = "ES"

host = "http://www.mejortorrent.com"

DEBUG = config.get_setting("debug")



def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.mejortorrent mainlist")

    itemlist = []

    thumb_pelis = get_thumbnail("thumb_canales_peliculas.png")
    thumb_pelis_hd = get_thumbnail("thumb_canales_peliculas_hd.png")
    thumb_series = get_thumbnail("thumb_canales_series.png")
    thumb_series_hd = get_thumbnail("thumb_canales_series_hd.png")
    thumb_series_az = get_thumbnail("thumb_canales_series_az.png")
    thumb_buscar = get_thumbnail("thumb_buscar.png")

    itemlist.append( Item(channel=__channel__, title="Peliculas" , action="getlist", url="http://www.mejortorrent.com/torrents-de-peliculas.html", thumbnail=thumb_pelis ))
    itemlist.append( Item(channel=__channel__, title="Peliculas HD" , action="getlist", url="http://www.mejortorrent.com/torrents-de-peliculas-hd-alta-definicion.html", thumbnail=thumb_pelis_hd ))
    itemlist.append( Item(channel=__channel__, title="Series" , action="getlist", url="http://www.mejortorrent.com/torrents-de-series.html", thumbnail=thumb_series ))
    itemlist.append( Item(channel=__channel__, title="Series HD" , action="getlist"           , url="http://www.mejortorrent.com/torrents-de-series-hd-alta-definicion.html", thumbnail=thumb_series_hd ))
    itemlist.append( Item(channel=__channel__, title="Series Listado Alfabetico" , action="listalfabetico"           , url="http://www.mejortorrent.com/torrents-de-series.html", thumbnail=thumb_series_az ))
    itemlist.append( Item(channel=__channel__, title="Buscar..." , action="search", thumbnail=thumb_buscar ))

    return itemlist

def listalfabetico(item):
    logger.info("pelisalacarta.mejortorrent listalfabetico")

    itemlist = []

    for letra in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']:
        itemlist.append( Item(channel=__channel__, action="getlist" , title=letra, url="http://www.mejortorrent.com/series-letra-" + letra.lower() + ".html"))

    itemlist.append( Item(channel=__channel__, action="getlist" , title="Todas",url="http://www.mejortorrent.com/series-letra..html"))

    return itemlist


def search(item,texto):
    logger.info("pelisalacarta.mejortorrent search")
    texto = texto.replace(" ","+")

    item.url = "http://www.mejortorrent.com/secciones.php?sec=buscador&valor=%s" % (texto)
    try:
        return buscador(item)

    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

    return itemlist




def buscador(item):
    logger.info("pelisalacarta.mejortorrent buscador")
    itemlist = []

    data = scrapertools.cachePage(item.url)

    # pelis
    # <a href="/peli-descargar-torrent-9578-Presentimientos.html">
    # <img src="/uploads/imagenes/peliculas/Presentimientos.jpg" border="1"></a
    #
    # series
    #
    #<a href="/serie-descargar-torrents-11589-11590-Ahora-o-nunca-4-Temporada.html">
    #<img src="/uploads/imagenes/series/Ahora o nunca4.jpg" border="1"></a>
    #
    # docs
    #
    #<a href="/doc-descargar-torrent-1406-1407-El-sueno-de-todos.html">
    #<img border="1" src="/uploads/imagenes/documentales/El sueno de todos.jpg"></a>

    #busca series
    patron  = "<a href='(/serie-descargar-torrent[^']+)'.*? "
    patron += "<span style='color:gray;'>([^']+)</span>"
    patron_enlace = "/serie-descargar-torrents-\d+-\d+-(.*?)\.html"


    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedinfo in matches:
        title = scrapertools.get_match(scrapedurl, patron_enlace) + scrapedinfo
        title = title.replace("-"," ")
        url = urlparse.urljoin(item.url,scrapedurl)
        logger.debug("title=["+title+"], url=["+url+"]")

        itemlist.append( Item(channel=__channel__, action="episodios", title=title , url=url , folder=True, extra="series") )

    #busca pelis
    patron  = "<a href='(/peli-descargar-torrent-[^']+).*? "
    patron += "<span style='color:gray;'>([^']+)</a>"
    patron_enlace = "/peli-descargar-torrent-\d+(.*?)\.html"


    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedinfo in matches:
        title = scrapertools.get_match(scrapedurl, patron_enlace) + scrapedinfo
        title = title.replace("-"," ")
        url = urlparse.urljoin(item.url,scrapedurl)
        logger.debug("title=["+title+"], url=["+url+"]")

        itemlist.append( Item(channel=__channel__, action="play", title=title , url=url , folder=False, extra="") )


    #busca docu
    patron  = "<a href='(/doc-descargar-torrent[^']+)' .*?"
    patron += "<td align='right' width='20%'>(.*?)</td>"
    patron_enlace = "/doc-descargar-torrent-\d+-\d+-(.*?)\.html"

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl, scrapedinfo in matches:
        title = scrapertools.get_match(scrapedurl, patron_enlace) + scrapedinfo
        title = title.replace("-"," ")
        url = urlparse.urljoin(item.url,scrapedurl)
        logger.debug("title=["+title+"], url=["+url+"]")

        itemlist.append( Item(channel=__channel__, action="episodios", title=title , url=url , folder=True, extra="docu") )


    return itemlist


def getlist(item):
    logger.info("pelisalacarta.mejortorrent seriesydocs")
    itemlist = []

    data = scrapertools.cachePage(item.url)

    # pelis
    # <a href="/peli-descargar-torrent-9578-Presentimientos.html">
    # <img src="/uploads/imagenes/peliculas/Presentimientos.jpg" border="1"></a
    #
    # series
    #
    #<a href="/serie-descargar-torrents-11589-11590-Ahora-o-nunca-4-Temporada.html">
    #<img src="/uploads/imagenes/series/Ahora o nunca4.jpg" border="1"></a>
    #
    # docs
    #
    #<a href="/doc-descargar-torrent-1406-1407-El-sueno-de-todos.html">
    #<img border="1" src="/uploads/imagenes/documentales/El sueno de todos.jpg"></a>

    if item.url.find("peliculas") > -1:
        patron  = '<a href="(/peli-descargar-torrent[^"]+)">[^<]+'
        patron += '<img src="([^"]+)"[^<]+</a>'
        patron_enlace = "/peli-descargar-torrent-\d+(.*?)\.html"
        action = "show_movie_info"
        folder = True
        extra = ""
    elif item.url.find("series-letra") > -1:
        patron  = "<a href='(/serie-descargar-torrent[^']+)'>()"
        patron_enlace = "/serie-descargar-torrents-\d+-\d+-(.*?)\.html"
        action = "episodios"
        folder = True
        extra = "series"
    elif item.url.find("series") > -1:
        patron  = '<a href="(/serie-descargar-torrent[^"]+)">[^<]+'
        patron += '<img src="([^"]+)"[^<]+</a>'
        patron_enlace = "/serie-descargar-torrents-\d+-\d+-(.*?)\.html"
        action = "episodios"
        folder = True
        extra = "series"
    else:
        patron  = '<a href="(/doc-descargar-torrent[^"]+)">[^<]+'
        patron += '<img src="([^"]+)"[^<]+</a>'
        patron_enlace = "/doc-descargar-torrent-\d+-\d+-(.*?)\.html"
        action = "episodios"
        folder = True
        extra = "docus"

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail in matches:
        title = scrapertools.get_match(scrapedurl, patron_enlace)
        title = title.replace("-"," ")
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url, urllib.quote(scrapedthumbnail))
        plot = ""
        logger.debug("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action=action, title=title , url=url , thumbnail=thumbnail , plot=plot , folder=folder, extra=extra) )


    # Extrae el paginador
    patronvideos  = "<a href='([^']+)' class='paginar'> Siguiente >>"
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="getlist", title="Pagina siguiente >>" , url=scrapedurl , folder=True) )

    return itemlist


def episodios(item):
    logger.info("pelisalacarta.mejortorrent episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    total_capis = scrapertools.get_match(data,"<input type='hidden' name='total_capis' value='(\d+)'>")
    tabla = scrapertools.get_match(data,"<input type='hidden' name='tabla' value='([^']+)'>")
    titulo = scrapertools.get_match(data,"<input type='hidden' name='titulo' value='([^']+)'>")

    item.thumbnail = scrapertools.find_single_match(data, "src='http://www\.mejortorrent\.com(/uploads/imagenes/" + tabla + "/[a-zA-Z0-9_ ]+.jpg)'")
    item.thumbnail = 'http://www.mejortorrent.com' + urllib.quote(item.thumbnail)

    #<form name='episodios' action='secciones.php?sec=descargas&ap=contar_varios' method='post'>
    data = scrapertools.get_match(data,"<form name='episodios' action='secciones.php\?sec=descargas\&ap=contar_varios' method='post'>(.*?)</form>")
    '''
        <td bgcolor='#C8DAC8' style='border-bottom:1px solid black;'><a href='/serie-episodio-descargar-torrent-18741-Juego-de-tronos-4x01.html'>4x01 - Episodio en V.O. Sub Esp.</a></td>
        <td width='120' bgcolor='#C8DAC8' align='right' style='border-right:1px solid black; border-bottom:1px solid black;'><div style='color:#666666; font-size:9px; margin-right:5px;'>Fecha: 2014-04-07</div></td>
        <td width='60' bgcolor='#F1F1F1' align='center' style='border-bottom:1px solid black;'>
        <input type='checkbox' name='episodios[1]' value='18741'>
        '''

    if item.extra == "series":
        patron  = "<td bgcolor[^>]+><a[^>]+>([^>]+)</a></td>[^<]+"
    else:
        patron  = "<td bgcolor[^>]+>([^>]+)</td>[^<]+"


    patron += "<td[^<]+<div[^>]+>Fecha: ([^<]+)</div></td>[^<]+"
    patron += "<td[^<]+"
    patron += "<input type='checkbox' name='([^']+)' value='([^']+)'"

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    tmdb_title = re.sub('\d+ Temporada', '', item.title)

    oTmdb= Tmdb(texto_buscado=tmdb_title.strip(), tipo='tv', idioma_busqueda="es")

    for scrapedtitle,fecha,name,value in matches:
        scrapedtitle = scrapedtitle.strip()
        title = scrapedtitle + " (" + fecha + ")"

        url = "http://www.mejortorrent.com/secciones.php?sec=descargas&ap=contar_varios"
        #"episodios%5B1%5D=11744&total_capis=5&tabla=series&titulo=Sea+Patrol+-+2%AA+Temporada"
        post = urllib.urlencode( { name:value , "total_capis":total_capis , "tabla":tabla , "titulo":titulo } )
        logger.debug("post="+post)

        epi = scrapedtitle.split("x")

        temporada = re.sub("\D", "", epi[0])
        capitulo  = re.sub("\D", "", epi[1])

        epi_data = oTmdb.get_episodio(temporada, capitulo)
        logger.debug("epi_data=" + str(epi_data))

        if epi_data:
            item.thumbnail = epi_data["temporada_poster"]
            item.fanart = epi_data["episodio_imagen"]
            item.plot = epi_data["episodio_sinopsis"]
            epi_title = epi_data["episodio_titulo"]
            if epi_title != "":
                title = scrapedtitle + " " + epi_title + " (" + fecha + ")"

        logger.debug("title=["+title+"], url=["+url+"], item=["+str(item)+"]")

        itemlist.append( Item(channel=__channel__, action="play", title=title , url=url , thumbnail=item.thumbnail , plot=item.plot, fanart=item.fanart, viewmode="movie_with_plot", extra=post, folder=False) )

    return itemlist

def show_movie_info(item):
    logger.info("pelisalacarta.mejortorrent show_movie_info")

    itemlist = []

    try:
        from core.tmdb import Tmdb
        oTmdb= Tmdb(texto_buscado=item.title,idioma_busqueda="es")
        item.fanart=oTmdb.get_backdrop()
        item.plot=oTmdb.get_sinopsis()
    except:
        pass

    data = scrapertools.cache_page(item.url)
    logger.debug("data="+data)

    patron  = "<a href='(secciones.php\?sec\=descargas[^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl in matches:
        url = urlparse.urljoin(item.url, scrapedurl)
        logger.debug("title=["+item.title+"], url=["+url+"], thumbnail=["+item.thumbnail+"]")

        torrent_data = scrapertools.cache_page(url)
        logger.debug("torrent_data="+torrent_data)
        #<a href='/uploads/torrents/peliculas/los-juegos-del-hambre-brrip.torrent'>
        link = scrapertools.get_match(torrent_data,"<a href='(/uploads/torrents/peliculas/.*?\.torrent)'>")
        link = urlparse.urljoin(url,link)

        logger.debug("link="+link)

        itemlist.append( Item(channel=__channel__, action="play", server="torrent", title=item.title, url=link, thumbnail=item.thumbnail , plot=item.plot, fanart=item.fanart, folder=False, viewmode="movie_with_plot") )

    return itemlist


def play(item):
    logger.info("pelisalacarta.mejortorrent play")
    itemlist = []

    if item.extra=="":
        itemlist.append( Item(channel=__channel__, action="play", server="torrent", title=item.title , url=item.url, thumbnail=item.thumbnail , plot=item.plot, fanart=item.fanart, folder=False) )

    else:
        data = scrapertools.cache_page(item.url, post=item.extra)
        logger.info("data="+data)

        # series
        #
        #<a href="http://www.mejortorrent.com/uploads/torrents/series/falling-skies-2-01_02.torrent"
        #<a href="http://www.mejortorrent.com/uploads/torrents/series/falling-skies-2-03.torrent"
        #
        # docus
        #
        #<a href="http://www.mejortorrent.com/uploads/torrents/documentales/En_Suenyos_De_Todos_DVDrip.torrent">El sueo de todos. </a>

        params = dict(urlparse.parse_qsl(item.extra))

        patron = '<a href="(http://www.mejortorrent.com/uploads/torrents/' + params["tabla"] +'/.*?\.torrent)"'

        link = scrapertools.get_match(data, patron)

        logger.info("link="+link)

        itemlist.append( Item(channel=__channel__, action="play", server="torrent", title=item.title , url=link , thumbnail=item.thumbnail , plot=item.plot , folder=False) )


    return itemlist

def get_thumbnail( thumb_name = None ):

    img_path = config.get_runtime_path() + '/resources/images/squares'

    if thumb_name:
        file_path = os.path.join(img_path, thumb_name) 
        if os.path.isfile(file_path):
            thumb_path = file_path
        else:
            thumb_path = urlparse.urljoin(get_thumbnail_path(), thumb_name)
    else:
        thumb_path = urlparse.urljoin(get_thumbnail_path(), thumb_name)

    return thumb_path

