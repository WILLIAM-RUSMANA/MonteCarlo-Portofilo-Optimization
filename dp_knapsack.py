import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from helper import calculate_sharpe_ratio

#dp knapsack portfolio allocator
#uses dynamic programming to find optimal allocation that maximizes sharpe ratio

RISK_FREE_RATE=0.04
MAX_ALLOCATION_PER_STOCK=0.20
MIN_ALLOCATION_PER_STOCK=0.005
DISCRETIZATION_STEPS=100


def get_current_stock_prices(tickers):
    #fetch current stock prices from yahoo finance for each ticker in list
    
    prices={}
    
    for ticker in tickers:
        try:
            #use yfinance to get ticker data object
            stock=yf.Ticker(ticker)
            #request 1 day of historical data to get most recent price
            hist=stock.history(period='1d')
            
            if not hist.empty:
                #extract the closing price from latest row (most recent)
                prices[ticker]=hist['Close'].iloc[-1]
                print(f"  {ticker}: ${prices[ticker]:.2f}")
            else:
                #no data returned from yahoo finance for this ticker
                prices[ticker]=None
                print(f"  {ticker}: No data available")
                
        except Exception as e:
            #any error fetching from yahoo finance results in none value
            prices[ticker]=None
            print(f"  {ticker}: Error - {e}")
    
    return prices


def allocate_whole_shares(target_allocations, stock_prices, budget):
    #Convert allocation percentages to actual whole shares
    #also uses cash sweep to buy more shares with leftover cash
    
    #first calculate target dollar amount for each stock based on allocation percentage
    #multiply each stock's target weight by total budget to get target dollars
    target_dollars={
        ticker: weight*budget 
        for ticker, weight in target_allocations.items()
    }
    
    #Now figure out how many whole shares we can buy for each stock
    shares={}
    actual_spent={}
    
    for ticker, target_amount in target_dollars.items():
        #get price of this stock from prices dictionary
        price=stock_prices.get(ticker)
        
        if price and price>0:
            #Divide target dollars by price to get shares (int removes decimals)
            num_shares=int(target_amount/price)
            #Store number of shares we can afford for this stock
            shares[ticker]=num_shares
            #Calculate actual dollars spent on these shares
            actual_spent[ticker]=num_shares*price
        else:
            #no valid price means we can't buy this stock
            shares[ticker]=0
            actual_spent[ticker]=0
    
    #calculate how much cash is left after initial allocation
    total_spent=sum(actual_spent.values())
    cash_remaining=budget-total_spent
    
    print(f"\nInitial allocation spent: ${total_spent:,.2f}")
    print(f"Cash remaining for sweep: ${cash_remaining:,.2f}")
    
    #cash sweep section tries to use leftover cash to buy more shares
    #starting with highest priority stocks (ones we wanted more of originally)
    print(f"\nStarting cash sweep...")
    sweep_count=0
    
    while cash_remaining>0:
        #find which stocks we can afford to buy more of with remaining cash
        affordable_stocks=[]
        
        for ticker, price in stock_prices.items():
            #only consider stocks that are in our original allocation list
            if ticker in target_allocations and price and price<=cash_remaining:
                #add tuple of (ticker, price, priority_weight for sorting)
                affordable_stocks.append((
                    ticker, 
                    price, 
                    target_allocations[ticker]
                ))
        
        if not affordable_stocks:
            #no stocks we can afford with remaining cash, stop sweeping
            break
        
        #Sort by original allocation weight (highest priority first)
        #this buys more of stocks we wanted higher allocation for
        affordable_stocks.sort(key=lambda x: x[2], reverse=True)
        
        #buy one share of highest priority stock from affordable list
        ticker, price, _=affordable_stocks[0]
        #increment share count for this ticker
        shares[ticker]=shares.get(ticker, 0)+1
        #update actual spending for this ticker
        actual_spent[ticker]=actual_spent.get(ticker, 0)+price
        #reduce remaining cash by the price of share bought
        cash_remaining-=price
        #increment counter of shares bought in sweep
        sweep_count+=1
    
    print(f"Bought {sweep_count} additional shares from sweep")
    print(f"Final cash remaining: ${cash_remaining:,.2f}")
    
    #calculate what percent of portfolio each stock actually represents
    total_spent=sum(actual_spent.values())
    #allocation is actual dollars spent divided by total portfolio value
    actual_allocations={
        ticker: spent/total_spent if total_spent>0 else 0
        for ticker, spent in actual_spent.items()
    }
    
    #remove stocks with 0 shares from results to clean up output
    shares={t: n for t, n in shares.items() if n>0}
    actual_allocations={t: a for t, a in actual_allocations.items() if a>0}
    
    return {
        'shares': shares,
        'actual_allocations': actual_allocations,
        'actual_spent': actual_spent,
        'total_spent': total_spent,
        'cash_remaining': cash_remaining,
        'budget': budget,
        'stock_prices': stock_prices,
        'sweep_count': sweep_count
    }


def display_allocation_results(results):
    #print out allocation results in a nicely formatted table showing all metrics
    
    print("\n"+"="*100)
    print("DP KNAPSACK PORTFOLIO ALLOCATION RESULTS")
    print("="*100)
    
    print("\nPortfolio Summary:")
    print(f"  Expected Annual Return: {results['portfolio_return']:.2%}")
    print(f"  Portfolio Std Deviation: {results['portfolio_std']:.2%}")
    print(f"  Portfolio Sharpe Ratio: {results['portfolio_sharpe']:.4f}")
    print(f"  Number of Stocks: {results['num_stocks']}")
    
    print("\n"+"-"*100)
    print(f"{'Stock':<8} {'Weight':<10} {'Sharpe':<12} {'Mean Return':<15} {'Std Dev':<12}")
    print("-"*100)
    
    #sort allocations by weight (highest first) for display
    sorted_allocs=sorted(
        results['allocations'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    #print each stock's allocation and metrics
    for stock, weight in sorted_allocs:
        if weight>0:
            #get sharpe ratio metrics for this stock from results
            metrics=results['sharpe_ratios'][stock]
            print(
                f"{stock:<8} {weight:>8.2%} {metrics['sharpe_ratio']:>11.4f} "
                f"{metrics['mean_return']:>14.2%} {metrics['std_return']:>11.2%}"
            )
    
    print("="*100)


def plot_allocation_results(results):
    #create pie chart of allocation and bar chart of sharpe ratios
    
    allocations=results['allocations']
    
    fig, (ax1, ax2)=plt.subplots(1, 2, figsize=(16, 6))
    
    #left plot: pie chart showing allocation percentages for each stock
    stocks=[s for s, w in allocations.items() if w>0]
    weights=[allocations[s] for s in stocks]
    colors=plt.cm.Set3(range(len(stocks)))
    
    #draw pie chart with labels and percentages
    wedges, texts, autotexts=ax1.pie(
        weights, 
        labels=stocks, 
        autopct='%1.1f%%',
        colors=colors, 
        startangle=90
    )
    ax1.set_title('Portfolio Allocation (DP Knapsack)', fontsize=14, fontweight='bold')
    
    #make percentage text readable (white, bold)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    #right plot: bar chart showing sharpe ratios for each stock
    sharpe_values=[results['sharpe_ratios'][s]['sharpe_ratio'] for s in stocks]
    
    #draw bar chart with colors matching pie chart
    sharpe_values=[results['sharpe_ratios'][s]['sharpe_ratio'] for s in stocks]
    ax2.bar(range(len(stocks)), sharpe_values, color=colors)
    ax2.bar(range(len(stocks)), sharpe_values, color=colors)
    ax2.set_xticks(range(len(stocks)))
    ax2.set_xticklabels(stocks, rotation=45, ha='right')
    ax2.set_ylabel('Sharpe Ratio', fontsize=12)
    ax2.set_title('Sharpe Ratio by Stock', fontsize=14, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    #save figure to file and display
    plt.tight_layout()
    plt.savefig('portfolio_allocation_dp.png', dpi=300, bbox_inches='tight')
    print("\nPlot saved as 'portfolio_allocation_dp.png'")
    plt.show()


def compare_with_equal_weight(results, stocks_metrics):
    #Compare DP allocation results with a simple equal-weight allocation
    #shows how much better DP allocation is than naive approach
    
    selected_stocks=list(results['allocations'].keys())
    
    if not selected_stocks:
        print("\nNo stocks selected")
        return
    
    #equal weight means each stock gets same percentage (1/n where n=number of stocks)
    equal_weight=1.0/len(selected_stocks)
    
    #calculate equal-weight portfolio return (sum of each stock's return * equal weight)
    equal_return=sum(
        equal_weight*stocks_metrics[stock]['mean_annual_return']
        for stock in selected_stocks
    )
    
    #calculate equal-weight portfolio risk (variance of weighted returns)
    equal_variance=sum(
        (equal_weight**2)*(stocks_metrics[stock]['std_annual_return']**2)
        for stock in selected_stocks
    )
    equal_std=np.sqrt(equal_variance)
    #calculate sharpe ratio for equal weight portfolio
    equal_sharpe=calculate_sharpe_ratio(equal_return, equal_std)
    
    #print comparison table showing dp vs equal weight metrics
    print("\n"+"="*100)
    print("COMPARISON: DP KNAPSACK vs EQUAL-WEIGHT ALLOCATION")
    print("="*100)
    print(
        f"{'Metric':<30} {'DP Knapsack':<25} {'Equal-Weight':<25} {'Difference':<15}"
    )
    print("-"*100)
    
    print(
        f"{'Expected Annual Return':<30} {results['portfolio_return']:<25.2%} "
        f"{equal_return:<25.2%} {results['portfolio_return']-equal_return:<15.2%}"
    )
    
    print(
        f"{'Portfolio Std Deviation':<30} {results['portfolio_std']:<25.2%} "
        f"{equal_std:<25.2%} {results['portfolio_std']-equal_std:<15.2%}"
    )
    
    print(
        f"{'Portfolio Sharpe Ratio':<30} {results['portfolio_sharpe']:<25.4f} "
        f"{equal_sharpe:<25.4f} {results['portfolio_sharpe']-equal_sharpe:<15.4f}"
    )
    
    print("="*100)


def dp_knapsack_portfolio_allocation(
    stocks_metrics,
    target_num_stocks=10,
    display_results=True,
    #set true or false
    plot_results=True,
    compare_equal_weight=True
):
    #dynamic programming knapsack portfolio optimization algorithm
    #finds the best allocation that maximizes sharpe ratio while respecting constraints

    print("\nStep 1: Calculating Sharpe ratios for all stocks...")
    
    #loop through each stock and calculate its sharpe ratio for comparison
    sharpe_ratios={}
    
    for stock, metrics in stocks_metrics.items():
        #extract mean and std return from monte carlo metrics
        mean_return=metrics['mean_annual_return']
        std_return=metrics['std_annual_return']
        #calculate sharpe ratio for this stock (return divided by risk)
        sharpe=calculate_sharpe_ratio(mean_return, std_return)
        
        #store all metrics for this stock in dictionary with sharpe as key metric
        sharpe_ratios[stock]={
            'sharpe_ratio': sharpe,
            'mean_return': mean_return,
            'std_return': std_return,
            'percentile_5': metrics['percentile_5'],
            'percentile_95': metrics['percentile_95']
        }
    
    print(f"  Calculated for {len(sharpe_ratios)} stocks")
    
    print(f"\nStep 2: Selecting top {target_num_stocks} stocks by Sharpe ratio...")
    
    #sort all stocks by their sharpe ratio (highest first)
    sorted_stocks=sorted(
        sharpe_ratios.items(),
        key=lambda x: x[1]['sharpe_ratio'],
        reverse=True
    )
    
    #take only the top n stocks where n=target_num_stocks
    selected_stocks=sorted_stocks[:target_num_stocks]
    #extract just the stock names from the sorted list for iteration
    selected_stock_list=[s for s, _ in selected_stocks]
    
    print(f"  Selected: {', '.join(selected_stock_list)}")
    
    print(f"\nStep 3: Running DP knapsack algorithm...")
    
    #this is the core dp knapsack algorithm section
    #the main difference from greedy is that we test thousands of combinations
    #greedy: allocates weight=sharpe_ratio/total_sharpe (simple one formula)
    #dp: builds a table testing all combinations and picks the optimal one

    #initialize units to represent discretized allocation grid (100 steps from 0-100%)
    units=DISCRETIZATION_STEPS
    #dp table maps allocation state to (best_sharpe_found, allocation_weights_dict)
    #state 0 means no stocks allocated yet (sharpe=negative infinity as baseline)
    dp={0: (float('-inf'), {})}
    
    #for each stock, try different allocations and find best combination with previous states
    for stock in selected_stock_list:
        #copy current dp table to build new version with this stock added
        new_dp=dp.copy()
        
        #calculate min and max units for this stock's allocation (5% to 20%)
        min_units=max(1, int(MIN_ALLOCATION_PER_STOCK*DISCRETIZATION_STEPS))
        max_units=int(MAX_ALLOCATION_PER_STOCK*DISCRETIZATION_STEPS)
        
        #try allocating different amounts to this stock (from 5% to 20% in small steps)
        for alloc_units in range(min_units, max_units+1):
            #convert unit count to actual allocation percentage
            allocation=alloc_units/DISCRETIZATION_STEPS
            
            #combine this stock allocation with each previous state in dp table
            #this is where dp magic happens: testing many combinations
            for prev_units in list(dp.keys()):
                #calculate total units if we add this stock to previous state
                new_units=prev_units+alloc_units
                
                #only consider if total doesn't exceed 100% allocation
                if new_units<=units:
                    #get the previous state's sharpe ratio and weights
                    prev_sharpe, prev_weights=dp[prev_units]
                    
                    #create new weights dictionary by adding this stock to previous
                    candidate_weights=prev_weights.copy()
                    candidate_weights[stock]=allocation
                    
                    #normalize all weights so they sum to exactly 1.0
                    current_total=sum(candidate_weights.values())
                    if current_total>0:
                        #divide each weight by total to normalize to 1.0
                        normalized_weights={
                            s: w/current_total 
                            for s, w in candidate_weights.items()
                        }
                    else:
                        normalized_weights=candidate_weights
                    
                    #calculate portfolio return with this allocation combination
                    #return is sum of (weight * stock_return) for each stock
                    portfolio_return=sum(
                        normalized_weights.get(s, 0)*sharpe_ratios[s]['mean_return']
                        for s in selected_stock_list
                    )
                    
                    #calculate portfolio risk (variance) with this allocation
                    #variance is sum of (weight^2 * stock_variance) for each stock
                    portfolio_variance=sum(
                        normalized_weights.get(s, 0)**2*sharpe_ratios[s]['std_return']**2
                        for s in selected_stock_list
                    )
                    
                    #convert variance to standard deviation (risk) by taking square root
                    portfolio_std=np.sqrt(max(portfolio_variance, 0))
                    #calculate sharpe ratio for this portfolio combination
                    portfolio_sharpe=calculate_sharpe_ratio(portfolio_return, portfolio_std)
                    
                    #keep this allocation if it's the best sharpe ratio for this unit count
                    #if this state didn't exist yet or if sharpe is better than previous, save it
                    if new_units not in new_dp or portfolio_sharpe>new_dp[new_units][0]:
                        new_dp[new_units]=(portfolio_sharpe, candidate_weights)
        
        #update dp table with new version that includes this stock
        dp=new_dp
    
    #extract the best allocation found in dp table
    #search through last 10 units to allow flexibility around 100% allocation
    best_sharpe=float('-inf')
    best_weights={}
    
    #iterate through possible unit counts near end of range
    for target_units in range(max(0, units-10), units+1):
        #check if this state exists in dp table
        if target_units in dp:
            #get sharpe ratio and weights for this state
            sharpe, weights=dp[target_units]
            
            #if this sharpe is better than best found so far, save it
            if sharpe>best_sharpe:
                best_sharpe=sharpe
                best_weights=weights.copy()
    
    #if no valid allocation was found, use equal weight as fallback
    if not best_weights:
        best_weights={
            stock: 1.0/len(selected_stock_list)
            for stock in selected_stock_list
        }
    
    #normalize and apply constraints to final allocation
    total=sum(best_weights.values())
    if total>0:
        #normalize weights to sum to 1.0
        allocations={s: w/total for s, w in best_weights.items()}
    else:
        allocations=best_weights
    
    #make sure no single stock is over 20% allocation (max constraint)
    for stock in allocations:
        if allocations[stock]>MAX_ALLOCATION_PER_STOCK:
            allocations[stock]=MAX_ALLOCATION_PER_STOCK
    
    #remove stocks below minimum allocation (0.5% threshold)
    allocations={
        s: w for s, w in allocations.items()
        if w>=MIN_ALLOCATION_PER_STOCK
    }
    
    #normalize again after removing small allocations
    total=sum(allocations.values())
    if total>0:
        allocations={s: w/total for s, w in allocations.items()}
    
    #calculate final portfolio metrics with optimal allocation
    #final portfolio return is weighted sum of individual stock returns
    portfolio_return=sum(
        allocations.get(stock, 0)*sharpe_ratios[stock]['mean_return']
        for stock in selected_stock_list
    )
    
    #final portfolio variance is sum of squared weight times stock variance
    portfolio_variance=sum(
        allocations.get(stock, 0)**2*sharpe_ratios[stock]['std_return']**2
        for stock in selected_stock_list
    )
    
    #calculate portfolio standard deviation from variance
    portfolio_std=np.sqrt(max(portfolio_variance, 0))
    #calculate sharpe ratio for final portfolio
    portfolio_sharpe=calculate_sharpe_ratio(portfolio_return, portfolio_std)
    
    #compile all results into dictionary for returning
    results={
        'allocations': allocations,
        'sharpe_ratios': sharpe_ratios,
        'portfolio_return': portfolio_return,
        'portfolio_std': portfolio_std,
        'portfolio_sharpe': portfolio_sharpe,
        'num_stocks': len(allocations)
    }
    
    print(f"  DP optimization complete")
    print(f"  Best Sharpe Ratio: {portfolio_sharpe:.4f}")
    
    #display results if requested by caller
    if display_results:
        display_allocation_results(results)
    
    #plot results if requested by caller
    if plot_results:
        plot_allocation_results(results)
    
    #compare with equal weight if requested by caller
    if compare_equal_weight:
        compare_with_equal_weight(results, stocks_metrics)
    
    print("\nDP Knapsack optimization complete!")
    
    return {
    "allocations": allocations,
    "portfolio_sharpe": portfolio_sharpe,
    "total_spent": 0,  #placeholder since no budget was passed
    "shares": {},  #placeholder since whole shares not calculated
    }



if __name__=="__main__":
    print("This module uses Dynamic Programming Knapsack for portfolio optimization.")
    print("\nUsage:")
    print("-"*70)
    print("from monte_carlo_method import monte_carlo_method")
    print("from dp_knapsack import dp_knapsack_portfolio_allocation")
    print("from greedy_whole import greedy_portfolio_allocation")
    print()
    print("stocks_metrics = monte_carlo_method()")
    print()
    print("# Run DP Knapsack (tries all combinations, finds optimal)")
    print("dp_allocations = dp_knapsack_portfolio_allocation(stocks_metrics)")
    print()
    print("# Run Greedy (simple proportional allocation)")
    print("greedy_allocations = greedy_portfolio_allocation(stocks_metrics)")
    print()
    print("# Compare results")
    print("# DP will usually have better or equal Sharpe ratio")
    print("# because it tests more combinations than greedy")
    print("-"*70)
