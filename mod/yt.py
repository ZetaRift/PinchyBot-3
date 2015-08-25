from datetime import timedelta
import time
import decimal
import json
import requests
import re
 
#To grab video stats off a youtube video using JSON


api_key = "" #As of v3, an API key is required.

def iso8601_time(timestr): #Youtube data v3 API gives out ISO 8601 time format for length of videos
 iso_8601_re = re.compile('P(?P<year>[0-9]*Y)?(?P<month>[0-9]*M)?(?P<week>[0-9]*W)?(?P<day>[0-9]*D)?(T)?(?P<hour>[0-9]*H)?(?P<minute>[0-9]*M)?(?P<second>[0-9]*S)?')
 ftime = re.match(iso_8601_re, timestr)
 year, month, week, day, hour, minute, second = '','','','','','',''
 return_time = ''
 if ftime.group('year'):
  year = ftime.group('year').rstrip('Y')
  return_time = return_time + year + 'y '
 if ftime.group('month'):
  month = ftime.group('month').rstrip('M')
  return_time = return_time + month + 'Mo '
 if ftime.group('week'):
  week = ftime.group('week').rstrip('W')
  return_time = return_time + week + 'w '
 if ftime.group('day'):
  day = ftime.group('day').rstrip('D')
  return_time = return_time + day + 'd '
 if ftime.group('hour'):
  hour = ftime.group('hour').rstrip('H')
  return_time = return_time + hour + 'H '
 if ftime.group('minute'):
  minute = ftime.group('minute').rstrip('M')
  return_time = return_time + minute + 'M '
 if ftime.group('second'):
  second = ftime.group('second').rstrip('S')
  return_time = return_time + second + 'S'

 return return_time
 
def fetch_video_info(video_id):
    r = requests.get('https://www.googleapis.com/youtube/v3/videos?id={id}&key={api_key}&part=snippet,statistics,contentDetails'.format(id=video_id,api_key=api_key))
    return json.loads(r.text)
 
_title = lambda vinfo: vinfo['items'][0]['snippet']['title']
_length = lambda vinfo: vinfo['items'][0]['contentDetails']['duration']
_view_count = lambda vinfo: int(vinfo['items'][0]['statistics']['viewCount'])
_upvote_count = lambda vinfo: int(vinfo['items'][0]['statistics']['likeCount'])
_downvote_count = lambda vinfo: int(vinfo['items'][0]['statistics']['dislikeCount'])
#_human_readable_duration = lambda seconds: str(timedelta(seconds=seconds))
 
def stats_string(video_id):   #something useless
    vinfo = fetch_video_info(video_id)
    return "[YouTube: {title} | Length: {length} | Views: {view_count} | Votes: {upvote_count} up - {downvote_count} down]".format(
        title=_title(vinfo),
        view_count=_view_count(vinfo),
        upvote_count=_upvote_count(vinfo),
        downvote_count=_downvote_count(vinfo),
        length=iso8601_time(_length(vinfo))
        )
