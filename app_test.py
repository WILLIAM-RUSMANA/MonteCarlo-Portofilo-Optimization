import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Setup paths and imports
ROOT = Path(__file__).resolve()
sys.path.append(str(ROOT))

from monte_carlo_method import monte_carlo_method
from algorithms.greedy import greedy_portfolio_allocation
from algorithms.equal_weight import equal_weight_allocation
from algorithms.dp_knapsack import dp_knapsack_portfolio_allocation
from greedy_whole import greedy_portfolio_allocation as greedy_whole_shares
from dp_knapsack_whole import dp_knapsack_portfolio_allocation as dp_whole_shares
from equal_whole import equal_weight_allocation as equal_whole_shares
from constants import CSV_BACKTEST_2025

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

@st.cache_data(ttl=3600)
def run_monte_carlo():
    return monte_carlo_method(num_simulations=3000)

@st.cache_data
def load_prices():
    df = pd.read_csv(CSV_BACKTEST_2025, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)
    return df

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

# --- PAGE LOGIC (Abbreviated for brevity) ---
if page == "Greedy":
    st.header("Greedy Sharpe Allocation")
    if st.button("Run Allocation", type="primary"):
        results = run_monte_carlo()
        allocs, g_results = greedy_portfolio_allocation(results, target_num_stocks=50, display_results=False)
        whole_shares = greedy_whole_shares(results, amount=amount, target_num_stocks=50, display_results=False)
        render_allocation_results(allocs, g_results, "Greedy Sharpe", load_prices(), amount, whole_shares)

elif page == "Equal Weight":
    st.header("Equal-Weight Allocation")
    if st.button("Run Allocation", type="primary"):
        results = run_monte_carlo()
        allocs_eq, eq_results = equal_weight_allocation(results, display_results=False)
        whole_shares = equal_whole_shares(results, amount=amount, num_stocks=len(allocs_eq), display_results=False)
        render_allocation_results(allocs_eq, eq_results, "Equal Weight", load_prices(), amount, whole_shares)