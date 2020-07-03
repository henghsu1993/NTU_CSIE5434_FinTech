class Strategy():
    # option setting needed
    def __setitem__(self, key, value):
        self.options[key] = value

    # option setting needed
    def __getitem__(self, key):
        return self.options.get(key, '')

    def __init__(self):
        # strategy property
        self.subscribedBooks = {
            'Binance': {
                'pairs': ['BTC-USDT'],
            },
        }
        self.period = 10 * 60   #variable
        self.options = {}

        # user defined class attribute
        self.last_type = 'sell'
        self.last_ma_cross_status = None
        self.last_macd_cross_status = None
        self.close_price_trace = np.array([])
        self.ma_long = 26   #variable
        self.ma_short = 12   #variable
        self.ma_signal = 9
        self.UP = 1
        self.DOWN = 2
        self.volume_trace = np.array([])


    def get_current_macd_cross(self):
        macd = talib.MACD(self.close_price_trace)[0][-1]
        macd_signal = talib.MACD(self.close_price_trace)[1][-1]
        if np.isnan(macd) or np.isnan(macd_signal):
            return None
        if macd > macd_signal:
            return self.UP, macd
        return self.DOWN, macd

    def get_rsi(self):
        rsi = talib.RSI(self.close_price_trace, 6)[-1]
        return rsi

    def get_obv_rsi(self):
        obv_rsi = talib.RSI(self.volume_trace)[-1]
        return obv_rsi


    # called every self.period
    def trade(self, information):

        exchange = list(information['candles'])[0]
        pair = list(information['candles'][exchange])[0]
        close_price = information['candles'][exchange][pair][0]['close']

        volume = information['candles'][exchange][pair][0]['volume']

        # add latest price into trace
        self.close_price_trace = np.append(self.close_price_trace, [float(close_price)])
        # only keep max length of ma_long count elements
        #self.close_price_trace = self.close_price_trace[-self.ma_long:]
        # calculate current ma cross status
        cur_macd_cross, macd = self.get_current_macd_cross()

        rsi = self.get_rsi()

        self.volume_trace = np.append(self.volume_trace, [float(volume)])
        obv_rsi = self.get_obv_rsi()

        Log('info: ' + str(information['candles'][exchange][pair][0]['time']) + ', ' + str(information['candles'][exchange][pair][0]['open']) + ', assets' + str(self['assets'][exchange]['ETH']))

        if cur_macd_cross is None:
            return []

        if self.last_macd_cross_status is None:
            self.last_macd_cross_status = cur_macd_cross
            return []

        # cross up
        if self.last_type == 'sell' and cur_macd_cross == self.UP and self.last_macd_cross_status == self.DOWN and macd>0 and rsi>50 and obv_rsi>50:
            Log('buying, opt1:' + self['opt1'])
            self.last_type = 'buy'
            self.last_macd_cross_status = cur_macd_cross
            #self.last_ma_cross_status = cur_ma_cross
            return [
                {
                    'exchange': exchange,
                    'amount': 1,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                }
            ]
        # cross down
        elif self.last_type == 'buy' and cur_macd_cross == self.DOWN and self.last_macd_cross_status == self.UP and macd<0 and rsi<50 and obv_rsi<50:
            Log('selling, ' + exchange + ':' + pair)
            self.last_type = 'sell'
            #self.last_ma_cross_status = cur_ma_cross
            self.last_macd_cross_status = cur_macd_cross
            return [
                {
                    'exchange': exchange,
                    'amount': -1,
                    'price': -1,
                    'type': 'MARKET',
                    'pair': pair,
                }
            ]
        #self.last_ma_cross_status = cur_ma_cross
        self.last_macd_cross_status = cur_macd_cross
        return []
