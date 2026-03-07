#!/usr/bin/env python3
"""Test all LLM provider connections - No external dependencies"""
import os
import sys
import requests

# Load environment variables from .env file manually
def load_env_file(env_path):
    """Load environment variables from .env file"""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load the .env file
load_env_file(os.path.expanduser('~/.openclaw/.env'))

# Provider configurations
PROVIDERS = {
    'GROQ': {
        'url': 'https://api.groq.com/openai/v1/models',
        'api_key': os.getenv('OPENCLAW_GROQ_API_KEY'),
        'timeout': 10
    },
    'NVIDIA': {
        'url': 'https://integrate.api.nvidia.com/v1/models',
        'api_key': os.getenv('OPENCLAW_NVIDIA_API_KEY'),
        'timeout': 10
    },
    'GEMINI': {
        'url': 'https://generativelanguage.googleapis.com/v1beta/models',
        'api_key': os.getenv('OPENCLAW_GEMINI_API_KEY'),
        'timeout': 10
    },
    'CEREBRAS': {
        'url': 'https://api.cerebras.ai/v1/models',
        'api_key': os.getenv('OPENCLAW_CEREBRAS_API_KEY'),
        'timeout': 10
    },
    'OPENROUTER': {
        'url': 'https://openrouter.ai/api/v1/models',
        'api_key': os.getenv('OPENCLAW_OPENROUTER_API_KEY'),
        'timeout': 10
    },
    'ZAI': {
        'url': 'https://api.z.ai/api/paas/v4/models',
        'api_key': os.getenv('OPENCLAW_ZAI_API_KEY'),
        'timeout': 10
    },
    'CHUTES': {
        'url': 'https://api.chutes.ai/v1/models',
        'api_key': os.getenv('OPENCLAW_CHUTES_API_KEY'),
        'timeout': 10
    }
}

def test_provider(name, config):
    """Test a single provider connection"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{'='*60}")
    
    if not config['api_key']:
        print(f"❌ FAIL: API key not found in environment")
        return False
    
    # Mask the key for display
    key_display = config['api_key'][:8] + '...' + config['api_key'][-4:] if len(config['api_key']) > 12 else '***'
    print(f"API Key: {key_display} [OK]")
    
    try:
        # Special handling for Gemini
        if name == 'GEMINI':
            # Gemini uses a different endpoint format
            url = f"{config['url']}?key={config['api_key']}"
            headers = {}
        else:
            url = config['url']
            headers = {'Authorization': f"Bearer {config['api_key']}"}
        
        response = requests.get(
            url,
            headers=headers,
            timeout=config['timeout']
        )
        
        if response.status_code == 200:
            print(f"✅ SUCCESS: Connection OK (HTTP {response.status_code})")
            data = response.json()
            if 'data' in data:
                print(f"   Models available: {len(data['data'])}")
                if len(data['data']) > 0:
                    print(f"   First model: {data['data'][0].get('id', 'N/A')}")
            return True
        elif response.status_code == 401:
            print(f"❌ FAIL: Invalid API key (HTTP 401)")
            return False
        elif response.status_code == 403:
            print(f"❌ FAIL: Access forbidden (HTTP 403)")
            return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ FAIL: Timeout after {config['timeout']}s")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ FAIL: Connection error - {str(e)[:100]}")
        return False
    except Exception as e:
        print(f"❌ FAIL: {type(e).__name__} - {str(e)[:100]}")
        return False

def main():
    print("="*60)
    print("LLM Provider Connection Test")
    print(f"Testing {len(PROVIDERS)} providers...")
    print("="*60)
    
    results = {}
    
    for provider, config in PROVIDERS.items():
        results[provider] = test_provider(provider, config)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for provider, success in sorted(results.items()):
        status = "✅ OK" if success else "❌ FAIL"
        print(f"{provider:12}: {status}")
    
    # Count successes
    success_count = sum(results.values())
    total = len(results)
    
    print(f"\nTotal: {success_count}/{total} providers working")
    
    if success_count == total:
        print("\n🎉 All providers are operational!")
        return 0
    elif success_count > 0:
        print(f"\n⚠️  {total - success_count} provider(s) failed. Check configuration.")
        return 1
    else:
        print("\n❌ All providers failed!")
        return 2

if __name__ == '__main__':
    sys.exit(main())
