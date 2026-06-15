# Table 3 基准回归复现说明

## 1. 复现目标

本阶段的目标是使用真实的企业—年份面板数据，复现原文 Table 3 中数字化转型与企业金融资产配置之间的基准回归。脚本分别以 `fin1` 和 `fin2` 为被解释变量，并报告企业固定效应、年份固定效应和企业层面聚类标准误。

运行命令：

```powershell
python scripts/06_baseline_fixed_effects.py
```

输入文件：

```text
data/processed/panel_for_replication.csv
```

输出文件：

```text
outputs/tables/table3_baseline_regression.txt
outputs/tables/table3_baseline_coefficients.csv
```

## 2. 基准模型设定

两个基准模型为：

\[
fin1_{i,t} =
\beta_1 digital_{i,t}
+ \gamma Controls_{i,t}
+ \mu_i + \lambda_t + \varepsilon_{i,t}
\]

\[
fin2_{i,t} =
\beta_2 digital_{i,t}
+ \gamma Controls_{i,t}
+ \mu_i + \lambda_t + \varepsilon_{i,t}
\]

控制变量包括 `Size`、`LEV`、`ROA`、`ListAge`、`TOP1` 和 `Indep`。其中，\(\mu_i\) 表示企业固定效应，\(\lambda_t\) 表示年份固定效应。标准误在企业层面聚类。

两个模型分别删除各自回归所需变量存在缺失的观测，因此在 `fin1` 和 `fin2` 缺失情况不同时，模型样本量可能不同。变量定义、缩尾处理和样本筛选仍须按照论文正文及附录核验。

## 3. 原文 Table 3 的核心结果

根据原文 Table 3：

- `digital` 对 `fin1` 的系数为 0.6104，且在 1% 水平显著；
- `digital` 对 `fin2` 的系数为 0.1364，且在 1% 水平显著。

以上数值仅作为后续复现结果的对照基准，未写入回归脚本，也不会被自动填入输出文件。实际输出必须由真实数据计算得到。

## 4. 当前复现范围

本阶段只复现企业固定效应和年份固定效应的基准回归。主要检查：

1. `digital` 系数的方向是否与原文一致；
2. 系数数量级是否接近原文；
3. 聚类标准误和显著性是否接近原文；
4. 两个模型的样本量是否与论文相近；
5. 固定效应、变量口径和样本清理是否一致。

即使系数方向和显著性与原文一致，Table 3 本身也只能说明控制模型设定下的显著正相关，不能单独证明严格的因果关系。

## 5. 后续分析

PSM、DID、机制分析和异质性分析将在后续阶段单独处理。实施这些分析前，需要先核验原论文的识别设计、处理组定义、时间设定和变量构造。本阶段不实施 staggered DID。

## 6. 数据与结果声明

脚本不会生成模拟数据、虚假系数或占位结果，也不会自动创建 `panel_for_replication.csv`。只有在真实且合法获得的面板数据准备到以下位置后，才能运行出回归结果：

```text
data/processed/panel_for_replication.csv
```

原始财务数据和处理后的企业层面微观数据不会上传。生成的回归结果在公开前也应检查数据库许可和研究合规要求。
