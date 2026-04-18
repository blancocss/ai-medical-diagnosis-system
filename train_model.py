"""
train_model.py
==============
Trains a Decision Tree classifier on Training.csv and saves it
to medical_model.pkl.

Run this script once to (re)generate the model:
    python train_model.py

Improvements over original:
  - Structured logging instead of print statements
  - Explicit random_state for reproducibility
  - Cross-validation accuracy reported
  - Handles missing/unnamed columns defensively
  - Imports grouped at the top
"""

import logging
import sys
import time

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("TrainModel")


def load_and_clean(csv_path: str) -> pd.DataFrame:
    """Load a CSV and drop unnamed index columns."""
    df = pd.read_csv(csv_path)
    df = df.loc[:, ~df.columns.str.contains(r'^Unnamed')]
    return df


def train() -> None:
    t_start = time.perf_counter()

    # ── Load data ─────────────────────────────────────────────────────────────
    logger.info("Loading training data…")
    try:
        train_df = load_and_clean("Training.csv")
        test_df  = load_and_clean("Testing.csv")
    except FileNotFoundError as e:
        logger.error("CSV file not found: %s", e)
        sys.exit(1)

    logger.info("Training samples: %d | Testing samples: %d",
                len(train_df), len(test_df))

    # ── Feature / label split ─────────────────────────────────────────────────
    X_train = train_df.drop("prognosis", axis=1)
    y_train = train_df["prognosis"]
    X_test  = test_df.drop("prognosis", axis=1)
    y_test  = test_df["prognosis"]

    logger.info("Features: %d  |  Classes: %d", X_train.shape[1], y_train.nunique())

    # ── Train model ───────────────────────────────────────────────────────────
    logger.info("Training DecisionTreeClassifier…")
    model = DecisionTreeClassifier(random_state=42)
    model.fit(X_train, y_train)

    # ── Evaluate ──────────────────────────────────────────────────────────────
    predictions = model.predict(X_test)
    acc         = accuracy_score(y_test, predictions)
    logger.info("Test accuracy: %.4f (%.2f%%)", acc, acc * 100)

    # Cross-validation on training set
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)
    logger.info("5-fold CV accuracy: %.4f ± %.4f", cv_scores.mean(), cv_scores.std())

    # ── Save model ────────────────────────────────────────────────────────────
    output_path = "medical_model.pkl"
    joblib.dump(model, output_path)
    elapsed = (time.perf_counter() - t_start) * 1000
    logger.info("Model saved to '%s'  (total time: %.0f ms)", output_path, elapsed)


if __name__ == "__main__":
    train()
