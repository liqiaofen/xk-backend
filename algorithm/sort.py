def select_sort(arr):
    # 选择排序
    length = len(arr)
    for i in range(length - 1):
        min_index = i
        for j in range(i + 1, length):
            if arr[j] < arr[min_index]:
                min_index = j
        arr[min_index], arr[i] = arr[i], arr[min_index]
    return arr


def quick_sort(arr):
    if len(arr) <= 1:  # edge case
        return arr

    pivot = arr[len(arr) // 2]  # it actually doesn't matter, you can define any element in the array as pivot
    print(pivot)
    left_bucket = [x for x in arr if x < pivot]  # push all element less than pivot to left bucket
    middle = [x for x in arr if x == pivot]  # middle is also a list
    right_bucket = [x for x in arr if x > pivot]  # push all element greater than pivot to left bucket

    return quick_sort(left_bucket) + middle + quick_sort(
        right_bucket)  # apply quick sort to left and right bucket recursively


if __name__ == '__main__':
    # arr = [11, 99, 33, 69, 77, 88, 55, 11, 33, 36, 39, 66, 44, 22]
    # print(select_sort(arr))
    arr = [54, 26, 93, 17, 77, 31, 44, 55, 20]
    quick_sort(arr)
