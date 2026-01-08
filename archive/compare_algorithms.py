#compare greedy and dp knapsack
from monte_carlo_method import monte_carlo_method
from greedy_whole import greedy_portfolio_allocation as greedy_whole
from dp_knapsack import dp_knapsack_portfolio_allocation

def main():
    #run monte carlo once
    print("Running Monte Carlo...")
    stocks_metrics=monte_carlo_method()
    
    print("\n"+"="*100)
    print("COMPARISON: GREEDY vs DP KNAPSACK")
    print("="*100)
    
    budget=100_000
    
    #run greedy first
    print("\n[1] GREEDY Algorithm")
    print("-"*100)
    greedy_results=greedy_whole(
        stocks_metrics,
        amount=budget,
        target_num_stocks=10,
        # set true or false
        plot_results=True
    )
    
    greedy_sharpe=greedy_results.get('portfolio_sharpe', 0)
    
    print(f"\nGreedy Results:")
    print(f"  Sharpe Ratio: {greedy_sharpe:.4f}")
    print(f"  Total Spent: ${greedy_results['total_spent']:,.2f}")
    print(f"  Cash Left: ${greedy_results['cash_remaining']:,.2f}")
    
    #run dp knapsack
    print("\n\n[2] DP KNAPSACK Algorithm")
    print("-"*100)
    dp_allocations=dp_knapsack_portfolio_allocation(
        stocks_metrics,
        target_num_stocks=10,
        display_results=True,
        #set true or false
        plot_results=True,
        compare_equal_weight=True
    )
    
    #summary
    print("\n\n"+"="*100)
    print("SUMMARY")
    print("="*100)
    print("\nGREEDY:")
    print("  - Simple proportional allocation")
    print("  - Fast (milliseconds)")
    print("  - Not guaranteed optimal")
    print()
    print("DP KNAPSACK:")
    print("  - Tests many combinations")
    print("  - Slower (few seconds)")
    print("  - Guaranteed optimal")
    print()
    print("Result: DP should have same or better Sharpe ratio")
    print("="*100)

if __name__=="__main__":
    main()