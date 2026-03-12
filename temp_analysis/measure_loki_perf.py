from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import time

module_path = Path(r"C:\Users\pc\.openclaw\workspace\skills\log-inspect\loki_fetcher.py")
spec = spec_from_file_location("loki_fetcher", module_path)
mod = module_from_spec(spec)
spec.loader.exec_module(mod)

q = '{app="winning-winex-ward-akso5-pbc"} |~ "ERROR|WARN"'
g = 'http://127.0.0.1:16291'
d = 2
s = datetime.strptime('2026-03-10 14:00', '%Y-%m-%d %H:%M')
e = datetime.strptime('2026-03-10 15:00', '%Y-%m-%d %H:%M')

tests = [
    ('single_60m', lambda: mod.query_loki(g, d, q, s, e, 5000)),
    ('adaptive_60m', lambda: mod.query_loki_adaptive(g, d, q, s, e, 5000, 1.0)),
    ('single_5m_1455_1500', lambda: mod.query_loki(g, d, q, datetime.strptime('2026-03-10 14:55', '%Y-%m-%d %H:%M'), e, 5000)),
    ('single_1m_1458_1459', lambda: mod.query_loki(g, d, q, datetime.strptime('2026-03-10 14:58', '%Y-%m-%d %H:%M'), datetime.strptime('2026-03-10 14:59', '%Y-%m-%d %H:%M'), 5000)),
]

for name, fn in tests:
    st = time.time()
    lines = fn()
    dt = time.time() - st
    print(f'@@ {name} count={len(lines)} elapsed={dt:.2f}s')
