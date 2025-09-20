
import matplotlib.pyplot as plt

def plot_profit_loss(values):
    fig, ax = plt.subplots()
    ax.plot(range(1, len(values)+1), values, marker='o')
    ax.set_xlabel("Period")
    ax.set_ylabel("Profit/Loss")
    ax.set_title("Profit/Loss Over Time")
    ax.axhline(0, linestyle='--', linewidth=1)
    return fig

def plot_funding_vs_valuation(funding, valuation):
    fig, ax = plt.subplots()
    ax.plot(range(1, len(funding)+1), funding, marker='o', label="Funding")
    ax.plot(range(1, len(valuation)+1), valuation, marker='o', label="Valuation")
    ax.set_xlabel("Round / Period")
    ax.set_ylabel("Amount")
    ax.set_title("Funding vs Valuation")
    ax.legend()
    return fig
