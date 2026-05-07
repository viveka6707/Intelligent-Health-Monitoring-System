import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

# ---------------- LOAD DATASET ----------------
data = pd.read_csv("health_dataset.csv")

print("Dataset Loaded")
print(data.head())

# ---------------- CONVERT GENDER ----------------
data["gender"] = data["gender"].map({"M":1, "F":0})

# ---------------- FEATURES & TARGET ----------------
X = data.drop("disease", axis=1)
y = data["disease"]

# ---------------- ENCODE DISEASE ----------------
le = LabelEncoder()
y = le.fit_transform(y)

# ---------------- TRAIN TEST SPLIT ----------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ---------------- MODEL ----------------
model = RandomForestClassifier(n_estimators=100)

model.fit(X_train, y_train)

print("Model Trained Successfully")

# ---------------- SAVE MODEL ----------------
pickle.dump(model, open("risk_model.pkl", "wb"))
pickle.dump(le, open("label_encoder.pkl", "wb"))

print("Model Saved Successfully")