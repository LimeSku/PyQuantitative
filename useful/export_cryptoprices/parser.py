from argparse import ArgumentParser

def get_args():
    parser = ArgumentParser(description='gen candles')

    subparsers = parser.add_subparsers(dest='mode')
    subparsers.required = True  # required since 3.7

    # parser for binary correlation
    parser_sql = subparsers.add_parser('sql_export')
    parser_sql.add_argument("-f",type=str)
    parser_sql.add_argument("-to",type=str)



    #search regression = SR
    parser_csv = subparsers.add_parser('csv_export')
    parser_mix = subparsers.add_parser('mix_export')

    return parser