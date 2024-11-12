import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM
import numpy as np


def load_model(model_path='models/ocsvm_model.pkl'):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

def detect_anomalies(spans):
    projectKey = spans['projectKey'].iloc[0]
    traceId = spans['traceId'].iloc[0]

    response_times = spans['duration'].values
    duration_differences = np.diff(response_times, prepend=0)

    sample_weights = np.where(duration_differences > 500, 3, 1)
    response_times_reshaped = duration_differences.reshape(-1, 1)

    threshold = np.median(duration_differences)
    mask = duration_differences <= threshold

    scaler = StandardScaler()
    response_times_scaled = scaler.fit_transform(response_times_reshaped)

    ocsvm = OneClassSVM(kernel='rbf', gamma=0.001, nu=0.05)  # nu: 이상치 비율
    ocsvm.fit(response_times_scaled, sample_weight=sample_weights)

    predictions = ocsvm.predict(response_times_scaled)

    high_indices = np.where(mask)[0]
    predictions[high_indices] = 1

    anomaly_index = [i for i, pred in enumerate(predictions) if pred == -1]
    anomaly_spans = spans.iloc[anomaly_index]['id'].tolist()

    anomalies = {}

    num_anomalies = sum(predictions == -1)

    if num_anomalies >= 3:
        print(f"Alert: Transaction {traceId} has {num_anomalies} anomalies!")
        anomalies['isAnomaly'] = True
        anomalies['projectKey'] = projectKey
        anomalies['anomalySpanIds'] = anomaly_spans
    else:
        anomalies['isAnomaly'] = False
        anomalies['projectKey'] = projectKey
        anomalies['anomalySpanIds'] = anomaly_spans

    return anomalies
