from flask import Flask, request, jsonify, render_template
import random
from threading import Timer

app = Flask(__name__)

class Stock:
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.history = [price]

    def update_price(self):
        change_percent = random.uniform(-0.1, 0.1)
        self.price += self.price * change_percent
        self.price = round(self.price, 2)
        self.history.append(self.price)

    def reset(self):
        self.price = self.history[0]
        self.history = [self.price]

    def show_history(self):
        return self.history

class Market:
    def __init__(self, stocks):
        self.stocks = {stock.name: stock for stock in stocks}

    def update_market(self):
        for stock in self.stocks.values():
            stock.update_price()

    def show_market(self):
        return {stock.name: stock.price for stock in self.stocks.values()}

    def get_stock_history(self, stock_name):
        if stock_name in self.stocks:
            stock = self.stocks[stock_name]
            return stock.show_history()
        return None

    def reset_market(self):
        for stock in self.stocks.values():
            stock.reset()

class Player:
    def __init__(self, name, cash):
        self.name = name
        self.cash = cash
        self.portfolio = {}

    def buy_stock(self, market, stock_name, amount):
        if stock_name in market.stocks:
            stock = market.stocks[stock_name]
            total_cost = stock.price * amount
            if self.cash >= total_cost:
                self.cash -= total_cost
                if stock_name in self.portfolio:
                    self.portfolio[stock_name] += amount
                else:
                    self.portfolio[stock_name] = amount
                return f"Bought {amount} shares of {stock_name}"
            else:
                return "Insufficient funds"
        else:
            return "Stock not found"

    def sell_stock(self, market, stock_name, amount):
        if stock_name in self.portfolio and self.portfolio[stock_name] >= amount:
            stock = market.stocks[stock_name]
            total_earnings = stock.price * amount
            self.cash += total_earnings
            self.portfolio[stock_name] -= amount
            if self.portfolio[stock_name] == 0:
                del self.portfolio[stock_name]
            return f"Sold {amount} shares of {stock_name}"
        else:
            return "Insufficient shares"

    def show_portfolio(self):
        return {
            "cash": self.cash,
            "stocks": self.portfolio
        }

    def reset_portfolio(self):
        self.cash = 10000.0
        self.portfolio = {}

# Initialize game with more stocks
stocks = [
    Stock("AAPL", 150.0),
    Stock("GOOGL", 2800.0),
    Stock("AMZN", 3500.0),
    Stock("TSLA", 700.0),
    Stock("MSFT", 300.0),
    Stock("NFLX", 500.0),
    Stock("FB", 340.0),
    Stock("NVDA", 750.0),
    Stock("INTC", 60.0),
    Stock("AMD", 95.0),
    Stock("BABA", 210.0),
    Stock("UBER", 45.0),
    Stock("LYFT", 55.0),
    Stock("TWTR", 70.0),
    Stock("SNAP", 80.0)
]
market = Market(stocks)
player = Player("Investor", 10000.0)

simulation_running = False
timer = None

def update_market_periodically():
    global timer
    if simulation_running:
        market.update_market()
        timer = Timer(30, update_market_periodically)
        timer.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/market', methods=['GET'])
def get_market():
    return jsonify(market.show_market())

@app.route('/stock-history/<stock_name>', methods=['GET'])
def get_stock_history(stock_name):
    history = market.get_stock_history(stock_name)
    if history:
        return jsonify({
            'dates': list(range(len(history))),
            'prices': history
        })
    return jsonify({'error': 'Stock not found'}), 404

@app.route('/buy', methods=['POST'])
def buy_stock():
    data = request.json
    stock_name = data.get('stock_name')
    amount = data.get('amount')
    result = player.buy_stock(market, stock_name, int(amount))
    return jsonify({"message": result, "portfolio": player.show_portfolio()})

@app.route('/sell', methods=['POST'])
def sell_stock():
    data = request.json
    stock_name = data.get('stock_name')
    amount = data.get('amount')
    result = player.sell_stock(market, stock_name, int(amount))
    return jsonify({"message": result, "portfolio": player.show_portfolio()})

@app.route('/portfolio', methods=['GET'])
def get_portfolio():
    return jsonify(player.show_portfolio())

@app.route('/start-simulation', methods=['POST'])
def start_simulation():
    global simulation_running
    simulation_running = True
    update_market_periodically()
    return jsonify({"message": "Simulation started"})

@app.route('/stop-simulation', methods=['POST'])
def stop_simulation():
    global simulation_running
    simulation_running = False
    if timer is not None:
        timer.cancel()
    return jsonify({"message": "Simulation stopped"})

@app.route('/reset', methods=['POST'])
def reset():
    global simulation_running
    simulation_running = False
    if timer is not None:
        timer.cancel()
    market.reset_market()
    player.reset_portfolio()
    return jsonify({"message": "Simulation and portfolio reset"})

if __name__ == '__main__':
    app.run(debug=True)
