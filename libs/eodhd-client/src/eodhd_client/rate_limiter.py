from datetime import datetime, timedelta
import time


class RateLimiter:
    """
    A simple rate limiter to control the frequency of API requests based on cost.
    """

    def __init__(self, limit: int, period_seconds: int):
        """
        Initializes the rate limiter.

        Args:
            limit (int): The maximum allowed total cost within the period.
            period_seconds (int): The duration of the rate limiting window in seconds.
        """
        if limit <= 0 or period_seconds <= 0:
            raise ValueError("limit and period_seconds must be positive integers.")

        self.limit = limit
        self.period_seconds = period_seconds
        # Stores tuples of (timestamp, cost)
        self.request_costs = []

    def _clean_old_requests(self):
        """
        Removes recorded requests that are outside the current rate limiting window.
        """
        now = datetime.now()
        self.request_costs = [
            (ts, cost)
            for ts, cost in self.request_costs
            if now - ts < timedelta(seconds=self.period_seconds)
        ]

    def wait_for_next_request(self, cost: int = 1):
        """
        Wait until enough 'cost' is available to perform the next request.

        Args:
            cost (int): The cost of the upcoming API request. Defaults to 1.
        """
        if cost <= 0:
            raise ValueError("Request cost must be a positive integer.")

        self._clean_old_requests()

        current_cost_sum = sum(c for _, c in self.request_costs)

        if (current_cost_sum + cost) > self.limit:
            # Calculate how long to wait until enough cost expires
            wait_seconds = 0
            temp_cost_sum = current_cost_sum

            # Find the earliest point in time where enough cost would have expired
            # to allow the new request.
            for _, (ts, c) in enumerate(self.request_costs):
                if (temp_cost_sum + cost) <= self.limit:
                    break
                temp_cost_sum -= c
                time_to_wait = (
                    ts + timedelta(seconds=self.period_seconds)
                ) - datetime.now()
                if time_to_wait.total_seconds() > wait_seconds:
                    wait_seconds = time_to_wait.total_seconds()

            if wait_seconds > 0:
                time.sleep(wait_seconds)

            # After waiting, clean again and re-check
            self._clean_old_requests()
            current_cost_sum = sum(c for _, c in self.request_costs)

            # If still over limit after waiting, it means the period has passed, but we might have
            # accumulated requests. This simple rate limiter will just wait for the next slot.
            if (current_cost_sum + cost) > self.limit:
                time.sleep(1)  # Fallback sleep

        self.request_costs.append((datetime.now(), cost))


class CompositeRateLimiter:
    """
    A composite rate limiter that combines multiple RateLimiter instances.
    It ensures that all configured rate limits are respected.
    """

    def __init__(self, limiters: list[RateLimiter]):
        """
        Initializes the composite rate limiter.

        Args:
            limiters (list[RateLimiter]): A list of RateLimiter instances to coordinate.
        """
        if not limiters:
            raise ValueError("At least one RateLimiter must be provided.")
        self.limiters = limiters

    def wait_for_next_request(self, cost: int = 1):
        """
        Blocks until all underlying rate limiters allow the next request.

        Args:
            cost (int): The cost of the upcoming API request. Defaults to 1.
        """
        for limiter in self.limiters:
            limiter.wait_for_next_request(cost=cost)
