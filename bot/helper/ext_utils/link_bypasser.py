"""
Link Bypasser Module
Bypass various link shorteners and return original URLs
"""

from urllib.parse import urlparse
from ... import LOGGER

# List of known shortener domains
SHORTENER_DOMAINS = [
    'droplink.co', 'ads.droplink.co.in',
    'tnlink.in', 'link.tnlink.in',
    'ez4short.com', 'xpshort.com', 'vearnl.in',
    'rocklinks.net', 'rocklink.in', 'go.rocklinks.net',
    'earn4link.in', 'tekcrypt.in', 'link.short2url.in',
    'linkvertise.com', 'link-center.net', 'link-target.net',
    'ouo.io', 'ouo.press',
    'adf.ly', 'bit.ly', 'tinyurl.com', 'thinfi.com',
    'shareus.in', 'shortly.xyz', 'hypershort.com',
    'safeurl.sirigan.my.id', 'gtlinks.me', 'loan.kinemaster.cc',
    'theforyou.in', 'shorte.st',
    'earn.moneykamalo.com', 'm.easysky.in', 'indianshortner.in',
    'open.crazyblog.in', 'link.tnvalue.in', 'shortingly.me',
    'open2get.in', 'dulink.in', 'bindaaslinks.com', 'za.uy',
    'pdiskshortener.com', 'mdiskshortner.link', 'go.earnl.xyz',
    'g.rewayatcafe.com', 'ser2.crazyblog.in', 'bitshorten.com',
    'adrinolinks.in', 'techymozo.com', 'linkbnao.com',
    'linksxyz.in', 'short-jambo.com', 'linkpays.in',
    'pi-l.ink', 'pkin.me', 'try2link.com'
]

# Mapping of domains to PyBypass name parameter
DOMAIN_NAME_MAP = {
    'link-center.net': 'linkvertise',
    'link-target.net': 'linkvertise',
    'ads.droplink.co.in': 'droplink',
    'link.tnlink.in': 'tnlink',
    'go.rocklinks.net': 'rocklinks',
}


def is_shortener_link(url: str) -> bool:
    """
    Check if URL is a known shortener link.
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if URL is a shortener, False otherwise
    """
    try:
        domain = urlparse(url).netloc.lower()
        # Remove www. prefix if present
        domain = domain.replace('www.', '')
        return any(shortener in domain for shortener in SHORTENER_DOMAINS)
    except Exception as e:
        LOGGER.error(f"Error checking shortener link: {e}")
        return False


def get_bypass_name(url: str) -> str:
    """
    Get the name parameter for PyBypass based on URL domain.
    
    Args:
        url: URL to get name for
        
    Returns:
        str: Name parameter for PyBypass, or empty string for auto-detect
    """
    try:
        domain = urlparse(url).netloc.lower()
        domain = domain.replace('www.', '')
        
        # Check if domain needs specific name parameter
        for key, value in DOMAIN_NAME_MAP.items():
            if key in domain:
                return value
        
        # Return empty string for auto-detect
        return ""
    except Exception as e:
        LOGGER.error(f"Error getting bypass name: {e}")
        return ""


async def bypass_link(url: str) -> dict:
    """
    Bypass link shortener and return original URL.
    
    Args:
        url: Shortened URL to bypass
        
    Returns:
        dict: {
            'success': bool,
            'original_url': str (if success),
            'error': str (if failed)
        }
    """
    if not url or not isinstance(url, str):
        return {
            'success': False,
            'error': 'Invalid URL provided'
        }
    
    # Check if it's a known shortener
    if not is_shortener_link(url):
        return {
            'success': False,
            'error': 'URL is not a recognized shortener link'
        }
    
    try:
        LOGGER.info(f"Attempting to bypass: {url}")
        
        # Import PyBypass here to avoid import errors if not installed
        try:
            import PyBypass
        except ImportError:
            LOGGER.error("PyBypass library not installed")
            return {
                'success': False,
                'error': 'PyBypass library not installed. Please install it using: pip install PyBypass'
            }
        
        # Get name parameter for specific domains
        name = get_bypass_name(url)
        
        # Try to bypass using PyBypass
        if name:
            LOGGER.info(f"Using PyBypass with name parameter: {name}")
            result = PyBypass.bypass(url, name=name)
        else:
            LOGGER.info("Using PyBypass with auto-detect")
            result = PyBypass.bypass(url)
        
        # Check if bypass was successful
        if result and result != url:
            LOGGER.info(f"Bypass successful: {url} -> {result}")
            return {
                'success': True,
                'original_url': result
            }
        else:
            LOGGER.warning(f"PyBypass returned same URL or empty result")
            return {
                'success': False,
                'error': 'Bypass failed: PyBypass returned same URL or empty result'
            }
            
    except Exception as e:
        error_msg = str(e)
        LOGGER.error(f"Bypass failed for {url}: {error_msg}")
        
        # Provide more specific error messages
        if 'timeout' in error_msg.lower():
            error_msg = 'Request timeout. The shortener site may be down or slow.'
        elif 'connection' in error_msg.lower():
            error_msg = 'Connection error. Please check your internet connection.'
        elif 'not supported' in error_msg.lower():
            error_msg = 'This shortener is not supported by PyBypass.'
        
        return {
            'success': False,
            'error': f'Bypass failed: {error_msg}'
        }


async def get_supported_shorteners() -> str:
    """
    Get list of supported shortener domains.
    
    Returns:
        str: Formatted string of supported shorteners
    """
    shorteners_list = sorted(set(SHORTENER_DOMAINS))
    
    # Group shorteners by category
    categories = {
        'Droplink': [s for s in shorteners_list if 'droplink' in s],
        'Rocklinks': [s for s in shorteners_list if 'rocklink' in s],
        'TNLink': [s for s in shorteners_list if 'tnlink' in s],
        'Linkvertise': [s for s in shorteners_list if 'linkvertise' in s or 'link-' in s],
        'OUO': [s for s in shorteners_list if 'ouo' in s],
        'Others': []
    }
    
    # Add remaining to Others
    categorized = set()
    for cat_list in categories.values():
        categorized.update(cat_list)
    
    categories['Others'] = [s for s in shorteners_list if s not in categorized]
    
    # Format output
    output = "📋 <b>Supported Shorteners:</b>\n\n"
    
    for category, domains in categories.items():
        if domains:
            output += f"<b>{category}:</b>\n"
            for domain in domains:
                output += f"  • {domain}\n"
            output += "\n"
    
    output += f"<b>Total:</b> {len(shorteners_list)} shorteners supported"
    
    return output

