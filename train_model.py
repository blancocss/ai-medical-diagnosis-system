import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# قراءة البيانات
train_data = pd.read_csv("Training.csv")
test_data = pd.read_csv("Testing.csv")

# حذف الأعمدة الفارغة مثل Unnamed
train_data = train_data.loc[:, ~train_data.columns.str.contains('^Unnamed')]
test_data = test_data.loc[:, ~test_data.columns.str.contains('^Unnamed')]

# فصل المدخلات والنتيجة
X_train = train_data.drop("prognosis", axis=1)
y_train = train_data["prognosis"]

X_test = test_data.drop("prognosis", axis=1)
y_test = test_data["prognosis"]

# إنشاء النموذج
model = DecisionTreeClassifier()

# تدريب النموذج
model.fit(X_train, y_train)

# التوقع
predictions = model.predict(X_test)

# حساب الدقة
accuracy = accuracy_score(y_test, predictions)

print("Model trained successfully!")
print("Accuracy:", accuracy)
import joblib

# حفظ النموذج
joblib.dump(model, "medical_model.pkl")

print("Model saved successfully!")