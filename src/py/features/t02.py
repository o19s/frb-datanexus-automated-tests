import datetime

import pandas as pd

from solr.solr import *


def t02(solr_cnx, args):
    """
    Executes the T02 test plan.
    :param solr_cnx: Solr connection.
    :param args: command-line args (All of them).
    :return: True (Success), or False (An error occurred during the execution)
    """
    test_exec_result = True
    test_name = 'T02'
    print('Test {} starting...'.format(test_name))
    query_count = 0
    try:
        # Read the test data
        xl = pd.ExcelFile(args.file)
        assert (xl is not None)
        # print(xl.sheet_names)
        df = xl.parse(args.feature)
        assert (df is not None)

        # DataFrame 0-based row and column indexes
        # Note: The first row in the spreadsheet was read as the column headers
        queries_row_idx = 1
        queries_col_from_idx = 3
        queries_col_to_idx = 45

        # facet_field_name = 'RecordType_s'
        facet_field_name = 'genres'  # For local tests with the movies index

        facet_values_row_idx = 10

        baseline_counts_not_filtered_row_idx = 17
        baseline_counts_filtered_row_idx = 17

        queries = []

        counts = []
        counts_baseline = []
        counts_test = []

        counts_filtered = []
        counts_filtered_baseline = []
        counts_filtered_test = []

        tests_pass_counter = 0
        tests_fail_counter = 0

        for col_idx in range(queries_col_from_idx, queries_col_to_idx + 1):
            query = df.iloc[queries_row_idx, col_idx]
            facet_value = df.iloc[facet_values_row_idx, col_idx]
            baseline_count_not_filtered = df.iloc[baseline_counts_not_filtered_row_idx, col_idx]
            baseline_count_filtered = df.iloc[baseline_counts_filtered_row_idx, col_idx]

            print('\nq={}, facet {} value={}, baseline counts: {} (not filtered), {} (filtered)'.format(
                query,
                facet_value,
                facet_field_name,
                baseline_count_not_filtered,
                baseline_count_filtered
            ))

            queries.append(query)
            counts_baseline.append(baseline_count_not_filtered)
            counts_filtered_baseline.append(baseline_count_filtered)

            rows_count = 10
            search_params = {
                'rows': rows_count,
                'facet': 'true',
                'facet.field': facet_field_name
            }
            results = solr_search_with_params(
                cnx=solr_cnx,
                what=query,
                params=search_params
            )
            assert (int(results['responseHeader']['status']) == 0)
            query_count += 1

            # Number of matches
            numFound = int(results['response']['numFound'])
            print('\tcounts={} retrieved in {} ms'.format(numFound, results['responseHeader']['QTime']))

            # Number of matches for the specified facet value
            facet_value_count = 0
            facet_array = results['facet_counts']['facet_fields'][facet_field_name]
            facet_dict = {}
            for idx, value in enumerate(facet_array):
                if idx % 2 == 0:
                    facet_dict[value] = facet_array[idx + 1]
                    # print('{}: {}'.format(value, facet_dict[value]))
            if facet_value in facet_dict.keys():
                facet_value_count = facet_dict[facet_value]

            print('\tfacet value {} count={}'.format(facet_value, facet_value_count))

            counts.append(numFound)
            counts_filtered.append(facet_value_count)

            count_test = 'PASS' if numFound == baseline_count_not_filtered else 'FAIL'
            (printGreen if count_test == 'PASS' else printRed)('\tcount_test: {}'.format(count_test))

            count_filtered_test = 'PASS' if facet_value_count == baseline_count_filtered else 'FAIL'
            (printGreen if count_filtered_test == 'PASS' else printRed)(
                '\tcount_filtered_test: {}'.format(count_filtered_test))

            counts_test.append(count_test)
            counts_filtered_test.append(count_filtered_test)

            if count_test == 'PASS' and count_filtered_test == 'PASS':
                tests_pass_counter += 1
            else:
                tests_fail_counter += 1

        # Test results
        test_results_filename = '{}_results.csv'.format(test_name)
        with open(test_results_filename, 'w') as f:

            for testdata_idx, testdata in enumerate([
                queries,
                counts_baseline,
                counts,
                counts_test,
                counts_filtered_baseline,
                counts_filtered,
                counts_filtered_test
            ]):
                if testdata_idx == 0:
                    f.write('Test Date')
                else:
                    f.write(datetime.datetime.now().strftime("%m-%d-%y"))

                for idx, value in enumerate(testdata):
                    f.write(',{}'.format(value))
                f.write('\n')

        print('\nTest results:')
        printGreen('\tPASS: {} ({} %)'.format(tests_pass_counter, round((tests_pass_counter/query_count)*100, 2)))
        printRed('\tFAIL: {} ({} %)'.format(tests_fail_counter, round((tests_fail_counter / query_count) * 100, 2)))
        print('\nSee test results in {}'.format(test_results_filename))

    except Exception as e:
        printRed('Error: {}'.format(e))
        test_exec_result = False
    finally:
        print('\nTest {} completed with {} queries.'.format(test_name, query_count))
    return test_exec_result
