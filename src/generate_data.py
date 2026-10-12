import sys
from pathlib import Path
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
from src.config import ROOT


def generate_data(n=2000, seed=42):
    rng = np.random.RandomState(seed)
    df = pd.DataFrame({
        'age': rng.randint(18, 70, n),
        'anciennete': rng.randint(1, 120, n),
        'revenu': rng.randint(150000, 1000000, n),
        'nb_reclamations': rng.poisson(2, n),
        'montant_mensuel': rng.randint(5000, 75000, n),
        'retards_paiement': rng.poisson(1, n),
    })
    score = .04 * df.nb_reclamations + .08 * df.retards_paiement - .015 * df.anciennete + .00001 * df.montant_mensuel
    df['churn'] = (rng.random_sample(n) < 1 / (1 + np.exp(-score))).astype(int)
    return df


def main():
    path = ROOT / 'data/raw/churn.csv'
    path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_data()
    df.to_csv(path, index=False)
    print(df.head())
    print(df.churn.value_counts())


if __name__ == '__main__':
    main()
