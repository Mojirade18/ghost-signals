// BUG VERSION: identical to the correct ALU except for one character in SUB.
// The borrow flag uses <= instead of <, so it wrongly fires when a equals b.
module alu (
    input  [7:0] a,          // Input pin: first number (8 wires, 0 to 255)
    input  [7:0] b,          // Input pin: second number (8 wires)
    input  [1:0] op,         // Input pin: operation chooser (00=ADD, 01=SUB, 10=AND, 11=OR)
    output reg [7:0] result, // Output pin: the answer (8 wires)
    output reg zero,         // Output pin: 1 if the answer is 0
    output reg carry         // Output pin: overflow or borrow flag
);
    reg [8:0] wide;          // Hidden 9-wire helper so ADD can keep its 9th bit

    always @(*) begin        // Re-run this block whenever any input changes
        carry = 1'b0;        // Start with the flag off
        wide  = 9'd0;        // Start the helper at 0
        case (op)            // Choose a branch based on op
            2'b00: begin     // op = 00 means ADD
                wide   = {1'b0, a} + {1'b0, b}; // Add the two numbers using 9 bits
                result = wide[7:0];             // Keep the lower 8 bits as the answer
                carry  = wide[8];               // The 9th bit tells us if the sum overflowed
            end              // End of ADD
            2'b01: begin     // op = 01 means SUB
                result = a - b;                 // Subtract b from a (wraps around if b is bigger)
                carry  = (a <= b);              // <-- THE BUG: "less than OR EQUAL". Should be (a < b)
            end              // End of SUB
            2'b10: result = a & b;              // op = 10 means AND
            2'b11: result = a | b;              // op = 11 means OR
        endcase              // End of the case choices
        zero = (result == 8'd0); // zero is 1 if the result is 0
    end                      // End of the always block
endmodule                    // End of the module