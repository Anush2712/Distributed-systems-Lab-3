"""
Client Service - Supports both basic and resilient modes
"""
import requests
import time
import os
import random
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend-service:8080/api/data')
REQUEST_INTERVAL = int(os.getenv('REQUEST_INTERVAL', '2'))
CLIENT_MODE = os.getenv('CLIENT_MODE', 'resilient')  # 'basic' or 'resilient'

# Circuit Breaker Configuration
CB_FAILURE_THRESHOLD = int(os.getenv('CB_FAILURE_THRESHOLD', '5'))
CB_RECOVERY_TIMEOUT = int(os.getenv('CB_RECOVERY_TIMEOUT', '10'))
RETRY_MAX_ATTEMPTS = int(os.getenv('RETRY_MAX_ATTEMPTS', '3'))

# Simple Circuit Breaker Implementation
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=10):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'
    
    def call(self, func):
        # Check if circuit should move from OPEN to HALF_OPEN
        if self.state == 'OPEN':
            if self.last_failure_time and (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                print("⟳ Circuit HALF_OPEN - testing recovery")
            else:
                raise Exception("Circuit breaker is OPEN - failing fast")
        
        try:
            result = func()
            # Success! Reset circuit breaker
            self.failure_count = 0
            if self.state == 'HALF_OPEN':
                print("✓ Circuit CLOSED - recovery successful")
            self.state = 'CLOSED'
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                if self.state != 'OPEN':
                    self.state = 'OPEN'
                    print(f"⊘ Circuit OPENED after {self.failure_count} failures")
            raise e

# Retry Logic with Exponential Backoff
def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 0.5)  # Exponential backoff + jitter
                print(f"⟳ Timeout - Retry {attempt + 1}/{max_retries} after {delay:.2f}s")
                time.sleep(delay)
            else:
                raise
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                delay = (2 ** attempt) + random.uniform(0, 0.5)
                print(f"⟳ Error - Retry {attempt + 1}/{max_retries} after {delay:.2f}s")
                time.sleep(delay)
            else:
                raise
    raise Exception("Max retries exceeded")

# Initialize circuit breaker
circuit_breaker = CircuitBreaker(
    failure_threshold=CB_FAILURE_THRESHOLD,
    recovery_timeout=CB_RECOVERY_TIMEOUT
)

# Counters
total_requests = 0
successful_requests = 0
failed_requests = 0
circuit_open_count = 0

def call_backend_basic():
    """Basic call without any resilience patterns"""
    response = requests.get(BACKEND_URL, timeout=3)
    if response.status_code >= 500:
        raise Exception(f"Server error: {response.status_code}")
    return response

def call_backend_with_retry():
    """Call with retry logic"""
    return retry_with_backoff(call_backend_basic, max_retries=RETRY_MAX_ATTEMPTS)

def call_backend_resilient():
    """Call with circuit breaker + retry logic"""
    return circuit_breaker.call(lambda: call_backend_with_retry())

def make_request():
    global total_requests, successful_requests, failed_requests, circuit_open_count
    
    total_requests += 1
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    print(f"\n[{timestamp}] Request #{total_requests}")
    
    if CLIENT_MODE == 'resilient':
        print(f"Circuit State: {circuit_breaker.state} | Failures: {circuit_breaker.failure_count}/{CB_FAILURE_THRESHOLD}")
    
    try:
        if CLIENT_MODE == 'resilient':
            response = call_backend_resilient()
        else:
            response = call_backend_basic()
        
        successful_requests += 1
        data = response.json()
        print(f"✓ SUCCESS: {data.get('message', data.get('data', 'OK'))}")
        
    except Exception as e:
        failed_requests += 1
        if 'Circuit breaker is OPEN' in str(e):
            circuit_open_count += 1
            print(f"⊘ CIRCUIT OPEN: Using fallback response")
        else:
            print(f"✗ FAILED: {str(e)}")
    
    # Print statistics
    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
    print(f"📊 Stats: {successful_requests}/{total_requests} successful ({success_rate:.1f}%) | Circuit opened: {circuit_open_count} times")

def main():
    print("=" * 70)
    print(f"CLIENT SERVICE - Mode: {CLIENT_MODE.upper()}")
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Request Interval: {REQUEST_INTERVAL}s")
    if CLIENT_MODE == 'resilient':
        print(f"Circuit Breaker: Threshold={CB_FAILURE_THRESHOLD}, Timeout={CB_RECOVERY_TIMEOUT}s")
        print(f"Retry: Max Attempts={RETRY_MAX_ATTEMPTS}")
    print("=" * 70)
    print("\nStarting requests...\n")
    
    while True:
        make_request()
        time.sleep(REQUEST_INTERVAL)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("SHUTTING DOWN")
        print(f"Final Stats: {successful_requests}/{total_requests} successful")
        print(f"Circuit opened {circuit_open_count} times")
        print("=" * 70)