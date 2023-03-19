Title: Reading from binary files: Zig vs Python
Description: Ah, another Sunday afternoon coding session. Sitting in a cafe in the heart of downtown Toronto, it's time to get to work writing code for my new favourite language: Zig.
Date: 2023-03-13

Ah, another Sunday afternoon coding session. Sitting in a cafe in the heart of downtown Toronto, it's time to get to work writing code for my new favourite language: Zig.

I've been looking into writing my own deep learning inference implementation in the language. When learning a new programming language, it's best to do something that you find interesting and challenges you.

For me, I cannot be bothered to write tic-tac-toe or some other tutorial based learning for the nth time. Yet, this often results in me doing things that are outside my peak level of learning. I am learning how to do something I don't know how to do in a language I don't know how to use.

Running machine learning models involves loading weights and other hyper-parameters into memory, typically at the programs start. These values were set during training, using back-propagation, when optimizing a specific loss or objective function. They're typically 32-bit floating point numbers, and for large models they take up a lot of space.

I had wrote a simple python script to pull the weights from torch and pack them into a binary file where one weight succeeds another. If you know the location of the start of the series of weights, then this method minimizes the file space taken.

### Reading into a buffer

#### Python

When reading a binary file in Python, you can simply do the following:

    :::python3
    # Open a binary file in read-only mode 
    with open('file.bin', 'rb') as file:
        contents = file.read()

This does a lot of the heavy lifting for you. When you read the file, Python allocates the size of the file into memory. This is inefficient for large files, as allocating all that memory can take time, and there may not be enough memory to read the entire file.

Instead, we can read into a buffer. The buffer can be considered a window into the entire file. (And if you're familiar with NN, consider it like a CNN with stride = width.) We read chunks at a time.

    :::python3
    # Open a binary file in read-only mode 
    with open('file.bin', 'rb') as file: 
        # Create a bytes object with a pre-allocated buffer of 10 bytes 
        buffer = bytearray(10) 
        # Read up to 10 bytes from the file into the buffer 
        num_bytes_read = file.readinto(buffer)

We can then use the [struct unpack function](https://docs.python.org/3/library/struct.html) in Python to convert our byte array object into a Python float.

#### Zig

The same operation in Zig similar, but Zig makes you explicitly allocate and free the memory.

    :::zig
    // Import the standard library
    const std = @import("std");

    pub fn main() !void {
        // Allocate a fixed amount of data. We're doing 4 KB. 
        // We use u8 because 1 byte = 8 bits.
        var data: [4096]u8 = undefined;
        // Initialize with a FixedBufferAllocator
        var fba = std.head.FixedBufferAllocator.init(&data);
        // Take the allocator pointer so we can allocate some data
        var allocator = &fba.allocator();
        // At the end of this method, free the buffer
        defer allocator.free(data);

        // Allocate our 2KB buffer using our fixed amount
        var memory = try allocator.alloc(2048);
        defer allocator.free(memory);

        // Open the file from the current working directory
        var file = std.fs.cwd().openFile("file.bin", .{ .mode = .read_only});
        defer file.close();

        // Read into the buffer. Stops at file end or when buffer is full.
        // Amount of bytes read is returned.
        var read_bytes = file.readAll(memory);

        // Read the 32-bit floats into an ArrayList. Allocate the ArrayList
        // memory using page allocation. This calls the OS to create 
        // new memory pages when required. This is slower than a 
        // fixed buffer allocated at the beginning of the program. Assume we 
        // know there are 800 32-bit float weights.
        var weights = 
            try std.ArrayList(f32).initCapacity(std.heap.page_allocator, 800);

        while (true) {
            // Provide a slice (like a pointer, setting values to 32-bit float)
            const slice = std.mem.bytesAsSlice(f32, memory[..read_bytes]);
            // Copy the floats from the buffer to the weights ArrayList.
            // Align the slice to 4 bytes (since f32 is 4 bytes each)
            weights.appendSliceAssumeCapacity(@alignCast(4, slice));
            read_bytes = file.readAll(memory);
            if (read_bytes == 0) {
                break;
            }
        }

        // Do something with the allocated weights!

    }

Yeah, that is a bit more complicated... Although we have more control.

First, we get to choose how and when our bytes are allocated. Any operation that allocates memory to the heap in Zig requires to specify an allocator. This way we can be more conscious about the speed of allocating memory. Making OS calls to allocate a page is more expensive than using an already allocated fixed buffer. When you're first starting out, I would recommend to use the page allocator. It's easier, and you can always refactor later!

Second, Zig is typed, although it has type inference at compile time. So we need to be explicit about types. 

Third, notice that we allocated bytes of memory (u8), but want to read 4 bytes at a time (f32). Fortunately, slices come to the rescue. This was the most challenging part for me to figure out as a newcomer to the language.

In Zig, not all pointers are created equal. If you have a pointer to a float, you have to explicitly cast it to another pointer value if you want to do those operations on it using [ptrCast()](https://ziglang.org/documentation/0.10.1/#ptrCast). Yet, this operation is unsafe. There are typically better methods.

This is where [`std.mem.bytesAsSlice`](https://ziglang.org/documentation/master/std/#A;std:mem.bytesAsSlice) comes in. We can confidently cast our byte array to the type we want. I can then append a whole slice to a ArrayList (which dynamically resizes the underlying array structure) in one operation. One last thing I have to worry about is alignment.

Alignment is the amount of bytes a data structure takes. An 8 bit value, u8, is naturally 1 byte aligned, but f32 is aligned to 4 bytes. Therefore, I need to cast the u8 aligned structure to 4 bytes in order to append to our ArrayList of f32.

Alignment can take a bit to get used to, but it's fundamental to [data oriented design](https://vimeo.com/649009599).

The Zig example for my purpose of loading weights could probably be simplified some more. However, at that time on a cold afternoon in Toronto, the coffee shop was getting ready to close and the caffeine had come and gone. So I will have to save that for another day.