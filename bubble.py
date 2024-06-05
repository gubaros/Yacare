def bubble_sort(arr):
    n = len(arr)
    # Traverse through all array elements
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n-i-1):
            # Traverse the array from 0 to n-i-1
            # Swap if the element found is greater than the next element
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

def main():
    import random
    import time

    # Generate a list of random integers
    arr = [random.randint(0, 1000) for _ in range(1000)]
    print("Unsorted array:", arr)

    # Record the start time
    start_time = time.time()

    # Sort the array using bubble sort
    bubble_sort(arr)

    # Record the end time
    end_time = time.time()

    # Print the sorted array
    print("Sorted array:", arr)
    print(f"Time taken to sort: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()

