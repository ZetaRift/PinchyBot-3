from datetime import timedelta
import time
import decimal
import json
import requests
 
#To grab video stats off a youtube video using JSON

#This is broken because youtube changed its API, bullshit changes being made

api_key = "" #Requires an API key
 
def fetch_video_info(video_id):
    r = requests.get('https://www.googleapis.com/youtube/v3/videos?id={id}&key={api_key}&part=snippet,statistics'.format(id=video_id,api_key=api_key))
    return json.loads(r.text)
 
_title = lambda vinfo: vinfo['items'][0]['snippet']['title']
#_length = lambda video_info: int(video_info['entry']['media$group']['yt$duration']['seconds'])
_view_count = lambda vinfo: int(vinfo['items'][0]['statistics']['viewCount'])
_upvote_count = lambda vinfo: int(vinfo['items'][0]['statistics']['likeCount'])
_downvote_count = lambda vinfo: int(vinfo['items'][0]['statistics']['dislikeCount'])
#_human_readable_duration = lambda seconds: str(timedelta(seconds=seconds))
 
def stats_string(video_id):   #something useless
    vinfo = fetch_video_info(video_id)
    return "[YouTube: {title} | Views: {view_count} | Votes: {upvote_count} up - {downvote_count} down]".format(
        title=_title(vinfo),
        view_count=_view_count(vinfo),
        upvote_count=_upvote_count(vinfo),
        downvote_count=_downvote_count(vinfo)
        )
