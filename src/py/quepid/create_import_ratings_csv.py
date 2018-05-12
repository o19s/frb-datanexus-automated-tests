import argparse
import time
from datetime import timedelta

import pandas as pd

from utils.utils import *

if __name__ == "__main__":
    """Usage example: 
    create_import_ratings_csv 
    --file <DataNexus spreadsheet file name> 
    --sheet <sheet name> 
    --row <row number (1-based)> 
    --columns <col_number_start:col_number_end (1-based)>
    [--phrase true] 
    """
    start_time = time.monotonic()
    try:
        parser = argparse.ArgumentParser(
            description='Quepid create import ratings CSV file from DataNexus spreadsheet.')
        parser.add_argument('-f', '--file', help='DataNexus spreadsheet filename', required=True)
        parser.add_argument('-s', '--sheet', help='DataNexus spreadsheet sheet name', required=True)
        parser.add_argument('-r', '--row', help='DataNexus spreadsheet sheet row index (1-based) number', required=True)
        parser.add_argument('-c', '--columns',
                            help='DataNexus spreadsheet sheet columns index (1-based) range (e.g., 1:5 for the first 5 columns)',
                            required=True)
        parser.add_argument('-p', '--phrase', help='Generate phrase queries', required=False)

        args = parser.parse_args()

        spreadsheet_filename = args.file
        print('Extracting queries from {}, sheet {}, row {}, columns {}...'.format(args.file, args.sheet, args.row,
                                                                                   args.columns))

        xl = pd.ExcelFile(args.file)
        # print(xl.sheet_names)
        df = xl.parse(args.sheet)
        # print(list(df.columns.values))

        # Sheet rows:
        # First: Read as column names
        # Second and later: 0-based indexed data rows
        row_idx = int(args.row) - 2
        cols_range = args.columns.split(':')
        col_start = int(cols_range[0]) - 1
        col_end = int(cols_range[1]) - 1
        col_count = col_end - col_start + 1
        assert (col_count > 0)

        print('Read sheet cells at DataFrame-indexed row {} from column {} to {}...'.format(row_idx, col_start,
                                                                                            col_start + col_count - 1))

        with open('quepid_{}_queries.csv'.format(args.sheet), 'w') as f:

            f.write('Query Text,Doc ID,Rating\n')

            dummy_doc_id = 0
            rating = 1

            for col_idx in range(col_start, col_start + col_count):
                query_text = df.iloc[row_idx, col_idx]
                csv_line = '{},{},{}'.format(query_text, dummy_doc_id, rating)
                print('[{},{}] {}'.format(row_idx, col_idx, csv_line))
                f.write('{}\n'.format(csv_line))
                if args.phrase:
                    csv_line_phrase = '"{}",{},{}'.format(query_text, dummy_doc_id, rating)
                    f.write('{}\n'.format(csv_line_phrase))

    except Exception as e:
        printRed('Error: {}'.format(e))
    finally:
        end_time = time.monotonic()
        print("\nTests execution time: {}".format(timedelta(seconds=end_time - start_time)))
