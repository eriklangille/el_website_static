Title: LLM Limitations and Zig
Description: I spent my Sunday understanding Zig. This started by trying to create a "simple" garbage collector. Then I tried leveraging ChatGPT...
Date: 2023-02-19

I spent my Sunday understanding Zig.

This started by trying to create a "simple" garbage collector in Zig.

The problem is I don't know where to start. *I've never written any Zig code before.*

Hey, ChatGPT could solve this.

I used ChatGPT to come up with a simple garbage collector data structure. Then I tried to compile it. 

*Complaint from the compiler.*

Fixed the complaint.

*Three more complaints from the compiler.*

Fixed those. Wait, this function doesn't work like this. Wait, this annotation doesn't even exist. Hold on...

Although LLMs have come a long way, they still need a lot of data in order to generalize. This means for a language like Zig, ChatGPT often hallucinates. I had to scrap the data structure the bot came up with.

This doesn't mean ChatGPT is useless. In languages such as Python, ChatGPT and Copilot can be quite powerful and generate exactly what you want. For example, I asked ChatGPT to create the code to upload my blog to S3. That code ran with no problem, and it allowed me to avoid writing trivial interface code. Worth the $20/mo.

Back to the Zig. I found myself reverting to my old methods to learn:

  - Stack overflow
  - [Reference documents](https://ziglang.org/documentation/0.10.1/) and cmd + f
  - Fighting with the compiler (trial and error)
  - Following examples from other large Zig projects ([bun](https://github.com/oven-sh/bun/))


I felt like my own LLM. However, unlike current LLMs, I can generalize with a small dataset.

I still don't have a working garbage collector - not even with the "simple" mark and sweep algorithm. But I have learned a lot about zig and remembered a lot about low-level development. 

And most importantly, I still have time before I'm replaced by a LLM.