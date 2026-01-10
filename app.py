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
from equal_whole import equal_weight_allocation as equal_whole_shares
from constants import CSV_BACKTEST_2025_50


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
    [ "Equal Weight", "Greedy Sharpe", "DP Knapsack"],
)


# Cache Monte Carlo results to avoid recomputation
@st.cache_data(ttl=3600)  # Cache for 1 hour
def run_monte_carlo():
    return monte_carlo_method(num_simulations=10000)


@st.cache_data
def load_prices():
    df = pd.read_csv(CSV_BACKTEST_2025_50, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df


# Shared function to render allocation results
def render_allocation_results(allocations, results, title, prices, amount, whole_shares_result):
    """Render pie chart, metrics, sidebar, and strict 2025 calendar year historical data"""
    
    # Sort allocations
    sorted_allocations = sorted(allocations.items(), key=lambda x: x[1], reverse=True)
    
    # Pie chart
    df_pie = pd.DataFrame({"Stock": list(allocations.keys()), "Weight": list(allocations.values())})
    fig = px.pie(df_pie, names="Stock", values="Weight", title=title, hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

    # --- FIX 1: Strict Calendar Year Slicing ---
    # Ensures we are ONLY looking at Jan 1 to Dec 31, 2025
    recent_prices = prices.loc['2025-01-01':'2025-12-31']
    
    if recent_prices.empty:
        st.error("No data found for the year 2025 in the provided dataset.")
        return

    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Projected Annual Return", f"{results['portfolio_return']:.2%}")
    with col2:
        st.metric("Portfolio Sharpe Ratio", f"{results['portfolio_sharpe']:.4f}")
    
    # --- FIX 2: Accurate Return Calculation ---
    with col3:
        available_stocks = [s for s in allocations.keys() if s in recent_prices.columns]
        
        if available_stocks:
            total_start_value = 0
            total_end_value = 0
            
            # We calculate based on the actual dollar amount allocated per weight
            for ticker in available_stocks:
                weight = allocations.get(ticker, 0)
                if weight > 0:
                    # Normalized start is 1.0, end is the relative growth
                    start_price = recent_prices[ticker].iloc[0]
                    end_price = recent_prices[ticker].iloc[-1]
                    
                    stock_growth = end_price / start_price
                    total_start_value += (amount * weight)
                    total_end_value += (amount * weight * stock_growth)
            
            actual_return = (total_end_value / total_start_value) - 1 if total_start_value > 0 else 0
            
            st.metric(
                "Actual 2025 Return",
                f"{actual_return:.2%}",
                delta=f"{(actual_return - results['portfolio_return']):.2%}"
            )
        else:
            st.metric("Actual 2025 Return", "N/A")

    # --- FIX 3: Portfolio Performance Charting ---
    st.subheader("Cumulative Portfolio Value (Jan - Dec 2025)")
    
    if available_stocks:
        portfolio_daily_values = pd.Series(0.0, index=recent_prices.index)
        
        for ticker in available_stocks:
            weight = allocations.get(ticker, 0)
            if weight > 0:
                # Track the growth of the dollar amount invested in each stock
                stock_series = (recent_prices[ticker] / recent_prices[ticker].iloc[0]) * (amount * weight)
                portfolio_daily_values += stock_series
        
        chart_df = pd.DataFrame({'Portfolio Value ($)': portfolio_daily_values})
        st.line_chart(chart_df, height=400)
    
    # Allocation Table
    st.subheader("Final Allocation Weights & Shares")
    alloc_data = [
        {"#": i+1, "Stock": t, "Weight (%)": round(w*100, 2), "Shares": whole_shares_result['shares'].get(t, 0)}
        for i, (t, w) in enumerate(sorted_allocations)
    ]
    st.dataframe(pd.DataFrame(alloc_data), hide_index=True, use_container_width=True)
    st.metric("Unallocated Cash", f"${whole_shares_result['cash_remaining']:,.2f}")


# ========== PAGE 1: GREEDY ==========
if page == "Greedy Sharpe":
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
    else:
        st.info("Click 'Run Allocation' to generate portfolio")


# ========== PAGE 3: EQUAL WEIGHT ==========
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

            # Get whole shares allocation using equal_whole
            whole_shares_result = equal_whole_shares(
                stocks_metrics=results,
                amount=amount,
                num_stocks=len(allocations_eq),
                display_results=False,
                plot_results=False
            )

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