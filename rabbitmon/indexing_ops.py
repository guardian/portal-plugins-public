INDEXNAME = 'rabbitmq_stats'
DOCTYPE = 'stats'


class RabbitIndex(object):
    def __init__(self, hosts):
        from elasticsearch import Elasticsearch

        self._client = Elasticsearch(hosts=hosts,)

    def setup_index(self,nshards=3,nreplicas=1):
        result = self._client.indices.create(index=INDEXNAME,
                                             body={
                                                 'settings': {
                                                     'number_of_shards': nshards,
                                                     'number_of_replicas': nreplicas,
                                                 },
                                                 'mappings': {
                                                     DOCTYPE: {
                                                         "properties": {
                                                             'name': {
                                                                 'type': 'string',
                                                                 'index': 'not_analyzed'
                                                             },
                                                             'node': {
                                                                 'type' : 'string',
                                                                 'index': 'not_analyzed'
                                                             },
                                                             'idle_since': {
                                                                 'type' : 'date'
                                                             },
                                                         }
                                                     }
                                                 }
                                             })

    def queue_names(self):
        from pprint import pprint
        result = self._client.search(index=INDEXNAME,doc_type=DOCTYPE,size=0,
                            body={
                                'query': {
                                    'match_all': {}
                                },
                                'aggs': {
                                    'fields': {
                                        'terms': {
                                            'field': 'name'
                                        }
                                    }
                                }
                            }
                            )
        return map(lambda x: x['key'],result['aggregations']['fields']['buckets'])