# currency_data.py

# Currency pair data with pip values and decimal places
CURRENCY_PAIRS = {
    'EUR/USD': {'pip_value_per_standard_lot': 10, 'decimals': 5, 'category': 'Major'},
    'GBP/USD': {'pip_value_per_standard_lot': 10, 'decimals': 5, 'category': 'Major'},
    'USD/JPY': {'pip_value_per_standard_lot': 9.13, 'decimals': 3, 'category': 'Major'},
    'AUD/USD': {'pip_value_per_standard_lot': 10, 'decimals': 5, 'category': 'Major'},
    'USD/CAD': {'pip_value_per_standard_lot': 7.96, 'decimals': 5, 'category': 'Major'},
    'USD/CHF': {'pip_value_per_standard_lot': 10.27, 'decimals': 5, 'category': 'Major'},
    'NZD/USD': {'pip_value_per_standard_lot': 10, 'decimals': 5, 'category': 'Major'},
    'EUR/JPY': {'pip_value_per_standard_lot': 9.13, 'decimals': 3, 'category': 'Cross'},
    'GBP/JPY': {'pip_value_per_standard_lot': 9.13, 'decimals': 3, 'category': 'Cross'},
    'EUR/GBP': {'pip_value_per_standard_lot': 10, 'decimals': 5, 'category': 'Cross'},
    'AUD/JPY': {'pip_value_per_standard_lot': 9.13, 'decimals': 3, 'category': 'Cross'},
    'GBP/CAD': {'pip_value_per_standard_lot': 7.96, 'decimals': 5, 'category': 'Cross'},
    'XAU/USD': {'pip_value_per_standard_lot': 1, 'decimals': 2, 'category': 'Commodity'},
    'XAG/USD': {'pip_value_per_standard_lot': 0.5, 'decimals': 2, 'category': 'Commodity'},
}

def get_currency_pairs_by_category():
    """Return currency pairs grouped by category"""
    categories = {
        'Major': [],
        'Cross': [],
        'Commodity': [],
        'Exotic': []
    }
    
    for pair, info in CURRENCY_PAIRS.items():
        cat = info.get('category')
        if cat in categories:
            categories[cat].append(pair)
    
    return categories

def get_all_pairs():
    """Return all currency pairs as a flat list"""
    return list(CURRENCY_PAIRS.keys())

def get_pair_info(currency_pair):
    """Return full info for a currency pair"""
    return CURRENCY_PAIRS.get(currency_pair)

def get_pip_value(currency_pair, lot_type='standard'):
    """
    Return pip value for given currency pair and lot type
    """
    pair_info = CURRENCY_PAIRS.get(currency_pair)
    if not pair_info:
        return None
    
    pip_value_per_standard = pair_info['pip_value_per_standard_lot']
    
    if lot_type == 'standard':
        return pip_value_per_standard
    elif lot_type == 'mini':
        return pip_value_per_standard / 10
    elif lot_type == 'micro':
        return pip_value_per_standard / 100
    else:
        return None
