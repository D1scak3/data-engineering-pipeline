import os, random
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense, LSTM


class LSTMSimple:
    def __init__(self, n_steps, n_features):
        # data for the model
        self.is_fitted = False
        self.data = None
        self.df_long = None
        self.df_wide = None

        # model itself
        self.n_steps = n_steps
        self.n_features = n_features

        self.model = Sequential()
        self.model.add(
            LSTM(50, activation="relu", input_shape=(self.n_steps, self.n_features))
        )
        self.model.add(Dense(1))
        self.model.compile(optimizer="adam", loss="mse")

    def fit(
        self, data_x, data_y, epochs, batch_size, validation_data, verbose, shuffle
    ):
        self.is_fitted = True
        self.model.fit(
            x=data_x,
            y=data_y,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=validation_data,
            verbose=verbose,
            shuffle=shuffle,
        )

    def predict(self, data):
        if self.is_fitted is not True:
            print("Model is not fitted.")
            return

        return self.model.predict(data)


if __name__ == "__main__":
    # setup seeds for deterministic values
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["TF_DETERMINISTIC_OPS"] = "1"
    random.seed(1234)
    np.random.seed(1234)
    # tf.random.set_seed(1234)

    # create model
    company = "movistar"
    steps = 7
    features = 1
    percent_train = 0.7
    Test_model = LSTMSimple(n_steps=steps, n_features=features)

    # read data
    data = pd.read_pickle("../data/long_product_group_id_23")

    # reorganize data ordered by timestamp and grouped by company
    reorg = (
        data.reset_index()
        .groupby(["timestamp", "company"])["price"]
        .first()
        .unstack()
        .reset_index()
        .set_index("timestamp")
    )

    # fill missing timestamps and fill missing values by interpolation
    # filling is made having into account data from other companies
    # since each company might not update values at the same time
    timestamps = pd.DataFrame(
        index=pd.date_range(reorg.index[0], reorg.index[-1], freq="D")
    )
    reorg = pd.merge(timestamps, reorg, left_index=True, right_index=True, how="left")
    reorg.columns.name = None
    reorg.interpolate(method="time", inplace=True, limit_direction="both")

    # select data of a certain company for fitting and predicting
    X = []
    Y = []
    raw_data = reorg[company]

    for i in range(len(raw_data)):
        end_ix = i + steps

        if end_ix > len(raw_data) - 1:
            break

        seq_x, seq_y = raw_data[i:end_ix], raw_data[end_ix]

        X.append(seq_x)
        Y.append(seq_y)

    X = np.array(X)
    Y = np.array(Y)

    value = int(len(X) * percent_train)
    fit = (X[:value], Y[:value])
    test = (X[value:], Y[value:])

    # fit model
    Test_model.fit(
        data_x=fit[0],
        data_y=fit[1],
        validation_data=test,
        epochs=100,
        batch_size=72,
        verbose=1,
        shuffle=False,
    )

    # predict values
    results = Test_model.predict(test[0])
    # print(results)

    # measure performance
    # mse = mean_squared_error(test[1], results)
    # print('Test MSE: %.3f' % mse)
