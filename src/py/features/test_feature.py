import argparse
import time
from datetime import timedelta

from features.t02 import *
from solr.solr import *

if __name__ == "__main__":
    """Usage example: 
    test_feature 
    --host <host name or IP address> 
    --port <port number> 
    --core <Solr core name, e.g., DataNexus>
    --search <search handler name, e.g., DataNexusSearch>
    --file <dataNexus spreadsheet pathname>
    --feature <feature code (e.g., T02)     
    """
    start_time = time.monotonic()
    solr_cnx = None
    try:
        parser = argparse.ArgumentParser(description='Run a feature test')
        parser.add_argument('-s', '--server', help='DataNexus Solr host name or IP address', required=True)
        parser.add_argument('-p', '--port', help='DataNexus Solr port number', required=True)
        parser.add_argument('-c', '--core', help='DataNexus Solr core name', required=True)
        parser.add_argument('-r', '--request', help='DataNexus Solr search request handler', required=True)
        parser.add_argument('-f', '--file', help='DataNexus spreadsheet filename (e.g., SystemTest_Master_FRB)',
                            required=True)
        parser.add_argument('-e', '--feature', help='DataNexus spreadsheet sheet name (e.g., T02)', required=True)

        args = parser.parse_args()

        print('host   : {}'.format(args.server))
        print('port   : {}'.format(args.port))
        print('core   : {}'.format(args.core))
        print('search : {}'.format(args.request))
        print('file   : {}'.format(args.file))
        print('feature: {}'.format(args.feature))

        solr_url = 'http://{}:{}/solr/{}'.format(args.server, args.port, args.core)

        # Connect to Solr
        solr_cnx = solr_connect(solr_url, args.request)
        if solr_cnx is None:
            raise Exception('Solr connection issue')

        # Self test
        print('self test...')
        rows_count = 10
        search_params = {
            'rows': rows_count
        }
        results = solr_search_with_params(
            cnx=solr_cnx,
            what='test',
            params=search_params
        )
        assert (int(results['responseHeader']['status']) == 0)
        print('self test successful. Proceeding...')

        feature_under_test = args.feature.lower()

        print('Executing test plan for feature {}...'.format(feature_under_test))

        # Features dictionary:
        # key=feature name, value=feature executor
        features = {
            't02': t02
        }

        if feature_under_test not in features.keys():
            raise Exception('Invalid feature/test name {}!'.format(feature_under_test))

        features[feature_under_test](solr_cnx, args)


    except Exception as e:
        printRed('\nError: {}'.format(e))
    finally:
        print('\nClosing the solr connection...')
        try:
            solr_cnx.get_session().close()
            printGreen("Successfully closed the Solr connection.")
        except Exception as e:
            printRed("An error occurred when closing the Solr connection:\n{}".format(e))
        end_time = time.monotonic()
        print("\nTests execution time: {}".format(timedelta(seconds=end_time - start_time)))
