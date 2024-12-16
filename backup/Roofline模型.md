参考：
Samuel Williams, Roofline Performance Modeling for HPC and Deep Learning Applications, https://crd.lbl.gov/assets/Uploads/S21565-Roofline-1-Intro.pdf  
YouTube English Presentation：Roofline Hackathon 2020 part 1 and 2 - YouTube  
Paper：Roofline charts were first introduced by David Patterson and others in 2008 in their ACM paper [“Roofline: An Insightful Visual Performance Model](https://people.eecs.berkeley.edu/~kubitron/cs252/handouts/papers/RooflineVyNoYellow.pdf)
[YOYO鹿鸣](https://blog.csdn.net/sinat_35360418/article/details/128704146?spm=1001.2014.3001.5502)
[Telesens](https://www.telesens.co/2018/07/26/understanding-roofline-charts/)
[Instruction Roofline](https://crd.lbl.gov/assets/Uploads/InstructionRooflineModel-PMBS19-.pdf)

# 引入：什么是较好的性能评价模型



![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131334071.png?imageSlim)
假设在GPU上对内核的循环测试进行性能分析，我们对不同的loop nest得到了随机的flop rates，有的很高，有的很低，这意味着只用GFLOP/s去评价性能可能有失偏颇.

![image.png|425](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131341297.png?imageSlim)
假设我们把某CPU代码移植到了Nvida GPU或者是AMD GPU中，将原CPU代码作为baseline（绿色），去对比移植后的代码性能（灰色）提升了多少，然后发现在有的循环中提升了非常多（例如第三根柱子、最后一根柱子），有的循环中只提升了一点点（例如第6根柱子），也不能很好的评价性能。

**那么什么是“好的”性能？**(GPU为例), 两个基本评价标准：
1. 能够在吞吐量有限的情况下运行

> ​ not sensitive to Amdahl effects, D2H/H2D transfers, launch overheads, etc…

​ 对于阿达姆效应不敏感、不会有连续的性能瓶颈；没有频繁的主机（Host）与设备内存（Device）之间的数据交换，保持尽量少的数据交换，使时间尽可能花在GPU计算上；启动开销尽量小，避免启动一堆很小的kernel(例如一个kernel只计算几微秒)，把时间浪费在launch kernel上.

2. 充分利用GPU的**计算**以及**访存带宽**能力

总之，我们需要一个定量的性能评价模型，而不是定性的类似“性能不错”这样的评价。例如，达到了GPU计算峰值的80%、利用了70%的访存带宽等。

# 什麽是roofline模型

roofline模型是一个面向吞吐量的性能模型
关注“率（rates）”而不是时间（time），例如flop rate（GFLOP/s）、bytes per second rate（GB/s）
与架构无关，可以应用于CPU、GPU、DCU、Google TPU、FPGA等等

# 怎样使用roofline模型分析性能？

## （DRAM） roofline model简化模型

首先我们对代码运行的计算机架构进行简单建模：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131412913.png?imageSlim)

首先假设当数据位于L1 Cache中时，SM通常可以达到计算能力峰值（此处举例为GFLOP/s）

假设在单一程序多数据流（SPMD, Single Program Multiple Data），所有的SM运行时都是负载均衡的，将它们合并，进行进一步简化
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131418376.png?imageSlim)

最后假设有足够的Cache空间以及访存带宽，即性能不会因为Cache空间不足以及访存带宽不够而被影响，基于此将模型再次简化:
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131419935.png?imageSlim)

对于简化后的模型来说，能够影响性能的只有我们写的代码能算多快以及在主机端和设备端之间传输数据的速度有多快。我们将上面的模型叫做**DRAM roofline model**。  

此时对于需要分析的任意一个程序或者Kernel，我们只需要考虑两个方面：
1. Computation (e.g. FLOPs)
2. Communication (e.g. moving data to/from DRAM)

##  （DRAM） roofline model基本公式
假设数据传输时间和运算时间可以完美重叠，那么我们的代码耗时应为：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131423069.png?imageSlim)

FLOPS / Peak GFLOP/s 是理论计算时间，即浮点操作数量除以峰值计算速度， Bytes  /  Peak GB/s 是理论访存时间，即需要从DRAM中存入以及读取的数据总量的Bytes除以DRAM峰值带宽。
前面提到roofline模型主要关注“率”，因此对上面公式进行变形，得到：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131427885.png?imageSlim)

也就是：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131428390.png?imageSlim)
最终：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131428218.png?imageSlim)
AI (Arithmetic Intensity) = FLOPs / Bytes (as presented to DRAM )  计算访存比
上面的公式就是roofline模型的基本公式，其中AI(Arithmetic Intensity)=FLOPs/Bytes=计算量/访存量，表示计算密度。当代码的计算量远大于访存量，我们说他是计算密集型的，当访存量远大于计算量，则说他是访存密集型的。

## （DRAM） roofline model图像

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131432901.png?imageSlim)

以AI（计算密度）为横坐标，FLOP/s（可达到的浮点性能）为纵坐标，可得出roofline模型图像（因图像长得像屋顶所以叫roofline模型）。蓝色段中，性能受限于理论带宽（即斜率，Peak GB/s），在粉色段中，性能受限于浮点计算峰值性能（Peak GFLOP/s）。图中的转折点的横坐标 称作“Machine Balance”，其表征了硬件架构的特点，而Arithmetic Intensity（计算密度）表征了我们的代码/应用的特点。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131438877.png?imageSlim)

我们大致可以把图像分为5个区域，粉色线以上和蓝色线以左的区域是程序无论如何都无法达到的性能，因为它意味着超过了计算机的峰值计算性能/访存带宽。淡蓝色区域（计算密度小于Machine Balance点）是性能较好的访存密集型程序，这部分程序的访存带宽利用率较高（可能50%或更高），评价访存密集型程序的指标主要选用访存带宽；淡粉色区域（计算密度大于Machine Balance点）是性能较好的计算密集型程序，有较好的数据重用率与数据局部性，这部分程序的浮点性能较高（可能50%或更高），评价计算密集型程序的指标主要选用浮点性能。最后就是可能带宽与浮点性能都低于50%峰值性能的poor performance，如果程序性能处于这个部分，需要考虑优化算法提高性能，达到粉色或者蓝色区域。

## 使用roofline模型分析性能示例

对于文章一开始的性能分析图（随机输出kernel性能），我们将其重新组织，计算每个kernel的计算密度，并以计算密度为横坐标，重新排列得到：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131520931.png?imageSlim)

将其与roofline模型相比较：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131520387.png?imageSlim)

那些贴近于roofline的kernel较好的利用了计算资源（绿色点点），而那些远离roofline的kernel（红色点点）则是我们重点需要去优化、提高计算资源利用率的。这里需要注意，对比FLOP/s很低的kernel（例如第一个绿点），红点虽然看起来FLOP/s更高，但是比绿点更有优化性价比。因为绿点已经很接近roofline模型了，无法突破机器能提供的最大资源，可能需要费很大的劲儿才能提高一点点（如果不改变计算密度的话）；而红点离roofline还有较远距离，可通过不断优化访存函数、计算函数来提高访存带宽/浮点计算性能利用率。除此之外，如果想要提高FLOP/s很低但是又比较接近roofline的kernel，可以通过改进计算方法/减少数据传输时间来提高计算密度（例如提高空间局部性、提高cache命中率、改进数据结构、数据类型）。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131533479.png?imageSlim)

# 有哪些低于roofline的原因？

首先，有可能是roofline的图本身的误差：

1. kernel的误差：算错了FLOP/s或者算错了Byte、计算密度
2. 访存带宽和计算峰值线的误差：roofline模型本身对计算机的体系结构做了很大的简化以及一些假设，但实际上影响性能的不只有访存带宽和计算速度，计算机实际能达到的性能/访存带宽可能也只有峰值的80%；并且我们假设了整个系统是负载均衡的，如果运行的代码只利用到20%的SM，那么实际的峰值肯定无法达到roofline，这种情况下需要我们提高GPU的线程利用率。
3. roofline可能不只有访存带宽和峰值性能两条线，也许我们缺少了其他的影响因素：
	1. cache的访存带宽和数据局部性（在一般的roofline中我们假设完美cache，但实际程序运行过程中很难达到这样的情况）
	2. 没有用到FMA指令（优化指令，乘积与累加合并为一条指令）、向量乘指令、张量乘指令
	3. 太多非浮点运算指令
	4. 。。。

## 机器特征

理论上的roofline性能可能太过于乐观了：

- 实际上持续的DRAM bandwith可能远低于理论上的
- CPU可能会处于Turbo模式（允许关闭一些核心，将电力加到其他核心让他们更高频运行，减少CPU的功耗和发热量）或者降频（降低电力消耗，减少对散热装置的需求，高温环境中可以提高系统稳定性，但是以牺牲某些系统性能为代价的）
- 在高计算密度的循环代码中，可能会编译失败

我们需要更加实际的/实验的roofline性能数据作为参考
例如LBL开发的Empirical Roofline Toolkit:
- 描述CPU/GPU系统特征
- 实验测量机器的峰值计算性能
- 实验测量每个内存层级的访存带宽（DRAM、L1 cache、L2 cache等）
- 代码由MPI+OpenMP/CUDA编写，可在多GPU架构上运行进行测试

测试例：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131554541.png?imageSlim)
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131554205.png?imageSlim)
理论vs.实验测量:

实验测量的访存带宽和峰值浮点计算性能通常比理论上的要低
实际上的计算密度（AI）可能比我们理论上的要高或者低：

AI比理论上高：理论的FLOP数：1 C++ FLOP=1 ISA(指令集) FLOP，然而实际上1 C++ FLOP≥1 ISA FLOP（例如除法，C++中一个除法语句转换为指令可能有多条指令来实现除法功能），因此实验测量的计算密度（AI）应该比理论上的AI要大（FLOPs大而Bytes没变），也就是说实验测量的AI应更接近Machine Balance点。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131556598.png?imageSlim)

-AI比理论低：当我们不止假设data movement只包含DRAM到计算部件的数据，还考虑cache的影响（换入换出等），那么实际的Bytes可能会更高，导致AI比理论上（简化的模型分析）要低。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131557771.png?imageSlim)


## 内存层次和Cache瓶颈

计算机有不同层次的存储部件，不同的存储部件之间有不同的访存带宽：
![image.png|228](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131559024.png?imageSlim)
由于访存带宽不同，不同层次存储之间有不同的Machine Balance:
![image.png|304](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131559684.png?imageSlim)
不同层次存储之间还有不同的访存量：
![image.png|425](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131600504.png?imageSlim)

由于访存量不同，不同层次存储之间还有不同的计算密度：
![image.png|425](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131600807.png?imageSlim)

对于不同的内存层次，我们可以把roofline增加一些项：
![image.png|500](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131601365.png?imageSlim)

可视化新的roofline模型：
![image.png|450](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131618355.png?imageSlim)

需要注意，上面的蓝色点与绿色点实际上是同一个kernel，kernel性能总是取决于所有内存层次界限的最小值，例如上图绿色点的AI * 访存带宽小于蓝色点的，假如充分利用了L2cache的性能（即实际L2层级的kernel点落于绿色roofline线上），那么DRAM层级（HBM）的kernel点就会低于DRAM roofline线。

![image.png|475](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131619367.png?imageSlim)

如果L2层和HBM层的AI离很远，那么实际上在L2缓存中有非常高的重用率，在上图的例子中，我们访存L2的字节数比直接访存DRAM的字节数多几个数量级，说明L2的命中率很高，只有一部分字节需要从DRAM中拿取。
![image.png|425](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131619334.png?imageSlim)

相反，假如L2层和HBM层的AI离得很近，那就意味着数据重用率很低甚至于没有，每次当从L2 cache中移入移出数据时，都需要从DRAM中移入移出，说明L2基本没有发挥到它应该发挥的作用。

## 指令集方面（FMA，vectors，tensors）

摩尔定律的逐渐失效使得复杂指令集重新焕发生机，现代cpu和gpu越来越依赖于执行多种操作的特殊(融合)指令(融合常见指令序列)：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131621685.png?imageSlim)

如果一条指令混合了标量计算、向量计算、张量积算，那么性能是他们的加权平均。

例如假设NVIDA GPU上不同指令的理论峰值性能如下：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131622459.png?imageSlim)

那么整体的实际峰值性能应是不同指令的加权平均：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/202412131622287.png?imageSlim)

## 浮点运算指令不足

后续学习完
>Ding, Nan, and Samuel Williams. _An instruction roofline model for gpus_. IEEE, 2019.

在来补充。。