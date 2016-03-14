import elasticsearch
from django.conf import settings
from datetime import datetime


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

    def for_wordcloud(self):
        """
        Returns the contents of the aggregation as a list of lists, suitable for wordcloud
        https://github.com/timdream/wordcloud2.js
        :return: list of lists
        """
        rtn = []
        for k,v in self.data.items():
            rtn.append([k,v])
        return rtn


class ReutersEntry(object):
    def __init__(self,content):
        self.content = content

    def __unicode__(self):
        return u"{0}: ({1}) {2}".format(self.content['_source']['start'],self.content['_source']['usn_id'],
                                        self.content['_source']['slugword'])

    @staticmethod
    def datetime_values(dt):
        from dateutil.parser import parse
        if isinstance(dt,basestring):
            dt = parse(dt)
        if not isinstance(dt,datetime): raise TypeError("supplied value {dt} is not a datetime")
        return {
            'year': dt.year,
            'month': dt.month,
            'day': dt.day,
            'hour': dt.hour,
            'minute': dt.minute,
            'second': dt.second,
        }

    def for_timelinejs(self):
        #build a 'slide object': http://timeline.knightlab.com/docs/json-format.html
        rtn = {
            'start_date': self.datetime_values(self.content['_source']['start']),
            'end_date': self.datetime_values(self.content['_source']['end']),
            'text': {'headline': self.content['_source']['slugword'], 'text': self.content['_source']['description']},
            #'group': self.content['_source']['usn_id'], #group by content ID
            'group': self.content['_source']['location'],
            'autolink': False,
        }
        return rtn


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
                yield ReutersEntry(r)
            if one_page or len(result['hits']['hits'])<page_length:
                break
            page+=1

    def specific_id(self,docid):
        return self._client.get(self.indexname,docid,self.doctype)

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
        elif isinstance(r,ReutersEntry):
            print unicode(r)
        else:
            print "{0}: ({1}) {2}".format(r['_source']['start'],r['_source']['usn_id'],r['_source']['slugword'])