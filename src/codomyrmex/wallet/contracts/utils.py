"""Blockchain utility functions."""


def wei_to_ether(wei: int) -> float:
    return wei / 10**18


def ether_to_wei(ether: float) -> int:
    return int(ether * 10**18)


def gwei_to_wei(gwei: float) -> int:
    return int(gwei * 10**9)
