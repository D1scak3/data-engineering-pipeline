import os
import shutil
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense,LSTM 
from keras.models import load_model
from sklearn.metrics import mean_squared_error

class Lstm:

    def __init__(self, steps, features):
        self.steps = steps
        self.features = features
        self.model = Sequential()
        self.model.add(LSTM(50, activation='relu', input_shape=(steps, features)))
        self.model.add(Dense(1))
        self.model.compile(optimizer='adam', loss='mse')
    

    def save_model(self, path, name):
        self.model.save(path + "/" + name)
        shutil.make_archive(base_name=name, 
                            format="zip", 
                            root_dir=f"{path}/{name}")
        shutil.move("lstm.zip", "saved_models/lstm.zip")
        shutil.rmtree(f"{path}/{name}")


    def load_model(self, path, name):
        shutil.unpack_archive(f"{path}/{name}.zip")
        self.model = load_model(f"{path}/{name}")
        shutil.rmtree(f"{path}/{name}")


    def fit(self, data_x, data_y, test_x, test_y, epochs, batch_size, verbose, shuffle):
        self.model.fit(data_x, data_y, epochs=epochs, batch_size=batch_size, verbose=verbose, validation_data=(test_x, test_y), shuffle=shuffle)


    def predict(self, data):
        return self.model.predict(data)


def get_data(path, company, train_percent, steps):
    # read data
    long = pd.read_pickle(path)
    wide = long.reset_index().groupby(['timestamp', "company"])["price"].first().unstack().reset_index().set_index("timestamp")

    # fill missing timestamps
    timestamps = pd.DataFrame(index = pd.date_range(wide.index[0], wide.index[-1], freq="D"))
    wide = pd.merge(timestamps, wide, left_index=True, right_index=True, how="left")
    wide.columns.name = None

    # interpolate values of filling timestamps
    wide.interpolate(method="time", inplace=True, limit_direction="both")
    raw_seq = wide[company]

    # do something with the data
    X = []
    Y = []
    for i in range(len(raw_seq) - 1):
        end_ix = i + steps

        if end_ix > len(raw_seq) - 1:
            break

        x, y = raw_seq[i:end_ix], raw_seq[end_ix]

        X.append(x)
        Y.append(y)

    X = np.array(X)
    Y = np.array(Y)
    
    # divide the data for fitting and predicting
    value = int(len(X) * train_percent)
    fit = (X[:value], Y[:value])
    predict = (X[value:], Y[value:])

    return fit, predict


if __name__ == "__main__":

    steps = 7
    features = 1
    epochs = 100
    batch_size = 72
    verbose = 1
    shuffle = False
    company = "Abcdin"

    model = Lstm(steps, features)

    fit_data, predict_data = get_data("../../data/long_product_group_id_23", company, 0.7, steps)

    # print(fit_data[1])
    # input(...)

    model.fit(fit_data[0], fit_data[1], predict_data[0], predict_data[1], epochs, batch_size, verbose, shuffle)

    # print(predict_data[0])
    # print(predict_data[1])
    # input(...)
    
    results = model.predict(predict_data[0])

    print(results)
