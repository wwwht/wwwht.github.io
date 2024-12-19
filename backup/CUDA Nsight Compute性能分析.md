参考：
https://zhuanlan.zhihu.com/p/707107808
[BBuf](https://github.com/BBuf/how-to-optim-algorithm-in-cuda/blob/master/cuda-mode/CUDA-MODE%20%E7%AC%AC%E4%B8%80%E8%AF%BE%E8%AF%BE%E5%90%8E%E5%AE%9E%E6%88%98%EF%BC%88%E4%B8%8A%EF%BC%89.md)
[官方文档](https://docs.nvidia.com/nsight-compute/NsightCompute/index.html#quickstart)

> [!WARNING]
>在办公电脑上运行，显卡是RTX 1660Ti，对应的nsight compute版本可能已经比较低了。

# Nsight Compute简介
Nsight Compute是一个CUDA kernel分析器，它通过硬件计数器和软件收集指标。它使用内置的专业知识来检测kernel常见的性能问题并指出发生这些问题的位置并给出一些解决方法的建议。这一内置规则集和指南就是我们所说的Guided Analysis。下面就结合Lecture1的例子来深入了解下Nsight Compute。

在Nsight Compute中，如果我们把鼠标悬停在各个指标上，我们能获得对应的讲解。
# Nsight Compute Profile流程
BBuf的Blog中使用的是 Triton 实现的矩阵开方代码使用Nsight Compute进行Profile，我们这里使用naive方式的sgemm和cublas的gemm进行实验。打开方式是直接使用管理员权限的Nsight Compute，完全不使用用ncu 命令行。实验环境为Windows专业版，显卡为GTX 1660Ti。
下面给出naive的kernel代码。
```c++
__global__ void naiveSgemm(float *__restrict__ a, float *__restrict__ b,  
                           float *__restrict__ c, const int M, const int N,  
                           const int K) {  
  
  int n = blockIdx.x * blockDim.x + threadIdx.x;  
  int m = blockIdx.y * blockDim.y + threadIdx.y;  
  if (m < M && n < N) {  
    float psum = 0.0;  
#pragma unroll  
    for (int k = 0; k < K; k++) {  
      psum += a[OFFSET(m, k, K)] * b[OFFSET(k, n, N)];  
    }    c[OFFSET(m, n, N)] = psum;  
  }}
```
cublas的代码：
```c++
cublasSgemm(cublas_handle, CUBLAS_OP_N, CUBLAS_OP_N, N, M, K, &cublas_alpha,  
            d_b, N, d_a, K, &cublas_beta, d_c, N);
```
下面开始分析，注意需要管理员权限打开Nsight Compute
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412091612961.png?imageSlim)
注意Sections选择full

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412091656105.png?imageSlim)
然后直接launch。弹出的terminal上可以看到我们程序的输出。
## Summary
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412091700649.png?imageSlim)

Summary部分长这样，可以看到我们启动的三个kernel：第一个是warm up，第二个是cublas的实现，第三个是我们的naive cuda实现。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412091704052.png?imageSlim)

使用page可以切换不同的界面，我们先看Summary
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412091705750.png?imageSlim)
这部分内容是选中kernel的一些信息，先混个脸熟。

| Result       | Kernel名字              |
| ------------ | --------------------- |
| Time         | Kernel耗时              |
| Cycles       | 时钟周期数                 |
| Regs         | 每个thread分配的寄存器数       |
| GPU          | 显卡型号                  |
| SM Frequency | SM频率，单位是GHz           |
| CC           | GPU架构号，7.5表示Turing 架构 |
| Process      | 可执行文件的名称              |

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412091724114.png?imageSlim)
下面是表示这个Summary选择下可以看到的Profile程序里面有哪些Kernel。下面是指标的一些含义，同样现在不需要了解每个的具体含义。

|     | **ID**                 | 每个函数的唯一标识符    |
| --- | ---------------------- | ------------- |
|     | **Issue Detected**     | 检测到的问题数量      |
|     | **Function Name**      | 函数的名称         |
|     | **Demangled Name**     | 去掉修饰符的函数名称    |
|     | **Duration (ms)**      | 函数执行时间        |
|     | **Compute Throughput** | 计算吞吐量         |
|     | **Memory Throughput**  | 内存吞吐量         |
|     | **Registers**          | 每个线程使用的寄存器数量  |
|     | **GridSize**           | kernel启动的网格大小 |
|     | **BlockSize**          | 每个Block的线程数   |
|     | **Cycles**             | 指令周期          |
### Compute Throughput
在 CUDA 中，**Compute Throughput 百分比** 是衡量 GPU 计算单元（SM, Streaming Multiprocessor）的<font color="#ff0000">利用率</font>的指标。
鼠标悬停在这一指标时，会出现如下提示：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241218171230339.png?imageSlim)

同 SM Throughput，SM（流式多处理器）是 GPU 的基本计算单元，负责并行执行 CUDA 程序中的大量线程。每个 SM 可以并行地执行多个**warp**，并且每个 warp 包含 32 个线程。每个 SM 有一定数量的计算资源（如 ALU、寄存器、共享内存等），这些资源用于执行程序中的指令。

- **Warp** 是 32 个线程的组合，它们在同一周期内执行相同的指令。
- **CTA**（Cooperative Thread Array）或线程块，是由多个 warp 组成的
- **SMSPs**：每个SM被划分为四个处理块，称为SM子分区。 SM子分区是SM上的主要处理单元。 一个子分区管理一个固定大小的warp池。

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241218172012455.png?imageSlim)
计算步骤：
计算 Compute Throughput 百分比涉及以下几个步骤：

Step 1: **获取 GPU 的理论最大 FLOPS**
首先，你需要知道 GPU 的规格，包括以下信息：

- **SM 核心数量**：例如 NVIDIA A100 有 108 个 SM，每个 SM 包含 64 个 CUDA 核心，总共 6912 个 CUDA 核心。
- **时钟频率**：例如 A100 的基础时钟频率是 1410 MHz（1.41 GHz）。
- **每周期浮点操作数**：每个 CUDA 核心通常可以在每个时钟周期执行 2 次浮点操作（一次 FMA）。

理论 FLOPS 计算公式：

$$
\text{理论 FLOPS} = \text{核心数量} \times 2 \times \text{时钟频率 (Hz)}
$$

**示例：**
- GPU：NVIDIA A100
- 核心数：6912
- 时钟频率：1.41 GHz
- 理论 FLOPS：

$$
6912×2×1.41×10^9=19.47 TFLOPS
$$

Step 2: **计算实际执行的计算操作数（FLOP）**
实际的 FLOP 需要通过程序运行时收集，常用的方法包括：
- **使用 CUDA Profiler 工具**：
    - `Nsight Compute` 和 `nvprof` 可以记录 CUDA 核函数执行的 FLOP 数。
    - FLOP 的具体计数通常包含单精度 (FP32)、双精度 (FP64) 和混合精度 (Tensor Core) 的统计数据。
- **手动估算**： 如果你清楚代码中执行的计算逻辑，可以估算每次循环或每个线程的浮点操作数，再乘以线程总数和循环次数。

Step 3: 计算 Compute Throughput%
### Memory Throughput
Memory Throughput 百分比 是衡量 CUDA 程序运行时 GPU 内存带宽利用效率的一个关键指标。通过计算 Memory Throughput 百分比，可以评估程序对 GPU 全局内存、共享内存或其他存储资源的访问效率，从而识别内存相关的性能瓶颈并进行优化。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241218173320494.png?imageSlim)
计算内存管道吞吐量 （此吞吐量指标表示在所有子单元实例的经过周期内达到的峰值持续率的百分比）
### Registers
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219085322095.png?imageSlim)
寄存器：每个子分区有一组32位寄存器，由硬件以固定大小的块分配。

线程：在GPU的一个SM单元上运行的单个线程。
### Cycles
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219085456414.png?imageSlim)
CUDA程序在GPU上运行时，每个指令都需要一定的硬件时钟周期来完成。一个cycle代表一个时钟信号的周期，是GPU硬件执行工作的基本时间单位。
Warp执行与Cycles： GPU的基本调度单位是warp（一组32个线程）。在CUDA中，warp中的所有线程是同步执行的（SIMD模型）。一个指令执行完成需要一定数量的cycles。

延迟与吞吐量： 一些CUDA指令（如内存读取、计算指令）可能需要多个周期（cycles）才能完成。这取决于指令类型、寄存器访问、线程分支情况以及内存访问模式等。
## Details 
### GPU Speed Of Light Throughput
首先是 GPU Speed Of Light Throughput部分，它通常位于Details部分的顶部。它清晰的描述了GPU资源的利用情况。在下面的截图中，我们同样可以通过鼠标悬停的方式去看每个指标的细节。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219091228817.png?imageSlim)

| 指标                             | 说明                                                  |                                                              |
| ------------------------------ | --------------------------------------------------- | ------------------------------------------------------------ |
| Compute (SM) Throughput [%]    | 计算单元 (Streaming Multiprocessors, SM) 的吞吐量占理论峰值的百分比。 | **77.89%** 表示当前任务利用了理论计算能力的 77.89%。                          |
| Memory Throughput [%]          | GPU 全局内存（Global Memory）的吞吐量占理论最大值的百分比。              | **77.89%** 表示当前任务利用了 GPU 全局内存带宽的 77.89%。                     |
| L1/TEX Cache Throughput [%]    | L1 缓存和纹理缓存的吞吐量占理论最大值的百分比。                           | **78.16%** 表示该缓存的使用接近理论最大值。                                  |
| L2 Cache Throughput [%]        | L2 缓存的吞吐量占理论最大值的百分比。                                | **10.45%** 表示二级缓存利用率较低，说明大部分内存访问可能直接从全局内存（DRAM）读取，或缓存未被充分利用。 |
| DRAM Throughput [%]            | GPU 显存（DRAM）的吞吐量占理论最大值的百分比。                         | **11.22%** 表明显存带宽使用率很低，可能是因为大部分数据通过缓存访问，未直接涉及显存。             |
| Duration [msecond]             | 执行时间，以毫秒为单位。                                        |                                                              |
| Elapsed Cycles [cycle]         | GPU 执行内核时的总耗费周期数。                                   |                                                              |
| SM Active Cycles [cycle]       | Streaming Multiprocessor（SM）处于活动状态的周期数。             |                                                              |
| SM Frequency [cycle/nsecond]   | SM 的工作频率（每纳秒的时钟周期数）。                                |                                                              |
| DRAM Frequency [cycle/nsecond] | DRAM 的工作频率（每纳秒的时钟周期数）。                              |                                                              |

**Balanced Throughput**： 平衡吞吐量的提示，此处计算吞吐量与内存吞吐量都约为 77.89%，表明任务优化良好，避免了瓶颈。  
**Roofline Analysis**：当前设备的 fp32（单精度浮点）与 fp64（双精度浮点）性能比为 **32:1**。此内核只达到了设备 fp32 峰值性能的 10%，说明仍有优化空间。双精度性能（fp64）未被利用（达成 0% 峰值性能）。  

下面这些了解一下就行，暂时还没有用到。  

**Compute Throughput Breakdown**

| **指标**                                     | **说明**                                            |
| ------------------------------------------ | ------------------------------------------------- |
| SM: Inst Executed Pipe Lsu [%]             | Load/Store 单元 (LSU) 执行的指令占比。表示内存加载和存储操作的利用率。      |
| SM: Issue Active [%]                       | 指令发射器 (Issue Unit) 的活跃时间百分比。表示 GPU 核心忙于分派指令的时间比例。 |
| SM: Inst Executed [%]                      | 实际执行的指令占比。反映 GPU 核心的整体计算工作量。                      |
| SM: Mio Inst Issued [%]                    | MIO 单元（算术逻辑运算单元）发出的指令占比。                          |
| SM: Pipe Fma Cycles Active [%]             | FMA（浮点融合乘加）管道的活跃周期百分比。表示浮点运算性能的利用率。               |
| SM: Mio2Rf Writeback Active [%]            | 数据从 MIO 单元写回寄存器的活跃时间百分比。                          |
| SM: Pipe Alu Cycles Active [%]             | ALU（算术逻辑单元）管道的活跃周期百分比，表示算术和逻辑运算的占比。               |
| SM: Inst Executed Pipe Adu [%]             | ADD 单元（加法运算单元）指令执行占比。                             |
| SM: Inst Executed Pipe Cbu Pred On Any [%] | CBU（条件分支单元）执行带谓词的指令占比。                            |
| SM: Mio Pq Read Cycles Active [%]          | 从 PQ 单元读取的活跃周期百分比。                                |
| SM: Mio Pq Write Cycles Active [%]         | 向 PQ 单元写入的活跃周期百分比。                                |
| IDC: Request Cycles Active [%]             | 数据传输请求（Interconnect Data Communication）的活跃周期百分比。  |
| SM: Inst Executed Pipe Fp16 [%]            | FP16（半精度浮点）指令执行占比。                                |
| SM: Inst Executed Pipe Ipa [%]             | IPA（整数加法单元）指令执行占比。                                |
| SM: Inst Executed Pipe Tex [%]             | 纹理单元的指令执行占比，表示纹理处理的利用率。                           |
| SM: Inst Executed Pipe Uniform [%]         | Uniform（统一变量）处理单元的指令执行占比。                         |
| SM: Pipe Fp64 Cycles Active [%]            | FP64（双精度浮点）管道的活跃周期百分比。                            |
| SM: Pipe Shared Cycles Active [%]          | 共享内存操作管道的活跃周期百分比。                                 |
| SM: Pipe Tensor Cycles Active [%]          | Tensor Core（张量核心）的活跃周期百分比。                        |
**Memory Throughput Breakdown**

| **指标**                                 | **说明**                               |
| -------------------------------------- | ------------------------------------ |
| L1: Lsuin Requests [%]                 | L1 缓存中 LSU 请求的占比。反映一级缓存中加载和存储操作的利用率。 |
| L1: Data Pipe LSU Wavefronts [%]       | LSU 数据管道的波前利用率。                      |
| L1: Lsu Writeback Active [%]           | 从 L1 缓存写回的数据占比。                      |
| DRAM: Cycles Active [%]                | DRAM（显存）处于活跃状态的周期占比。                 |
| L2: T Sectors [%]                      | L2 缓存的扇区使用占比。表示 L2 缓存的数据吞吐量情况。       |
| L2: Lts2xbar Cycles Active [%]         | 从 L2 缓存到 XBAR（交叉开关）的活跃周期占比。          |
| L1: Data Bank Reads [%]                | L1 数据存储模块读取的占比。                      |
| L2: Xbar2lts Cycles Active [%]         | 从 XBAR 到 L2 缓存的活跃周期占比。               |
| L1: T Tag Requests [%]                 | L1 缓存的标签请求占比，表示缓存命中的操作频率。            |
| DRAM: Dram Sectors [%]                 | DRAM 使用的扇区占比，反映显存的访问频率。              |
| L2: D Sectors Fill Device [%]          | L2 缓存从设备填充的扇区占比。                     |
| L2: D Sectors Fill System [%]          | L2 缓存从系统填充的扇区占比。                     |
| M: Xbar2lttex Read Sectors [%]         | 交叉开关到纹理单元的读取扇区占比。                    |
| L1: Data Bank Writes [%]               | L1 数据存储模块写入的占比。                      |
| L1: F Wavefronts [%]                   | 一级缓存中的波前频率，表示缓存处理多个并行任务的能力。          |
| L1: Texin Sm2tex Reg Cycles Active [%] | SM 到纹理单元（Texture）寄存器访问的活跃周期占比。       |
| L1: Data Pipe Tex Wavefronts [%]       | 纹理管道的波前占比。                           |
| L1: Tex Writeback Active [%]           | L1 缓存纹理写回的活跃状态百分比。                   |
| L2: D Atomic Input Cycles Active [%]   | L2 缓存原子操作（Atomic Operations）的活跃周期占比。 |

接下来是Roofline

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219093301967.png?imageSlim)

关于roofline的可以看另一个blog，有详细的讲解。
可以看到naiveSgemm的内存访问和计算都有优化的空间。

### Compute Workload Analysis
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219094625897.png?imageSlim)

**总体指标**

| **指标**                                | **说明**                                                              |
| ------------------------------------- | ------------------------------------------------------------------- |
| **Executed Ipc Elapsed [inst/cycle]** | 已执行的每周期指令数（IPC，Instructions Per Cycle），反映 GPU 的整体执行效率。值为 **1.17**。  |
| **Executed Ipc Active [inst/cycle]**  | 在活跃状态下的每周期指令数，表示仅统计 GPU 核心在忙碌时的执行效率。值为 **1.18**。                    |
| **Issued Ipc Active [inst/cycle]**    | 活跃时发出的每周期指令数，表示指令分发效率。值为 **1.18**。                                  |
| **SM Busy [%]**                       | Streaming Multiprocessors（SM）处于忙碌状态的时间占比。值为 **29.42%**，表明当前任务的活跃时间。 |
| **Issue Slots Busy [%]**              | 指令分发槽的使用时间占比。值为 **29.42%**，表示指令调度槽在任务中的占用率。                         |
**管道利用率（Pipe Utilization）**

| **管道**  | **说明**                                                                        |
| ------- | ----------------------------------------------------------------------------- |
| **LSU** | Load/Store Unit（加载/存储单元），用于处理内存加载和存储操作。当前任务利用率为 **78.2%**，说明内存操作占用比重大，可能成为瓶颈。 |
| **FMA** | Fused Multiply-Add（浮点乘加单元），用于执行浮点运算的核心组件。利用率为 **约 50%**，说明浮点运算有一定占比。          |
| **ALU** | Arithmetic Logic Unit（算术逻辑单元），用于整数运算和逻辑操作。利用率为 **约 30%**，说明整数运算需求较少。          |

**分析与优化方向：**
**内存瓶颈：LSU** 利用率达到 **78.2%**，显著高于其他管道，说明内存加载/存储操作是当前任务的主要性能瓶颈。
优化方向：
- 减少不必要的内存访问，增加数据局部性（使用共享内存或缓存）。
- 合并内存操作，减少内存访存的频率。

**计算单元**：**FMA** 和 **ALU** 管道的利用率尚未达到满负载，说明计算性能尚未完全释放。
优化方向：
- 增加浮点运算和整数运算的并行度。
- 优化核函数（Kernel）代码逻辑，提升计算密集度。

**整体利用率**：**SM Busy** 和 **Issue Slots Busy** 均为 **29.42%**，表明 GPU 的整体利用率较低。
优化方向：
- 提高任务的线程并行度。
- 减少线程阻塞和数据依赖，提高 GPU 核心的占用率

### Memory Workload Analysis
**Memory Workload Analysis（内存工作负载分析）**，用于分析 GPU 的内存资源利用情况，包括内存访问模式、带宽使用情况以及潜在的内存瓶颈。

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219095431560.png?imageSlim)

#### **顶部主要指标**

| **指标**                               | **说明**                                                                | **当前值**        |
| ------------------------------------ | --------------------------------------------------------------------- | -------------- |
| **Memory Throughput [Gbyte/second]** | GPU 的实际内存吞吐量，以 GB/s 为单位，表示当前任务的内存读写速度。反映了内存带宽的实际利用情况。                 | **30.93** GB/s |
| **L1/TEX Hit Rate [%]**              | 一级缓存（L1 缓存）或纹理缓存（TEX 缓存）的命中率，表示内存访问请求被缓存命中的百分比。较高的命中率说明缓存利用较好。        | **94.93%**     |
| **L2 Hit Rate [%]**                  | 二级缓存（L2 缓存）的命中率，表示从 L2 缓存获取数据的比率，而不是直接访问显存（DRAM）。较高的命中率可以减少显存访问开销。    | **77.89%**     |
| **Mem Busy [%]**                     | 内存硬件资源的繁忙时间占比，表示显存模块在执行任务时的繁忙程度。高值可能表明内存已经成为性能瓶颈。                     | **38.95%**     |
| **Mem Pipes Busy [%]**               | 内存管道（Memory Pipes）的繁忙时间占比，表示内存读写请求占用管道资源的情况。高值可能意味着内存带宽的瓶颈。           | **49.22%**     |
| **Max Bandwidth [%]**                |  计算内存管道：SM<->缓存<->DRAM之间互连的吞吐量 （这个吞吐量指标表示在所有子单元实例的经过周期内达到的峰值持续速率的百分比） |                |

L2 Load Access Pattern: 这部分详细描述了从 L1/TEX 缓存加载到 L2 缓存时的访问模式

|**指标**|**说明**|**当前值**|
|---|---|---|
|**Sectors per L2 Request**|每次从 L1 缓存向 L2 缓存发出的请求所访问的扇区数量（一个 L2 缓存行包含 4 个扇区，每个扇区大小为 32 字节）。理想情况下应该是 4 扇区全被利用。|**1.6**|

当前分析：Sectors per L2 Request 为 1.6，远小于 4。说明内存访问模式未能充分利用 L2 缓存行，每次加载的数据块较小，导致带宽浪费或缓存效率低下。原因可能是 **非合并内存访问（Uncoalesced Accesses）**，即多个线程对不连续的内存地址进行访问。

接下来是Memory Chart：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219101044483.png?imageSlim)

任务的大部分内存请求都集中在 **全局内存**，共发起了 **268.44M 请求**，可能是性能瓶颈的主要来源。
L1 缓存：高命中率（94.93%），有效减少了对全局内存的访问，但仍有部分请求流入 L2 缓存。
L2 缓存：命中率较低（49.22%），需要优化数据访问模式，进一步减少全局内存访问。
内存瓶颈：
全局内存（Device Memory）的流量较高（573.34 MB），可能导致较高的延迟。

### Scheduler Statistics
**Scheduler Statistics（调度器统计）** 的分析结果，用于评估 GPU 的线程调度器在内核执行期间的活跃度和利用率。调度器是 GPU 的核心组件之一，负责管理和调度多个线程组（即 **warps**）执行指令。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219102042829.png?imageSlim)

|**指标**|**含义**|**当前值**|
|---|---|---|
|**Active Warps Per Scheduler [warp]**|每个调度器当前活跃的 Warp（线程束）数量，表示调度器正在管理的 Warp 数量。这些 Warp 可能正在执行，也可能因为等待资源或数据而停顿。|**7.99**|
|**Eligible Warps Per Scheduler [warp]**|每个调度器中可以发出指令的 Warp 数量，即那些准备好执行下一条指令的 Warp。Eligible Warp 是 Active Warp 的子集，反映了 Warp 的执行效率。|**0.74**|
|**Issued Warp Per Scheduler [warp]**|每个调度器中实际发出指令的 Warp 数量，即每个周期中调度器真正调度的 Warp 数量。数值较低可能表明 Warp 受阻或调度器未充分利用。|**0.29**|
|**No Eligible [%]**|调度器周期中没有可调度 Warp 的时间比例。当这个值高时，说明许多 Warp 处于停顿状态，可能因为内存延迟或其他资源争用导致。|**70.56%**|
|**One or More Eligible [%]**|调度器周期中至少有一个 Warp 准备好发出指令的时间比例。当这个值低时，说明 Warp 停顿严重，调度器资源未被充分利用。|**29.44%**|
柱状图：

| **柱状图类别**                           | **含义**                                                                                          | **当前值**  |
| ----------------------------------- | ----------------------------------------------------------------------------------------------- | -------- |
| **GPU Maximum Warps Per Scheduler** | 每个调度器的理论最大 Warp 数量（硬件支持的上限）。当前值为 **8 warp**，这是每个调度器可以并行管理的最大 Warp 数量。                           | **8**    |
| **Theoretical Warps Per Scheduler** | 理论上的 Warp 数量，受任务配置（如线程块大小和占用率）限制。当前任务的理论值为 **8 warp**，与硬件支持的上限相同。                               | **8**    |
| **Active Warps Per Scheduler**      | 每个调度器当前管理的活跃 Warp 数量，表示参与任务执行的 Warp 数量。当前值为 **7.99 warp**，说明调度器几乎达到了满负载。                        | **7.99** |
| **Eligible Warps Per Scheduler**    | 每个调度器中可以发出指令的 Warp 数量，表示准备好执行指令的 Warp。当前值为 **0.74 warp**，说明绝大多数 Warp 处于非 Eligible 状态（可能因停顿而等待）。 | **0.74** |
| **Issued Warp Per Scheduler**       | 每个调度器中实际发出指令的 Warp 数量。当前值为 **0.29 warp**，说明调度器大部分时间处于空闲状态，利用率较低。                                | **0.29** |
#### 分析与优化
**调度器活跃 Warp 数量： Active Warps Per Scheduler** 接近理论最大值（7.99 / 8 warp），表明任务在调度器上分配了足够多的 Warp，调度器的硬件资源已接近饱和。

 **Eligible Warp 数量较少 ： Eligible Warps Per Scheduler** 仅为 **0.74 warp**，说明大部分 Warp 处于停顿状态，可能因为以下原因：
    1. **内存延迟**：Warp 等待内存访问完成。
    2. **数据依赖**：Warp 等待前一指令的计算结果。
    3. **资源争用**：Warp 等待寄存器或其他硬件资源的可用性。

**Issued Warp 数量低** ： 每个调度器平均每周期只有 **0.29 warp** 实际发出了指令，说明大部分调度器的发射槽（Issue Slot）处于空闲状态，未能充分利用 GPU 的并行计算能力。

**No Eligible 占比高** ： 调度器中 **70.56% 的周期没有可发出指令的 Warp**，进一步表明 Warp 停顿严重。

| **优化方向**                | **优化措施**                                                     | **目标**                                |
| ----------------------- | ------------------------------------------------------------ | ------------------------------------- |
| **减少 Warp 停顿**          | - **优化内存访问模式**：确保内存访问是合并的（Coalesced Memory Access），减少内存访问延迟。 | 减少内存延迟对 Warp 的影响，提高 Eligible Warp 数量。 |
|                         | - **使用共享内存**：将常用数据放入共享内存，减少对全局内存的依赖。                         | 缩短内存访问时间，减少 Warp 等待周期。                |
|                         | - **减少数据依赖**：优化线程间数据通信，分解依赖链较长的指令序列。                         | 提高 Warp 发出指令的可能性，降低调度器空闲时间。           |
| **增加 Eligible Warp 数量** | - **增加线程块尺寸（thread block size）**：合理分配更多线程至每个调度器。             | 提高调度器中活跃 Warp 的数量，避免硬件资源浪费。           |
|                         | - **减少分支发散（Branch Divergence）**：通过统一控制流减少 Warp 内线程分支行为。      | 提高 Warp 执行效率，使更多 Warp 处于 Eligible 状态。 |
| **提高调度器利用率**            | - **优化调度器分配**：均匀分配线程块到所有调度器，避免某些调度器过载或空闲。                    | 确保硬件资源充分利用，提高整体并行计算效率。                |
|                         | - **分析资源使用冲突**：优化寄存器使用，避免 Warp 因寄存器不足而停顿。                    | 降低资源争用导致的 Warp 停顿，增加指令发出机会。           |
|                         | - **避免硬件资源瓶颈**：减少对稀缺硬件资源（如 Tensor Core）的过度依赖，平衡资源分配。         | 提高硬件利用率，减少 Warp 等待时间。                 |
| **优化代码逻辑**              | - **重构核函数（Kernel Function）**：减少长时间执行的指令块，分解复杂逻辑。             | 提高 Warp 执行效率，缩短执行时间。                  |
|                         | - **减少循环深度**：通过展开循环或优化循环结构，避免过多线程停顿。                         | 降低线程同步和数据依赖，增加 Warp 发出指令的频率。          |
### Warp State Statistics
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219103040216.png?imageSlim)
Warp State Statistics（线程束状态统计） 的分析结果，用于了解 GPU 任务执行中 Warp（线程束）的执行和停顿状态。Warp 停顿（Stall）是 GPU 性能的主要瓶颈之一，这个图揭示了 Warp 在每周期中的状态分布以及主要的停顿原因。

|**指标**|**说明**|**当前值**|
|---|---|---|
|**Warp Cycles Per Issued Instruction [cycle]**|每发出一条指令的 Warp 平均停顿周期数，表示 Warp 等待下次发射指令的平均时间。较大的值表明存在较大的性能瓶颈。|**27.15**|
|**Warp Cycles Per Executed Instruction [cycle]**|每执行一条指令的 Warp 平均周期数，通常与上一指标相同。这表明指令之间的延迟和 Warp 停顿对性能的影响。|**27.15**|
|**Avg. Active Threads Per Warp**|每个 Warp 的平均活跃线程数，表示 Warp 中正在参与指令执行的线程数量。|**32**|
|**Avg. Not Predicated Off Threads Per Warp**|平均未被谓词关闭的线程数量，表示每个 Warp 中真正参与计算的线程数量。这表明线程发散对 Warp 的影响。|**31.98**|

柱状图显示了 Warp 状态在所有周期中的分布，包括主要停顿原因和其他状态：

|**状态**|**含义**|**当前值**|
|---|---|---|
|**Stall Long Scoreboard**|Warp 因 L1TEX 数据依赖而停顿的时间占比，表示 L1 缓存或寄存器访问延迟对性能的影响。|**43.6%**|
|**Stall LG Throttle**|Warp 因本地或全局内存操作队列未满而停顿的时间占比，表示全局内存延迟对性能的影响。|**36.3%**|
|**Stall Wait**|Warp 因等待硬件资源（如寄存器或其他计算单元）可用而停顿的时间占比。|**较少**|
|**Stall Not Selected**|Warp 没有被调度器选择的时间占比，表示调度器未充分利用 Warp 的时间。|**很少**|
|**Selected**|Warp 被调度器选中执行指令的时间占比，表示 Warp 实际执行指令的时间。|**最低**|****
#### 分析与优化

| **停顿原因**                  | **含义**                                                                        | **当前表现**                 | **占比**    | **优化建议**                                                               |
| ------------------------- | ----------------------------------------------------------------------------- | ------------------------ | --------- | ---------------------------------------------------------------------- |
| **Stall Long Scoreboard** | Warp 因为 **L1TEX 数据依赖**（如本地内存、全局内存、纹理或寄存器操作）而停顿。Warp 等待之前的指令完成或数据准备好才能执行下一条指令。 | 平均每 Warp 等待 **11.8 个周期** | **43.6%** | - **优化 L1 缓存命中率**：通过合并内存访问和优化数据局部性。  <br>- **使用共享内存**：减少全局内存依赖，提升访问效率。 |
| **Stall LG Throttle**     | Warp 因 **本地内存或全局内存队列未满** 而停顿。这通常发生在内存操作非常频繁时，内存访问指令等待队列资源。                    | 平均每 Warp 等待 **9.9 个周期**  | **36.3%** | - **合并内存操作**：将多个小范围内存访问合并为更宽的内存操作。  <br>- **指令交错**：在内存访问之间插入计算指令以隐藏延迟。 |
| **Stall Wait**            | Warp 因等待 **硬件资源（如寄存器或计算单元）** 可用而停顿。                                           | 时间较少                     | **较少**    | - **优化寄存器分配**：减少 Warp 的寄存器需求。                                          |
| **Stall Not Selected**    | Warp 没有被调度器选中执行指令的时间，表明调度器资源未被充分利用。                                           | 时间较少                     | **很少**    | - **增加调度器活跃 Warp 数量**：增加线程块或分配更多 Warp 至调度器。                            |
| **Selected**              | Warp 被调度器选中执行指令的时间，表示 Warp 实际执行的时间。                                           | 时间较少                     | **最低**    | - **减少停顿时间**：通过优化内存访问模式和减少分支发散，提高 Warp 被选中的频率。                         |

### Instruction Statistics

**Instruction Statistics（指令统计）**，主要用来分析 GPU 内核中已执行和已发射的低级汇编指令（SASS）。这些统计信息提供了关于指令类型和频率的见解，帮助了解指令发射和执行的效率以及潜在的性能瓶颈。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219111235525.png?imageSlim)

| **指标**                                              | **含义**                                                    | **当前值**          |
| --------------------------------------------------- | --------------------------------------------------------- | ---------------- |
| **Executed Instructions [inst]**                    | 已执行指令数，表示 GPU 在运行内核时执行的总指令数。这反映了内核的计算密集度和执行负载。            | **809,631,744**  |
| **Issued Instructions [inst]**                      | 已发射指令数，表示 GPU 调度器向计算单元（SM）分配的总指令数。发射的指令可能因资源限制或停顿而未能立即执行。 | **809,635,617**  |
| **Avg. Executed Instructions Per Scheduler [inst]** | 每个调度器平均执行的指令数，表示 GPU 调度器之间的工作分配是否均衡。                      | **8,433,664**    |
| **Avg. Issued Instructions Per Scheduler [inst]**   | 每个调度器平均发射的指令数，反映调度器的指令发射活动是否高效。                           | **8,433,704.34** |

### Occupancy
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219111427485.png?imageSlim)

Occupancy（占用率） 的相关指标，用于分析 GPU 核函数（Kernel）在 Streaming Multiprocessor（SM）上的 Warp 分配和利用情况。

| **指标**                                     | **含义**                                                                 | **当前值**   |
| ------------------------------------------ | ---------------------------------------------------------------------- | --------- |
| **Theoretical Occupancy [%]**              | 理论占用率，是指最大可能活跃 Warp 数占 SM 支持的最大 Warp 数的比例。100% 表示所有可能的 Warp 资源都被分配并利用。 | **100**   |
| **Theoretical Active Warps Per SM [warp]** | 每个 SM 上理论最大活跃 Warp 数量，反映硬件支持的最大并行度。                                    | **32**    |
| **Achieved Occupancy [%]**                 | 实际占用率，表示内核执行时实际活跃 Warp 数占理论最大活跃 Warp 数的比例。                             | **99.92** |
| **Achieved Active Warps Per SM [warp]**    | 每个 SM 上实际活跃的 Warp 数量，反映任务运行时的实际并行度。                                    | **31.98** |

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219112401062.png?imageSlim)

块大小对性能的影响，每块共享内存用量对性能的影响

### Source Counters
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20241219112542501.png?imageSlim)

在这个电脑上只有SASS的代码，具体可以看这个BLOG [CUDA MODE](https://zhuanlan.zhihu.com/p/709873278)

# 总结
使用Nsight Compute进行核函数的性能分析，主要可以概括为以下几个步骤：

1. **定位性能瓶颈**：通过采集 GPU 执行的详细性能数据，确定性能瓶颈所在（内存、计算、线程分配等）。
2. **分析关键指标**：重点分析影响性能的指标，如计算效率、内存利用率、线程并行度、指令吞吐量等。
3. **优化与验证**：针对瓶颈采取优化措施，并通过再次分析验证优化效果。

| **性能瓶颈**                               | **关键指标**                                                                           | **优化方法**                                                                                                               |
| -------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| **内存带宽不足 (Memory Bound)**              | - 全局内存带宽利用率高  <br>- L1/L2 缓存命中率低  <br>- DRAM 利用率低  <br>- 高内存延迟                     | - 使用共享内存（Shared Memory）优化访问  <br>- 确保内存访问对齐（Coalesced Memory Access）  <br>- 减少全局内存访问，充分利用寄存器和缓存  <br>- 使用纹理或常量内存访问只读数据 |
| **计算性能不足 (Compute Bound)**             | - 指令吞吐率低  <br>- 核心利用率低（FLOPS/SM 利用率低）  <br>- 高访存/计算比  <br>- Pipeline Stall (流水线停顿) | - 合并冗余计算，提高并行性  <br>- 利用 CUDA 高效数学库（如 cuBLAS、cuFFT）  <br>- 减少条件分支分化，提高 Warp 执行一致性  <br>- 优化数据复用，减少访存需求                 |
| **线程占用率不足 (Low Occupancy)**            | - 线程占用率（Occupancy）低  <br>- 寄存器和共享内存使用量过高，限制了活跃线程数  <br>- 部分 SM 资源闲置                | - 调整线程块大小（Thread Block Size），确保更高的并行度  <br>- 减少寄存器和共享内存使用  <br>- 增加线程块数量，平衡工作负载  <br>- 使用 `launch_bounds` 限制资源分配       |
| **Warp 分支分化 (Warp Divergence)**        | - Warp 效率低  <br>- 条件分支执行耗时显著  <br>- Warp 中线程执行不同路径                                 | - 重构条件分支逻辑，减少分支判断  <br>- 使用 Warp 级同步或 Warp Shuffle 优化  <br>- 避免不必要的条件分支逻辑，统一 Warp 内部执行路径                               |
| **内存访存效率低 (Memory Latency)**           | - L1/L2 缓存命中率低  <br>- 内存访问模式不连续（非 Coalesced Access）  <br>- 高内存访问延迟                 | - 优化访存模式，确保内存访问对齐（Coalesced Access）  <br>- 使用共享内存缓存局部数据  <br>- 合理规划线程访问模式，避免不必要的数据重访                                   |
| **指令吞吐率低 (Instruction Throughput)**    | - 核心吞吐率低  <br>- FP16/FP32 吞吐率未达到设备峰值  <br>- 高访存开销影响计算吞吐                            | - 使用低精度运算（FP16）优化性能  <br>- 合并访存和计算操作，避免访存/计算切换开销  <br>- 使用矢量化计算，尽量减少每个线程的单独计算                                          |
| **同步和通信开销 (Synchronization Overhead)** | - 核间同步耗时高  <br>- 使用原子操作频繁  <br>- Host/Device 数据传输时间长                               | - 减少线程同步点，优化线程协作方式  <br>- 避免频繁的原子操作，改用共享内存中间处理  <br>- 合并 Host 和 Device 的数据传输，减少 PCIe 通信开销                              |
| **负载不均衡 (Load Imbalance)**             | - 不同 SM 的执行时间差异显著  <br>- 部分线程块执行时间显著高于其他线程块  <br>- GPU 资源未充分利用                     | - 确保工作负载均匀分配到各线程块和 SM  <br>- 重构算法逻辑，避免单线程/单块任务过重  <br>- 使用动态并行性 (Dynamic Parallelism) 动态调整任务分配                         |
| **缓存利用率不足 (Cache Utilization)**        | - L1/L2 缓存命中率低  <br>- 数据复用性不足，频繁的全局内存访问  <br>- DRAM 访问占比高                          | - 通过数据局部性优化提升缓存命中率  <br>- 合理规划线程访问模式，避免缓存冲突  <br>- 增加共享内存使用，存储局部复用数据                                                   |

最后，注意Nsight Compute中的提示，通常都是一些可以优化的点。
