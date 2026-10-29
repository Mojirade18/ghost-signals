// An "ALU" (Arithmetic Logic Unit) is the part of a processor that does maths.
// A "module" is a Verilog building block, like a chip with pins.
module alu (
    input  [7:0] a,          // Input pin: first number. [7:0] means 8 wires, so values 0 to 255
    input  [7:0] b,          // Input pin: second number, also 8 wires
    input  [1:0] op,         // Input pin: chooses the operation. 2 wires = 4 choices (00, 01, 10, 11)
    output reg [7:0] result, // Output pin: the answer. "reg" means it is assigned inside an always block
    output reg zero,         // Output pin: 1 wire, becomes 1 if the answer is 0
    output reg carry         // Output pin: 1 wire, a warning flag (overflow for ADD, borrow for SUB)
);
    reg [8:0] wide;          // A hidden helper with 9 wires, so an addition can keep its 9th bit

    always @(*) begin        // "Run this block again whenever any input changes". No clock needed
        carry = 1'b0;        // Start with carry turned off. 1'b0 means "1 bit, value 0"
        wide  = 9'd0;        // Start the helper at 0. 9'd0 means "9 bits, decimal value 0"
        case (op)            // Look at op and pick the matching branch below
            2'b00: begin     // If op is 00, do ADD
                wide   = {1'b0, a} + {1'b0, b}; // Put a 0 in front of each number (making 9 bits), then add
                result = wide[7:0];             // The answer is the lower 8 bits of the sum
                carry  = wide[8];               // The 9th bit is the carry: 1 if the sum was above 255
            end              // End of the ADD branch
            2'b01: begin     // If op is 01, do SUB
                result = a - b;                 // Subtract. If b is bigger, the result wraps around (3 - 5 = 254)
                carry  = (a < b);               // Carry (borrow) is 1 only if a is strictly smaller than b
            end              // End of the SUB branch
            2'b10: result = a & b;              // If op is 10, AND: each bit is 1 only if both bits are 1
            2'b11: result = a | b;              // If op is 11, OR: each bit is 1 if either bit is 1
        endcase              // End of the case choices
        zero = (result == 8'd0); // zero becomes 1 if the result equals 0, otherwise 0
    end                      // End of the always block
endmodule                    // End of the ALU module