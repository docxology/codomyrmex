def main():
    """
    This script demonstrates an intentional failure.
    """
    print("Attempting to process prompt...")
    raise ValueError("Invalid prompt that should fail")


if __name__ == "__main__":
    main()
