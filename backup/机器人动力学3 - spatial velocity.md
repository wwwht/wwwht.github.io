<img src="https://cdn.nlark.com/yuque/0/2026/png/2636058/1778120488424-82894246-ec46-4ed4-82c6-1082da7725ee.png" width="904" title="" crop="0,0,1,1" id="ufae473a9" class="ne-image">

 这部分是在建立一个概念：**刚体的瞬时运动可以用两个 3D 向量完整描述：角速度 **$ ω $** 和某个参考点处的线速度 **$ v_O $

 也就是所谓的 **spatial velocity / 空间速度**

这里通过一个例子开始，参考上图，定义了一个刚体B和一个坐标系O， $ v_O $表示刚体相对于参考系O的线速度， $ ω $表示刚体的角速度。

那么对于刚体上任意一点P的线速度为 $ v_P = v_O + ω × \overrightarrow{OP} $

**这里需要理解几点**：

1. 任意一点P的线速度 $ v_P $和参考坐标系O的位置无关。也就是说 $ v_P $表示的是在同一时刻、同一个刚体运动、同一个点 `P` 的线速度 。坐标系的选择只是为了将$ v_P $表示出来，方便计算等。
2. 公式也可以写成 $ v_P - v_O = ω × \overrightarrow{OP} $， 意思是：同一个刚体上两个点的速度差，只来自刚体的旋转。  

通过上面我们知道了刚体上任意一点P的线速度，**那么如何描述整个刚体的瞬时速度呢？**

首先定义坐标系O的三维正交基：

$$
\{\mathbf{i}, \mathbf{j}, \mathbf{k}\} \subset E^3
$$

所以角速度可以分解为：  

$$
\boldsymbol{\omega}
=
\omega_x \mathbf{i}
+
\omega_y \mathbf{j}
+
\omega_z \mathbf{k}
$$

线速度可以分解为：

$$
\mathbf{v}_O
=
v_{Ox}\mathbf{i}
+
v_{Oy}\mathbf{j}
+
v_{Oz}\mathbf{k}
$$

刚体运动可以看成六个基本运动的叠加， 因为角速度有三个分量，线速度也有三个分量，所以刚体瞬时运动可以看成六个基本运动叠加：  

$$
\hat{\mathbf v} = (\boldsymbol{\omega} , \mathbf{v}_0)
$$

接下来我们考虑刚体运动的计算，两个刚体运动可以相加：

$$
\hat{\mathbf v}_1 = (\boldsymbol{\omega}_1 , \mathbf{v}_{01})
$$

$$
\hat{\mathbf v}_2 = (\boldsymbol{\omega}_2 , \mathbf{v}_{02})
$$

$$
\hat{\mathbf v}_1 + \hat{\mathbf v}_1= (\boldsymbol{\omega}_1 + \boldsymbol{\omega}_2 , \mathbf{v}_{01} + \mathbf{v}_{02})
$$

 也可以数乘：  

$$
\alpha\hat{\mathbf v} = (\alpha\boldsymbol{\omega} , \alpha\mathbf{v}_0)
$$

所以所有刚体瞬时运动满足“向量空间”的基本规则：可以加法、可以数乘。(向量相乘和取模等操作没有意义)

因此我们把这个空间叫做：

$$
\mathbf{M}^6
$$

 也就是 **motion vector space，运动向量空间**。  

接下来如何将$ \hat{\mathbf v} = (\boldsymbol{\omega} , \mathbf{v}_0) $写成坐标，方便计算和编程？例如现在有一个刚体在运动，我们如何数值上量化出来？如何把“一个刚体运动”变成“可计算的 6 个数” ？

**这时必须选择一组基底。**

一个向量本身是没有意义的， 除非你知道它是相对于哪组基写的。 就像一个平移向量，必须知道是相对于哪个原点的平移，否则就没有意义。

速度向量是基于** Plücker 基  ：**

$$
\mathcal D_O =
\{
\mathbf d_{Ox},
\mathbf d_{Oy},
\mathbf d_{Oz},
\mathbf d_x,
\mathbf d_y,
\mathbf d_z
\}
$$

来表示：

$$
\hat{v}
=
\omega_x\mathbf d_{Ox}
+
\omega_y\mathbf d_{Oy}
+
\omega_z\mathbf d_{Oz}
+
v_{Ox}\mathbf d_x
+
v_{Oy}\mathbf d_y
+
v_{Oz}\mathbf d_z
$$

写成矩阵形式：

$$
\underline{\hat{v}}_O
=
\begin{bmatrix}
\omega_x \\
\omega_y \\
\omega_z \\
v_{Ox} \\
v_{Oy} \\
v_{Oz}
\end{bmatrix}
=
\begin{bmatrix}
\underline{\boldsymbol{\omega}} \\
\underline{\mathbf v}_O
\end{bmatrix}
$$

这里的下标 O很重要 ，表达的就是 **这个空间速度是用以O为原点的 Plücker 坐标系来表示的。  **

如果换一个坐标原点P，**那么角速度不变，线速度会发生变化。**

因为
$$
\mathbf v_P
=
\mathbf v_O
+
\boldsymbol{\omega}
\times
\overrightarrow{OP}
$$

这里每一项都依赖坐标系 $ O_{xyz} $, 如果换成坐标系 $ P_{xyz} $, **数值上可能会发生变化，但是真实表达的运动是不变的。**

**空间速度描述整个刚体的速度场；角速度是这个速度场的全局旋转部分，所以不随参考点变；线速度部分是“所选参考点处的点速度”，参考点换了，取的点不同，所以线速度分量会变。  **
