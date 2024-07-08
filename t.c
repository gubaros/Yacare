#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 10

void shuffleArray(int arr[], int size) {
    for (int i = size - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}

int main() {
    int numbers[SIZE];
    srand(time(NULL));
    
    for (int i = 0; i < SIZE; i++) {
        numbers[i] = i + 1;
    }
    
    shuffleArray(numbers, SIZE);
    
    printf("Shuffled numbers: ");
    for (int i = 0; i < SIZE; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\n");
    
    return 0;
}
