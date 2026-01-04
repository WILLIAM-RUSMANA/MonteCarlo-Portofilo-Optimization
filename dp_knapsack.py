import numpy as np
import matplotlib.pyplot as plt
from helper import calculate_sharpe_ratio

# Configuration
RISK_FREE_RATE = 0.04
MAX_ALLOCATION_PER_STOCK = 0.20
MIN_ALLOCATION_PER_STOCK = 0.005
DISCRETIZATION_STEPS = 100


def display_allocation_results(results):
    """Display portfolio allocation results"""
    print("\n" + "=" * 100)
    print("DYNAMIC PROGRAMMING KNAPSACK PORTFOLIO ALLOCATION")
    print("=" * 100)
    print("\nSummary:")
    print(f"  Expected Annual Return: {results['portfolio_return']:.2%}")
    print(f"  Portfolio Std Deviation: {results['portfolio_std']:.2%}")
    print(f"  Portfolio Sharpe Ratio: {results['portfolio_sharpe']:.4f}")
    print(f"  Number of Stocks: {results['num_stocks']}")
    print("\n" + "-" * 100)
    print(f"{'Stock':<8} {'Weight':<10} {'Sharpe':<12} {'Mean Return':<15} {'Std Dev':<12}")
    print("-" * 100)
    
    sorted_allocations = sorted(results['allocations'].items(), 
                               key=lambda x: x[1], 
                               reverse=True)
    
    for stock, weight in sorted_allocations:
        if weight > 0:
            metrics = results['sharpe_ratios'][stock]
            print(f"{stock:<8} {weight:<10.2%} {metrics['sharpe_ratio']:<12.4f} "
                  f"{metrics['mean_return']:<15.2%} {metrics['std_return']:<12.2%}")
    
    print("=" * 100)


def plot_allocation_results(results):
    """Visualize portfolio allocation"""
    allocations = results['allocations']
    
    fig, ax1, ax2 = plt.subplots(1, 2, figsize=(16, 6))
    
    stocks = [s for s, w in allocations.items() if w > 0]
    weights = [allocations[s] for s in stocks]
    
    colors = plt.cm.Set3(range(len(stocks)))
    wedges, texts, autotexts = ax1.pie(weights, labels=stocks, autopct='%1.1f%%', 
                                        colors=colors, startangle=90)
    ax1.set_title('Portfolio Allocation (DP Knapsack)', fontsize=14, fontweight='bold')
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    sharpe_values = [results['sharpe_ratios'][s]['sharpe_ratio'] for s in stocks]
    ax2.bar(range(len(stocks)), sharpe_values, color=colors)
    ax2.set_xticks(range(len(stocks)))
    ax2.set_xticklabels(stocks, rotation=45, ha='right')
    ax2.set_ylabel('Sharpe Ratio', fontsize=12)
    ax2.set_title('Sharpe Ratio by Stock', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('portfolio_allocation_dp.png', dpi=300, bbox_inches='tight')
    print("\nPlot saved as portfolio_allocation_dp.png")
    plt.show()


def compare_with_equal_weight(results, stocks_metrics):
    """Compare DP allocation with equal-weight portfolio"""
    selected_stocks = list(results['allocations'].keys())
    
    if not selected_stocks:
        print("No stocks selected - cannot compare with equal-weight")
        return
    
    equal_weight = 1.0 / len(selected_stocks)
    equal_portfolio_return = sum(equal_weight * stocks_metrics[stock]['mean_annual_return'] 
                                for stock in selected_stocks)
    equal_portfolio_variance = sum(equal_weight**2 * stocks_metrics[stock]['std_annual_return']**2 
                                  for stock in selected_stocks)
    equal_portfolio_std = np.sqrt(equal_portfolio_variance)
    equal_portfolio_sharpe = calculate_sharpe_ratio(equal_portfolio_return, equal_portfolio_std)
    
    print("\n" + "=" * 100)
    print("COMPARISON: DP KNAPSACK vs EQUAL-WEIGHT ALLOCATION")
    print("=" * 100)
    print(f"{'Metric':<30} {'DP Knapsack':<25} {'Equal-Weight':<25} {'Difference':<15}")
    print("-" * 100)
    print(f"{'Expected Annual Return':<30} {results['portfolio_return']:<25.2%} "
          f"{equal_portfolio_return:<25.2%} {results['portfolio_return'] - equal_portfolio_return:<15.2%}")
    print(f"{'Portfolio Std Deviation':<30} {results['portfolio_std']:<25.2%} "
          f"{equal_portfolio_std:<25.2%} {results['portfolio_std'] - equal_portfolio_std:<15.2%}")
    print(f"{'Portfolio Sharpe Ratio':<30} {results['portfolio_sharpe']:<25.4f} "
          f"{equal_portfolio_sharpe:<25.4f} {results['portfolio_sharpe'] - equal_portfolio_sharpe:<15.4f}")
    print("=" * 100)


def get_current_stock_prices(tickers):
    """Get current stock prices"""
    import yfinance as yf
    
    prices = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')
            if not hist.empty:
                prices[ticker] = hist['Close'].iloc[-1]
            else:
                prices[ticker] = None
        except:
            prices[ticker] = None
    
    return prices


def allocate_whole_shares_dp(target_allocations, stock_prices, budget):
    """Allocate portfolio using whole shares"""
    shares = {}
    actual_spent = {}
    
    target_dollars = {ticker: weight * budget for ticker, weight in target_allocations.items()}
    
    for ticker, target_amount in target_dollars.items():
        price = stock_prices.get(ticker)
        if price and price > 0:
            num_shares = int(target_amount / price)
            shares[ticker] = num_shares
            actual_spent[ticker] = num_shares * price
        else:
            shares[ticker] = 0
            actual_spent[ticker] = 0
    
    total_spent = sum(actual_spent.values())
    cash_remaining = budget - total_spent
    
    sweep_count = 0
    while cash_remaining > 0:
        affordable_stocks = []
        for ticker, price in stock_prices.items():
            if ticker in target_allocations and price and price <= cash_remaining:
                affordable_stocks.append((ticker, price))
        
        if not affordable_stocks:
            break
        
        affordable_stocks.sort(key=lambda x: target_allocations.get(x[0], 0), reverse=True)
        
        ticker, price = affordable_stocks[0]
        shares[ticker] = shares.get(ticker, 0) + 1
        actual_spent[ticker] = actual_spent.get(ticker, 0) + price
        cash_remaining -= price
        sweep_count += 1
    
    total_spent = sum(actual_spent.values())
    actual_allocations = {ticker: spent / total_spent if total_spent > 0 else 0 
                         for ticker, spent in actual_spent.items()}
    
    shares = {ticker: num for ticker, num in shares.items() if num > 0}
    
    return {
        'shares': shares,
        'actual_spent': actual_spent,
        'total_spent': total_spent,
        'cash_remaining': cash_remaining,
        'actual_allocations': actual_allocations,
        'sweep_count': sweep_count,
        'budget': budget,
        'stock_prices': stock_prices
    }


def dp_knapsack_portfolio_allocation(stocks_metrics, target_num_stocks=10, 
                                     display_results=True, plot_results=True, 
                                     compare_equal_weight=True):
    """
    Dynamic Programming Knapsack Portfolio Optimization
    
    Finds optimal portfolio allocation maximizing Sharpe ratio
    while enforcing diversification constraints (20% max, 0.5% min).
    """
    
    # Calculate Sharpe ratios
    sharpe_ratios = {}
    for stock, metrics in stocks_metrics.items():
        mean_return = metrics['mean_annual_return']
        std_return = metrics['std_annual_return']
        sharpe = calculate_sharpe_ratio(mean_return, std_return)
        
        sharpe_ratios[stock] = {
            'sharpe_ratio': sharpe,
            'mean_return': mean_return,
            'std_return': std_return,
            'percentile_5': metrics['percentile_5'],
            'percentile_95': metrics['percentile_95']
        }
    
    # Select top N stocks by Sharpe ratio
    sorted_stocks = sorted(sharpe_ratios.items(), 
                          key=lambda x: x[1]['sharpe_ratio'], 
                          reverse=True)
    selected_stocks = sorted_stocks[:target_num_stocks]
    
    if not selected_stocks:
        print("Error: No stocks selected")
        return {}
    
    # DP Algorithm
    units = DISCRETIZATION_STEPS
    dp = {0: (float('-inf'), {})}
    
    selected_stock_list = [stock for stock, _ in selected_stocks]
    
    for stock in selected_stock_list:
        new_dp = dp.copy()
        
        min_units = max(1, int(MIN_ALLOCATION_PER_STOCK * DISCRETIZATION_STEPS))
        max_units = int(MAX_ALLOCATION_PER_STOCK * DISCRETIZATION_STEPS)
        
        for allocation_units in range(min_units, max_units + 1):
            allocation = allocation_units / DISCRETIZATION_STEPS
            
            for prev_units in list(dp.keys()):
                new_units = prev_units + allocation_units
                
                if new_units <= units:
                    prev_sharpe, prev_weights = dp[prev_units]
                    
                    candidate_weights = prev_weights.copy()
                    candidate_weights[stock] = allocation
                    
                    current_total = sum(candidate_weights.values())
                    if current_total > 0:
                        normalized_weights = {s: w / current_total 
                                            for s, w in candidate_weights.items()}
                    else:
                        normalized_weights = candidate_weights
                    
                    portfolio_return = sum(normalized_weights.get(s, 0) * 
                                         sharpe_ratios[s]['mean_return']
                                         for s in selected_stock_list)
                    portfolio_variance = sum(normalized_weights.get(s, 0)**2 * 
                                           sharpe_ratios[s]['std_return']**2
                                           for s in selected_stock_list)
                    portfolio_std = np.sqrt(max(portfolio_variance, 0))
                    portfolio_sharpe = calculate_sharpe_ratio(portfolio_return, portfolio_std)
                    
                    if new_units not in new_dp or portfolio_sharpe > new_dp[new_units][0]:
                        new_dp[new_units] = (portfolio_sharpe, candidate_weights)
        
        dp = new_dp
    
    # Find best allocation
    best_sharpe = float('-inf')
    best_weights = {}
    
    for target_units in range(max(0, units - 10), units + 1):
        if target_units in dp:
            sharpe, weights = dp[target_units]
            if sharpe > best_sharpe:
                best_sharpe = sharpe
                best_weights = weights.copy()
    
    if not best_weights:
        best_weights = {stock: 1.0 / len(selected_stock_list) 
                       for stock, _ in selected_stocks}
    
    # Apply constraints
    total = sum(best_weights.values())
    if total > 0:
        allocations = {s: w / total for s, w in best_weights.items()}
    else:
        allocations = best_weights
    
    for stock in allocations:
        allocations[stock] = min(allocations[stock], MAX_ALLOCATION_PER_STOCK)
    
    allocations = {s: w for s, w in allocations.items() 
                  if w >= MIN_ALLOCATION_PER_STOCK}
    
    total = sum(allocations.values())
    if total > 0:
        allocations = {s: w / total for s, w in allocations.items()}
    
    # Calculate final metrics
    portfolio_return = sum(allocations.get(stock, 0) * sharpe_ratios[stock]['mean_return']
                          for stock in selected_stock_list)
    portfolio_variance = sum(allocations.get(stock, 0)**2 * sharpe_ratios[stock]['std_return']**2
                            for stock in selected_stock_list)
    portfolio_std = np.sqrt(max(portfolio_variance, 0))
    portfolio_sharpe = calculate_sharpe_ratio(portfolio_return, portfolio_std)
    
    results = {
        'allocations': allocations,
        'sharpe_ratios': sharpe_ratios,
        'portfolio_return': portfolio_return,
        'portfolio_std': portfolio_std,
        'portfolio_sharpe': portfolio_sharpe,
        'num_stocks': len(allocations)
    }
    
    if display_results:
        display_allocation_results(results)
    
    if plot_results:
        plot_allocation_results(results)
    
    if compare_equal_weight:
        compare_with_equal_weight(results, stocks_metrics)
    
    return allocations


if __name__ == "__main__":
    print("This module should be imported and called with Monte Carlo results.")
    print("\nUsage:")
    print("-" * 70)
    print("from monte_carlo_method import monte_carlo_method")
    print("from dp_knapsack import dp_knapsack_portfolio_allocation")
    print()
    print("# Run Monte Carlo simulation")
    print("stocks_metrics = monte_carlo_method()")
    print()
    print("# Run DP Knapsack optimization")
    print("allocations = dp_knapsack_portfolio_allocation(stocks_metrics)")
    print("-" * 70)