import pandas as pd


def add_column(df, index, col_name, default_data):
    df = df.insert(index, col_name, default_data)
    return df

def main():
    path = 'data/last data/fans.csv'
    df = pd.read_csv(path, index_col=False, sep='\t')
    print(df.head())
    df = add_column(df, 0, 'friendship', 'fans')
    print(df.head())


if __name__ == '__main__':
    main()