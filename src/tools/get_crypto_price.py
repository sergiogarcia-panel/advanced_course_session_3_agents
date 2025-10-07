import requests


def get_crypto_price(symbol: str, currency: str = "usd") -> str:
    """
    Get the current price of any cryptocurrency by symbol.
    
    Args:
        symbol (str): The cryptocurrency symbol (e.g., "bitcoin", "ethereum", "cardano")
        currency (str): The currency to get the price in (default: "usd")
    
    Returns:
        str: The current price in the specified currency,
             or "Error" if the request fails

    Example:
        >>> eth_price = get_crypto_price("ethereum")
        >>> print(f"Ethereum price: ${eth_price}")
        Ethereum price: $2650.75
    """
    try:
        # Using CoinGecko API
        url = f"https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": symbol.lower(),
            "vs_currencies": currency
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        price = data.get(symbol.lower(), {}).get(currency)

        return str(price) if price is not None else f"Error fetching {symbol} price"

    except requests.exceptions.RequestException as e:
        return f"Error fetching {symbol} price: {e}"
        
    except (ValueError, KeyError, TypeError) as e:
        return f"Error parsing {symbol} price data: {e}"


if __name__ == "__main__":
    # Example usage
    print("Getting Bitcoin price...")
    btc_price = get_crypto_price('bitcoin')
    if btc_price:
        print(f"Bitcoin price: ${btc_price} USD")
    else:
        print("Failed to get Bitcoin price")