#!/usr/bin/env python3
"""
1부터 100까지의 숫자 중 소수(Prime Number)를 판별하고
소수의 목록과 총 개수를 출력하는 스크립트입니다.
"""

from typing import List


def is_prime(n: int) -> bool:
    """주어진 정수 n이 소수인지 판별합니다."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    # 6k ± 1 최적화 알고리즘
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def find_primes_in_range(start: int, end: int) -> List[int]:
    """지정된 범위 [start, end] 내의 소수 목록을 반환합니다."""
    return [num for num in range(start, end + 1) if is_prime(num)]


def main() -> None:
    start_num = 1
    end_num = 100

    primes = find_primes_in_range(start_num, end_num)

    print(f"[{start_num}부터 {end_num}까지의 소수 탐색 결과]")
    print(f"- 소수 개수: {len(primes)}개")
    print(f"- 소수 목록: {primes}")


if __name__ == "__main__":
    main()
