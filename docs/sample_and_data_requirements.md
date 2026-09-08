# 样本范围与数据字段要求

本文档记录复现项目当前阶段的第 1、2 步结论：样本范围确认与数据字段清单。口径优先来自原论文；原文未完全展开的数据库字段名，按 Wind/CSMAR 常见导出字段进行映射，正式跑数前仍需对照数据库数据字典。

## 1. 样本范围

### 1.1 原论文样本

原论文题目为 *Digital Transformation and Corporate Financial Asset Allocation: Evidence from China*，作者为 Yundan Guo、Han Liang、Li Shen，arXiv 编号为 `2509.09095`。

根据原论文摘要与第 4.3 节，复现应优先采用以下样本口径：

| 项目 | 原论文口径 | 复现执行口径 |
|---|---|---|
| 研究对象 | 中国 A 股上市公司 | 沪深 A 股上市公司，保留公司代码和年份 |
| 样本期 | 2010-2022 年 | 先按 2010-2022 年准备数据 |
| 年报来源 | 上海证券交易所、深圳证券交易所官方网站 | 可从交易所官网、巨潮资讯等合法来源取得年报 PDF/文本 |
| 财务与股票市场数据 | Wind、CSMAR | 优先使用 Wind 或 CSMAR；没有授权时使用合法替代来源并记录差异 |
| 软件 | Python、Stata | 本项目用 Python 复现主流程，必要时记录与 Stata 结果差异 |

### 1.2 样本筛选规则

原论文第 4.3 节给出的筛选规则如下：

| 步骤 | 原论文规则 | 复现执行要求 |
|---|---|---|
| 1 | 剔除已退市或 ST/*ST 状态公司 | 年度层面标记 ST/*ST 和退市状态，剔除对应观测 |
| 2 | 剔除关键变量缺失观测 | 对 `fin1`、`fin2`、`digital`、控制变量和主键缺失做检查 |
| 3 | 连续变量缩尾 | 除解释变量和虚拟变量外，连续变量按 1% 和 99% 分位缩尾 |
| 4 | 异常影响点处理 | 原文提到剔除 20 个对 `digital` 系数影响过大的观测；复现时应先跑基准结果，再单独记录是否能识别同类影响点 |

注意：原论文表述为“exclude manufacturing firms that have been delisted or are under ST/*ST status”，其中 “manufacturing firms” 可能是作者笔误或样本行业限制表达不清。严格复现前要回查全文语境和数据表。如果无法确认，应做两个版本：

- 主版本：全部 A 股，剔除退市和 ST/*ST。
- 稳健性版本：仅制造业 A 股，剔除退市和 ST/*ST。

### 1.3 原文结果对照规模

原文 Table 2/3 可作为样本构造后的核验目标：

| 表 | 指标 | 原文数量 |
|---|---|---|
| Table 2 | `digital`、多数控制变量观测数 | 27,903 |
| Table 2 | `fin1`、`fin2` 观测数 | 27,897 |
| Table 2 | `TobinQ` 观测数 | 27,436 |
| Table 2 | `Indep` 观测数 | 27,901 |
| Table 3 | `fin1` 基准回归样本量 | 27,895 |
| Table 3 | `fin2` 基准回归样本量 | 27,875 |

如果复现后的样本量与上述数量差距较大，优先检查年份范围、ST/退市剔除、金融业或制造业口径、关键变量缺失、缩尾前后样本是否被误删。

## 2. 数据字段清单

### 2.1 最终面板文件

目标文件：

```text
data/processed/panel_for_replication.csv
```

最低字段：

| 字段 | 用途 | 是否必须 |
|---|---|---|
| `firm_id` | 企业代码，建议保留 6 位字符串 | 是 |
| `year` | 会计年度，2010-2022 | 是 |
| `fin1` | 短期金融资产配置比例 | 是 |
| `fin2` | 长期金融资产配置比例 | 是 |
| `digital` | 数字化转型指数 | 是 |
| `Size` | 企业规模 | 是 |
| `LEV` | 资产负债率 | 是 |
| `ROA` | 总资产收益率 | 是 |
| `ListAge` | 上市年龄 | 是 |
| `TobinQ` | 市账比 | 是 |
| `TOP1` | 第一大股东持股比例 | 是 |
| `Indep` | 独立董事比例 | 是 |
| `industry` | 行业代码，用于筛选和稳健性记录 | 强烈建议 |
| `is_st` | 是否 ST/*ST | 强烈建议 |
| `is_delisted` | 是否退市 | 强烈建议 |
| `province` 或 `region` | 异质性：东部/非东部 | 后续扩展需要 |
| `soe` | 异质性：国企/非国企 | 后续扩展需要 |

### 2.2 数字化转型数据

原文第 4.2.1 节采用年报文本分析，统计预设数字化关键词总频次并取自然对数。

建议输入：

```text
data/interim/annual_report_text/{firm_id}_{year}.txt
```

构造字段：

| 字段 | 来源 | 构造方式 |
|---|---|---|
| `firm_id` | 年报文件名或元数据 | 统一为 6 位股票代码 |
| `year` | 年报年度 | 使用会计年度 |
| `digital_keyword_count` | 年报文本 | 原文关键词词典总频次 |
| `digital` | 计算 | `ln(1 + digital_keyword_count)` |

原文关键词分为五类：数字技术应用、数字信息系统、智能数字管理、数字营销模式、数字效率提升。当前项目脚本应继续对齐这五类词典。

### 2.3 金融资产配置数据

建议输入：

```text
data/raw/financial_data/financial_statement_items.csv
```

原文第 4.2.2 节定义：

```text
fin1 = (货币资金 + 以公允价值计量且其变动计入当期损益的金融资产) / 总资产

fin2 = (应收利息净额 + 应收股利净额 + 可供出售金融资产净额
        + 持有至到期投资净额 + 长期股权投资净额 + 投资性房地产净额) / 总资产
```

需要字段：

| 目标变量 | 数据字段 | 中文含义 |
|---|---|---|
| `total_assets` | `total_assets` | 总资产 |
| `monetary_funds` | `monetary_funds` | 货币资金 |
| `fair_value_through_profit_or_loss_financial_assets` | `fair_value_through_profit_or_loss_financial_assets` | 以公允价值计量且其变动计入当期损益的金融资产 |
| `interest_receivable_net` | `interest_receivable_net` | 应收利息净额 |
| `dividend_receivable_net` | `dividend_receivable_net` | 应收股利净额 |
| `available_for_sale_fin_assets_net` | `available_for_sale_fin_assets_net` | 可供出售金融资产净额 |
| `held_to_maturity_investments_net` | `held_to_maturity_investments_net` | 持有至到期投资净额 |
| `long_term_equity_investments_net` | `long_term_equity_investments_net` | 长期股权投资净额 |
| `investment_property_net` | `investment_property_net` | 投资性房地产净额 |

### 2.4 控制变量数据

建议输入：

```text
data/raw/financial_data/control_variables.csv
```

原文第 4.2.3 节控制变量：

| 目标变量 | 原文含义 | 所需原始字段或构造方式 |
|---|---|---|
| `Size` | 企业规模 | `ln(total_assets)` |
| `LEV` | 资产负债率 | `total_liabilities / total_assets` |
| `ROA` | 总资产收益率 | `net_profit / total_assets` |
| `TOP1` | 第一大股东持股比例 | 第一大股东持股比例，注意单位为百分数还是小数 |
| `ListAge` | 上市年龄对数 | `ln(year - listing_year + 1)`；原文 Table 2 最小值为 `0.6931`，暗示可能使用 `ln(listing_years + 1)` |
| `TobinQ` | 市账比 | Wind/CSMAR 市值与账面价值字段，按数据库定义保留说明 |
| `Indep` | 独立董事比例 | 独立董事人数 / 董事总人数，注意单位为百分数还是小数 |

### 2.5 数据来源优先级

| 数据类别 | 标准来源 | 备选来源 | 备注 |
|---|---|---|---|
| 年报 PDF/文本 | 上交所、深交所官网 | 巨潮资讯 | 必须保留下载来源、公告日期、文件名 |
| 财务报表项目 | Wind、CSMAR | CNRDS、iFinD、公开年报手工整理 | 优先导出合并报表、年度数据 |
| 股票市场数据 | Wind、CSMAR | CNRDS、iFinD | `TobinQ` 通常需要市场价值数据 |
| 公司治理数据 | CSMAR、Wind | CNRDS、iFinD、年报手工整理 | `TOP1`、`Indep`、`soe`、地区字段常来自治理或公司基本信息表 |

### 2.6 下一步采集清单

先准备以下 4 类文件，不上传 GitHub：

```text
data/raw/annual_reports/
data/interim/annual_report_text/
data/raw/financial_data/financial_statement_items.csv
data/raw/financial_data/control_variables.csv
```

拿到数据后，第一轮检查不是直接回归，而是核对：

1. 企业代码和年份是否唯一；
2. 样本期是否覆盖 2010-2022；
3. 关键变量缺失比例；
4. `fin1`、`fin2`、`digital` 的均值和范围是否接近原文 Table 2；
5. `TOP1`、`Indep` 是否需要从百分数转换为 0-1；
6. 缩尾前后观测数是否合理。
