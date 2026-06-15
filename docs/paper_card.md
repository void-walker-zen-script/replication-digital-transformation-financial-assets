# 论文卡片

## 基本信息

- 论文：*Digital Transformation and Corporate Financial Asset Allocation: Evidence from China*
- 作者：Yundan Guo、Han Liang、Li Shen
- 来源：arXiv:2509.09095
- 提交日期：2025-09-11

> 本卡片是第一阶段的复现框架。变量口径、样本范围和模型细节须依据论文正文与附录继续核验。

## 现实背景

数字技术正在改变企业的信息处理、生产组织、供应链和内部治理。同时，非金融企业持有金融资产可能服务于流动性管理、风险管理或投资收益目标，也可能引发“脱实向虚”的讨论。因此，考察数字化转型与企业金融资产配置之间的关系具有现实意义。

## 研究问题

1. 企业数字化转型程度是否与金融资产配置比例相关？
2. 这种关系在短期金融资产与长期金融资产之间是否不同？
3. 企业所有制、行业、地区等特征是否带来异质性？
4. 潜在机制能否由后续扩展分析加以检验？

## 核心解释变量

`digital_index`：企业数字化转型指数。初步计划依据年报文本中的数字化相关关键词频次构造，可考虑使用 `log(1 + 关键词总频次)`。最终词典、文本范围、否定语境处理和标准化方式须按论文口径核验。

## 被解释变量

- `financial_assets_ratio`：金融资产总额占总资产的比例；
- `short_fin_assets_ratio`：短期金融资产占总资产的比例；
- `long_fin_assets_ratio`：长期金融资产占总资产的比例。

各变量所包含的具体会计科目须结合论文定义和样本期会计准则变化确认。

## 控制变量

- `size`：企业规模，通常以总资产自然对数衡量；
- `lev`：资产负债率；
- `roa`：总资产收益率；
- `growth`：企业成长性；
- `cashflow`：经营活动现金流指标。

## 固定效应

- Firm fixed effects：企业固定效应；
- Year fixed effects：年份固定效应。

## 基准模型

\[
FinancialAssetsRatio_{i,t}
= \beta DigitalIndex_{i,t}
+ \gamma Controls_{i,t}
+ \mu_i + \lambda_t + \varepsilon_{i,t}
\]

其中，\(\mu_i\) 为企业固定效应，\(\lambda_t\) 为年份固定效应。初步模板使用企业层面聚类稳健标准误。实际设定须按原论文核验。

## 预期表格结构

| 列 | 被解释变量 | 核心设定 |
|---|---|---|
| (1) | financial_assets_ratio | 仅加入 digital_index 与双向固定效应 |
| (2) | financial_assets_ratio | 加入全部控制变量与双向固定效应 |
| (3) | short_fin_assets_ratio | 加入全部控制变量与双向固定效应 |
| (4) | long_fin_assets_ratio | 加入全部控制变量与双向固定效应 |

表格预期报告系数、聚类稳健标准误、观测值、企业数、拟合优度及固定效应设置。此处仅定义输出结构，不包含任何结果。

