下面这部分讲的是**空间力（spatial force）**，也常叫 **wrench（力旋量）**。它把三维力 $ \mathbf f $ 和该力对某点的力矩 $ \mathbf n_O $ 合在一起，用一个六维量表示。

<img src="https://cdn.nlark.com/yuque/0/2026/png/2636058/1778464106310-74c585a4-2293-4dbf-9b8e-c0882d3d2f11.png" width="1012.6666666666666" title="" crop="0,0,1,1" id="u0de94d41" class="ne-image">

#  一个刚体受到的一般力作用
对于刚体B，最一般的外力可以分成两部分： $ \mathbf f $ 和 $ \mathbf n_O $ 

 $ \mathbf f $ ： 表示作用在刚体上的合力，方向和大小就是普通三维力。  

$ \mathbf n_O $ ： 表示该力系关于点 $ O $ 的总力矩，也可以理解为作用在刚体上的力偶矩。  

 因此，一个空间力可以用下面这一对三维向量描述：  

$$
(O,\mathbf n_O,\mathbf f)
$$

更本质的说，是用 $ (\mathbf n_O,\mathbf f) $来描述相对于点O的空间力。

 这里和空间速度类似：空间速度由角速度 $ \boldsymbol\omega $ 和点 $ O $ 的线速度 $ \mathbf v_O $ 组成；空间力则由力矩 $ \mathbf n_O $ 和线力 $ \mathbf f $ 组成。  

# 为什么力矩依赖参考点
力 ($ \mathbf f $) 本身与选哪个点作为参考点无关，但是力矩与参考点有关。

如果已知力系关于点 (O) 的总力矩为 $ \mathbf n_O $ 那么它关于另一个点 (P) 的总力矩为

$$
\mathbf n_P=\mathbf n_O+\mathbf f\times \overrightarrow{OP}.
$$

这里：$ \overrightarrow{OP} $ 表示从点 (O) 指向点 (P) 的位置向量。

这个公式的含义是：**同一个力系，如果换一个参考点计算力矩，力矩会增加一项由力 (**$ \mathbf f $**) 和参考点偏移量产生的附加力矩。**

因为叉乘反交换：

$$
\mathbf f\times \overrightarrow{OP} = 
-\overrightarrow{OP}\times \mathbf f.
$$

所以这个公式也常见地写成：

$$
\mathbf n_P=\mathbf n_O-\overrightarrow{OP}\times \mathbf f.
$$

两种写法等价。

# 坐标展开
现在在点 O 建立笛卡尔坐标系

$$
Oxyz
$$

其正交单位基为 $ {\mathbf i,\mathbf j,\mathbf k}. $

那么力矩 $ \mathbf n_O $ 可以展开为：

$$
\mathbf n_O =
n_{Ox}\mathbf i+n_{Oy}\mathbf j+n_{Oz}\mathbf k.
$$

力 $ \mathbf f $ 可以展开为：

$$
\mathbf f =
f_x\mathbf i+f_y\mathbf j+f_z\mathbf k.
$$

其中：

$$
n_{Ox},n_{Oy},n_{Oz}
$$

是关于 O 点的力矩分量；

$$
f_x,f_y,f_z
$$

是线力分量。

# 六个基本空间力
空间力可以看成六个基本力的线性组合。

前三个是单位力偶：

$$
\mathbf e_x,\mathbf e_y,\mathbf e_z
$$

分别表示绕 (x,y,z) 方向的单位力矩。

后三个是单位线力：

$$
\mathbf e_{Ox},\mathbf e_{Oy},\mathbf e_{Oz}
$$

分别表示沿 (Ox,Oy,Oz) 三条直线作用的单位线力。

因此定义 Plücker 力坐标基：

$$
\mathcal E_O=
\{\mathbf e_x,\mathbf e_y,\mathbf e_z,
\mathbf e_{Ox},\mathbf e_{Oy},\mathbf e_{Oz}\}
\subset \mathbb F^6.
$$

这个基的顺序很重要：**前三个对应力矩，后三个对应力。**

# 空间力向量的表达式
空间力向量记为

$$
\hat{\mathbf f}
$$

它可以写成六个基向量的线性组合：

$$
\hat{\mathbf f} =
n_{Ox}\mathbf e_x
+n_{Oy}\mathbf e_y
+n_{Oz}\mathbf e_z
+f_x\mathbf e_{Ox}
+f_y\mathbf e_{Oy}
+f_z\mathbf e_{Oz}.
$$

它的结构可以看成：

$$
\underline{\hat{\mathbf f}}_O =
\begin{bmatrix}
n_{Ox}\\
n_{Oy}\\
n_{Oz}\\
f_x\\
f_y\\
f_z
\end{bmatrix}.
$$

也可以紧凑地写成：

$$
\underline{\hat{\mathbf f}}_O =
\begin{bmatrix}
\underline{\mathbf n}_O\\
\underline{\mathbf f}
\end{bmatrix}.
$$

# 为什么说整体是不变的？
文中说：

> Each individual term on the right-hand side depends on the position and orientation of (Oxyz), but the expression as a whole is invariant.
>

意思是：单独看某个分量，例如

 $ \mathbf f $ 和 $ \mathbf n_O $ 

它们当然依赖坐标系。你换一个坐标系，分量数值会变。

但是整个空间力

$$
\hat{\mathbf f}
$$

作为一个几何对象，不依赖于你怎么选坐标系。变化的只是它的坐标表示。

这和普通三维向量完全类似。比如一个力 $ \mathbf f $ 本身是客观存在的，但它在不同坐标系中的坐标会不同。空间力也是如此。
