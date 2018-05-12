import pysolr

from utils.utils import *


def solr_connect(url, handler):
    solr_cnx = None
    try:
        print('Connecting to Solr at {0}...'.format(url))
        # Optional arg: results_cls=dict
        solr_cnx = pysolr.Solr(url, timeout=30, search_handler=handler, results_cls=dict)
        printGreen('Successfully connected to solr at "{}" with handler "{}"!'.format(url, handler))
    except Exception as e:
        printRed('ERROR: An exception occurred when connecting to Solr host "{}"'.format(url))
    return solr_cnx


def solr_search_with_params(cnx, what, params):
    return cnx.search(what, **params, timeout=60)
