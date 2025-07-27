"""
Forex lot sizing calculator with risk management
"""

import numpy as np
from currency_data import get_pip_value, get_pair_info

class LotSizeCalculator:
    """
    Forex lot size calculator for risk management
    """
    
    def __init__(self):
        self.lot_sizes = {
            'standard': 100000,
            'mini': 10000,
            'micro': 1000
        }
    
    def calculate_position_size_by_risk_percentage(self, account_balance, risk_percentage, 
                                                 stop_loss_pips, currency_pair):
        """
        Calculate position size based on risk percentage of account balance
        """
        if account_balance <= 0 or risk_percentage <= 0 or stop_loss_pips <= 0:
            return None
            
        # Calculate maximum risk amount in USD
        max_risk_amount = account_balance * (risk_percentage / 100)
        
        return self._calculate_position_size(max_risk_amount, stop_loss_pips, currency_pair)
    
    def calculate_position_size_by_dollar_amount(self, risk_amount, stop_loss_pips, currency_pair):
        """
        Calculate position size based on specific dollar risk amount
        """
        if risk_amount <= 0 or stop_loss_pips <= 0:
            return None
            
        return self._calculate_position_size(risk_amount, stop_loss_pips, currency_pair)
    
    def _calculate_position_size(self, risk_amount, stop_loss_pips, currency_pair):
        """
        Internal method to calculate position size
        """
        pair_info = get_pair_info(currency_pair)
        if not pair_info:
            return None
        
        results = {}
        
        for lot_type in ['standard', 'mini', 'micro']:
            pip_value = get_pip_value(currency_pair, lot_type)
            
            if pip_value is None:
                continue
                
            # Calculate required position size in lots
            position_size_lots = risk_amount / (pip_value * stop_loss_pips)
            
            # Calculate actual risk with this position size
            actual_risk = position_size_lots * pip_value * stop_loss_pips
            
            # Calculate position size in units
            position_size_units = position_size_lots * self.lot_sizes[lot_type]
            
            results[lot_type] = {
                'position_size_lots': round(position_size_lots, 4),
                'position_size_units': round(position_size_units, 0),
                'pip_value': pip_value,
                'actual_risk': round(actual_risk, 2),
                'lot_size_units': self.lot_sizes[lot_type]
            }
        
        return results
    
    def calculate_pip_value_info(self, currency_pair):
        """
        Calculate pip values for all lot types for a given pair
        """
        pair_info = get_pair_info(currency_pair)
        if not pair_info:
            return None
        
        pip_values = {}
        for lot_type in ['standard', 'mini', 'micro']:
            pip_values[lot_type] = {
                'pip_value': get_pip_value(currency_pair, lot_type),
                'lot_size': self.lot_sizes[lot_type],
                'decimals': pair_info['decimals']
            }
        
        return pip_values
    
    def calculate_risk_reward_ratio(self, take_profit_pips, stop_loss_pips):
        """
        Calculate risk-to-reward ratio
        """
        if stop_loss_pips <= 0:
            return None
        return take_profit_pips / stop_loss_pips
    
    def calculate_margin_required(self, lot_size, entry_price, leverage, currency_pair):
        """
        Calculate margin required for a trade
        """
        pair_info = get_pair_info(currency_pair)
        if not pair_info:
            return None
        
        # Standard contract size
        contract_size = 100000
        
        # Calculate notional value
        notional_value = lot_size * contract_size * entry_price
        
        # For USD-based pairs, adjust calculation
        if currency_pair.startswith('USD/'):
            margin = notional_value / leverage
        else:
            # For pairs like EUR/USD, GBP/USD etc.
            margin = (lot_size * contract_size) / leverage
            
        return margin
    
    def calculate_price_levels(self, entry_price, stop_loss_pips, take_profit_pips, 
                             trade_direction, currency_pair):
        """
        Calculate stop loss and take profit price levels
        """
        pair_info = get_pair_info(currency_pair)
        if not pair_info:
            return None
        
        # Calculate pip size based on decimal places
        if pair_info['decimals'] == 2:
            pip_size = 0.01
        else:
            pip_size = 0.0001
        
        if trade_direction.lower() == 'buy':
            sl_price = entry_price - (stop_loss_pips * pip_size)
            tp_price = entry_price + (take_profit_pips * pip_size)
        else:  # sell
            sl_price = entry_price + (stop_loss_pips * pip_size)
            tp_price = entry_price - (take_profit_pips * pip_size)
        
        return {
            'stop_loss_price': round(sl_price, pair_info['decimals']),
            'take_profit_price': round(tp_price, pair_info['decimals'])
        }
    
    def calculate_reward_amount(self, lot_size, take_profit_pips, currency_pair, lot_type='standard'):
        """
        Calculate potential reward amount
        """
        pip_value = get_pip_value(currency_pair, lot_type)
        if pip_value is None:
            return None
            
        return lot_size * pip_value * take_profit_pips
    
    def check_account_health(self, risk_percentage):
        """
        Check if risk percentage is within healthy limits
        """
        if risk_percentage <= 1:
            return {
                'status': 'excellent',
                'message': '✅ Excellent risk management - Very conservative approach',
                'color': 'success'
            }
        elif risk_percentage <= 2:
            return {
                'status': 'good',
                'message': '✅ Good risk management - Balanced approach',
                'color': 'success'
            }
        elif risk_percentage <= 3:
            return {
                'status': 'moderate',
                'message': '⚠️ Moderate risk - Consider reducing position size',
                'color': 'warning'
            }
        elif risk_percentage <= 5:
            return {
                'status': 'high',
                'message': '🚨 High risk - You\'re risking more than recommended!',
                'color': 'error'
            }
        else:
            return {
                'status': 'dangerous',
                'message': '🚨 DANGEROUS - This could wipe out your account quickly!',
                'color': 'error'
            }
    
    def validate_inputs(self, account_balance=None, risk_percentage=None, 
                       risk_amount=None, stop_loss_pips=None, take_profit_pips=None,
                       entry_price=None):
        """
        Validate calculator inputs
        """
        errors = []
        
        if account_balance is not None and account_balance <= 0:
            errors.append("Account balance must be greater than 0")
            
        if risk_percentage is not None and (risk_percentage <= 0 or risk_percentage > 100):
            errors.append("Risk percentage must be between 0 and 100")
            
        if risk_amount is not None and risk_amount <= 0:
            errors.append("Risk amount must be greater than 0")
            
        if stop_loss_pips is not None and stop_loss_pips <= 0:
            errors.append("Stop loss pips must be greater than 0")
            
        if take_profit_pips is not None and take_profit_pips <= 0:
            errors.append("Take profit pips must be greater than 0")
            
        if entry_price is not None and entry_price <= 0:
            errors.append("Entry price must be greater than 0")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, ""