#!/bin/bash
echo "aioredis python3 one-GET-at-once loop"
time python3 bench_aioredis_get.py
echo "rust python3 one-GET-at-once loop"
time python3 bench_rust_get.py
echo "aioredis python3 one-SET-at-once loop"
time python3 bench_aioredis_single.py
echo "rust python3 one-SET-at-once loop"
time python3 bench_rust_single.py
echo "aioredis python3 1,000,000 SETs in parallel"
time python3 bench_aioredis.py
echo "rust python3 1,000,000 SETs in parallel"
time python3 bench_rust.py
