from datetime import datetime, timedelta
from deskhive_core.booking import compute_price

start = datetime(2030, 1, 15, 10)
print(f"2.5 hours at EUR 12/hour: EUR {compute_price('12', start, start + timedelta(hours=2.5))}")
