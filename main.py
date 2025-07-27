"""
Streamlit Forex Lot Sizing Calculator
A professional tool for calculating forex position sizes with risk management
"""

import streamlit as st
import pandas as pd
import numpy as np
from lot_calculator import LotSizeCalculator
from currency_data import get_currency_pairs_by_category, get_all_pairs, get_pair_info

# Page configuration
st.set_page_config(
    page_title="Forex Lot Size Calculator",
    page_icon="💱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize calculator
calculator = LotSizeCalculator()

def main():
    """
    Main application function
    """
    # Header
    st.title("💱 Forex Lot Size Calculator")
    st.markdown("**Professional position sizing tool with risk management for all currency pairs and gold**")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📊 Trading Parameters")
        
        # Currency pair selection
        st.subheader("Currency Pair")
        
        # Group pairs by category for better organization
        categories = get_currency_pairs_by_category()
        
        # Create a selectbox with organized options
        all_pairs = []
        for category in ['Major', 'Cross', 'Commodity', 'Exotic']:
            if category in categories:
                all_pairs.extend(categories[category])
        
        selected_pair = st.selectbox(
            "Select Currency Pair",
            options=all_pairs,
            index=0,
            help="Choose the currency pair you want to trade"
        )
        
        # Display pair category
        pair_info = get_pair_info(selected_pair)
        if pair_info:
            st.info(f"**Category:** {pair_info['category']} | **Decimals:** {pair_info['decimals']}")
        
        st.divider()
        
        # Risk calculation method
        st.subheader("Risk Calculation Method")
        calc_method = st.radio(
            "Choose calculation method:",
            ["Percentage of Account", "Fixed Dollar Amount"],
            help="Select how you want to calculate your risk"
        )
        
        # Account and risk inputs
        if calc_method == "Percentage of Account":
            account_balance = st.number_input(
                "Account Balance ($)",
                min_value=1.0,
                value=10000.0,
                step=100.0,
                help="Your total trading account balance in USD"
            )
            
            risk_percentage = st.number_input(
                "Risk Percentage (%)",
                min_value=0.1,
                max_value=100.0,
                value=2.0,
                step=0.1,
                help="Percentage of account balance you're willing to risk per trade"
            )
            
            risk_amount = account_balance * (risk_percentage / 100)
            st.metric("Calculated Risk Amount", f"${risk_amount:,.2f}")
            
        else:
            risk_amount = st.number_input(
                "Risk Amount ($)",
                min_value=1.0,
                value=200.0,
                step=10.0,
                help="Fixed dollar amount you're willing to risk on this trade"
            )
            account_balance = None
            risk_percentage = None
        
        # Stop loss input
        stop_loss_pips = st.number_input(
            "Stop Loss (pips)",
            min_value=0.1,
            value=20.0,
            step=0.1,
            help="Distance to your stop loss in pips"
        )
        
        st.divider()
        
        # Additional trading parameters
        st.subheader("📈 Trade Setup")
        
        # Take profit input
        take_profit_pips = st.number_input(
            "Take Profit (pips)",
            min_value=0.1,
            value=40.0,
            step=0.1,
            help="Distance to your take profit in pips"
        )
        
        # Entry price input
        default_price = 1.0000
        if selected_pair == 'EUR/USD':
            default_price = 1.10000
        elif selected_pair == 'XAU/USD':
            default_price = 1800.0
        elif selected_pair and selected_pair.startswith('USD/JPY'):
            default_price = 110.0
            
        entry_price = st.number_input(
            "Entry Price",
            min_value=0.00001,
            value=default_price,
            step=0.00001,
            format="%.5f",
            help="Your intended entry price for the trade"
        )
        
        # Trade direction
        trade_direction = st.radio(
            "Trade Direction:",
            ["Buy", "Sell"],
            help="Are you buying or selling the currency pair?"
        )
        
        # Leverage selection
        leverage = st.selectbox(
            "Account Leverage",
            [30, 50, 100, 200, 500],
            index=2,
            help="Your broker's leverage ratio"
        )
        
        # Calculate button
        calculate_button = st.button("📈 Calculate Position Size", type="primary")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if calculate_button:
            # Validate inputs
            is_valid, error_msg = calculator.validate_inputs(
                account_balance=account_balance,
                risk_percentage=risk_percentage,
                risk_amount=risk_amount,
                stop_loss_pips=stop_loss_pips,
                take_profit_pips=take_profit_pips,
                entry_price=entry_price
            )
            
            if not is_valid:
                st.error(f"❌ Input Error: {error_msg}")
                return
            
            # Account Health Check
            if calc_method == "Percentage of Account":
                health_check = calculator.check_account_health(risk_percentage)
                if health_check['color'] == 'success':
                    st.success(health_check['message'])
                elif health_check['color'] == 'warning':
                    st.warning(health_check['message'])
                else:
                    st.error(health_check['message'])
            
            # Calculate Risk-to-Reward Ratio
            rrr = calculator.calculate_risk_reward_ratio(take_profit_pips, stop_loss_pips)
            if rrr:
                st.subheader("⚖️ Risk-to-Reward Analysis")
                col_rrr1, col_rrr2, col_rrr3 = st.columns(3)
                
                with col_rrr1:
                    st.metric("Risk-to-Reward Ratio", f"1:{rrr:.2f}")
                
                with col_rrr2:
                    if rrr >= 2.0:
                        st.success("✅ Excellent RRR")
                    elif rrr >= 1.5:
                        st.info("✅ Good RRR")
                    elif rrr >= 1.0:
                        st.warning("⚠️ Acceptable RRR")
                    else:
                        st.error("❌ Poor RRR")
                
                with col_rrr3:
                    if rrr < 1.5:
                        st.warning("Consider increasing TP or reducing SL")
            
            # Calculate position sizes
            if calc_method == "Percentage of Account":
                results = calculator.calculate_position_size_by_risk_percentage(
                    account_balance, risk_percentage, stop_loss_pips, selected_pair
                )
            else:
                results = calculator.calculate_position_size_by_dollar_amount(
                    risk_amount, stop_loss_pips, selected_pair
                )
            
            if results is None:
                st.error("❌ Unable to calculate position size. Please check your inputs.")
                return
            
            # Display results
            st.subheader("📊 Position Size Results")
            
            # Create results table
            results_data = []
            for lot_type, data in results.items():
                results_data.append({
                    'Lot Type': lot_type.title(),
                    'Position Size (Lots)': f"{data['position_size_lots']:.4f}",
                    'Position Size (Units)': f"{data['position_size_units']:,.0f}",
                    'Pip Value': f"${data['pip_value']:.2f}",
                    'Risk Amount': f"${data['actual_risk']:.2f}"
                })
            
            df_results = pd.DataFrame(results_data)
            st.dataframe(df_results, use_container_width=True, hide_index=True)
            
            # Key metrics
            st.subheader("🎯 Key Metrics")
            
            col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
            
            with col_metrics1:
                st.metric(
                    "Recommended Standard Lots",
                    f"{results['standard']['position_size_lots']:.4f}",
                    help="Position size in standard lots (100,000 units each)"
                )
            
            with col_metrics2:
                st.metric(
                    "Total Risk",
                    f"${results['standard']['actual_risk']:.2f}",
                    help="Actual dollar amount at risk with this position"
                )
            
            with col_metrics3:
                if calc_method == "Percentage of Account":
                    risk_ratio = (results['standard']['actual_risk'] / account_balance) * 100
                    st.metric(
                        "Risk Ratio",
                        f"{risk_ratio:.2f}%",
                        help="Percentage of account balance at risk"
                    )
                else:
                    st.metric(
                        "Pip Value (Standard)",
                        f"${results['standard']['pip_value']:.2f}",
                        help="Value of one pip for a standard lot"
                    )
            
            # Risk management insights
            st.subheader("💡 Risk Management Insights")
            
            if calc_method == "Percentage of Account":
                if risk_percentage <= 1:
                    st.success("✅ Conservative risk level - Good for long-term capital preservation")
                elif risk_percentage <= 2:
                    st.info("ℹ️ Moderate risk level - Balanced approach for steady growth")
                elif risk_percentage <= 3:
                    st.warning("⚠️ Aggressive risk level - Higher potential returns but increased risk")
                else:
                    st.error("🚨 Very high risk level - Consider reducing position size")
            
            # Calculate price levels
            price_levels = calculator.calculate_price_levels(
                entry_price, stop_loss_pips, take_profit_pips, 
                trade_direction.lower(), selected_pair
            )
            
            # Calculate margin required
            standard_lot_size = results['standard']['position_size_lots']
            margin_required = calculator.calculate_margin_required(
                standard_lot_size, entry_price, leverage, selected_pair
            )
            
            # Calculate reward amount
            reward_amount = calculator.calculate_reward_amount(
                standard_lot_size, take_profit_pips, selected_pair, 'standard'
            )
            
            # Trade Summary Box
            st.subheader("📋 Trade Summary")
            if price_levels and margin_required and reward_amount:
                st.info(f"""
                **Trade Details:**
                • **Pair:** {selected_pair} ({trade_direction.upper()})
                • **Entry Price:** {entry_price:.5f}
                • **Stop Loss Price:** {price_levels['stop_loss_price']:.5f}
                • **Take Profit Price:** {price_levels['take_profit_price']:.5f}
                
                **Position Details:**
                • **Position Size:** {standard_lot_size:.4f} standard lots
                • **Risk Amount:** ${risk_amount:.2f}
                • **Reward Amount:** ${reward_amount:.2f}
                • **Risk-to-Reward:** 1:{rrr:.2f}
                
                **Account Impact:**
                • **Margin Required:** ${margin_required:.2f}
                • **Leverage Used:** 1:{leverage}
                """)
            
            # Margin and Account Info
            if margin_required:
                st.subheader("💰 Margin & Account Information")
                
                col_margin1, col_margin2, col_margin3 = st.columns(3)
                
                with col_margin1:
                    st.metric(
                        "Margin Required",
                        f"${margin_required:.2f}",
                        help="Amount of money locked as margin for this trade"
                    )
                
                with col_margin2:
                    if calc_method == "Percentage of Account" and account_balance:
                        free_margin_after = account_balance - margin_required
                        st.metric(
                            "Free Margin After Trade",
                            f"${free_margin_after:.2f}",
                            help="Available margin after opening this position"
                        )
                    else:
                        st.metric(
                            "Leverage Ratio",
                            f"1:{leverage}",
                            help="Your account leverage setting"
                        )
                
                with col_margin3:
                    if account_balance and account_balance > 0:
                        margin_percentage = (margin_required / account_balance) * 100
                        st.metric(
                            "Margin Usage",
                            f"{margin_percentage:.1f}%",
                            help="Percentage of account used as margin"
                        )
                        
                        if margin_percentage > 50:
                            st.error("⚠️ High margin usage - be careful!")
                        elif margin_percentage > 30:
                            st.warning("⚠️ Moderate margin usage")
            
            # Position size recommendations
            st.info(
                f"""
                **Position Size Recommendations for {selected_pair}:**
                
                • **Conservative traders:** Use micro lots ({results['micro']['position_size_lots']:.2f} lots)
                • **Moderate traders:** Use mini lots ({results['mini']['position_size_lots']:.2f} lots)  
                • **Experienced traders:** Use standard lots ({results['standard']['position_size_lots']:.4f} lots)
                
                **Stop Loss:** {stop_loss_pips} pips | **Risk Amount:** ${risk_amount:.2f}
                """
            )
    
    with col2:
        # Pip value information
        st.subheader("📈 Pip Value Information")
        
        pip_info = calculator.calculate_pip_value_info(selected_pair)
        if pip_info:
            pip_data = []
            for lot_type, data in pip_info.items():
                pip_data.append({
                    'Lot Type': lot_type.title(),
                    'Lot Size': f"{data['lot_size']:,} units",
                    'Pip Value': f"${data['pip_value']:.2f}"
                })
            
            df_pip = pd.DataFrame(pip_data)
            st.dataframe(df_pip, use_container_width=True, hide_index=True)
        
        # Trading tips
        st.subheader("💭 Trading Tips")
        st.markdown("""
        **Risk Management Best Practices:**
        
        • Never risk more than 1-2% per trade
        • Use appropriate stop losses
        • Consider market volatility
        • Account for spread costs
        • Practice proper money management
        
        **Position Sizing Guidelines:**
        
        • **Micro Lots:** Beginners, small accounts
        • **Mini Lots:** Intermediate traders
        • **Standard Lots:** Experienced traders
        
        **Important Notes:**
        
        • Calculations assume USD account currency
        • Pip values may vary with market conditions
        • Always verify with your broker
        • Consider slippage and spreads
        """)
        
        # Market hours info
        st.subheader("🕐 Market Information")
        if selected_pair == 'XAU/USD':
            st.info("""
            **Gold (XAU/USD) Trading:**
            • 24-hour trading Sunday-Friday
            • High volatility during economic news
            • Popular safe-haven asset
            • Consider wider stop losses
            """)
        else:
            st.info("""
            **Forex Market Hours:**
            • 24 hours, 5 days a week
            • Most active: London & NY overlap
            • Lower spreads during major sessions
            • Avoid trading during low liquidity
            """)

if __name__ == "__main__":
    main()