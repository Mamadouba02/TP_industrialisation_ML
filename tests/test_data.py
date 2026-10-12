from src.generate_data import generate_data
from src.config import FEATURES


def test_dataset_reproducibility():
    df = generate_data()
    assert df.equals(generate_data())
    assert df.shape == (2000, 7)
    assert list(df.columns) == FEATURES + ['churn']
    assert not df.isna().any().any()
    assert set(df.churn) == {0, 1}
