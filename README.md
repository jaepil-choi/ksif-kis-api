# KSIF Dashboard

A comprehensive financial dashboard built with Streamlit for Korea Securities Investment Fund (KSIF). This dashboard provides real-time portfolio monitoring, position tracking, P&L analysis, and benchmark comparisons.

## Features

### 📊 Multi-Page Application
- **🏠 Dashboard**: Core overview with Position Summary and P&L Report
- **💼 Positions**: Detailed portfolio positions view
- **📋 Transactions**: Comprehensive trade history with filtering capabilities  
- **📈 Reports**: Benchmark comparison and portfolio performance analysis
- **👥 Teams**: Team management and performance tracking
- **⚙️ Settings**: Application configuration and user preferences

### 🎛️ Interactive Controls
- **Date Range Picker**: Filter data by custom date ranges
- **Team Filter**: View data for specific teams or all teams
- **Currency Filter**: Display values in different currencies (KRW, USD, EUR, JPY)
- **Period Selection**: Daily, Weekly, MTD, YTD analysis options

### 📱 User Interface
- Clean, modern design matching the KSIF brand
- Responsive layout with intuitive navigation
- Real-time data updates
- Interactive charts and tables

## Installation & Setup

### Prerequisites
- Python 3.12+
- Poetry (for dependency management)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd ksif-kis-api
   ```

2. **Install dependencies**:
   ```bash
   poetry install --no-root
   ```

3. **Run the dashboard**:
   ```bash
   poetry run streamlit run app/ksif_dashboard.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:8501
   ```

## Usage

### Running the Dashboard

To start the dashboard, use the following command:

```bash
poetry run streamlit run app/ksif_dashboard.py
```

The dashboard will be available at `http://localhost:8501` in your web browser.

### Navigation

- **Sidebar Navigation**: Click navigation buttons to switch between pages:
  - **🏠 Dashboard**: Main overview with positions and P&L
  - **💼 Positions**: Detailed portfolio view
  - **📋 Transactions**: Trade history and transaction management
  - **📈 Reports**: Benchmark comparisons and performance analysis
  - **👥 Teams**: Team management interface
  - **⚙️ Settings**: Application configuration
- **Header Controls**: Use date range picker, team filter, and currency selector to customize the view (available on all pages)
- **Interactive Elements**: Click on charts, tables, and buttons to explore data in detail

### Data Integration Points

The current implementation uses placeholder data with comments indicating where real data sources should be integrated:

1. **Position Data**: Replace `generate_position_data()` with actual KIS API calls
2. **P&L Data**: Replace `generate_pl_data()` with real trading system data  
3. **Transaction Data**: Replace `generate_transaction_data()` with actual trade history
4. **Benchmark Data**: Replace `generate_benchmark_data()` with financial market data APIs

## Technical Architecture

### Dependencies
- **Streamlit**: Web application framework
- **Plotly**: Interactive charts and visualizations
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing support
- **python-kis**: Korea Investment & Securities API integration

### File Structure
```
app/
├── ksif_dashboard.py          # Main dashboard application
├── ...                       # Additional modules (to be added)

docs/
├── references/
│   ├── v0-ksif-dashboard.md   # Original design specification
│   └── ...

pyproject.toml                 # Poetry configuration and dependencies
```

### Key Components

1. **Layout Management**: Streamlit columns and containers for responsive design
2. **Data Generation**: Placeholder functions that simulate real data sources
3. **Visualization**: Plotly charts for interactive data exploration
4. **Styling**: Custom CSS for professional appearance
5. **State Management**: Streamlit session state for user interactions

## Customization

### Styling
The dashboard uses custom CSS defined in the main application file. Key style elements include:
- Color scheme: Blue (#4A90E2), Green (#7ED321), Red (#D0021B)
- Typography: Clean sans-serif fonts
- Layout: Card-based design with subtle shadows

### Data Sources
To connect real data sources, modify these functions in `app/ksif_dashboard.py`:
- `generate_position_data()`: Connect to KIS API for current positions
- `generate_pl_data()`: Connect to trading system for P&L calculations  
- `generate_transaction_data()`: Connect to trade database
- `generate_benchmark_data()`: Connect to market data providers

### Configuration
Environment variables and configuration can be managed through:
- `.env` files for API keys and secrets
- `config/` directory for application settings
- Streamlit's secrets management for production deployment

## Development

### Adding New Features
1. Create new widget functions following the existing pattern
2. Add navigation menu items in `create_sidebar()`
3. Implement new data generation/integration functions
4. Update the main layout in the `main()` function

### Testing
```bash
# Run the application locally
poetry run streamlit run app/ksif_dashboard.py

# Access at http://localhost:8501
```

### Deployment
The dashboard can be deployed using:
- **Streamlit Cloud**: Direct deployment from GitHub
- **Docker**: Containerized deployment
- **AWS/Azure/GCP**: Cloud platform deployment

## Contributing

1. Follow the existing code structure and naming conventions
2. Add comments for data integration points
3. Test all interactive elements
4. Update this README for any new features

## License

© 2025 Korea Securities Investment Fund. All rights reserved.
