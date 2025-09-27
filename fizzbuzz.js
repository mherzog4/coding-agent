/**
 * FizzBuzz Implementation
 * 
 * This program prints numbers from 1 to 10, with the following rules:
 * - For multiples of 3, print "Fizz" instead of the number
 * - For multiples of 5, print "Buzz" instead of the number
 * - For multiples of both 3 and 5, print "FizzBuzz" instead of the number
 */

function fizzbuzz() {
    // Loop from 1 to 10
    for (let i = 1; i <= 10; i++) {
        // Variable to hold the output
        let output = '';
        
        // Check if the number is divisible by 3
        if (i % 3 === 0) {
            output += 'Fizz';
        }
        
        // Check if the number is divisible by 5
        if (i % 5 === 0) {
            output += 'Buzz';
        }
        
        // If output is still empty, use the number
        if (output === '') {
            output = i;
        }
        
        // Print the result to the console
        console.log(output);
    }
}

// Execute the fizzbuzz function
console.log("Starting FizzBuzz:");
fizzbuzz();
console.log("FizzBuzz completed!");