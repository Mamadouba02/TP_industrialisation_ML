import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from src.config import ROOT


def main():
    df = pd.read_csv(ROOT / 'data/raw/churn.csv')
    print(df.head(), df.shape, df.dtypes, df.isna().sum(), df.describe(), sep='\n')
    sns.countplot(data=df, x='churn')
    plt.title('Répartition du churn')
    plt.savefig(ROOT / 'data/churn_distribution.png')
    plt.close()
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.corr(), annot=True, fmt='.2f')
    plt.tight_layout()
    plt.savefig(ROOT / 'data/correlation.png')
    plt.close()


if __name__ == '__main__':
    main()
