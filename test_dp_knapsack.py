#test dp knapsack
from monte_carlo_method import monte_carlo_method
from dp_knapsack import dp_knapsack_portfolio_allocation

def main():
    #get stock data from monte carlo
    print("Running Monte Carlo...")
    stocks_metrics=monte_carlo_method()
    
    #run dp optimization
    print("\nRunning DP Knapsack...")
    allocations=dp_knapsack_portfolio_allocation(
        stocks_metrics,
        target_num_stocks=10,
        display_results=True,
        #set true or false
        plot_results=True,
        compare_equal_weight=True
    )
    
    #show final result
    print("\n\nFinal allocations:")
    print(allocations)
    
    print("\nDone!")

if __name__=="__main__":
    main()