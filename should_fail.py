def main():
    """
    A simple script that demonstrates a failure condition.
    """
    raise RuntimeError("This is an invalid prompt error intended to fail.")


if __name__ == "__main__":
    main()
