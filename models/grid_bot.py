from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt


class GridBot:
    def __init__(self, levels_num=10, balance=100000, levels_step=0.001, fee=0.2181 / 100):
        assert 0 < levels_step < 1, f'levels_step must be in (0, 1) range, {levels_step}'
        assert levels_num >= 1, f'levels_num must be greater than 0, {levels_num}'

        self.levels_num = levels_num
        self.levels_step = levels_step
        self.balance = balance
        self.history = []
        self.assets = [0]
        self.ref_price = None
        self.buy_orders = []
        self.sell_orders = []
        self.fee = fee
        self.buy_points = []
        self.sell_points = []
        self.bought = [False for _ in range(self.levels_num)]

    def trade(self, df_path):
        df = pd.read_csv(df_path)
        # use_mean - use mean price over last month as a ref level, else use first open price
        ref_price = df.iloc[0]['Open']
        self.ref_price = ref_price
        buy_orders = [ref_price * (1 - k * self.levels_step) for k in range(1, self.levels_num + 1)]
        sell_orders = [ref_price * (1 - k * self.levels_step) for k in range(self.levels_num)]
        self.buy_orders = buy_orders
        self.sell_orders = sell_orders
        
        for index, row in tqdm(df.iterrows()):

            for i in range(len(self.bought)):
                if self.bought[i] and row.High >= sell_orders[i]:
                    self.bought[i] = False
                    self.balance += (sell_orders[i] - self.fee*sell_orders[i])
                    self.assets  += [ self.assets[-1] - sell_orders[i] / row.High]
                    self.history += [self.balance]
                    self.sell_points += [(index, row.High)]
                    
                elif not self.bought[i] and row.Low <= buy_orders[i] and self.balance > row.Low:
                    self.bought[i] = True
                    self.balance -= (buy_orders[i] + self.fee * buy_orders[i])
                    self.assets  += [(buy_orders[i] - self.fee * buy_orders[i]) / row.Low]
                    self.history += [self.balance]
                    self.buy_points += [(index, row.Low)]
                    
                    
    def plot(self, df_path):
        df = pd.read_csv(df_path)
        self = self.trade(df_path)
        plt.figure(figsize=(24,8))
        plt.plot(df.index, (df.High+df.Low)/2, color='black', marker='o', linestyle='-',
             linewidth=1, markersize=1)

        plt.plot(df.index, [self.ref_price for i in df.index ], color='blue', linewidth=3, label='ref')
        plt.plot(df.index, [self.buy_orders for i in df.index ], color ='green', linewidth =0.5, linestyle='--' )
        plt.plot(df.index, [self.sell_orders for i in df.index ] , color ='red', linewidth =0.5, linestyle='--')

        plt.plot([i[0] for i in self.sell_points], [i[1] for i in self.sell_points] , 'ro', linewidth =2)
        plt.plot([i[0] for i in self.buy_points], [i[1] for i in self.buy_points] , 'go', linewidth =2)

        plt.legend()
        plt.show()
                    

# grid_bot = GridBot()
# grid_bot.trade('data/raw/btcusdt.csv')
# print(grid_bot.balance)
# print(grid_bot.history)
