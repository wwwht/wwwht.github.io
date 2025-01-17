![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250114140729096.png?imageSlim)
参考：[873_ic29-2014.pdf](https://www.yuque.com/attachments/yuque/0/2025/pdf/2636058/1736234338923-b5f416dc-9488-45dd-b362-4c3de6127c4d.pdf)
# 1. Kinematic Chain

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250114140658779.png?imageSlim)

> A robotic manipulator may be considered as set of links connected in a chain called **kinematic chain** by joints (figure 1).

维基百科中关于 Kinematic Chain 的概念：

> In [mechanical engineering](https://en.wikipedia.org/wiki/Mechanical_engineering), a kinematic chain is an assembly of [rigid bodies](https://en.wikipedia.org/wiki/Rigid_body) connected by [joints](https://en.wikipedia.org/wiki/Joint_(mechanics)) to provide constrained motion that is the [mathematical model](https://en.wikipedia.org/wiki/Mathematical_model) for a [mechanical system](https://en.wikipedia.org/wiki/Mechanical_system)

简单理解就是由刚体和 joint 组成的一个系统，可以做一些受约束的运动，比如人的手臂是或者机械臂，都可以抽象成一个 Kinematic Chain.

重点理解 joint 和 link 的概念：joint 是关节，常见的有移动副（prismatic joint）和转动副（revolute joint）如图二。
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250116145326271.png?imageSlim)

每个 joint 都有**2 个**link 和它连接，这里只举了这两个例子。对于复杂的多自由度关节（例如球窝关节有 2 个自由度，球形腕部有 3 个自由度），可以将它们看作由**长度为零的虚拟连杆**和多个单自由度关节组合而成。例如一个球窝关节可以拆解为两个单自由度的旋转关节，用一个零长度连杆隔开。

这种假设不会导致一般性的丢失（real loss of generality），因为所有复杂的关节都可以被分解成这种形式。

URDF 种常见的 joint 如下：

![image.png|975](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250116145635803.png?imageSlim)

- <span style="background:#affad1">编号规则</span>
对于一个具有 $n$ 个关节的机械臂，连杆的数量是 $n + 1$ ，连杆的编号从 $0\sim n$ , 其中
**Link 0**：固定基座（base of the manipulator）
**Link n**：末端执行器（end-effector），例如机械臂的抓取器或工具
**Joint i**：连接 $link_{i-1}$ 和 $link_{i}$  

- <span style="background:#affad1">运动规则:</span>
当**joint i** 被驱动（actuated）时，**Link i** 会运动

- <span style="background:#affad1">连杆参数:</span>
每个连杆可以用两个参数来定义其在空间中的位置关系：这些参数是<font color="#ff0000">静态</font>的，也就是不会随着关节的运动而变化，在下一章会详细讲解
**Link Length**（连杆长度）： 连杆之间的距离，通常沿着某个轴定义。
**Link Twist**（连杆扭转角）： 两个轴之间的扭转关系，定义它们在空间中的相对位置。

- <span style="background:#affad1">关节参数:</span>
关节可以通过以下两个参数来描述，这些参数是<font color="#ff0000">动态</font>的，通常由机器人控制器实时调整，以实现特定的运动。
**Offset Length（偏移长度）**：沿关节轴线从一个连杆到下一个连杆的距离。
**Joint Angle（关节角度）** ： 一个连杆相对于下一个连杆的旋转角度，围绕关节轴线。

- <span style="background:#affad1">坐标系的设计：</span>
> A coordinate frame is attached rigidly to each link.

每个连杆（link）都固定一个坐标系（coordinate frame），为了描述连杆在空间中的位置和方向。这些坐标系在机械臂运动中是固定在连杆上的，随连杆一起移动。

> To facilitate describing the location of each link we affix a coordinate frame to it: frame i is attached to link i.

为方便描述连杆的位置，**每个连杆都附加一个编号的坐标系**。坐标系 $i$ 用于描述 Link i 的位置和方向。坐标系编号与连杆编号相对应，便于管理和数学建模。

连杆运动中，坐标系不变。

> When the robotic manipulator executes a motion, the coordinates of each point on the link are constant.

当机械臂运动时，每个连杆上的点（如某些物理特征点）的坐标在其附加的坐标系中是固定的。即：坐标系是刚性地附着在连杆上的，不会因为机械臂的运动而变化。

- <span style="background:#affad1">关节的轴线与坐标系的 z-轴对齐:</span>

> Each joint has a joint axis with respect to which the motion of joint is described. By convention, the **z-axis** of a coordinate frame is aligned with the joint axis.

**关节轴线（Joint Axis）**：关节的运动是围绕或沿着某个轴线进行的，这个轴线称为关节轴线。

如果是旋转关节（revolute joint），运动是围绕该轴线的旋转。

如果是平移关节（prismatic joint），运动是沿着该轴线的平移。

惯例：机械臂的运动学建模中，通常将关节轴线对齐到坐标系的 𝑧-轴。这样可以简化运动学方程的建立。

+ <span style="background:#affad1">末端执行器的自由度</span>
机械臂的末端执行器（end-effector，例如机械手抓取器或焊接头）在空间中的位置和方向由 6 个自由度描述：3 个平移自由度：在 xyz 方向上的位移。3 个旋转自由度：围绕 xyz 轴的旋转角度（即欧拉角或四元数描述）。

+  <span style="background:#affad1">正向运动学（Forward Kinematics，FK）</span>

> The objective of forward kinematic analysis is to determine the cumulative effect of the entire set of joint variables.

FK 的目标是通过已知的关节变量（关节角度或平移距离）计算机械臂末端执行器的位置和方向。

+ <span style="background:#affad1">关节变量</span>

> The displacement of joint is denoted by $q_{i}$ and is called joint variable.

关节变量（Joint Variable）, 每个关节变量用一个 $q_{i}$ 表示，如果是旋转关节则表示关节旋转的角度；如果是移动关节，表示移动的距离。

所有关节变量的集合组成关节向量（Joint Vector），n 是关节数量，关节向量是正向运动学的输入。
>The collection of joint variables ![](https://cdn.nlark.com/yuque/__latex/27776d7dab158c0270d05964840c7d6e.svg)is called the joint vector.

- <span style="background:#affad1">末端执行器位置向量 r</span>

> The position of the end-effector is denoted by the dimensional vector ![](https://cdn.nlark.com/yuque/__latex/d244417d91fd4c11f5d47e3ed538108c.svg)

R 是一个位置向量（dimensional vector），他的维度 m 和末端执行器有关。如果末端执行器只考虑空间种的位置 xyz，r 就是三维向量；如果同时包含方向信息，r 就是六维向量。

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250116180006261.png?imageSlim)

正向运动学就是找到一个函数 f，它描述了关节变量 q 和末端执行器位置 r 之间的关系。

# 2. Link and Joint Parameters
Link 连杆是机械臂中位于关节之间的刚性部分，每个连杆有两个端点：

**Proximal end（近端）**：靠近机械臂基座的一端。

**Distal end（远端）**：靠近机械臂末端（工具、末端执行器）的另一端。

每个连杆由编号较小的关节连接到编号较大的关节。

Link Parameters（连杆参数）：

每个连杆可以通过 **4 个**参数完整描述其几何和运动学特性，这种描述主要基于 **Denavit-Hartenberg (D-H) 参数化方法**。其中 2 个平移方向（translation）用于描述连杆之间的线性关系， 2 个旋转轴（rotation）描述连杆之间的旋转关系。

上一节已经说到在定义连杆 Link 时，有 2 个参数来定义其在空间中的位置关系分别是**Link Length**（连杆长度）和**Link Twist**（连杆扭转角），这两个参数是**静态**的，它们是机械臂的几何参数，描述的是连杆和关节轴之间的固定空间关系，这两个参数在关节运动过程中始终保持不变。

下面是这两个参数的详细定义：
**Link Length（连杆长度， $a_{i}$ ）**: 沿两个关节轴线的公法线（common normal，垂直于两个轴）测量的距离。简单来说， $a_i$ 表示关节 i 和关节 i+1 之间的水平距离（沿 x-轴方向）。这个参数用来描述相邻关节之间的水平分离。

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117090325983.png?imageSlim)

**Twist Angle (扭转角， $\alpha_i$ )**：关节和关节轴线之间的夹角。这个角度是在两条关节轴线的正交投影到公法线平面上测量的。简单来说，它表示两个相邻关节之间的“旋转偏差”。

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117090453447.png?imageSlim)

同时，结合两个动态的关节参数 Link **Offset Length（偏移长度）和 Joint Angle（关节角度）：**
连杆偏移量（Link Offset, $d_i$ ) : 表示当前关节轴，连杆与关节之间沿关节 $z_i$ 轴线的平移距离
关节角（Joint Angle, $\theta_i$ ) : 绕关节 $z_{i}$ 轴的旋转角度。对于旋转关节，关节角是其运动的变量，控制关节的旋转状态。

在一个机械臂中，关节可以是旋转关节或平移关节 (复杂的关节也可以转换成最简单的旋转和平移关节的组合)，**对于旋转关节， $\theta_i$ 是变量，用于描述旋转运动， $d_{i}$ 是固定的，用于描述关节的位置偏移。** 
**对于平移关节， $d_{i}$ 是变量，用于描述平移运动， $\theta_i$ 是固定的，用于描述关节的旋转偏移。**

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117090845662.png?imageSlim)

如上图所示，再来理解一下四个参数的具体计算：
这里需要理解 $Link_{i}$ , $Joint_{i}$ 和 $O_{xyz}$ 的下标对应关系。
对于 $Link_{i}$  连接两个关节， $Joint_{i}$ 和 $Joint_{(i+1)}$ 
对于 $Joint_{i}$ ，连接两个 Link，分别是 $Link_{(i-1)}$ 和 $Link_{i}$ 
记不住的话可以再看下图：
![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117090911541.png?imageSlim)

Joint 1 连接 Link 0（Base）和 Link 1，Link 1 连接 Joint 1 和 Joint 2
上一节说到过，坐标系是描述 Link 的运动，对于 $Link_{i}$ ，坐标系 $O_{i}$ 建在 $Joint_{(i+1)}$ 这一侧。所以轴 $z_{i}$ 是 $Joint_{(i+1)}$ 的转动轴或者移动轴。
对于 $Link_{i}$ ：
**连杆长度** $a_{i}$  是轴 $z_{i-1}$ 到 $z_{i}$ 沿 $x_{i}$ 方向的距离。
**扭转角** $\alpha_i$  是轴 $z_{i-1}$ 和 $z_{i}$ 之间的夹角。这个角度是在 $x_{i}$ 轴上按照右手定则测量的。
**连杆偏移量**  $d_{i}$ 是 $Link_{i-1}$ 和 $Link_{i}$ 坐标系沿轴 $z_{i-1}$ 方向的平移距离
**关节角** $\theta_i$  $Link_{i-1}$ 和 $Link_{i}$ 坐标系沿轴 $z_{i-1}$ 方向的转动角度

# 3. Link Frames

定义一个坐标系，我们需要知道 4 个因素：原点 $O$ 的位置，xyz 轴的方向。
每个连杆 $i$ 的坐标系 $O_i ,x_i,y_i,z_i$ 被定义如下：  
1.  $z_i$ 轴：表示关节 $i+1$ 的运动方向，如果是旋转关节 $z_i$ 表示旋转轴；如果是平移关节， $z_i$ 表示平移轴。
2.  $x_i$ 轴： $z_{i-1}$ 轴到 $z_i$ 轴公法线方向，描述了连杆之间的水平分离。
3.  $y_i$ 轴：通过 $z_i$ 轴和 $x_i$ 轴叉乘获得 $y_i = z_i \times x_i$ 
4. 原点 $O_i$ :  $z_{i-1}$ 轴到 $z_i$ 轴公法线和 $z_i$ 轴的交点。

那么 $O_0,x_0,y_0,z_0$ 如何定义？

对于 Link 0 的坐标系，通常称之为 Base 坐标系。通常将 Base 坐标系原点与机械臂的第一个连杆（Link 0）的原点对齐，这样可以简化坐标变换。并且 Z 轴垂直向上，满足右手定则即可。
通常情况下，显示 z-轴和 x-轴就足够了，因为这两个轴有意义（运动放心，水平分离），y 轴通过叉乘获得，不需要单独画出来。
通过上述流程，可以定义一个从 $Link_{1}$ 到 $Link_{n-1}$ 的坐标系。（ $Link_{0}$ 坐标系是 Base 坐标系，通常提前定义好了，  $Link_{n}$ 是末端执行器）。

# 4. DENAVIT - HARTENBERG (D-H) CONVENTION 

在机器人应用中，选择参考坐标系的常用约定是 Denavit-Hartenberg (D-H) 约定。在这种约定中，末端执行器的位置和方向由以下公式表示：

$$
H = ^0T_{n} = ^0T_{1}^1T_{2}^2T_{3}...^{n-1}T_{n}
$$

其中：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117111459495.png?imageSlim)

DH 有两种形式：
- **经典形式（Classical/Standard DH）**： 按照 Denavit 和 Hartenberg 的原始论文提出的约定。
- **修改形式（Modified DH）：** 由 John J. Craig 在其教科书中引入。

两种形式都将 joint 表示为 2 个平移 ( $a,d$ ) 和两个角度 ( $\alpha, \theta$ )。
但是 Link 的变换矩阵不同。
> However the expressions for the link transform matrices are quite  different.

简而言之，你需要知道自己使用的是哪种 DH 方法。
> [!TIP]
最简单的一种区分方式是看变量的下标，对于 $Link_{i}$ 4 个参数如果下标都是 $i$ ，则是标准 DH；如果有 $i-1$ 则是 Modified DH

## 4.1 Classical Convention  

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117112944455.png?imageSlim)

如上图所示，对于 $Link_{i}$ 的 4 个 DH 参数：（和上一节中定义是相同的）

连杆长度： $a_{i}$ 是轴 $z_{i-1}$ 到 $z_{i}$ 沿 $x_{i}$ 方向的距离。
扭转角： $\alpha_i$ 是轴 $z_{i-1}$ 和 $z_{i}$ 之间的夹角。这个角度是在 $x_{i}$ 轴上按照右手定则测量的。
连杆偏移量 $d_{i}$ 是 $Link_{i-1}$ 和 $Link_{i}$ 坐标系沿轴 $z_{i-1}$ 方向的平移距离
关节角 $\theta_i$ $Link_{i-1}$ 和 $Link_{i}$ 坐标系沿轴 $z_{i-1}$ 方向的转动角度
通常将所有 Link 的 DH 参数写在一个表中：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117113725072.png?imageSlim)

接下来就是通过 DH 参数，构建变换矩阵 T。
齐次变换矩阵 $^{i-1}T_{i}$ 是一个 4×4 的齐次变换矩阵，描述了从连杆 $i-1$ 的坐标系到连杆 $i$ 的坐标系的变换关系。  
 从 $i-1$ 到 $i$ 的坐标系的齐次变换可以分解为 4 个基本步骤（即 4 个基本变换）：  
1. 绕 $z_{i-1}$ 轴旋转 $\theta_{i}$
2. 沿 $z_{i-1}$ 轴平移 $d_{i}$
3. 沿 $x_i$ 轴平移 $a_i$
4. 绕 $x_i$ 轴旋转 $\alpha_i$
齐次变换矩阵 $^{i-1}T_i$ 的公式表示为:
$^{i−1}T_i=R(z_{i−1},θ_i)⋅T(z_{i−1},d_i)⋅T(x_i,a_i)⋅R(x_i,α_i)$
将我们的 DH 参数代入：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132037042.png?imageSlim)

下面是经典 DH 方法的算法流程：
1.  识别并对连杆（links）进行编号，从基座（base）开始，一直到末端执行器（end-effector）。连杆从 0 到 n 编号。
  a. 基座坐标系为{0]，末端执行器坐标系为{n}。
  b. 确定并标记各个关节轴线 $z_0,z_1,z_2...z_{n-1}$ 
  
2.  确定基座坐标系的位置：
  a. 基坐标系的原点是随意的，通常设置在 Link 0 的末端。 $z_0$ 轴通常竖直向上。
  b. $x_0$ 轴垂直于 $z_0$ 轴，并在初始位置（home position）中，当第一个关节角变量 $\theta_1 = 0$ 时，与 $x_1$ 轴平行。  
  c. $y_0$ 轴通过叉乘定义： $y_0 = z_0 \times x_0$
 对于 i=1,2,…, n 执行步骤 3 到步骤 5。
 
3.  确定原点 $O_i$ 的位置：
  a.  原点 $O_i$ 是 $z_i$ 轴和 $z_{i-1}$ 轴的公法线（common normal）的交点。 
  b. 如果 $z_i$ 轴和 $z_{i-1}$ 轴相交，则将 $O_i$ 定义在该交点上。
  c. 如果 $z_i$ 轴和 $z_{i-1}$ 轴平行，则可以在 $z_i$ 轴上选择任意方便的位置作为 $O_i$ 。  
  
4.  沿 $z_i$ 和 $z_{i-1}$ 的公法线方向建立 $x_i$ 轴：
  a. $x_i$ 轴沿公法线方向，并通过原点 $O_i$ 。  
  b. $x_i$ 轴与 $z_i$ 和 $z_{i-1}$ 轴均垂直，并从 $z_i$ 轴上指向外部。 

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132223195.png?imageSlim)

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132228849.png?imageSlim)

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132232474.png?imageSlim)

5. 找到 $y_i$ ，满足右手定则，通过叉乘找到。
6. 为机械臂末端执行器（End-Effector）定义坐标系：
  a. 确定 $z_n$ 轴，假设第 n 个关节是旋转关节， $z_n$ 沿着 $z_{n-1}$ 并且远离末端执行器的方向。 $z_n$ 通常是接近方向（Approach Direction）  
  b. 确定原点 $O_n$ ，原点通常位于末端执行器的中心（如夹持器的中心）或任何工具的尖端。
  c. 确定 $y_n$ , 通常表示滑动方向（Sliding Direction），如果末端工具是一个夹持器（Gripper），则 $y_n$ 是夹持器手指滑动的方向，即打开或关闭夹持器的方向。
  d. 确定 $x_n$ , 叉乘获得。

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132343420.png?imageSlim)

7. 建立 DH 参数和 Link 的表格

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132403975.png?imageSlim)

8. 计算齐次变换矩阵 $^{i-1}T_i$
9. 计算 $^0T_n = ^0T_1 ^1T_2...^{n-1}T_n$ 得到末端执行器坐标系在 Base 坐标系下的表示。
注意：
基座坐标系的原点与第一个关节坐标系的原点重合。通过这个假设，基座坐标系和第一个关节的坐标系在初始时刻的位置完全相同，简化了运动学建模。在正向运动学（Forward Kinematics）中，变换从 $T_1$ 开始计算，避免了额外的坐标变换。    

## 4.2. Modified Convention

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132522529.png?imageSlim)

Modified DH 如上图所示，
Twist angle， $\alpha_{i-1}$ 表示 $z_{i-1}$ 到 $z_{i}$ 沿着 $x_{i-1}$ 轴的旋转。
Link length， $a_{i-1}$ 表示 $z_{i-1}$ 到 $z_{i}$ 沿着 $x_{i-1}$ 轴的平移。
Offset length， $d_{i}$ 表示 $x_{i-1}$ 到 $x_{i}$ 沿着 $z_{i}$ 轴的距离 
Joint angle,  $\theta_i$ 表示 $x_{i-1}$ 到 $x_{i}$ 沿着 $z_{i}$ 轴的旋转
DH 参数表格如下图所示：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132542917.png?imageSlim)

坐标系的转换关系 $^{i-1}T_i$ 描述 Link i-1 到 Link i 的运动，分解成以下几个运动：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132602663.png?imageSlim)

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132608926.png?imageSlim)

Modified DH 算法流程：

1. 基坐标系的设置：基坐标系被分给 Link 0，基座坐标系可以是任意的，但为了简化，选择 $z_0$ 轴与第一个关节轴 $z_1$ 共线 （当第一个关节变量 $\theta_1 = 0$ 时）。通过这种设置，
  a. $a_0=0$ ，即连杆 0 的长度为零。
  b. $\alpha_0 = 0$ ，即连杆 0 的扭转角为零。
  c. 如果第一个关节是旋转关节，则 $d_1 = 0$ 。
  d. 如果第一个关节是平移关节，则 $\theta_1 = 0$ 。
2. 确定连杆和关节, 每个连杆的坐标系根据其所连接的连杆编号命名。例如，坐标系{2} 是刚性地连接到连杆 2 的。每个坐标系的 $z_i$ 轴与关节轴 $i$ 共线，每个连杆 $i$ 有两个关节轴， $z_i$ 和 $z_{i+1}$
 对于 i=1,2,..., n 执行步骤 3 到步骤 6。
3. 确定 $z_i$ 和 $z_{i+1}$ 轴的公法线（Common Normal） 或者交点。坐标系 {i}的原点 $O_i$ 被设置在公法线与 $z_i$ 轴的交点处。
4. 指定 $z_i$ 轴为第 $i$ 个关节的运动轴方向。
5. 指定 $x_i$ 轴沿着 $z_i$ 和 $z_{i+1}$ 轴的公法线方向。如果 $z_i$ 和 $z_{i+1}$ 轴相交，则 $x_i$ 垂直于 $z_i$ 和 $z_{i+1}$ 轴所在的平面；如果 $z_i$ 和 $z_{i+1}$ 轴平行，则有无数条公法线，我们选择和上一个关节共线的公法线作为 $x_i$ 轴。
6. 通过右手定则和叉乘找到 $y_i$
7. 指定末端执行器的坐标系：
  a. 如果 joint n 是旋转关节， $x_n$ 设置为 $\theta = 0$ 时的 $x_{n-1}$ 方向。坐标系 {n}的原点 $O_n$ 被设置使得参数 $d_n = 0$ 。
  b.  如果关节 n 是平移关节（Prismatic Joint）， $x_n$ 轴被选择为当 $\theta_n = 0$ 时的初始方向。原点 $O_n$ 被设置在 $x_{n-1}$ 轴与 $z_n$ 轴的交点处, 此时 $d_n = 0$ .
8. 建立 DH 表格：（表头第二个值为 $\alpha_{i-1}$ ）

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132708983.png?imageSlim)

9. 计算 $^0T_n = ^0T_1 ^1T_2...^{n-1}T_n$ 得到末端执行器坐标系在 Base 坐标系下的表示。

# 5. Case Studies

1. 平面两轴机械臂

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132758441.png?imageSlim)

## 5.1. Classical DH

机械臂由两个转动轴组成，对于转动轴 $d=0$
坐标系的建立如下图：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117132943860.png?imageSlim)

写出标准 DH 参数表格：

| Link i | ![](https://cdn.nlark.com/yuque/__latex/5d496a3b872073b90e3b920cacfc3dc6.svg) | ![](https://cdn.nlark.com/yuque/__latex/d380efc20440f7892e981f77b69951dc.svg) | ![](https://cdn.nlark.com/yuque/__latex/2addd237806c5ad1ae2619c7bc89e57b.svg) | ![](https://cdn.nlark.com/yuque/__latex/a5cd685134cff4e097eecbda45bf397e.svg) |
| ------ | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| 1      | ![](https://cdn.nlark.com/yuque/__latex/82c15d6a06cb167d5478998f59fa0eb2.svg) | 0                                                                             | 0                                                                             | ![](https://cdn.nlark.com/yuque/__latex/dea01345c9d7225bedc2b81e54f6f267.svg) |
| 2      | ![](https://cdn.nlark.com/yuque/__latex/9488ec12d725cedfb1925ce32d674e3f.svg) | 0                                                                             | 0                                                                             | ![](https://cdn.nlark.com/yuque/__latex/b783bc6e21e7cc1af6839966ca34da4e.svg) |

根据顺序 $\theta,d,a,\alpha$ 构造出 $T$ ，注意 $\theta$ 是绕 $z$ 轴的旋转， $\alpha$ 是绕 x 轴的旋转

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117133050012.png?imageSlim)

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117133053572.png?imageSlim)

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117133058155.png?imageSlim)

## 5.2. Modified DH

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117133108859.png?imageSlim)

需要注意的是 Base 坐标系的构建，Base 坐标系 $z_0$ 和 Link 1 的坐标系 $z_1$ 重合，保证 $a_0=0$ 和 $\alpha_0=0$ ,
并且由于 Joint 1 是旋转轴，那么 $d_1=0$ ，所以在 $\theta_1=0$ 时，Base 坐标系和 Link 1 的坐标系完全重合。
写出 DH 表：

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117133128098.png?imageSlim)

根据 $\alpha,a,\theta,d$ 的顺序（先 x 轴，再 z 轴。RTRT）, 计算变换矩阵

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117133206193.png?imageSlim)

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117133212735.png?imageSlim)

注意，最后一个 Link 2 的长度 $a_2$ 并没有出现在 Modified DH 的变换中，因为在 Modified D-H 方法中，最后一个坐标系（末端执行器坐标系）的原点位于最后一个关节轴 $z_n$ 上。由于正向运动学的终点是末端坐标系，最后一个连杆的长度并没有影响到末端执行器的位姿（位置和方向）。

## 5.3 Difference between Classical and Modified Conventions

Classical DH 和 Modified DH 相同点是都是将坐标系和 Link 固连，但是不同点是坐标系建立的位置不同。
Modified DH 将坐标系建立在 Link 的近端（例如连杆 $Link_{i}$ , 连接 $Joint_{i}$ 和 $Joint_{i+1}$ ，近端指的是 $Joint_{i}$ 一端，远端是 $Joint_{i+1}$ ）
下图中 SDH 就是 Classical DH 也记为 Standard DH

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117133351827.png?imageSlim)

# 6. Conclusion

Classical DH 和 Modified DH 最大的区别是坐标系建立的位置不同。Modified DH 可能更加符合人的直观感觉。
Modified DH 最后一个坐标系建在最后一个 joint 上，如果需要到执行器的变换，还需要乘一个到执行器坐标系的齐次矩阵。

![image.png](https://wwwhtblog-1309008871.cos.ap-beijing.myqcloud.com/blog/20250117133452544.png?imageSlim)
