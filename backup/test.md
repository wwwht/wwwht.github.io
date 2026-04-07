机器人视觉的基本概念:

1. 摄像机标定
2. 视觉系统标定

机器人和摄像机之间的关系的确定, 例如手眼系统的标定, 就是找到摄像机坐标系和机器人坐标系之间的关系. 

3. 手眼系统

机械手和摄像机构成的机器人视觉系统. 摄像机安装在机械手末端并随机械手一起运动的视觉系统称为Eye in Hand式手眼系统; 摄像机不安装在机械手末端，且摄像机不随机械手运动的视觉系统称为Eye to Hand式手眼系统。

4. 视觉测量

# 手眼系统
<img src="https://cdn.nlark.com/yuque/0/2024/png/2636058/1725583847316-b0fa8b3f-55fe-44a5-93bd-23aa8b9afc39.png" width="276" title="" crop="0,0,1,1" id="u7080f469" class="ne-image">

## 概述
在生活中，我们需要用手移动某一物体时，需要经过哪些步骤？

        第一步：通过眼睛去观察三维世界，将**三维世界的信息**传递至视网膜，转换成**二维平面的信息**传递给我们的大脑；

        第二步：假设，当我们需要移动三维空间下的物体时，对我们的大脑而言，是将一个物体从二维平面的 A' 点移动至 B' 点，因此大脑需要计算从**二维坐标转换到三维坐标 A 点和 B 点**。

        第三步：当大脑获得了 A 点和 B 点的坐标，就可以用手将物体进行相应的移动。

        其中，第二步就是进行手眼标定，即得到**二维坐标（像素坐标系）到三维坐标（世界坐标系）的转换矩阵**。

        在实际的控制过程中，相机在检测到目标在图像中的像素位置后，通过标定好的坐标转换矩阵将相机的**像素坐标变换到机械手的空间坐标系中**，然后根据机械手坐标系计算出各个电机该如何运动，从而控制机械手到达指定位置。

## 坐标系
基础坐标系

<img src="https://cdn.nlark.com/yuque/0/2024/png/2636058/1725584497795-7c89e9fd-ddbb-47e4-b898-3b4bf23502a9.png" width="822" title="" crop="0,0,1,1" id="uc12543ae" class="ne-image">

## 手眼标定
Eye in Hand                                                    Eye to Hand

<img src="https://cdn.nlark.com/yuque/0/2024/png/2636058/1725583976912-20793778-224e-4d27-851d-8b1bfd7e2bf3.png" width="326" title="" crop="0,0,1,1" id="u435b09b9" class="ne-image"><img src="https://cdn.nlark.com/yuque/0/2024/png/2636058/1725584003547-5e6c8c06-08a3-48ea-bd37-24c734ee464b.png" width="305" title="" crop="0,0,1,1" id="u607149c2" class="ne-image">



$$ ^{B}T_{O} = ^{B}T_{E} \cdot ^{E}T_{C} \cdot ^{C}T_{O} $$

<img src="https://cdn.nlark.com/yuque/0/2024/png/2636058/1725584058126-1b9c4274-754e-41da-b503-1486fd48ebcc.png" width="1741" title="" crop="0,0,1,1" id="ud6cbbd51" class="ne-image">

Eye to hand

 为什么 $^{E}T_{O} = ^{E}T_{B} \cdot ^{B}T_{C} \cdot ^{C}T_{O}$

<img src="https://cdn.nlark.com/yuque/0/2024/png/2636058/1725596422202-18d252a6-655f-4071-bade-9adfbefc2f32.png" width="1740" title="" crop="0,0,1,1" id="u0fdcd8af" class="ne-image">

接下来就是解 AX=XB

## TCP标定
<img src="https://cdn.nlark.com/yuque/0/2024/png/2636058/1725354759435-b3d1c226-bb02-47d4-949b-01fd70c19383.png?x-oss-process=image%2Fformat%2Cwebp%2Fresize%2Cw_566%2Climit_0" width="476" title="" crop="0,0,1,1" id="R048J" class="ne-image">

$ ^{E}T_{O} = ^{E}T_{B} \cdot ^{B}T_{C} \cdot ^{C}T_{O} $

现在我们需要求$ ^{E}T_{O} $, 所以要把$ ^{B}T_{C} $消去

$ ^{B}T_{C} = ^{B}T_{E} \cdot ^{E}T_{O} \cdot ^{O}T_{C} $

移动机械臂采集两组位姿: 

$ ^{B}T_{C} = ^{B}T_{E1} \cdot ^{E}T_{O} \cdot ^{O1}T_{C} $

$ ^{B}T_{C} = ^{B}T_{E2} \cdot ^{E}T_{O} \cdot ^{O2}T_{C} $

所以:

$ ^{B}T_{E1} \cdot ^{E}T_{O} \cdot ^{O1}T_{C} = ^{B}T_{E2} \cdot ^{E}T_{O} \cdot ^{O2}T_{C} $

写成AX=XB的格式:

$ (^{B}T_{E2})^{-1} \cdot ^{B}T_{E1} \cdot ^{E}T_{O} = ^{E}T_{O} \cdot ^{O2}T_{C} \cdot (^{O1}T_{C})^{-1} $

$ A = (^{B}T_{E2})^{-1} \cdot ^{B}T_{E1}  $

$B=  ^{O2}T_{C} \cdot (^{O1}T_{C})^{-1} = (^{C}T_{O2})^{-1} \cdot ^{C}T_{O1}$
