\# FPGA Multi-Type Infinite Precision Binary Calculator



A high-performance, arbitrary-precision binary calculator and multi-data-type converter built specifically for FPGA developers, timing analysis, and hardware engineering edge cases.



🚀 \*\*Live Interactive Demo:\*\* https://fpgacalculatormobile.onrender.com/ for mobile

🚀 \*\*Live Interactive Demo:\*\* https://fpgacalculatorapp.streamlit.app/ for PC

\*(Note: Hosted on a cloud free-tier server. Please allow 60–90 seconds for the initial wake-up spin-up on your first click.)\*



\## 🛠️ The Problem It Solves

When working with hardware description languages (Verilog/VHDL), fixed-point math, and complex floating-point boundaries, standard calculators introduce floating-point representation limits. This tool executes its calculations using an underlying binary-based math engine to achieve near-infinite precision, ensuring multi-digit strings stretch flawlessly without clipping boundaries or rounding bits.



\## ✨ Core Engineering Features

\* \*\*Multi-Data-Type Converter:\*\* Seamlessly switch and translate between `REAL`, `HEX`, `BIN`, `FP32` (Single-Precision), and `FP64` (Double-Precision).

\* \*\*Advanced Radix \& Fixed-Point Constraints:\*\* Full support for custom fixed-point parameters including explicit two's complement arithmetic with dynamic binary points.

\* \*\*Responsive Layout:\*\* Tailored with a custom mobile-first viewport design, optimizing string wrapping (`break-all`) to display long, multi-digit binary strings perfectly across smartphone displays.



\## 🧪 Rigorous Verification \& Testing

This software is heavily validated against a hardware-grade automated verification suite to guarantee stability and fault tolerance:

1\. \*\*Walking 1s Testbench:\*\* A 920-iteration walking 1s path validation testing bit-flip propagation, routing leaks, and system boundary edge cases.

2\. \*\*Random Fuzzing Regression Suite:\*\* A 2,000-iteration random permutation engine feeding dynamic format pairs into the ALU framework to challenge mathematical edge cases.

3\. \*\*Monkey Typing / Chaos Fuzzer:\*\* An automated 500-iteration keyboard-smash injection test hitting the interface inputs with random ASCII formatting strings, ensuring \*\*0 unhandled exceptions or system crashes\*\*.



\## 💻 Tech Stack

\* \*\*Language:\*\* Python 3.12

\* \*\*Frontend UI Framework:\*\* NiceGUI / Tailwind CSS

\* \*\*Deployment Platform:\*\* Render (ASGI Web Service / Uvicorn stack)



