import requests




def grab_info(story_URL): #Either the number ID or the whole url works
 r = requests.get('http://www.fimfiction.net/api/story.php?story={url}'.format(url=story_URL))
 if r.status_code != 200:
  return None
 else:
  return r.json()
  

_title = lambda fic_info: fic_info["story"]["title"]
_views = lambda fic_info: int(fic_info["story"]["total_views"])
_words = lambda fic_info: int(fic_info["story"]["words"])
_rating = lambda fic_info: fic_info["story"]["content_rating_text"]
_likes = lambda fic_info: int(fic_info["story"]["likes"])
_dislikes = lambda fic_info: int(fic_info["story"]["dislikes"])
_chapters = lambda fic_info: int(fic_info["story"]["chapter_count"])
_author = lambda fic_info: fic_info["story"]["author"]["name"]


def statstring(url):
 fic_info = grab_info(url)
 if fic_info is None:
  return "Nothing"
 else:
  return "({rt}) <b>{t}</b> by <b>{au}</b> | <b>Views</b>: {v} | <b>Chapters</b>: {cc}, <b>Total words</b>: {w} | <b>Likes</b>: {l} | <b>Dislikes</b>: {dl}".format(
   rt=_rating(fic_info),
   t=_title(fic_info),
   v=_views(fic_info),
   cc=_chapters(fic_info),
   w=_words(fic_info),
   l=_likes(fic_info),
   dl=_dislikes(fic_info),
   au=_author(fic_info)
   )
