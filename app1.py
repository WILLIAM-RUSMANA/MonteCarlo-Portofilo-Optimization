import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from monte_carlo_method import monte_carlo_method
from greedy import greedy_portfolio_allocation as greedy_cont
from greedy_whole import greedy_portfolio_allocation as greedy_whole

# Page config
st.set_page_config(page_title="Portfolio Allocator", layout="wide")

# Title
st.title("Portfolio Allocator")

# Amount input (shared across all pages)
amount = st.number_input(
    "Amount of USD to allocate",
    min_value=100.0,
    value=100000.0,
    step=1000.0,
)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Algorithm",
    ["Greedy", "Algorithm 2", "Algorithm 3"],
)

# Helper functions
@st.cache_data
def run_monte_carlo():
    return monte_carlo_method()

@st.cache_data
def load_prices():
    df = pd.read_csv("data/stocks_close_2013_2025.csv", parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    return df

def projected_return_from_alloc(alloc, results):
    return sum(
        w * results[t]["mean_annual_return"] for t, w in alloc.items() if t in results
    )

# ========== PAGE 1: GREEDY ==========

if page == "Greedy":
    st.header("Greedy Algorithm")
    st.write("Selects top N stocks by Sharpe ratio and allocates proportionally")

    if st.button("Run Allocation", type="primary"):
        with st.spinner("Running Monte Carlo simulation and allocation algorithms..."):
            # Run Monte Carlo and algorithms
            results = run_monte_carlo()

            cont_alloc = greedy_cont(
                results,
                target_num_stocks=50,
                plot_results=False,
                compare_equal_weight=False,
                display_results=False,
            )

            whole_alloc = greedy_whole(
                results,
                amount,
                target_num_stocks=50,
                plot_results=False,
                compare_equal_weight=False,
                display_results=False,
            )

            shares = whole_alloc["shares"]
            cash_remaining = whole_alloc["cash_remaining"]
            stock_prices = whole_alloc["stock_prices"]

            # === CONTINUOUS WEIGHTS ===

            st.subheader("1. Continuous-weight allocation")

            cont_df = pd.DataFrame(
                {
                    "Stock": list(cont_alloc.keys()),
                    "Weight": list(cont_alloc.values()),
                }
            )

            fig_cont = px.pie(
                cont_df,
                names="Stock",
                values="Weight",
                title="Portfolio Allocation (Continuous Weights)",
            )

            st.plotly_chart(fig_cont, use_container_width=True)

            proj_return_cont = projected_return_from_alloc(cont_alloc, results)

            st.metric("Projected annual return (continuous)", f"{proj_return_cont:.2%}")

            # === WHOLE SHARES ===

            st.subheader("2. Whole-share allocation")

            amounts = {t: shares[t] * stock_prices[t] for t in shares}
            total_amount = sum(amounts.values()) or 1.0

            whole_df = pd.DataFrame(
                {
                    "Stock": list(amounts.keys()),
                    "Weight": [v / total_amount for v in amounts.values()],
                }
            )

            fig_whole = px.pie(
                whole_df,
                names="Stock",
                values="Weight",
                title="Portfolio Allocation (Whole Shares)",
            )

            st.plotly_chart(fig_whole, use_container_width=True)

            weights_whole = {t: amt / total_amount for t, amt in amounts.items()}
            proj_return_whole = projected_return_from_alloc(weights_whole, results)

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Projected annual return (whole shares)", f"{proj_return_whole:.2%}"
                )

            with col2:
                st.metric("Cash remaining", f"${cash_remaining:,.2f}")

            # === SIDEBAR ===

            st.sidebar.subheader("📊 Shares to Buy")
            st.sidebar.caption("Sorted by number of shares (descending)")

            share_items = sorted(shares.items(), key=lambda x: x[1], reverse=True)
            for ticker, n_shares in share_items:
                st.sidebar.write(f"**{ticker}**: {n_shares} shares")

            st.sidebar.divider()

            st.sidebar.write(f"💰 **Cash remaining**: ${cash_remaining:,.2f}")

            # === HISTORICAL PERFORMANCE ===

            st.subheader("3. Historical Stock Performance")

            prices = load_prices()
            st.line_chart(prices)

    else:
        st.info("👈 Set amount on the left, then click 'Run Allocation'")

# ========== PAGE 2: ALGORITHM 2 ==========

elif page == "Algorithm 2":
    st.header("Algorithm 2 - Dynamic Programming Knapsack")
    st.write("Optimizes portfolio using Dynamic Programming for mathematically optimal allocation")

    if st.button("Run Allocation", type="primary"):
        with st.spinner("Running DP Knapsack optimization..."):
            try:
                # Import Algorithm 2
                from dp_knapsack import dp_knapsack_portfolio_allocation, allocate_whole_shares_dp

                # Step 1: Run Monte Carlo
                results = run_monte_carlo()

                # Step 2: Get stock prices
                prices = load_prices()
                stock_prices_dict = {}
                for ticker in results.keys():
                    if ticker in prices.columns:
                        stock_prices_dict[ticker] = prices[ticker].iloc[-1]

                # Step 3: Run Algorithm 2 (DP Knapsack)
                dp_weights = dp_knapsack_portfolio_allocation(
                    results,
                    target_num_stocks=50,
                    display_results=False,
                    plot_results=False,
                    compare_equal_weight=False,
                )

                # Step 4: Allocate whole shares
                dp_shares_result = allocate_whole_shares_dp(dp_weights, stock_prices_dict, amount)

                shares = dp_shares_result["shares"]
                cash_remaining = dp_shares_result["cash_remaining"]
                stock_prices = dp_shares_result["stock_prices"]

                # === CONTINUOUS WEIGHTS ===
                st.subheader("1. Continuous-weight allocation (DP Knapsack)")

                dp_df = pd.DataFrame(
                    {
                        "Stock": list(dp_weights.keys()),
                        "Weight": list(dp_weights.values()),
                    }
                )

                fig_dp = px.pie(
                    dp_df,
                    names="Stock",
                    values="Weight",
                    title="Portfolio Allocation - DP Knapsack (Continuous Weights)",
                )

                st.plotly_chart(fig_dp, use_container_width=True)

                proj_return_dp = projected_return_from_alloc(dp_weights, results)
                st.metric("Projected annual return (continuous)", f"{proj_return_dp:.2%}")

                # === WHOLE SHARES ===
                st.subheader("2. Whole-share allocation (DP Knapsack)")

                amounts = {t: shares[t] * stock_prices[t] for t in shares}
                total_amount = sum(amounts.values()) or 1.0
                weights_whole = {t: amt / total_amount for t, amt in amounts.items()}

                dp_whole_df = pd.DataFrame(
                    {
                        "Stock": list(amounts.keys()),
                        "Weight": [v / total_amount for v in amounts.values()],
                    }
                )

                fig_whole = px.pie(
                    dp_whole_df,
                    names="Stock",
                    values="Weight",
                    title="Portfolio Allocation - DP Knapsack (Whole Shares)",
                )

                st.plotly_chart(fig_whole, use_container_width=True)

                proj_return_whole = projected_return_from_alloc(weights_whole, results)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Projected annual return (whole shares)", f"{proj_return_whole:.2%}")

                with col2:
                    st.metric("Cash remaining", f"${cash_remaining:,.2f}")

                # === SIDEBAR ===
                st.sidebar.subheader("📊 Shares to Buy (DP Knapsack)")
                st.sidebar.caption("Sorted by number of shares (descending)")

                share_items = sorted(shares.items(), key=lambda x: x[1], reverse=True)
                for ticker, n_shares in share_items:
                    st.sidebar.write(f"**{ticker}**: {n_shares} shares")

                st.sidebar.divider()
                st.sidebar.write(f"💰 **Cash remaining**: ${cash_remaining:,.2f}")

                # === HISTORICAL PERFORMANCE ===
                st.subheader("3. Historical Stock Performance")
                st.line_chart(load_prices())

            except ImportError as e:
                st.error(f"❌ Error importing Algorithm 2: {e}")
                st.info("Make sure dp_knapsack.py is in your project root directory")
            except Exception as e:
                st.error(f"❌ Error running Algorithm 2: {e}")
                import traceback
                st.error(traceback.format_exc())

    else:
        st.info("👈 Set amount on the left, then click 'Run Allocation'")

# ========== PAGE 3: ALGORITHM 3 ==========

elif page == "Algorithm 3":
    st.header("Algorithm 3")
    st.info("🔮 Algorithm 3 - Coming soon!")

    st.warning("This page is reserved for Algorithm 3 (future implementation)")