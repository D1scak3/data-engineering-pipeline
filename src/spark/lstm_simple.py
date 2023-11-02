import os
import shutil
import numpy as np
import pandas as pd
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense,LSTM 
from keras.models import load_model
from sklearn.metrics import mean_squared_error

# np.random.seed(1234)
# tf.random.set_seed(1234)

# os.getenv("TF_DETERMINISTIC_OPS")

class LstmSimple:

    def __init__(self, data: 'pickle' = None, n_steps: int = 7, n_features: int = 1, train_percent: float = 0.7, company: str = "Abcdin"):
        self.df_long = data
        self.df_wide = self.df_long.reset_index().groupby(['timestamp', 'company'])["price"].first().unstack().reset_index().set_index("timestamp")

        timestamps  = pd.DataFrame(index = pd.date_range(self.df_wide.index[0], self.df_wide.index[-1], freq='D'))
        self.df_wide = pd.merge(timestamps, self.df_wide, left_index = True, right_index = True, how = 'left')
        self.df_wide.columns.name = None

        # model characteristics
        self.n_steps = n_steps
        self.n_features = n_features
        self.train_percent = train_percent
        self.target_company = company

        # data setup
        methods= ["linear","time","slinear","quadratic","cubic","barycentric",
        "krogh", "from_derivatives", "pchip", "akima", "cubicspline"]
        orders = ["polynomial","spline"]
        methods += orders
        order = 5

        method = methods[1]
        for name in self.df_wide.columns:
            if method in orders:
                self.df_wide.interpolate(method=method,order=order,inplace=True,limit_direction="both")
            else:
                self.df_wide.interpolate(method=method,inplace=True,limit_direction="both")

        raw_seq = self.df_wide[self.target_company]

        # print(raw_seq)
        # print(self.df_wide)
        # print(raw_seq)
        # input(...)

        # for x in self.df_wide[self.target_company]:
        #     print(x)
        # input(...)

        X, y = self.__split_sequence(raw_seq, self.n_steps)
        print(y)
        input(...)
        value = int(len(X) * self.train_percent)
        self.train = (X[:value], y[:value])
        self.test = (X[value:], y[value:])

        # print(self.test[0])
        # input(...)

        # create model
        X = X.reshape((X.shape[0], X.shape[1], self.n_features))

        # print(X)
        # input(...)

        # with open("respahe.txt", "w") as file:
        #     for x in X:
        #         file.write(str(x) + "\n")

        # with open("test.txt", "w") as file:
        #     for x in self.test[0]:
        #         file.write(str(x) + "\n")

        """
        dataframe has 663 elements
        each element has 7 rows
        4641 elements total

        test array has the same len as the results
        each row of the test array has 7 rows
        each row of the results has 1 row, corresponding to the linear regression of each test row
        """
        # print("Row: " + str(len(X)))
        # print("Columns: " + str(len(X[0])))
        # print(len(self.test[0]))
        # input(...)

        self.model = Sequential()
        self.model.add(LSTM(50, activation='relu', input_shape=(self.n_steps, self.n_features)))
        self.model.add(Dense(1))
        self.model.compile(optimizer='adam', loss='mse')


    def save_model(self, path, name):
        """
        save model
        create zip
        move zip to desired directory
        delete unzipped files 
        """

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


    def __split_sequence(self, sequence, n_steps):
        X, y = list(), list()

        for i in range(len(sequence)):

            # find the end of this pattern
            end_ix = i + n_steps

            # check if we are beyond the sequence
            if end_ix > len(sequence)-1:
                break
            
            # gather input and output parts of the pattern
            seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
            
            X.append(seq_x)
            y.append(seq_y)

        return np.array(X),np.array(y)


    def fit(self, epochs, batch_size, verbose, shuffle):
        self.model.fit(self.train[0], self.train[1], epochs=epochs, batch_size=batch_size, validation_data=self.test, verbose=verbose, shuffle=shuffle)


    def predict(self):
        return  self.model.predict(self.test[0])


    def performance_compare(self, predicted_data):
        mse = mean_squared_error(self.test[1], predicted_data)
        return mse