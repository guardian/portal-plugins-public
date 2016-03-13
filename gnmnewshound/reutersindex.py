import elasticsearch
from django.conf import settings


class ReutersAggregation(object):
    def __init__(self,name,content):
        self.name = name
        self.data = {}
        for entry in content['buckets']:
            self.data[entry['key']] = entry['doc_count']

    def __unicode__(self):
        str = u'Aggregation for {0}'.format(self.name)
        for k,v in self.data.items():
            str += '\n\t{0}: {1}'.format(k,v)
        return str


class ReutersIndex(object):
    indexname = "reuters"
    doctype = "advisory"

    def __init__(self, cluster=None):
        if cluster is None:
            cluster = settings.NEWSHOUND_ES_CLUSTER
        self._client = elasticsearch.Elasticsearch(cluster)

    def results_for_daterange(self,start_date,end_date,include_aggregations=False,page=0,page_length=10,one_page=False):
        from datetime import datetime
        if not isinstance(start_date,datetime): raise TypeError('start_date')
        if not isinstance(end_date,datetime): raise TypeError('end_date')
        from pprint import pprint

        while True:
            query = {
                "query": {
                    "filtered": {
                        "filter": {
                            "and": [
                                {
                                    "range": {
                                        "start": {
                                            "lte": end_date.strftime("%Y-%m-%dT%H:%M:%S%z"),
                                            "gte": start_date.strftime("%Y-%m-%dT%H:%M:%S%z")
                                        }
                                    }
                                }
                            ]
                        }
                    }
                },
                "sort": [
                    {
                        "start": "desc"
                    }
                ]
            }
            if include_aggregations:
                query["aggs"]= {
                    "topics": {
                        "terms": {"field": "topic" }
                    },
                    "locations": {
                        "terms": {"field": "location" }
                    },
                    "slugwords": {
                        "terms": {"field": "slugword" }
                    }
                }
            result = self._client.search(index=self.indexname,doc_type=self.doctype,
                                         body=query,params={'size': page_length,'from': page*page_length})

            yield result['hits']['total']
            if 'aggregations' in result:
                for k,v in result['aggregations'].items():
                    a = ReutersAggregation(k,v)
                    #print unicode(a)
                    yield a
                include_aggregations = False    #don't include aggregations the next time around

            for r in result['hits']['hits']:
                yield r
            if one_page or len(result['hits']['hits'])<page_length:
                break
            page+=1


if __name__ == '__main__':
    import sys
    from datetime import datetime

    i = ReutersIndex(cluster=sys.argv[1])

    endtime = datetime.now()
    starttime = datetime.now().replace(hour=0,minute=0,second=0)
    for r in i.results_for_daterange(starttime,endtime,include_aggregations=True,one_page=True):
        if isinstance(r,int):
            print "Got {0} results".format(r)
        elif isinstance(r,ReutersAggregation):
            print unicode(r)
        else:
            print "{0}: ({1}) {2}".format(r['_source']['start'],r['_source']['usn_id'],r['_source']['slugword'])