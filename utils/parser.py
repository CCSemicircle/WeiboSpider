import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Model Params')
    parser.add_argument('--top_100_date', nargs='?', required=True, help='Top 100 date, format: "YYYY-mm-dd" or "YYYY-mm".')
    parser.add_argument('--top_100_type', nargs='?', default='week', help='Top 100 type, Choose from {"week", "month"}, Default: "week".')
    parser.add_argument('--friend_num', type=int, default=2000, help='Number of fans or followers. Default: 2000.')
    parser.add_argument('--weibo_start_date', nargs='?', required=True, help='Start date of weibo, format: "YYYY-mm-dd".')
    parser.add_argument('--weibo_end_date', nargs='?', required=True, help='End date of weibo, format: "YYYY-mm-dd".')
    return parser.parse_args()


args = parse_args()