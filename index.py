def print_even_numbers(numbers):
    for num in numbers:
        if num % 2 == 0:
            print(num)

sample_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print_even_numbers(sample_list)