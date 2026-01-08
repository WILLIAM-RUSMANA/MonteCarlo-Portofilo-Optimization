import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# ROOT = Path(__file__).resolve().parent.parent
ROOT = Path(__file__).resolve()
sys.path.append(str(ROOT))

from monte_carlo_method import monte_carlo_method
from algorithms.greedy import greedy_portfolio_allocation
from algorithms.equal_weight import equal_weight_allocation
from algorithms.dp_knapsack import dp_knapsack_portfolio_allocation
from greedy_whole import greedy_portfolio_allocation as greedy_whole_shares
from dp_knapsack_whole import dp_knapsack_portfolio_allocation as dp_whole_shares
from constants import CSV_BACKTEST


st.set_page_config(page_title="Portfolio Allocator", layout="wide")
st.title("Portfolio Allocator")

amount = st.number_input(
    "Amount of USD to allocate",
    min_value=100.0,
    value=100000.0,
    step=1000.0,
)

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Algorithm",
    ["Greedy", "DP Knapsack", "Equal Weight"],
)


# Cache Monte Carlo results to avoid recomputation
@st.cache_data(ttl=3600)  # Cache for 1 hour
def run_monte_carlo():
    return monte_carlo_method(num_simulations=3000)


@st.cache_data
def load_prices():
    df = pd.read_csv(CSV_BACKTEST, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df


# Shared function to render allocation results
def render_allocation_results(allocations, results, title, prices, amount, whole_shares_result):
    """Render pie chart, metrics, sidebar, and backtesting data"""
    
    # Sort allocations once at the beginning
    sorted_allocations = sorted(
        allocations.items(), key=lambda x: x[1], reverse=True
    )
    
    # Pie chart with reduced complexity
    df = pd.DataFrame(
        {
            "Stock": list(allocations.keys()),
            "Weight": list(allocations.values()),
        }
    )

    fig = px.pie(
        df,
        names="Stock",
        values="Weight",
        title=title,
        hole=0.3,  # Donut chart is lighter
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

    # Prepare recent_prices FIRST (needed for metrics calculation)
    recent_prices = prices.last('252D')

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Projected Annual Return",
            f"{results['portfolio_return']:.2%}",
        )
    with col2:
        st.metric(
            "Portfolio Sharpe Ratio",
            f"{results['portfolio_sharpe']:.4f}",
        )
    
    # Calculate actual return from backtest data (using FULL price history)
    with col3:
        # Get all stocks in allocation
        all_stocks = [ticker for ticker, _ in sorted_allocations]
        available_stocks = [s for s in all_stocks if s in prices.columns]
        
        if available_stocks:
            # Get weights for available stocks
            weights_dict = {ticker: weight for ticker, weight in sorted_allocations if ticker in available_stocks}
            total_weight = sum(weights_dict.values())
            normalized_weights = {ticker: weight/total_weight for ticker, weight in weights_dict.items()}
            
            # Calculate actual portfolio return using SAME date range as chart
            weighted_returns = 0
            for ticker in available_stocks:
                weight = normalized_weights[ticker]
                # Use recent_prices (252D) for consistency with chart
                stock_return = (recent_prices[ticker].iloc[-1] / recent_prices[ticker].iloc[0]) - 1
                weighted_returns += weight * stock_return
            
            st.metric(
                "Actual Backtest Return",
                f"{weighted_returns:.2%}",
                delta=f"{(weighted_returns - results['portfolio_return']):.2%}"
            )
        else:
            st.metric("Actual Backtest Return", "N/A")

    # Historical - use sampling for better performance
    st.subheader("Backtesting Portfolio Performance (2025)")
    
    # Calculate portfolio collective return
    all_stocks = [ticker for ticker, _ in sorted_allocations]
    available_stocks = [s for s in all_stocks if s in recent_prices.columns]
    
    if available_stocks:
        # Get weights for available stocks only
        weights_dict = {ticker: weight for ticker, weight in sorted_allocations if ticker in available_stocks}
        total_weight = sum(weights_dict.values())
        
        # Normalize weights
        normalized_weights = {ticker: weight/total_weight for ticker, weight in weights_dict.items()}
        
        # Calculate weighted portfolio returns
        portfolio_values = pd.DataFrame()
        for ticker in available_stocks:
            weight = normalized_weights[ticker]
            # Normalize each stock to start at the input amount and multiply by weight
            normalized_stock = (recent_prices[ticker] / recent_prices[ticker].iloc[0]) * amount * weight
            portfolio_values[ticker] = normalized_stock
        
        # Sum all weighted stocks to get portfolio performance
        portfolio_performance = portfolio_values.sum(axis=1)
        portfolio_df = pd.DataFrame({'Portfolio Value': portfolio_performance})
        
        st.line_chart(portfolio_df, height=400)
    else:
        st.warning("No matching stocks found in historical data")
    
    # Allocation weights table below historical chart - SHOW ALL
    st.subheader("All Portfolio Allocation Weights")
    
    # Create DataFrame with numbering and whole shares
    alloc_data = []
    for idx, (ticker, weight) in enumerate(sorted_allocations, start=1):
        shares = whole_shares_result['shares'].get(ticker, 0)
        alloc_data.append({
            "#": idx,
            "Stock": ticker,
            "Weight (%)": round(weight * 100, 2),
            "Whole Shares": shares
        })
    
    alloc_df = pd.DataFrame(alloc_data)
    
    # Display single table
    st.dataframe(alloc_df, hide_index=True, use_container_width=True, height=600)

def print_cash_remaining(whole_share_results):
    st.text(f'{whole_share_results["cash_remaining"]}')

# ========== PAGE 1: GREEDY ==========
if page == "Greedy":
    st.header("Greedy Sharpe Algorithm")

    if st.button("Run Allocation", type="primary", key="greedy_btn"):
        with st.spinner("Running Monte Carlo and Greedy allocation..."):
            results = run_monte_carlo()

            allocations, greedy_results = greedy_portfolio_allocation(
                results,
                target_num_stocks=50,
                display_results=False,
            )

            # Get whole shares allocation
            whole_shares_result = greedy_whole_shares(
                stocks_metrics=results,
                amount=amount,
                target_num_stocks=50,
                display_results=False,
                plot_results=False,
                compare_equal_weight=False
            )

            prices = load_prices()
            render_allocation_results(
                allocations,
                greedy_results,
                "Greedy Sharpe Allocation",
                prices,
                amount,
                whole_shares_result
            )
            print_cash_remaining(whole_shares_result)
    else:
        st.info("Click 'Run Allocation' to generate portfolio")

# ========== PAGE 2: DP KNAPSACK ==========
elif page == "DP Knapsack":
    st.header("DP Knapsack Algorithm")

    if st.button("Run Allocation", type="primary", key="dp_btn"):
        with st.spinner("Running Monte Carlo and DP Knapsack allocation..."):
            results = run_monte_carlo()

            allocations, dp_results = dp_knapsack_portfolio_allocation(
                results,
                target_num_stocks=50,
                display_results=False,
            )

            # Get whole shares allocation
            whole_shares_result = dp_whole_shares(
                stocks_metrics=results,
                amount=amount,
                target_num_stocks=50,
                display_results=False,
                plot_results=False,
                compare_equal_weight=False
            )

            prices = load_prices()
            render_allocation_results(
                allocations,
                dp_results,
                "DP Knapsack Allocation",
                prices,
                amount,
                whole_shares_result
            )
            st.text(f'{whole_shares_result["cash_remaining"]}')
            print_cash_remaining(whole_shares_result)
    else:
        st.info("Click 'Run Allocation' to generate portfolio")


# ========== PAGE 3: EQUAL WEIGHT ==========
# TODO: finish
elif page == "Equal Weight":
    st.header("Equal-Weight Algorithm")

    if st.button("Run Allocation", type="primary", key="eq_btn"):
        with st.spinner(
            "Running Monte Carlo simulation and equal-weight allocation..."
        ):
            results = run_monte_carlo()

            allocations_eq, eq_results = equal_weight_allocation(
                results,
                display_results=False,
            )

            # For equal weight, create a simple whole shares result (equal distribution)
            # Note: You may want to create an equal_weight_whole.py file similar to the others
            whole_shares_result = {"shares": {ticker: 0 for ticker in allocations_eq.keys()}}

            prices = load_prices()
            render_allocation_results(
                allocations_eq,
                eq_results,
                "Equal-Weight Portfolio Allocation",
                prices,
                amount,
                whole_shares_result
            )
    else:
        st.info("Click 'Run Allocation' to generate portfolio")