import requests
def search(terms):
        newterms = terms.replace(" ", "%20")
        baseurl = "http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q="
        url = baseurl + newterms
        response = requests.get(url)
        jsondata = response.json()
        try:
                image = jsondata['responseData']['results'][0]['unescapedUrl']
        except:
                image = "image not found"
        return image
