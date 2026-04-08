111所以，**IBVS 虽然是“基于图像”的方法，但并不是完全不需要几何信息**；至少要知道或近似知道深度和内参。

# 单个点特征的交互矩阵（图像雅可比矩阵）推导

## 1. 问题描述

考虑相机观察一个静态的三维点。设该点在相机坐标系下的坐标为：

$$
\mathbf{P} = \begin{bmatrix} X \\
Y \\
Z \end{bmatrix}
$$

其对应的图像点（归一化平面坐标）为：

$$
\mathbf{x} = \begin{bmatrix} x \\
y \end{bmatrix} = \begin{bmatrix} \frac{X}{Z} \\
\frac{Y}{Z} \end{bmatrix}
$$

其中，$ Z > 0 $ 是点的深度。

在视觉伺服中，我们通常选取图像点的坐标作为视觉特征，即：

$$
\mathbf{s} = \mathbf{x} = \begin{bmatrix} x \\
y \end{bmatrix}
$$

$$
\mathbf{s} = \mathbf{x} = \begin{bmatrix} x \\
 y \end{bmatrix}
$$

目标是建立图像特征变化率 $ \dot{\mathbf{s}} = [\dot{x}, \dot{y}]^\top $ 与相机运动速度 $ \mathbf{v}\_c = [v_x, v_y, v_z, \omega_x, \omega_y, \omega_z]^\top $ 之间的线性关系：

$$
\dot{\mathbf{s}} = \mathbf{L}\_s \mathbf{v}\_c
$$

其中，$ \mathbf{L}\_s $ 即为**交互矩阵**（Interaction Matrix），也称为**图像雅可比矩阵**（Image Jacobian）。

## 2. 对投影方程求导

由 $ x = \dfrac{X}{Z} $, $ y = \dfrac{Y}{Z} $，对时间求导，利用商的求导法则：

$$
\dot{x} = \frac{\dot{X}Z - X\dot{Z}}{Z^2} = \frac{\dot{X} - x\dot{Z}}{Z} \tag{1}
$$

$$
\dot{y} = \frac{\dot{Y}Z - Y\dot{Z}}{Z^2} = \frac{\dot{Y} - y\dot{Z}}{Z} \tag{2}
$$

注意，这里 $ \dot{X}, \dot{Y}, \dot{Z} $ 是点 $ \mathbf{P} $ 在相机坐标系下的速度分量。由于我们假设点是静止的，而相机在运动，因此 $ \dot{X}, \dot{Y}, \dot{Z} $ 实际上是由相机运动引起的点在相机坐标系中的相对速度。

## 3. 将点的速度表示为相机速度的函数

对于一个相对于相机以角速度 $ \boldsymbol{\omega} = [\omega_x, \omega_y, \omega_z]^\top $ 和平移速度 $ \mathbf{v} = [v_x, v_y, v_z]^\top $ 运动的点（注意：由于点是静止的，相机运动导致点在相机坐标系中的运动速度正好相反），其在相机坐标系中的运动速度为：

$$
\dot{\mathbf{P}} = -\mathbf{v} - \boldsymbol{\omega} \times \mathbf{P}
$$

写成分量形式：

$$
\begin{aligned}
\dot{X} &= -v_x - \omega_y Z + \omega_z Y \\
\dot{Y} &= -v_y - \omega_z X + \omega_x Z \\
\dot{Z} &= -v_z - \omega_x Y + \omega_y X
\end{aligned} \tag{3}
$$
