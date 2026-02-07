
try:
    from codomyrmex.data_visualization import create_bar_chart
    print(f"create_bar_chart is: {create_bar_chart}")
    if create_bar_chart is None:
        print("create_bar_chart is None")
    else:
        test_data = {
            "categories": ["A", "B"],
            "values": [10, 20]
        }
        try:
            result = create_bar_chart(test_data, "Test Chart")
            print("Success")
        except Exception as e:
            print(f"Error calling create_bar_chart: {e}")
            import traceback
            traceback.print_exc()

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"General Error: {e}")
