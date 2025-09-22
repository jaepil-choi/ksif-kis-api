# ---
# Purpose: KSIF Dashboard - A comprehensive financial dashboard built with Streamlit
# Contents: Main dashboard with position summary, P&L report, transaction history, and benchmark comparison
# Mod Date: 2025-09-22 - Initial implementation
# ---

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Import data service
from data_service import get_data_service

# Page configuration
st.set_page_config(
    page_title="KSIF Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    /* Main content styling */
    .main > div {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Header styling */
    .main-header {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .dashboard-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        height: 100%;
    }
    
    /* Metric styling */
    .big-metric {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E8B57;
        margin: 0;
    }
    
    .negative-metric {
        color: #D0021B;
    }
    
    .positive-metric {
        color: #7ED321;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #4A90E2;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #2C3E50;
    }
    
    /* Table styling */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Footer styling */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #666;
        text-align: center;
        padding: 10px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation
def create_sidebar():
    with st.sidebar:
        st.markdown("### 🏢 KSIF")
        
        # Initialize session state for page navigation
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "Dashboard"
        
        # Navigation menu
        menu_items = [
            ("🏠", "Dashboard"),
            ("💼", "Positions"),
            ("📋", "Transactions"),
            ("📈", "Reports"),
            ("👥", "Teams"),
            ("⚙️", "Settings")
        ]
        
        st.markdown("---")
        
        for icon, name in menu_items:
            if st.session_state.current_page == name:
                st.markdown(f"**{icon} {name}** ← Current")
            else:
                if st.button(f"{icon} {name}", key=name, width='stretch'):
                    st.session_state.current_page = name
                    st.rerun()
        
        st.markdown("---")
        
        # Additional sidebar info
        st.markdown("### 📊 Quick Stats")
        st.metric("Total Teams", "5")
        st.metric("Active Positions", "12")
        st.metric("Today's Trades", "23")
    
    return st.session_state.current_page

# Header with filters
def create_header():
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns([3, 2, 1.5, 1.5, 1])
    
    with col1:
        st.markdown("# 📊 KSIF Dashboard")
    
    with col2:
        # Date range picker
        default_start = datetime.now() - timedelta(days=30)
        default_end = datetime.now()
        date_range = st.date_input(
            "📅 Date Range",
            value=(default_start, default_end),
            key="date_range"
        )
    
    with col3:
        # Team filter
        teams = ["All Teams", "Team Alpha", "Team Beta", "Team Gamma", "Team Delta"]
        selected_team = st.selectbox("👥 Team", teams, key="team_filter")
    
    with col4:
        # Currency filter
        currencies = ["KRW", "USD", "EUR", "JPY"]
        selected_currency = st.selectbox("💰 Currency", currencies, key="currency_filter")
    
    with col5:
        # Refresh button and status
        st.markdown("##### 🔄 Data")
        
        # Get data service instance
        data_service = get_data_service()
        
        # Manual refresh button
        if st.button("🔄 Refresh", key="manual_refresh", help="Click to refresh all data immediately"):
            # Trigger data refresh
            data_service.refresh_all_data(force=True)
            st.success("Data refreshed!")
            st.rerun()
        
        # Show last update time
        last_update = data_service.get_last_update()
        if last_update:
            st.caption(f"Updated: {last_update.strftime('%H:%M:%S')}")
        else:
            st.caption("Not updated yet")
        
        # Connection status indicator
        if data_service.is_connected():
            st.success("🟢 Connected")
        else:
            st.error("🔴 Disconnected")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return date_range, selected_team, selected_currency

# Data access functions - now using DataService
def get_position_data():
    """Get position data from DataService"""
    data_service = get_data_service()
    df = data_service.get_positions_data()
    
    # Format display columns
    df['Price_Formatted'] = df['Price'].apply(lambda x: f"₩{x:,}")
    df['Market_Value_Formatted'] = df['Market_Value'].apply(lambda x: f"₩{x:,}")
    df['PL_Formatted'] = df['PL'].apply(lambda x: f"₩{x:,}")
    df['PL_Percent_Formatted'] = df['PL_Percent'].apply(lambda x: f"{x:.2f}%")
    
    return df

def get_balance_data():
    """Get balance data from DataService"""
    data_service = get_data_service()
    return data_service.get_balance_data()

def get_pl_data(period="Daily"):
    """Get P&L data from DataService"""
    data_service = get_data_service()
    return data_service.get_pl_data(period)

def get_transaction_data():
    """Get transaction data from DataService"""
    data_service = get_data_service()
    df = data_service.get_transactions_data()
    
    # Format display columns
    df['Price_Formatted'] = df['Price'].apply(lambda x: f"₩{x:,}")
    df['Total_Formatted'] = df['Total'].apply(lambda x: f"₩{x:,}")
    
    return df

def get_benchmark_data():
    """Get benchmark data from DataService"""
    data_service = get_data_service()
    return data_service.get_benchmark_data()

# Widget components
def position_summary_widget():
    """Position Summary Widget - Large card showing current positions"""
    st.markdown("### 💼 Position Summary")
    st.markdown("*Current open positions for All Teams*")
    
    # Get position data from DataService
    df = get_position_data()
    balance_data = get_balance_data()
    
    # Display table
    display_columns = ['Symbol', 'Quantity', 'Price_Formatted', 'Market_Value_Formatted', 'PL_Formatted', 'PL_Percent_Formatted']
    display_df = df[display_columns].copy()
    display_df.columns = ['Symbol', 'Quantity', 'Price', 'Market Value', 'P&L', 'P&L %']
    
    st.dataframe(
        display_df,
        width='stretch',
        hide_index=True,
        column_config={
            "P&L": st.column_config.TextColumn("P&L"),
            "P&L %": st.column_config.TextColumn("P&L %")
        }
    )
    
    # Summary metrics from balance data
    total_market_value = df['Market_Value'].sum()
    total_pl = df['PL'].sum()
    total_pl_percent = (total_pl / (total_market_value - total_pl)) * 100 if total_market_value > total_pl else 0
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        available_cash = balance_data.get('available_cash', 250000000)
        st.metric("💰 Available Cash", f"₩{available_cash:,}")
    
    with col2:
        total_assets = balance_data.get('total_assets', total_market_value + available_cash)
        st.metric("📊 Total Assets", f"₩{total_assets:,}")
    
    # Total row
    st.markdown("**Totals:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Market Value", f"₩{total_market_value:,}")
    with col2:
        st.metric("Total P&L", f"₩{total_pl:,}")
    with col3:
        st.metric("Total P&L %", f"{total_pl_percent:.2f}%")

def pl_report_widget():
    """Profit & Loss Report Widget"""
    st.markdown("### 📈 Profit & Loss Report")
    st.markdown("*P&L analysis for All Teams*")
    
    # Period selection
    periods = ["Daily", "Weekly", "MTD", "YTD"]
    selected_period = st.radio("Period", periods, horizontal=True, key="pl_period")
    
    # Get P&L data from DataService
    pl_data = get_pl_data(selected_period)
    
    # Main P&L figure
    current_pl = pl_data['Daily_PL'].tail(7).sum()  # Last 7 days
    pl_color = "#7ED321" if current_pl >= 0 else "#D0021B"
    
    st.markdown(f'<p style="font-size: 3rem; color: {pl_color}; font-weight: bold; margin: 0;">₩{current_pl:,.0f}</p>', unsafe_allow_html=True)
    st.markdown(f"*Total P&L for the last 7 days*")
    
    # Bar chart
    recent_data = pl_data.tail(7)
    fig = px.bar(
        recent_data, 
        x='Date', 
        y='Daily_PL',
        title="Daily P&L",
        color_discrete_sequence=['#2C3E50']
    )
    fig.update_layout(
        showlegend=False,
        height=300,
        yaxis_title="P&L (KRW)",
        xaxis_title="Date"
    )
    fig.update_traces(hovertemplate='Date: %{x}<br>P&L: ₩%{y:,.0f}<extra></extra>')
    
    st.plotly_chart(fig, width='stretch')

def transaction_history_widget():
    """Transaction History Widget"""
    st.markdown("### 📋 Transaction History")
    st.markdown("*Recent trades for the selected period*")
    
    # Controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("📥 Export", key="export_btn"):
            st.info("Export functionality would be implemented here")
    
    with col2:
        search_term = st.text_input("🔍 Search transactions...", key="search_tx")
    
    with col3:
        tx_types = ["All", "Buy", "Sell"]
        selected_type = st.selectbox("Type", tx_types, key="tx_type_filter")
    
    # Get transaction data from DataService
    df = get_transaction_data()
    
    # Apply filters
    if search_term:
        df = df[df['Symbol'].str.contains(search_term, case=False, na=False)]
    
    if selected_type != "All":
        df = df[df['Type'] == selected_type]
    
    # Group by date and display
    if len(df) == 0:
        st.info("No transactions found matching the current filters.")
        return
    
    for date in df['Date'].unique():
        st.markdown(f"**{date}**")
        date_transactions = df[df['Date'] == date]
        
        for _, tx in date_transactions.iterrows():
            type_color = "#7ED321" if tx['Type'] == "Buy" else "#D0021B"
            
            col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
            
            with col1:
                st.text(f"{tx['TX_ID']}\n{tx['Time']}")
            
            with col2:
                st.text(f"{tx['Symbol']}")
                st.markdown(f'<span style="color: {type_color}; font-weight: bold;">{tx["Type"]}</span>', unsafe_allow_html=True)
            
            with col3:
                st.text(f"Qty: {tx['Quantity']:,}\nPrice: {tx['Price_Formatted']}\nTotal: {tx['Total_Formatted']}")
            
            with col4:
                st.text(tx['Team'])
        
        st.markdown("---")

def benchmark_comparison_widget():
    """Benchmark Comparison Widget"""
    st.markdown("### 📊 Benchmark Comparison")
    st.markdown("*Portfolio performance % vs market indices*")
    
    # Get benchmark data from DataService
    df = get_benchmark_data()
    
    # Legend/Filter checkboxes
    benchmarks = ["Portfolio", "KOSPI", "KOSPI 200", "KOSDAQ", "S&P 500", "DJIA", "USD/KRW"]
    colors = ["#000000", "#8E44AD", "#E91E63", "#2196F3", "#4CAF50", "#FF9800", "#F44336"]
    
    selected_benchmarks = []
    
    cols = st.columns(4)
    for i, (benchmark, color) in enumerate(zip(benchmarks, colors)):
        with cols[i % 4]:
            if st.checkbox(benchmark, value=True, key=f"benchmark_{benchmark}"):
                selected_benchmarks.append(benchmark)
    
    # Line chart
    if selected_benchmarks:
        fig = go.Figure()
        
        for benchmark in selected_benchmarks:
            color = colors[benchmarks.index(benchmark)]
            line_width = 3 if benchmark == "Portfolio" else 2
            
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df[benchmark],
                mode='lines',
                name=benchmark,
                line=dict(color=color, width=line_width),
                hovertemplate=f'{benchmark}: %{{y:.2f}}%<br>Date: %{{x}}<extra></extra>'
            ))
        
        fig.update_layout(
            height=400,
            yaxis_title="Performance %",
            xaxis_title="Date",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Please select at least one benchmark to display")

# Page functions
def dashboard_page():
    """Main dashboard page with position summary and P&L report"""
    st.markdown("# 🏠 Dashboard")
    
    # Main content area - Position Summary and P&L Report only
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Position Summary (spans full height on left)
        with st.container():
            position_summary_widget()
    
    with col2:
        # P&L Report (top right)
        with st.container():
            pl_report_widget()

def positions_page():
    """Positions page - detailed portfolio view"""
    st.markdown("# 💼 Positions")
    st.info("Detailed positions view would be implemented here")
    
    # For now, show the position summary widget
    with st.container():
        position_summary_widget()

def transactions_page():
    """Transactions page with transaction history"""
    st.markdown("# 📋 Transactions")
    
    # Transaction History (moved from dashboard)
    with st.container():
        transaction_history_widget()

def reports_page():
    """Reports page with benchmark comparison and other reports"""
    st.markdown("# 📈 Reports")
    
    # Benchmark Comparison (moved from dashboard)
    with st.container():
        benchmark_comparison_widget()

def teams_page():
    """Teams page"""
    st.markdown("# 👥 Teams")
    st.info("Team management interface would be implemented here")
    
    # Placeholder content
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### Team Alpha")
        st.metric("Members", "5")
        st.metric("Active Positions", "8") 
        st.metric("Total P&L", "₩15,200,000")
    
    with col2:
        st.markdown("### Team Beta")
        st.metric("Members", "4")
        st.metric("Active Positions", "6")
        st.metric("Total P&L", "₩-2,800,000")
    
    with col3:
        st.markdown("### Team Gamma")
        st.metric("Members", "3")
        st.metric("Active Positions", "4")
        st.metric("Total P&L", "₩8,900,000")

def settings_page():
    """Settings page"""
    st.markdown("# ⚙️ Settings")
    st.info("Application settings would be implemented here")
    
    # Placeholder settings
    st.markdown("### User Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.selectbox("Default Currency", ["KRW", "USD", "EUR", "JPY"], key="settings_currency")
        st.selectbox("Default Team", ["All Teams", "Team Alpha", "Team Beta", "Team Gamma"], key="settings_team")
        st.selectbox("Theme", ["Light", "Dark"], key="settings_theme")
    
    with col2:
        st.number_input("Refresh Interval (seconds)", min_value=1, max_value=300, value=30, key="settings_refresh")
        st.checkbox("Enable Notifications", value=True, key="settings_notifications")
        st.checkbox("Show Advanced Features", value=False, key="settings_advanced")

def main():
    """Main application function with page routing"""
    # Create sidebar and get current page
    current_page = create_sidebar()
    
    # Create header with filters (shown on all pages)
    date_range, selected_team, selected_currency = create_header()
    
    # Route to appropriate page based on selection
    if current_page == "Dashboard":
        dashboard_page()
    elif current_page == "Positions":
        positions_page()
    elif current_page == "Transactions":
        transactions_page()
    elif current_page == "Reports":
        reports_page()
    elif current_page == "Teams":
        teams_page()
    elif current_page == "Settings":
        settings_page()
    
    # Footer (shown on all pages)
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>Last updated: September 22nd, 2025 2:18 PM</span>
                <span>KSIF Dashboard v1.0 © 2025 Korea Securities Investment Fund</span>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
