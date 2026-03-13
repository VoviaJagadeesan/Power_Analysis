import numpy as np
import pandas as pd


def forecast_future(model, scaler, df, seq_length=24, days=30):

    # Get last known sequence
    last_sequence = df.values[-seq_length:]

    future_predictions = []

    current_sequence = last_sequence.copy()

    for _ in range(days * 24):

        # Scale input
        scaled_input = scaler.transform(current_sequence)

        # Reshape for LSTM
        scaled_input = scaled_input.reshape(1, seq_length, 1)

        # Predict next value
        pred_scaled = model.predict(scaled_input, verbose=0)

        # Convert back to original scale
        pred = scaler.inverse_transform(pred_scaled)[0][0]

        future_predictions.append(pred)

        # Update sliding window
        current_sequence = np.vstack((current_sequence[1:], [[pred]]))

    # Create future timestamps
    last_timestamp = df.index[-1]

    future_index = pd.date_range(
        start=last_timestamp + pd.Timedelta(hours=1),
        periods=days * 24,
        freq="H"
    )

    forecast_df = pd.DataFrame(
        future_predictions,
        index=future_index,
        columns=["Forecast"]
    )

    return forecast_df
