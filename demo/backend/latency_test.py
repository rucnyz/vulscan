# -*- coding: utf-8 -*-
# @Time    : 4/1/2025 11:26 AM
# @Author  : yuzhounie
# @File    : latency_test.py
# @Software: PyCharm

import asyncio
import json
import time
import statistics
from pathlib import Path
import argparse
import os
import random
import httpx

from vulscan.test.test_utils.utils import load_reasoning_data
from vulscan.utils.project_info import PROJECT_PATH
from vulscan.utils.sys_prompts import our_cot, policy
from vulscan.utils.cwes import remove_idx


async def test_endpoint_latency(client, code, num_requests=10):
    """Test the latency of the analysis endpoint."""
    latencies = []

    for _ in range(num_requests):
        start_time = time.time()
        try:
            response = await client.post(
                "http://localhost:4400/analyze", json={"code": code}
            )
            response.raise_for_status()
            result = response.json()
            end_time = time.time()
            latency = end_time - start_time
            latencies.append(latency)
            print(f"Request completed in {latency:.4f} seconds")
        except Exception as e:
            print(f"Request failed: {e}")

    return latencies


async def run_latency_test(examples, num_samples=10, requests_per_sample=5):
    """Run latency tests on a subset of examples."""
    # Randomly select samples
    if len(examples) > num_samples:
        test_samples = random.sample(examples, num_samples)
    else:
        test_samples = examples

    all_latencies = []

    async with httpx.AsyncClient(timeout=600.0) as client:  # 10-minute timeout
        for i, sample in enumerate(test_samples):
            print(f"\nTesting sample {i+1}/{len(test_samples)}")
            code = sample["code"]
            print(f"Code length: {len(code)} characters")

            # Test the endpoint latency
            latencies = await test_endpoint_latency(client, code, requests_per_sample)
            all_latencies.extend(latencies)

            # Print statistics for this sample
            if latencies:
                avg = statistics.mean(latencies)
                med = statistics.median(latencies)
                min_lat = min(latencies)
                max_lat = max(latencies)
                print(
                    f"Sample stats - Avg: {avg:.4f}s, Median: {med:.4f}s, Min: {min_lat:.4f}s, Max: {max_lat:.4f}s"
                )

    return all_latencies


def set_args():
    parser = argparse.ArgumentParser(description="Test API latency")
    parser.add_argument("--dataset_path", type=str, nargs="+", required=True)
    parser.add_argument("--language", type=str, required=True, nargs="+")
    parser.add_argument(
        "--num_samples", type=int, default=10, help="Number of code samples to test"
    )
    parser.add_argument(
        "--requests_per_sample",
        type=int,
        default=5,
        help="Number of requests per code sample",
    )
    parser.add_argument("--use_policy", action="store_true", default=False)
    parser.add_argument("--random_cwe", action="store_true", default=False)
    parser.add_argument("--output_file", type=str, default="latency_results.json")
    return parser.parse_args()


if __name__ == "__main__":
    args = set_args()

    # Convert dataset paths to resolved Path objects
    args.dataset_path = [
        Path(dataset_path).resolve() for dataset_path in args.dataset_path
    ]

    # Set current working directory
    os.chdir(PROJECT_PATH)

    all_examples = []
    for dataset_path in args.dataset_path:
        for language in args.language:
            if not os.path.exists(os.path.join(dataset_path, language)):
                continue

            # Load data using the same method as test.py
            ood_dict = {language: []}
            eval_examples, _, _ = load_reasoning_data(
                dataset_path,
                "/dev/null",
                ood_dict,
                "latency_test",
                policy if args.use_policy else "",
                our_cot,
                False,
                skip_human=False,
                random_cwe=args.random_cwe,
                reduced=False,
                addition_constraint=False,
            )

            # Filter out examples with IDs in remove_idx
            eval_examples = [
                item for item in eval_examples if str(item["idx"]) not in remove_idx
            ]
            all_examples.extend(eval_examples)

    print(f"Loaded {len(all_examples)} examples")

    # Run the latency test
    latencies = asyncio.run(
        run_latency_test(
            all_examples,
            num_samples=args.num_samples,
            requests_per_sample=args.requests_per_sample,
        )
    )

    # Calculate statistics
    if latencies:
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        stddev_latency = statistics.stdev(latencies) if len(latencies) > 1 else 0

        print("\nOverall Latency Statistics:")
        print(f"Average: {avg_latency:.4f} seconds")
        print(f"Median: {median_latency:.4f} seconds")
        print(f"Min: {min_latency:.4f} seconds")
        print(f"Max: {max_latency:.4f} seconds")
        print(f"Standard Deviation: {stddev_latency:.4f} seconds")
        print(f"Total requests: {len(latencies)}")

        # Save results to file
        results = {
            "latencies": latencies,
            "stats": {
                "average": avg_latency,
                "median": median_latency,
                "min": min_latency,
                "max": max_latency,
                "stddev": stddev_latency,
                "total_requests": len(latencies),
            },
            "test_config": {
                "dataset_paths": [str(path) for path in args.dataset_path],
                "language": args.language,
                "num_samples": args.num_samples,
                "requests_per_sample": args.requests_per_sample,
                "use_policy": args.use_policy,
                "random_cwe": args.random_cwe,
            },
        }

        with open(args.output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output_file}")
    else:
        print("No successful requests to calculate statistics")
