# ---
# Purpose: KIS Data Service - Manages persistent PyKis connection and data fetching
# Contents: DataService class for API management, caching, and real-time updates
# Mod Date: 2025-09-22 - Initial implementation
# ---

import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd
from pathlib import Path
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from pykis import PyKis, KisAuth, KisStock, KisBalance, KisQuote, KisChart, KisOrderbook
    from pykis import KisRealtimePrice, KisSubscriptionEventArgs, KisWebsocketClient
    PYKIS_AVAILABLE = True
except ImportError:
    logger.warning("PyKis not available - using mock data only")
    PYKIS_AVAILABLE = False

class DataService:
    """
    Persistent data service that manages KIS API connections and provides cached data
    """
    
    def __init__(self, secret_path: str = "secret1.json", virtual_secret_path: str = None):
        self.secret_path = secret_path
        self.virtual_secret_path = virtual_secret_path
        self._kis: Optional[Any] = None
        self._is_connected = False
        self._last_update = None
        self._update_interval = 120  # seconds - increased to avoid API rate limits
        self._auto_refresh_enabled = True
        self._update_thread = None
        self._shutdown_event = threading.Event()
        
        # Data cache
        self._cached_data = {
            'positions': None,
            'balance': None,
            'quotes': {},
            'transactions': None,
            'pl_data': None,
            'benchmark_data': None
        }
        
        # Initialize connection
        self.initialize_connection()
        
        # Start auto-refresh thread
        self.start_auto_refresh()
    
    def initialize_connection(self) -> bool:
        """Initialize PyKis connection with persistent token management"""
        try:
            if not PYKIS_AVAILABLE:
                logger.info("PyKis not available - running in mock mode")
                self._is_connected = False
                return False
            
            # Check if secret files exist
            if not Path(self.secret_path).exists():
                logger.error(f"Secret file not found: {self.secret_path}")
                self._is_connected = False
                return False
            
            # Initialize PyKis with token persistence (using actual API from demo.ipynb)
            # Real-world example: kis = PyKis(KisAuth.load("secret1.json"), keep_token=True)
            auth = KisAuth.load(self.secret_path)
            
            # For now, only use real authentication to avoid virtual trading setup issues
            # Virtual trading can be added later if needed
            self._kis = PyKis(auth, keep_token=True)
            logger.info("Initialized PyKis with real authentication only")
            
            # Test connection by getting account balance
            account = self._kis.account()
            balance = account.balance()
            
            self._is_connected = True
            logger.info(f"KIS API connection established successfully for account: {account.account_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize KIS connection: {e}")
            self._is_connected = False
            return False
    
    def is_connected(self) -> bool:
        """Check if KIS API is connected"""
        return self._is_connected
    
    def get_last_update(self) -> Optional[datetime]:
        """Get last update timestamp"""
        return self._last_update
    
    def start_auto_refresh(self):
        """Start background thread for auto-refreshing data"""
        if self._update_thread is None or not self._update_thread.is_alive():
            self._shutdown_event.clear()
            self._update_thread = threading.Thread(target=self._auto_refresh_worker, daemon=True)
            self._update_thread.start()
            logger.info("Auto-refresh thread started")
    
    def stop_auto_refresh(self):
        """Stop auto-refresh thread"""
        if self._update_thread and self._update_thread.is_alive():
            self._shutdown_event.set()
            self._update_thread.join(timeout=5)
            logger.info("Auto-refresh thread stopped")
    
    def _auto_refresh_worker(self):
        """Background worker for automatic data refresh"""
        while not self._shutdown_event.is_set():
            try:
                if self._auto_refresh_enabled:
                    self.refresh_all_data()
                
                # Wait for next update or shutdown signal
                if self._shutdown_event.wait(timeout=self._update_interval):
                    break  # Shutdown requested
                    
            except Exception as e:
                logger.error(f"Error in auto-refresh worker: {e}")
                # Wait a bit before retrying
                if self._shutdown_event.wait(timeout=30):
                    break
    
    def refresh_all_data(self, force: bool = False):
        """Refresh all cached data from KIS API"""
        try:
            # Skip if recently updated (unless forced) - avoid API rate limits
            if not force and self._last_update and datetime.now() - self._last_update < timedelta(seconds=60):
                return
            
            logger.info("Refreshing all data from KIS API...")
            
            if self._is_connected and self._kis:
                # Refresh positions and balance
                self._refresh_positions_and_balance()
                
                # Refresh stock quotes for held positions  
                self._refresh_stock_quotes()
                
                # Refresh transaction history
                self._refresh_transactions()
                
                # Refresh P&L data
                self._refresh_pl_data()
            
            # Always refresh benchmark data (from external sources)
            self._refresh_benchmark_data()
            
            self._last_update = datetime.now()
            logger.info(f"Data refresh completed at {self._last_update}")
            
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            # Try to reconnect if connection lost
            if "token" in str(e).lower() or "auth" in str(e).lower():
                logger.info("Token issue detected, attempting to reconnect...")
                self.initialize_connection()
    
    def _refresh_positions_and_balance(self):
        """Refresh positions and balance data using actual PyKis API"""
        if not self._kis:
            return
            
        try:
            account = self._kis.account()
            balance = account.balance()  # Returns KisIntegrationBalance
            
            # Convert positions to DataFrame format expected by dashboard
            positions_data = []
            
            for stock in balance.stocks:  # List of KisDomesticBalanceStock
                # Get stock info to get readable name using actual symbol code from API
                stock_symbol_code = stock.symbol  # This is the 6-digit code like '005930', '079160'
                try:
                    stock_obj = self._kis.stock(stock_symbol_code)
                    # Get the actual stock name (e.g., "삼성전자" for "005930")
                    stock_name = stock_obj.info.name if hasattr(stock_obj.info, 'name') else stock_symbol_code
                except Exception as stock_error:
                    logger.warning(f"Could not get name for stock {stock_symbol_code}: {stock_error}")
                    stock_name = stock_symbol_code
                
                positions_data.append({
                    "Symbol": stock_name,
                    "Quantity": float(stock.qty),
                    "Price": float(stock.price),
                    "Market_Value": float(stock.amount),
                    "PL": float(stock.profit),
                    "PL_Percent": float(stock.profit_rate)
                })
            
            self._cached_data['positions'] = pd.DataFrame(positions_data)
            
            # Extract balance information (based on actual demo.ipynb API structure)
            krw_deposit = balance.deposits.get('KRW')
            available_cash = float(krw_deposit.amount) if krw_deposit else 0.0
            
            self._cached_data['balance'] = {
                'available_cash': available_cash,
                'total_assets': float(balance.current_amount) + available_cash,
                'total_pl': float(balance.profit),
                'total_pl_percent': float(balance.profit_rate)
            }
            
            logger.info(f"Updated positions data: {len(positions_data)} positions")
            logger.info(f"Available cash: ₩{available_cash:,.0f}")
            logger.info(f"Total assets: ₩{float(balance.current_amount) + available_cash:,.0f}")
            logger.info(f"Total P&L: ₩{float(balance.profit):,.0f} ({float(balance.profit_rate):.2f}%)")
            
        except Exception as e:
            logger.error(f"Error refreshing positions and balance: {e}")
            # Clear cached data on error so we don't serve stale data
            self._cached_data['positions'] = None
            self._cached_data['balance'] = None
    
    def _refresh_stock_quotes(self):
        """Refresh stock quotes for monitoring using actual PyKis API"""
        if not self._kis or 'positions' not in self._cached_data or self._cached_data['positions'] is None:
            return
            
        try:
            # Get quotes for held positions
            # Note: We need to use the actual symbol codes, not the names
            account = self._kis.account()
            balance = account.balance()
            
            for stock_position in balance.stocks:
                symbol = stock_position.symbol  # Use actual symbol code
                try:
                    stock = self._kis.stock(symbol)
                    quote = stock.quote()  # Returns KisQuote object
                    
                    self._cached_data['quotes'][symbol] = {
                        'price': float(quote.price),
                        'change': float(quote.change),
                        'rate': float(quote.rate),
                        'volume': int(quote.volume),
                        'market_cap': float(quote.market_cap) if hasattr(quote, 'market_cap') else 0.0,
                        'timestamp': datetime.now()
                    }
                    
                except Exception as e:
                    logger.warning(f"Could not fetch quote for {symbol}: {e}")
            
            logger.info(f"Updated quotes for {len(self._cached_data['quotes'])} symbols")
            
        except Exception as e:
            logger.error(f"Error refreshing quotes: {e}")
    
    def _refresh_transactions(self):
        """Refresh transaction history using actual PyKis API"""
        if not self._kis:
            return
            
        try:
            account = self._kis.account()
            # Get recent daily orders (last 7 days) - based on demo.ipynb API
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
            
            daily_orders = account.daily_orders(start=start_date, end=end_date)
            
            transactions_data = []
            
            # Process each order from the actual API response
            for order in daily_orders.orders:
                try:
                    # Extract order information based on actual API structure
                    symbol_code = order.order_number.code if hasattr(order, 'order_number') and hasattr(order.order_number, 'code') else 'Unknown'
                    order_number = order.order_number.number if hasattr(order, 'order_number') and hasattr(order.order_number, 'number') else '000000'
                    
                    # Get stock name for display
                    try:
                        stock = self._kis.stock(symbol_code)
                        symbol_name = stock.info.name if hasattr(stock.info, 'name') else symbol_code
                    except Exception as stock_error:
                        logger.debug(f"Could not get name for stock {symbol_code}: {stock_error}")
                        symbol_name = symbol_code
                    
                    # Extract transaction details from actual API response structure
                    order_type = order.type.title() if hasattr(order, 'type') else 'Unknown'
                    executed_qty = int(order.executed_qty) if hasattr(order, 'executed_qty') else 0
                    price = float(order.price) if hasattr(order, 'price') else 0.0
                    
                    # Only include orders with actual executions
                    if executed_qty > 0:
                        # Use actual timestamp if available, otherwise current time
                        if hasattr(order, 'time_kst') and order.time_kst:
                            transaction_date = order.time_kst
                        else:
                            transaction_date = datetime.now()
                        
                        transactions_data.append({
                            "Date": transaction_date.strftime("%Y.%m.%d"),
                            "Time": transaction_date.strftime("%H:%M"),
                            "TX_ID": f"TX{order_number}",
                            "Symbol": symbol_name,
                            "Type": order_type,
                            "Quantity": executed_qty,
                            "Price": price,
                            "Total": price * executed_qty,
                            "Team": "Team Alpha"  # TODO: Map to actual team from account or order data
                        })
                    
                except Exception as order_error:
                    logger.warning(f"Error processing order {getattr(order, 'order_number', 'Unknown')}: {order_error}")
                    continue
            
            self._cached_data['transactions'] = pd.DataFrame(transactions_data)
            logger.info(f"Updated {len(transactions_data)} transactions for date range {start_date} to {end_date}")
            
        except Exception as e:
            logger.error(f"Error refreshing transactions: {e}")
            # Clear cached data on error
            self._cached_data['transactions'] = None
    
    def _refresh_pl_data(self):
        """Refresh P&L data using actual PyKis API"""
        if not self._kis:
            return
            
        try:
            account = self._kis.account()
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
            
            # Get profit data - based on demo.ipynb API
            profits = account.profits(start=start_date)  # Returns KisIntegrationOrderProfits
            
            # Convert to time series data based on actual realized profits
            pl_data = []
            current_date = start_date
            cumulative_pl = 0
            
            # If there are actual realized profits, use them
            if profits.orders and len(profits.orders) > 0:
                while current_date <= end_date:
                    daily_pl = 0
                    
                    # Calculate daily P&L from actual realized profits
                    for order in profits.orders:
                        try:
                            if hasattr(order, 'time_kst') and order.time_kst:
                                order_date = order.time_kst.date()
                                if order_date == current_date:
                                    daily_pl += float(order.profit) if hasattr(order, 'profit') else 0.0
                        except Exception as order_error:
                            logger.debug(f"Error processing P&L order: {order_error}")
                            continue
                    
                    cumulative_pl += daily_pl
                    pl_data.append({
                        'Date': pd.to_datetime(current_date),
                        'Daily_PL': daily_pl,
                        'PL': cumulative_pl
                    })
                    current_date += timedelta(days=1)
                    
                logger.info(f"Updated P&L data from realized profits: {len(pl_data)} days, total realized profit: ₩{profits.profit:,.0f}")
                
            else:
                # No realized profits yet - create P&L based on unrealized gains from current balance
                try:
                    balance = account.balance()
                    total_unrealized_pl = float(balance.profit)  # Current unrealized P&L
                    
                    # Distribute the unrealized P&L across the time period
                    # This gives a view of how the portfolio has performed
                    for i in range(30):
                        # Simple linear distribution - in reality this would need historical data
                        daily_unrealized_change = total_unrealized_pl / 30
                        
                        pl_data.append({
                            'Date': pd.to_datetime(current_date + timedelta(days=i)),
                            'Daily_PL': daily_unrealized_change,
                            'PL': daily_unrealized_change * (i + 1)
                        })
                    
                    logger.info(f"Updated P&L data from unrealized gains: 30 days, current unrealized P&L: ₩{total_unrealized_pl:,.0f}")
                    
                except Exception as balance_error:
                    logger.error(f"Could not get balance for P&L calculation: {balance_error}")
                    # Create empty P&L data
                    for i in range(30):
                        pl_data.append({
                            'Date': pd.to_datetime(current_date + timedelta(days=i)),
                            'Daily_PL': 0.0,
                            'PL': 0.0
                        })
            
            self._cached_data['pl_data'] = pd.DataFrame(pl_data)
            
        except Exception as e:
            logger.error(f"Error refreshing P&L data: {e}")
            # Clear cached data on error
            self._cached_data['pl_data'] = None
    
    def _refresh_benchmark_data(self):
        """Refresh benchmark comparison data (mock for now)"""
        # TODO: Integrate with actual market data providers (Yahoo Finance, etc.)
        try:
            days = 30
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            
            # Mock benchmark data - replace with real market data API
            import numpy as np
            np.random.seed(int(time.time()) % 1000)  # Semi-random but stable for short periods
            
            benchmarks = {
                "Portfolio": np.cumsum(np.random.normal(0.2, 1.2, days)),
                "KOSPI": np.cumsum(np.random.normal(0.1, 1.0, days)),
                "KOSPI 200": np.cumsum(np.random.normal(0.08, 0.9, days)),
                "KOSDAQ": np.cumsum(np.random.normal(0.3, 1.5, days)),
                "S&P 500": np.cumsum(np.random.normal(0.15, 0.8, days)),
                "DJIA": np.cumsum(np.random.normal(0.12, 0.7, days)),
                "USD/KRW": np.cumsum(np.random.normal(-0.05, 0.3, days))
            }
            
            df = pd.DataFrame(benchmarks)
            df['Date'] = dates
            self._cached_data['benchmark_data'] = df
            
        except Exception as e:
            logger.error(f"Error refreshing benchmark data: {e}")
    
    # Data getter methods
    def get_positions_data(self) -> pd.DataFrame:
        """Get cached positions data"""
        if self._cached_data['positions'] is not None and len(self._cached_data['positions']) > 0:
            return self._cached_data['positions'].copy()
        
        # If no cached data and not connected, try to refresh once
        if not self._is_connected or self._cached_data['positions'] is None:
            logger.info("No cached positions data, attempting to refresh...")
            self.refresh_all_data(force=True)
            
        # Return cached data if available after refresh, otherwise empty DataFrame
        if self._cached_data['positions'] is not None:
            return self._cached_data['positions'].copy()
        else:
            # Return empty DataFrame with correct structure
            return pd.DataFrame(columns=['Symbol', 'Quantity', 'Price', 'Market_Value', 'PL', 'PL_Percent'])
    
    def get_balance_data(self) -> Dict[str, Any]:
        """Get cached balance data"""
        if self._cached_data['balance'] is not None:
            return self._cached_data['balance'].copy()
        
        # If no cached data, try to refresh once
        if not self._is_connected or self._cached_data['balance'] is None:
            logger.info("No cached balance data, attempting to refresh...")
            self.refresh_all_data(force=True)
            
        # Return cached data if available after refresh, otherwise defaults
        if self._cached_data['balance'] is not None:
            return self._cached_data['balance'].copy()
        else:
            return {
                'available_cash': 0.0,
                'total_assets': 0.0,
                'total_pl': 0.0,
                'total_pl_percent': 0.0
            }
    
    def get_pl_data(self, period: str = "Daily") -> pd.DataFrame:
        """Get cached P&L data"""
        if self._cached_data['pl_data'] is not None and len(self._cached_data['pl_data']) > 0:
            return self._cached_data['pl_data'].copy()
        
        # If no cached data, try to refresh once
        if not self._is_connected or self._cached_data['pl_data'] is None:
            logger.info("No cached P&L data, attempting to refresh...")
            self.refresh_all_data(force=True)
            
        # Return cached data if available after refresh, otherwise create basic structure
        if self._cached_data['pl_data'] is not None and len(self._cached_data['pl_data']) > 0:
            return self._cached_data['pl_data'].copy()
        else:
            # Create minimal P&L data structure
            days = 7 if period == "Daily" else (30 if period == "MTD" else 365)
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            return pd.DataFrame({
                'Date': dates,
                'Daily_PL': [0.0] * days,
                'PL': [0.0] * days
            })
    
    def get_transactions_data(self) -> pd.DataFrame:
        """Get cached transactions data"""
        if self._cached_data['transactions'] is not None and len(self._cached_data['transactions']) > 0:
            return self._cached_data['transactions'].copy()
        
        # If no cached data, try to refresh once
        if not self._is_connected or self._cached_data['transactions'] is None:
            logger.info("No cached transactions data, attempting to refresh...")
            self.refresh_all_data(force=True)
            
        # Return cached data if available after refresh, otherwise empty DataFrame
        if self._cached_data['transactions'] is not None:
            return self._cached_data['transactions'].copy()
        else:
            return pd.DataFrame(columns=['Date', 'Time', 'TX_ID', 'Symbol', 'Type', 'Quantity', 'Price', 'Total', 'Team'])
    
    def get_benchmark_data(self) -> pd.DataFrame:
        """Get cached benchmark data"""
        if self._cached_data['benchmark_data'] is not None:
            return self._cached_data['benchmark_data'].copy()
        
        # Refresh benchmark data if not available
        self._refresh_benchmark_data()
        
        if self._cached_data['benchmark_data'] is not None:
            return self._cached_data['benchmark_data'].copy()
        else:
            # Return minimal benchmark structure
            days = 30
            dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
            return pd.DataFrame({
                'Date': dates,
                'Portfolio': [0.0] * days,
                'KOSPI': [0.0] * days,
                'KOSPI 200': [0.0] * days,
                'KOSDAQ': [0.0] * days,
                'S&P 500': [0.0] * days,
                'DJIA': [0.0] * days,
                'USD/KRW': [0.0] * days
            })
    
    
    def __del__(self):
        """Cleanup when service is destroyed"""
        self.stop_auto_refresh()


# Global data service instance
_data_service_instance = None

def get_data_service() -> DataService:
    """Get singleton DataService instance"""
    global _data_service_instance
    if _data_service_instance is None:
        _data_service_instance = DataService()
    return _data_service_instance
