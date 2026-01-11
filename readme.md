# Portfolio Allocation Optimization Using Monte Carlo Simulation

A comprehensive Python project for analyzing and comparing portfolio allocation algorithms using Monte Carlo simulations. This project implements three distinct allocation strategies (Equal Weight, Greedy Sharpe, and Dynamic Programming Knapsack) and benchmarks their performance across stock portfolios of varying sizes.

## 🎯 Project Overview

This project analyzes how different portfolio allocation algorithms perform in constructing diversified stock portfolios. It uses **Monte Carlo simulations** to estimate stock performance metrics and compares algorithms based on:
- **Solution Quality**: Portfolio Sharpe ratio, expected returns, and volatility
- **Computational Efficiency**: Execution time and scalability
- **Trade-offs**: Speed vs. quality analysis across dataset sizes

### Key Features
- 🎲 **Monte Carlo Simulation**: 10,000 iterations for robust performance estimation
- 📊 **Three Allocation Algorithms**: Equal Weight, Greedy Sharpe, DP Knapsack
- 📈 **Multi-Scale Analysis**: Tests on 50, 100, 250, and 500 stock portfolios
- 🏃 **Performance Benchmarking**: Comparative time and quality metrics
- 🎨 **Interactive Dashboard**: Real-time portfolio visualization and analysis
- 📉 **Backtesting**: 2025 historical performance validation

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
cd MonteCarlo-Portfolio-Optimization

# Install dependencies
pip install -r requirements.txt
```

### Running the CLI Analysis

```bash
# Run the complete benchmark suite
python main.py
```

This will:
1. Execute Monte Carlo simulations (10,000 iterations each) on 4 dataset sizes
2. Benchmark all three algorithms across each dataset
3. Display results ranked by execution time and solution quality
4. Generate trade-off analysis comparing speed vs. quality
5. Save results to `data/benchmark_results_50.csv`

### Running the Interactive Dashboard

```bash
# Launch the Streamlit web interface
streamlit run app.py
```

Then visit `http://localhost:8501` in your browser to:
- Allocate a custom USD amount across stocks
- Compare algorithms side-by-side
- Visualize portfolio allocation as interactive pie charts
- View projected returns and risk metrics
- Analyze 2025 historical performance data

---

## 📁 Project Structure

```
├── main.py                          # CLI: Runs benchmarks and analysis
├── app.py                           # Web Dashboard: Streamlit interface
├── monte_carlo_method.py            # Monte Carlo simulation engine
├── benchmark.py                     # Benchmarking framework
├── helper.py                        # Utility functions (Sharpe ratio, etc.)
├── constants.py                     # Configuration and file paths
├── requirements.txt                 # Python dependencies
│
├── algorithms/
│   ├── greedy.py                    # Greedy Sharpe ratio algorithm
│   ├── equal_weight.py              # Equal weight allocation
│   ├── dp_knapsack.py               # DP knapsack algorithm
│   └── __pycache__/
│
├── data/
│   ├── 50stocks_close_2013_2024.csv      # 50-stock dataset
│   ├── 100stocks_close_2013_2024.csv     # 100-stock dataset
│   ├── 250stocks_close_2013_2024.csv     # 250-stock dataset
│   ├── 500stocks_close_2013_2024.csv     # 500-stock dataset
│   ├── 50stocks_close_2025_2026.csv      # 2025-2026 backtest data
│   ├── benchmark_results.csv             # Output: Algorithm performance
│   ├── monte_carlo_results.csv           # Output: Simulation results
│   └── portfolio_allocation.csv          # Output: Final allocations
│
├── archive/                         # Legacy and experimental code
└── README.md                        # This file
```

---

## 🔧 Main Entry Points

### 1. **main.py** - Command-Line Interface

**Purpose**: Run comprehensive benchmarks and analysis across all datasets.

**What it does**:
```python
# Step 1: Runs Monte Carlo simulations
stocks_metrics_50 = monte_carlo_method(num_simulations=10000)
stocks_metrics_100 = monte_carlo_method(10000, 252, CSV_FILE_100)
# ... for 250 and 500 stocks

# Step 2: Benchmarks all algorithms
results_50 = benchmark_all_algorithms(stocks_metrics_50, target_num_stocks=50, num_runs=5)
# ... for other dataset sizes

# Step 3: Analyzes results
# - Time efficiency ranking
# - Solution quality ranking (by Sharpe ratio)
# - Trade-off analysis: speed vs. quality
```

**Output**:
- Console display of rankings and analysis
- CSV file: `data/benchmark_results_50.csv`
- Comparative metrics across all algorithms and dataset sizes

**Example Output**:
```
PORTFOLIO ALLOCATION ALGORITHM ANALYSIS
====================================

Step 1: Running Monte Carlo simulation (10000 iterations)...
Simulation complete. Analyzing 50 stocks.

Step 2: Benchmarking algorithms (5 runs each)...

Time Efficiency Ranking:
  1. Greedy           12.34 ms
  2. Equal Weight     45.67 ms
  3. DP Knapsack      123.45 ms

Solution Quality Ranking (by Sharpe Ratio):
  1. DP Knapsack          Sharpe: 0.8945, Return: 12.34%
  2. Greedy               Sharpe: 0.8723, Return: 11.89%
  3. Equal Weight         Sharpe: 0.7234, Return: 10.56%
```

---

### 2. **app.py** - Interactive Dashboard

**Purpose**: Provide an interactive web interface for portfolio allocation and analysis.

**Features**:

#### Input Controls
- **USD Amount**: Slider/input to specify investment amount (default: $100,000)
- **Algorithm Selection**: Radio buttons to choose between:
  - Equal Weight
  - Greedy Sharpe
  - DP Knapsack

#### Visualizations
- **Portfolio Allocation Pie Chart**: Donut chart showing stock weights
- **Key Metrics**:
  - Projected Annual Return (from Monte Carlo)
  - Portfolio Sharpe Ratio
  - Actual 2025 Year-to-Date Return (backtested)

#### Data Handling
- **Monte Carlo Caching**: Results cached for 1 hour to avoid recomputation
- **Historical Data**: Loads 2025 price data from `CSV_BACKTEST_2025_50`
- **Strict Date Slicing**: Only analyzes Jan 1 - Dec 31, 2025 data
- **Price-Based Returns**: Calculates actual returns using opening/closing prices

#### Stock Allocation Display
```
Allocations are shown as:
- Weight: Percentage of portfolio
- USD Amount: Dollar allocation (amount × weight)
- Shares: Whole number of shares you can buy
- Cost: Actual cost at purchase price
```

**Example Workflow**:
1. User enters $100,000 to invest
2. Selects "Greedy Sharpe" algorithm
3. App displays:
   - Pie chart of stock weights
   - Projected return: 12.5%
   - Sharpe ratio: 0.8723
   - 2025 actual performance: +8.3%
4. Shows exact share counts and costs for each stock

---

## 📊 Algorithms Explained

### 1. **Equal Weight** (`algorithms/equal_weight.py`)
```
Allocates equal percentage to each stock: 1/N
```
- **Speed**: ⚡⚡⚡ Very fast
- **Quality**: ⭐⭐ Basic benchmark
- **Use case**: Simple baseline for comparison

### 2. **Greedy Sharpe** (`algorithms/greedy.py`)
```
1. Calculate Sharpe ratio for each stock
2. Select top K stocks by Sharpe ratio
3. Weight inversely proportional to Sharpe
4. Apply min/max allocation constraints
5. Normalize to sum to 100%
```
- **Speed**: ⚡⚡ Fast
- **Quality**: ⭐⭐⭐ Good (ignores correlations)
- **Use case**: Quick, intuitive allocation

### 3. **DP Knapsack** (`algorithms/dp_knapsack.py`)
```
Uses Dynamic Programming to optimize portfolio:
1. Discretizes stock returns into bins
2. Treats allocation as knapsack optimization
3. Maximizes expected return subject to budget
```
- **Speed**: ⚡ Slow
- **Quality**: ⭐⭐⭐⭐ Best (multi-objective)
- **Use case**: Thorough analysis when computation time isn't critical

---

## 🎲 Monte Carlo Simulation Details

### How It Works

```python
monte_carlo_method(num_simulations=10000, days=252, filepath=CSV_FILE_50)
```

**Process**:
1. **Load Historical Data**: Daily closing prices (2013-2024)
2. **Calculate Daily Returns**: Percentage change day-over-day
3. **Estimate Parameters**:
   - Mean daily return (μ)
   - Standard deviation (σ)
4. **Simulate Paths**: Generate 10,000 random walks using:
   ```
   Daily Return ~ N(μ, σ)  [Normal distribution]
   ```
5. **Calculate Annual Metrics**:
   - Cumulative annual return
   - Mean, median, std dev of returns
   - 5th and 95th percentile (Value at Risk bounds)

### Output Per Stock
```python
{
    "AAPL": {
        "mean_annual_return": 0.1234,      # 12.34% expected return
        "std_annual_return": 0.1856,       # 18.56% volatility
        "median_annual_return": 0.1245,
        "var_5": -0.0432,                  # 5th percentile (worst case)
        "var_95": 0.3145,                  # 95th percentile (best case)
        "simulated_annual_returns": [...]  # Array of 10,000 returns
    }
    # ... for all stocks
}
```

---

## 📈 Benchmarking Framework

### What Gets Measured

```python
benchmark_all_algorithms(stocks_metrics, target_num_stocks=50, num_runs=5)
```

**Metrics Per Algorithm Run**:
- `algorithm`: Algorithm name
- `execution_time_ms`: Time in milliseconds
- `portfolio_return`: Expected annual return
- `portfolio_std`: Portfolio volatility
- `portfolio_sharpe`: Sharpe ratio (risk-adjusted return)
- `num_stocks`: Number of stocks selected
- `allocation_count`: Complexity metric

**Output Format**:
```python
[
    {
        "algorithm": "Greedy",
        "execution_time_ms": 12.34,
        "portfolio_return": 0.1234,
        "portfolio_std": 0.1856,
        "portfolio_sharpe": 0.6645,
        "num_stocks": 50
    },
    # ... more results
]
```

---

## 🔬 Usage Examples

### Example 1: Run Benchmarks and Export Results

```bash
python main.py > analysis_output.txt
```

Produces rankings like:
- Fastest algorithm (Greedy: 12.34 ms)
- Best quality (DP Knapsack: Sharpe 0.8945)
- Trade-off analysis (quality gain vs. time cost)

### Example 2: Interactive Portfolio Building

```bash
streamlit run app.py
```

Then:
1. Enter $250,000
2. Choose "DP Knapsack"
3. View allocations with exact share counts
4. See 2025 backtest performance

### Example 3: Custom Dataset Size

Edit `constants.py`:
```python
CSV_FILE = "data/custom_stocks.csv"
```

Then run:
```bash
python main.py
```

---

## 📊 Data Files

### Input Datasets
| File | Stocks | Period | Size |
|------|--------|--------|------|
| `50stocks_close_2013_2024.csv` | 50 | 2013-2024 | ~2.6 MB |
| `100stocks_close_2013_2024.csv` | 100 | 2013-2024 | ~5.2 MB |
| `250stocks_close_2013_2024.csv` | 250 | 2013-2024 | ~13 MB |
| `500stocks_close_2013_2024.csv` | 500 | 2013-2024 | ~26 MB |
| `50stocks_close_2025_2026.csv` | 50 | 2025-2026 | ~2.6 MB |

### Output Files (Generated)
- `benchmark_results.csv`: Algorithm performance metrics
- `monte_carlo_results.csv`: Simulation outputs per stock
- `portfolio_allocation.csv`: Final allocation weights

---

## 🧮 Key Performance Indicators

### Sharpe Ratio
```
Sharpe = (Portfolio Return - Risk-Free Rate) / Portfolio Std Dev
```
Higher is better. Measures risk-adjusted returns.

### Portfolio Std Dev
```
σ_portfolio = √(Σ weights_i² × σ_i²)  [simplified, ignores correlations]
```
Lower is better. Measures portfolio volatility.

### Execution Time
```
Measures algorithm speed in milliseconds
```
Lower is better. Trade-off with solution quality.

---

## 🐛 Troubleshooting

### Issue: "No data found for the year 2025"
**Solution**: Ensure `CSV_BACKTEST_2025_50` path in `constants.py` is correct and contains 2025 data.

### Issue: Streamlit app is slow
**Solution**: Monte Carlo results are cached for 1 hour. Clear cache:
```bash
streamlit cache clear
```

### Issue: Memory error with 500-stock dataset
**Solution**: Reduce `num_simulations` in `main.py` from 10,000 to 5,000 or 1,000.

---

## 📦 Dependencies

- **pandas**: Data manipulation
- **numpy**: Numerical computations
- **matplotlib**: Plotting (for analysis)
- **streamlit**: Web dashboard
- **plotly**: Interactive charts in Streamlit
- **yfinance**: Optional for fetching live stock data

Install all with:
```bash
pip install -r requirements.txt
```

---

## 📝 Configuration

Edit `constants.py` to customize:

```python
CSV_FILE_50 = "data/50stocks_close_2013_2024.csv"
CSV_FILE_100 = "data/100stocks_close_2013_2024.csv"
NUM_SIMULATIONS = 10000          # Monte Carlo iterations
TRADING_DAYS_PER_YEAR = 252      # Standard trading days
MIN_ALLOCATION_PER_STOCK = 0.005 # 0.5% minimum per stock
MAX_ALLOCATION_PER_STOCK = 0.10  # 10% maximum per stock
```

---

## 🎓 Learning Outcomes

After exploring this project, you'll understand:
1. **Monte Carlo Simulations** in finance
2. **Portfolio Optimization** strategies
3. **Algorithm Trade-offs**: Speed vs. quality
4. **Financial Metrics**: Sharpe ratio, volatility, VaR
5. **Benchmarking Methodology**: Fair performance comparison
6. **Interactive Dashboards**: Building with Streamlit

---

## 🤝 Contributing

Feel free to fork and extend this project! Potential improvements:
- Add additional algorithms (Modern Portfolio Theory, Black-Litterman)
- Implement correlation matrices for better DP weighting
- Add transaction cost analysis
- Extend backtesting to multiple years
- Add risk metrics (Sortino ratio, max drawdown)

---

## 📄 License

This project is open source. Feel free to use and modify as needed.

---

## 📧 Support

For questions or issues, review the code comments or check the `archive/` folder for experimental approaches.

---

**Last Updated**: January 2026
