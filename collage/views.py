from django.shortcuts import render
from .forms import zoektermForm
import ssl
from lodstorage.sparql import SPARQL
import json
from urllib.error import HTTPError
from urllib.request import urlopen

# Create your views here.
def collage(request):
    if request.method == 'POST':
        form = zoektermForm(request.POST)
        if form.is_valid():
            zoekterm = form.cleaned_data['zoekterm']
            ssl._create_default_https_context = ssl._create_unverified_context

            sparqlQuery = """
             PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
             SELECT DISTINCT ?o ?title WHERE {
             ?object cidoc:P129i_is_subject_of ?o .
             ?object cidoc:P102_has_title ?title.
             FILTER (regex(?title, """ + ' "' + zoekterm + '" ' + """ , "i"))
             BIND(RAND() AS ?random) .
             } ORDER BY ?random
             LIMIT 20
             """

            sparql = SPARQL("https://stad.gent/sparql")
            qlod = sparql.queryAsListOfDicts(sparqlQuery)

            
            if len(qlod) == 0:
                return render(request, 'error.html')
            else:
                iiif_manifests = []
                webplatform_links = []
                titels = []
                for i in range(0, len(qlod)):
                    try:
                        response = urlopen(qlod[i]['o'])
                    except ValueError:
                        pass
                    except HTTPError:
                        pass
                    else:
                        data_json = json.loads(response.read())
                        afbeelding = data_json["sequences"][0]['canvases'][0]["images"][0]["resource"]["@id"]
                        afbeelding = afbeelding.replace("full/full/0/default.jpg", "square/1000,/0/default.jpg")
                        manifestje = data_json["@id"]
                        objectnummer = manifestje.rpartition('/')[2]
                        webplatform = "https://data.collectie.gent/entity/" + objectnummer
                        titel = data_json["label"]['@value']
                        iiif_manifests.append(afbeelding)
                        webplatform_links.append(webplatform)
                        titels.append(titel)


                
                if len(iiif_manifests) > 9:
                    iiif_manifests = iiif_manifests[:9]
                    data = zip(iiif_manifests, webplatform_links, titels)
                    print(data)
                    return render (request, 'collage.html', {'form': form, 'data':data})
                else:
                    return render (request, 'collage.html', {'form': form, 'data':data})
        else:
            return render(request, 'error.html')
    form = zoektermForm
    return render(request, 'collage.html', {'form': form})