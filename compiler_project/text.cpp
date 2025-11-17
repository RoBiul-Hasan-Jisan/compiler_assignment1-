// This is a single-line comment
/* This is a
   multi-line comment */

// Test 1: Comments and preprocessor some  issue like define max 10
#include <stdio.h>
constexpr int MAX = 10;
#ifdef DEBUG
#include "stl_library.py"
#include <vector>

// Test 2: Strings and characters  next line issue 
string a = "Hello, World!";
string b = "Line1\\nLine2";
string c = "Quotes: \\"C++\\"";
char ch1 = 'a';
char ch2 = '\\n';
char ch3 = '\\';

// Test 3: Numbers and types issue as real complier -5.5 allow akloge  hare not and int frac ar  por vlaue count not allow  but hare allow 
int a = 4;
int b = 4.4;
float f = -5.5;
int hex = 0x1A3F;

// Test 4: Keywords and operators  all okk
if (a >= 5 && flag) {
    a++;
    b += 2.0;
}

int* ptr = nullptr;
x <<= 2;
y >>= 3;

if (a == b && c != d) {
    x <= 10 || y >= 5;
}

// Test 5: Func m r all ok if mother func work some case i will  try divided rule jodi combo na chai than i can do del combo func  both are okk test okk
void solve() {
    printf("Solving problem...\\n");
}

int add(int a, int b) {
    return a + b;
}

float calculateAverage(int arr[], int size) {
    float sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum / size;
}

int main() {
    printf("Hello, EDU!");
    return 0;
}