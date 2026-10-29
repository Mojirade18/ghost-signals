`timescale 1ns/1ps          // Sets the time units: 1 time unit = 1 nanosecond, precision = 1 picosecond

module alu_tb;              // The testbench module. It has no pins because it is the outermost layer
    reg  [7:0] a, b;        // Variables we control, to feed into the ALU's a and b pins
    reg  [1:0] op;          // Variable we control, to feed into the op pin
    wire [7:0] result;      // A wire that carries the ALU's answer out so we can read it
    wire zero, carry;       // Wires that carry the ALU's two flags out

    // Place one ALU inside the testbench and name it "dut" (Device Under Test).
    // ".a(a)" means: connect the ALU's pin "a" to our variable "a". Same for the others.
    alu dut (.a(a), .b(b), .op(op), .result(result), .zero(zero), .carry(carry));

    integer pass_count, fail_count; // Two counters (whole numbers) to track how many tests pass and fail

    // A "task" is a reusable routine. Each time we call check, it runs one test.
    task check;
        input [127:0] id;   // The test name. 128 bits = 16 characters (each character uses 8 bits)
        input [1:0]   t_op; // Which operation to test
        input [7:0]   t_a;  // The first number to feed in
        input [7:0]   t_b;  // The second number to feed in
        input [7:0]   exp_result; // The result we EXPECT (worked out by hand)
        input         exp_zero;   // The zero flag we EXPECT
        input         exp_carry;  // The carry flag we EXPECT
        begin               // Start of the task's steps
            a = t_a; b = t_b; op = t_op; // Feed the test inputs into the ALU
            #10;            // Wait 10 time units so the ALU has time to settle on its answer
            // "===" is an exact comparison. Do all three outputs match what we expected?
            if (result === exp_result && zero === exp_zero && carry === exp_carry) begin
                pass_count = pass_count + 1; // Yes: add 1 to the pass counter
                // Print one line starting with PASS. %0s prints text, %0d prints a number.
                // The values after the quotes fill in the %0s and %0d slots in order.
                $display("TEST|%0s|PASS|op=%0d|a=%0d|b=%0d|exp_result=%0d|act_result=%0d|exp_zero=%0d|act_zero=%0d|exp_carry=%0d|act_carry=%0d",
                    id, t_op, t_a, t_b, exp_result, result, exp_zero, zero, exp_carry, carry);
            end else begin  // Otherwise, something did not match
                fail_count = fail_count + 1; // Add 1 to the fail counter
                // Print the same kind of line, but marked FAIL, showing expected vs actual ("act")
                $display("TEST|%0s|FAIL|op=%0d|a=%0d|b=%0d|exp_result=%0d|act_result=%0d|exp_zero=%0d|act_zero=%0d|exp_carry=%0d|act_carry=%0d",
                    id, t_op, t_a, t_b, exp_result, result, exp_zero, zero, exp_carry, carry);
            end             // End of the if/else
        end                 // End of the task's steps
    endtask                 // End of the task

    // An "initial" block runs once, at the start of the simulation. This is our test script.
    initial begin
        pass_count = 0; fail_count = 0; // Start both counters at zero

        // Each line below is one test: name, operation, a, b, expected result, expected zero, expected carry.
        check("ADD_BASIC",    2'd0, 8'd5,   8'd3,   8'd8,   1'b0, 1'b0); // 5 + 3 = 8, no carry
        check("ADD_ZERO",     2'd0, 8'd0,   8'd0,   8'd0,   1'b1, 1'b0); // 0 + 0 = 0, so zero flag is 1
        check("ADD_OVERFLOW", 2'd0, 8'd200, 8'd100, 8'd44,  1'b0, 1'b1); // 300 does not fit in 8 bits: wraps to 44, carry = 1
        check("SUB_BASIC",    2'd1, 8'd10,  8'd3,   8'd7,   1'b0, 1'b0); // 10 - 3 = 7, no borrow
        check("SUB_EQUAL",    2'd1, 8'd7,   8'd7,   8'd0,   1'b1, 1'b0); // 7 - 7 = 0, zero = 1, and NO borrow (this exposes the bug)
        check("SUB_BORROW",   2'd1, 8'd3,   8'd5,   8'd254, 1'b0, 1'b1); // 3 - 5 wraps to 254, borrow = 1
        check("AND_BASIC",    2'd2, 8'd12,  8'd10,  8'd8,   1'b0, 1'b0); // 1100 AND 1010 = 1000 (8)
        check("OR_BASIC",     2'd3, 8'd12,  8'd10,  8'd14,  1'b0, 1'b0); // 1100 OR 1010 = 1110 (14)

        // Print a final summary line with the total, passed, and failed counts
        $display("SUMMARY|total=%0d|passed=%0d|failed=%0d", pass_count + fail_count, pass_count, fail_count);
        $finish;            // Tell the simulator to stop
    end                     // End of the initial block
endmodule                   // End of the testbench module