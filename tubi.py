#!/usr/bin/env python3
# coding: utf-8

import argparse
import requests
import time
from datetime import datetime, date
import dateutil.parser
import html
import uuid

import json
import xml.etree.ElementTree as ET

xml_constants = {
    'source-info-url': 'https://tubitv.com',
    'source-info-name': 'tubi.com',
    'generator-info-name': 'web2tv',
    'generator-info-url': 'https://github.com/ReenigneArcher/web2tv'
}

default_headers = {
    'Accept': 'application/json'
}

# dictionary prebuild
rating_system = {
    'tv-y': 'TV Parental Guidelines',
     'tv-y7': 'TV Parental Guidelines',
     'tv-g': 'TV Parental Guidelines',
     'tv-pg': 'TV Parental Guidelines',
     'tv-14': 'TV Parental Guidelines',
     'tv-ma': 'TV Parental Guidelines',
     'g': 'MPAA',
     'pg': 'MPAA',
     'pg-13': 'MPAA',
     'r': 'MPAA',
     'nc-17': 'MPAA',
     'u': 'BBFC',
     # 'pg' : 'BBFC',
     '12': 'BBFC',
     '12a': 'BBFC',
     '15': 'BBFC',
     '18': 'BBFC',
     'r18': 'BBFC',
     '0+': 'GIO',
     '6+': 'GIO',
     '12+': 'GIO',
     '15+': 'GIO',
     '18+': 'GIO',
     'nr': 'n/a',
     'no rating': 'n/a',
     'not rated': 'n/a',
     'ur': 'n/a'
    }

rating_logo = {
    'tv-y': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/25/TV-Y_icon.svg/240px-TV-Y_icon.svg.png',
    'tv-y7': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/TV-Y7_icon.svg/240px-TV-Y7_icon.svg.png',
    'tv-g': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/TV-G_icon.svg/240px-TV-G_icon.svg.png',
    'tv-pg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/TV-PG_icon.svg/240px-TV-PG_icon.svg.png',
    'tv-14': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/TV-14_icon.svg/240px-TV-14_icon.svg.png',
    'tv-ma': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/34/TV-MA_icon.svg/240px-TV-MA_icon.svg.png',
    'g': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/RATED_G.svg/276px-RATED_G.svg.png',
    'pg': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/RATED_PG.svg/320px-RATED_PG.svg.png',
    'pg-13': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/RATED_PG-13.svg/320px-RATED_PG-13.svg.png',
    'r': 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/RATED_R.svg/284px-RATED_R.svg.png',
    'nc-17': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Nc-17.svg/320px-Nc-17.svg.png',
    'u': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/BBFC_U_2019.svg/270px-BBFC_U_2019.svg.png',
    # 'pg' : 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/BBFC_PG_2019.svg/270px-BBFC_PG_2019.svg.png',
    '12': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/BBFC_12_2019.svg/240px-BBFC_12_2019.svg.png',
    '12a': 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/BBFC_12A_2019.svg/240px-BBFC_12A_2019.svg.png',
    '15': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/BBFC_15_2019.svg/240px-BBFC_15_2019.svg.png',
    '18': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/BBFC_18_2019.svg/240px-BBFC_18_2019.svg.png',
    'r18': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/BBFC_R18_2019.svg/240px-BBFC_R18_2019.svg.png',
    '0+': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/GSRR_G_logo.svg/240px-GSRR_G_logo.svg.png',
    '6+': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/5a/GSRR_P_logo.svg/240px-GSRR_P_logo.svg.png',
    '12+': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/GSRR_PG_12_logo.svg/240px-GSRR_PG_12_logo.svg.png',
    '15+': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c6/GSRR_PG_15_logo.svg/240px-GSRR_PG_15_logo.svg.png',
    '18+': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5/GSRR_R_logo.svg/240px-GSRR_R_logo.svg.png',
    'nr': 'https://loyoladigitaladvertising.files.wordpress.com/2014/02/nr-logo.png',
    'no rating': 'https://loyoladigitaladvertising.files.wordpress.com/2014/02/nr-logo.png',
    'not rated': 'https://loyoladigitaladvertising.files.wordpress.com/2014/02/nr-logo.png',
    'ur': 'http://3.bp.blogspot.com/-eyIrE_lKiMg/Ufbis7lWLlI/AAAAAAAAAK4/4XTYHCU8Dx4/s1600/ur+logo.png'
    }


def get_args():
    # argparse
    parser = argparse.ArgumentParser(description="Python script to convert tubi tv guide into xml/m3u format.",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-e', '--epgHours', type=int, required=False, default=10,
                        help='Hours of EPG to collect. tubi only provides a few hours of EPG. Max allowed is 12.')
    parser.add_argument('--number_as_name', action='store_true', required=False,
                        help='Use the channel number as the name and id. Improves channel display in Plex Media Server.')
    
    # xml arguments
    parser.add_argument('-x', '--xmlFile', type=str, required=False, default='tubi.xml',
                        help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.')
    parser.add_argument('--xml', action='store_true', required=False, help='Generate the xml file.')
    parser.add_argument('--long_date', action='store_true', required=False,
                        help='Use longer date format. Do not use for Plex Media Server.')
    
    # m3u arguments
    parser.add_argument('-m', '--m3uFile', type=str, required=False, default='tubi.m3u',
                        help='Full destination filepath. Full file path can be specified. If only file name is specified then file will be placed in the current working directory.')
    parser.add_argument('-p', '--prefix', type=str, required=False, default='', help='Channel name prefix.')
    parser.add_argument('-s', '--startNumber', type=int, required=False, default=1,
                        help='Start numbering here. For example 9000. If -k, --keepNumber is used then channel 2 would become channel 9002, otherwise the first channel number found would be 9000, second channel found would be 9001, etc.')
    parser.add_argument('-k', '--keepNumber', action='store_true', required=False,
                        help='Keep existing number scheme. Script will add existing number to start number. Recommended start number ends with a 0.')
    parser.add_argument('--m3u', action='store_true', required=False, help='Generate the m3u file.')
    parser.add_argument('--streamlink', action='store_true', required=False,
                        help='Generate the stream urls for use with Streamlink.')
    
    opts = parser.parse_args()
    
    # argument fixes
    if opts.epgHours > 12:
        opts.epgHours = 12
    
    opts.language = 'en'
    
    return opts


def load_json(url, headers=default_headers):
    result = requests.get(url=url, headers=headers).json()
    return result


def isotime_convert(iso_time, short=False):
    time_value = dateutil.parser.isoparse(iso_time)  # https://stackoverflow.com/a/15228038/11214013
    if not short:
        result = time_value.strftime('%Y%m%d%H%M%S')
    else:
        result = time_value.strftime('%Y%m%d')
    return result


def fix(text):
    text = str(html.escape(text, quote=False).encode('ascii', 'xmlcharrefreplace'))[
           2:-1]  # https://stackoverflow.com/a/1061702/11214013
    return text.replace("\\'", "'")


def fix2(text):
    return text


def get_number(channel):
    return channel.get('channelNumber')


def main():
    args = get_args()

    # constants
    hour = 60 * 60
    half_hour = 60 * 60 / 2
    timezone = '-0000'
    timezone = timezone[:-2] + ':' + timezone[-2:]

    now = time.time()
    now = int(now)
    now_30 = now - (now % half_hour)  # go back to nearest 30 minutes
    epg_begin = str(datetime.utcfromtimestamp(now_30)).replace(' ', 'T') + timezone

    epg_end = (args.epgHours * hour) + now_30 + half_hour
    epg_end = str(datetime.utcfromtimestamp(epg_end)).replace(' ', 'T') + timezone

    print('Loading Grid for tubi')

    #url = f'https://tubitv.com/oz/epg/programming?content_id=715943&lookahead=6'
    url = f'https://tubitv.com/oz/epg/programming?content_id=715943,715944,715941,613761,715949,715945,715938,715942,715939,618762,556174,555127,618763,597678,597681,555126,555129,578086,560215,682633,613683,613765,692073,693703,613758,557344,613763,613760,613762,613229,613695,613759,692115,692114,692051,692090,692088,692050,692087,692089,692086,691129,692057,689435,689413,603170,603906,692074,603175,603163,644789,689270,687460,687470,687458,687452,610464,685320,603171,603917,677785,687454,687382,685558,685835,685557,682057,684167,684170,684165,685457,685318,610469,610468,603908,688992,688740,687455,684164,682634,682630,678708,682059,682343,680706,680340,680353,680705,677790,675569,673500,673499,673498,673411,673408,667455,667442,671821,670604,670603,670602,670605,671073,671083,670587,666559,666613,664267,660349,660353,660350,660348,660347,658748,658746,653200,653208,656575,653241,653253,653199,656574,650246,650241,646488,618768,650252,628892,578083,644787,555118,578085,603178,618766,555120,644786,650208,555122,603181,603918,641496,641489,641492,555119,557345,555116,641290,629323,555124,571664,628896,603907,685308,687448,586035,687453,610466,610467,623575,618769,555110,610472,610471,555121,578082,618767,618764,687450,603194,613764,610463,555111,603169,646485,603915,603911,603910,586034,689346,689437,689473,687459,603909,603904,578084,644788,644781,603905,685307,588301,687449,586036,687474,610465,618765,650251,586032,603914,591002,685306,555117,581120,559144,628893,555125,555382,677010,677011,650666,650665,555130,555123,555112,555109,555108,610470,555113,555114,555115,555107&lookahead=6&limit_resolutions=h264_1080p&limit_resolutions=h265_1080p'
    print('url: ' + url)

    grid = load_json(url)

    #with open('tubi.json', 'w') as write_file:
        #json.dump(grid, write_file, indent=4)

    channel_numbers = []

    if args.xml:
        xml_tv = ET.Element("tv", xml_constants)

    if args.m3u:
        m3u_f = open(args.m3uFile, "w", encoding='utf-8')

        did = str(uuid.uuid4())  # https://docs.python.org/2.7/library/uuid.html
        sid = str(uuid.uuid4())  # https://docs.python.org/2.7/library/uuid.html

        m3u_f.write('#EXTM3U\n')

    x = 0

    for channel in grid['rows']:
        if not args.keepNumber:
            new_number = args.startNumber + x
        else:
            new_number = args.startNumber + channel['number']

        r = 0
        index = 0
        while r < len(channel_numbers):
            if str(new_number) == str(channel_numbers[r][0]):
                index = r
                s = len(channel_numbers[r])
                channel_numbers[r].append(str(new_number) + '.' + str(s))
                # print('Added sub channel: ' + channel_numbers[r][-1])
                new_number = channel_numbers[r][-1]
                break
            r += 1
        if index == 0:
            channel_numbers.append([str(new_number)])
            # print('Added channel: ' + str(channel_numbers[-1][0]))

        if args.number_as_name:
            channel_id = str(new_number)

        else:
            channel_id = f"{args.prefix}{channel['title']}"

        if args.xml:
            xml_channel = ET.SubElement(xml_tv, "channel", {"id": channel_id})

            if args.prefix != '':
                ET.SubElement(xml_channel, "display-name").text = f"{args.prefix}{channel['name']}"
            print(channel['title'])

            display_names_types = ['title', 'content_id']
            display_names = []
            for display_name_type in display_names_types:
                try:
                    if channel[display_name_type] not in display_names:
                        display_names.append(channel[display_name_type])
                        ET.SubElement(xml_channel, "display-name").text = f'{channel[display_name_type]}'
                except KeyError:
                    pass

            tvg_logo = channel['images']['landscape'][0]
            ET.SubElement(xml_channel, "icon", {'src': tvg_logo})

            y = 0
            for program in channel['programs']:
                time_start = isotime_convert(program['start_time'])
                time_end = isotime_convert(program['end_time'])
                # time_original_long = isotime_convert(program['episode']['clip']['originalReleaseDate'], short=False)
                # time_original_short = isotime_convert(program['episode']['clip']['originalReleaseDate'], short=True)

                # try:
                #     first_aired_long = isotime_convert(program['episode']['firstAired'], short=False)
                #     first_aired_short = isotime_convert(program['episode']['firstAired'], short=True)
                #     first_aired = True
                # except KeyError:
                #     first_aired = False

                offset = '+0000'

                program_header_dict = {
                    'start': f'{time_start} {offset}',
                    'stop': f'{time_end} {offset}',
                    'channel': channel_id
                }

                xml_program = ET.SubElement(xml_tv, "programme", program_header_dict)

                try:
                    ET.SubElement(xml_program, "title", {'lang': args.language}).text = program['title']
                    #print(program['title'])
                except KeyError:
                    pass

                try:
                    ET.SubElement(xml_program, "desc", {'lang': args.language}).text = program['description']
                except KeyError:
                    pass

                try:
                    ET.SubElement(xml_program, "length", {'units': 'seconds'}).text = str(program['duration'] / 1000)
                except KeyError:
                    pass

#                time_original = None
#                if time_original_long != '' and args.long_date:
#                    time_original = f'{time_original_long} {offset}'
#                elif time_original_short != '':
#                    time_original = time_original_short
#                elif args.long_date and first_aired:
#                    time_original = first_aired_long
#                elif first_aired:
#                    time_original = first_aired_short

#                if time_original is not None:
#                    ET.SubElement(xml_program, "date").text = time_original

                try:
                    ET.SubElement(xml_program, "date").text = program['year']
                except:
                    pass

                try:
                    if program['episode_title'] != program['tile']:
                        ET.SubElement(xml_program, "sub-title", {'lang': args.language}).text = program['episode_title']
                except KeyError:
                    pass

                try:
                    poster = program['images']['poster'][0]
                    if poster != 'https://cdn.adrise.tv/tubitv-assets/img/tubi_open-graph-512x512.png':
                        ET.SubElement(xml_program, "icon", {'src': poster})
                except KeyError:
                    pass

                numbers = ['season', 'number']
                onscreen_ns = ''
                common_ns = ''
                xmltv_ns = ''
#                pluto_ns = program['episode']['_id']

                season_found = False

                for number in numbers:
                    try:
                        program['episode'][number]
                        if number == 'season':
                            season_found = True
                    except KeyError:
                        pass

                    try:
                        if program['episode'][number] < 10:
                            program['episode'][number] = f"0{program['episode'][number]}"
                        else:
                            program['episode'][number] = f"{program['episode'][number]}"

                        if number == 'season':
                            onscreen_ns = f"S{program['episode'][number]}"
                            common_ns = f"S{program['episode'][number]}"
                            xmltv_ns = f"{int(program['episode'][number]) - 1}"
                        else:
                            if season_found:
                                onscreen_ns = f"{onscreen_ns}E{program['episode'][number]}"
                                common_ns = f"{common_ns}E{program['episode'][number]}"
                                xmltv_ns = f"{xmltv_ns}.{int(program['episode'][number]) - 1}."
                    except KeyError:
                        pass

                if onscreen_ns != '':
                    ET.SubElement(xml_program, "episode-num", {'system': 'onscreen'}).text = onscreen_ns

                if common_ns != '':
                    ET.SubElement(xml_program, "episode-num", {'system': 'common'}).text = common_ns

                if xmltv_ns != '':
                    ET.SubElement(xml_program, "episode-num", {'system': 'xmltv_ns'}).text = xmltv_ns

 #               if pluto_ns != '':
 #                   ET.SubElement(xml_program, "episode-num", {'system': 'pluto'}).text = pluto_ns

                try:
                    xml_rating = ET.SubElement(xml_program, "rating", {'system': rating_system[program['ratings'][0]['system'].lower()]})
                    ET.SubElement(xml_rating, "value").text = program['ratings'][0]['value']
                    ET.SubElement(xml_rating, "icon", {"src": rating_logo[program['ratings'][0]['value'].lower()]})
                except KeyError:
                    pass
                except:
                    pass

                genre_names = ['genre', 'subGenre']
                genres = []

                try:
                    for genre_name in genre_names:
                        genre = program['episode'][genre_name]
                        if genre not in genres:
                            genres.append(genre)
                except KeyError:
                    pass

                for genre in genres:
                    ET.SubElement(xml_program, "category", {'lang': args.language}).text = genre

#                if program['episode']['liveBroadcast']:
#                    ET.SubElement(xml_program, "live")

#                if time_start == first_aired_long and first_aired:
#                    ET.SubElement(xml_program, "premiere")
#                else:
#                    if first_aired_long != '' and first_aired:
#                        ET.SubElement(xml_program, "previously-shown", {'start': f'{first_aired_long} {offset}'})
#                    elif first_aired:
#                        ET.SubElement(xml_program, "previously-shown")

                xml_video = ET.SubElement(xml_program, "video")
                ET.SubElement(xml_video, "present").text = 'yes'
                ET.SubElement(xml_video, "aspect").text = '16:9'
                ET.SubElement(xml_video, "quality").text = 'HDTV'

                y += 1

        if args.m3u:
            if args.number_as_name:
                tvg_name = f"{new_number}"
                tvg_id = f"{new_number}"
            else:
                tvg_name = f"{args.prefix}{channel['title']}"
                tvg_id = f"{args.prefix}{channel['content_id']}"

            tvg_chno = f"{new_number}"
            cuid = channel['content_id']
            group_title = 'tubitv.com'

            # for image in channel['images']:
            #     if image['type'].lower() == 'poster':
            #         tvg_logo = image['url']
            #         break
            tvg_logo = channel['images']['landscape'][0]
            tvg_url = channel['video_resources'][0]['manifest']['url']

            m3u_f.write(
                f'#EXTINF:-1 tvg-ID="{tvg_id}" CUID="{cuid}" tvg-chno="{tvg_chno}" tvg-name="{tvg_name}" tvg-logo="{tvg_logo}" group-title={group_title}\n')

            # if args.streamlink:
            #     m3u_f.write(f"https://pluto.tv/live-tv/{channel['slug']}\n")

            m3u_f.write(f"{tvg_url}\n")

        x += 1

    if args.xml:
        # write the xml file
        print('xml is being created')
        with open(args.xmlFile, "wb") as xml_f:  # https://stackoverflow.com/a/42495690/11214013
            xml_f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf-8'))
            xml_f.write('<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'.encode('utf-8'))

            new_xml = ET.ElementTree(xml_tv)

            # for child in xml_tv:
            #     print(child.tag, child.attrib)

            try:
                ET.indent(new_xml, space="\t", level=0)
            except AttributeError:
                print('Warning: Upgrade to Python 3.9 to have indented xml')
            new_xml.write(xml_f, encoding='utf-8')

        print('xml has being written')

    if args.m3u:
        print('m3u is being closed')
        m3u_f.close()


if __name__ == '__main__':
    main()
