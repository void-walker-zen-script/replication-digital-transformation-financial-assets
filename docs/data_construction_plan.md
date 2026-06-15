# 数据构造计划

本阶段只建立真实数据构造流程，为 Table 2 描述性统计和 Table 3 基准回归准备
`data/processed/panel_for_replication.csv`。项目不会生成模拟企业、模拟年份、模拟变量
或占位面板数据。

## 1. 构造 digital：年报文本关键词统计

**目的**

从已合法获取并提取的上市公司年报文本中统计数字化关键词，构造企业—年份层面的
数字化转型指数 `digital`。

**输入文件**

- `data/interim/annual_report_text/*.txt`
- 文件名建议为 `firm_id_year.txt` 或 `firm_id_year_annual_report.txt`

**输出文件**

- `data/interim/digital_index.csv`

**关键字段**

- `firm_id`
- `year`
- `digital`
- `digital_keyword_count`
- 各关键词对应的计数列

**构造规则**

先对每份文本逐词统计，再计算：

```text
digital = ln(1 + digital_keyword_count)
```

这是当前可审查的框架定义。若原文对词典、文本范围、频率标准化或对数形式另有规定，
应以原文为准并记录修改。

**可能风险**

- 年报文件名无法正确识别企业代码和年份；
- 扫描版 PDF 的 OCR 质量影响文本；
- 页眉、目录或附录可能造成重复计数；
- 同义词、否定语境和关键词重叠可能带来测量误差；
- 年报长度差异可能影响未标准化的词频指标。

## 2. 构造 fin1 / fin2：金融资产配置变量

**目的**

依据原文会计科目口径，构造短期金融资产配置 `fin1` 和长期金融资产配置 `fin2`。

**输入文件**

- `data/raw/financial_data/financial_statement_items.csv`

**输出文件**

- `data/interim/financial_assets.csv`

**关键字段**

- 主键：`firm_id`、`year`
- 分母：`total_assets`
- `fin1` 科目：`monetary_funds`、
  `fair_value_through_profit_or_loss_financial_assets`
- `fin2` 科目：`interest_receivable_net`、`dividend_receivable_net`、
  `available_for_sale_financial_assets_net`、
  `held_to_maturity_investments_net`、`long_term_equity_investments_net`、
  `investment_property_net`

**构造规则**

```text
fin1 =（货币资金 + 以公允价值计量且其变动计入当期损益的金融资产）/ 总资产

fin2 =（应收利息净额 + 应收股利净额 + 可供出售金融资产净额
        + 持有至到期投资净额 + 长期股权投资净额
        + 投资性房地产净额）/ 总资产
```

**可能风险**

- 不同数据库字段名、单位和缺失值编码不同；
- 会计准则变化导致科目名称或列报方式变化；
- 缺失值不一定等于零，不能未经核验自动补零；
- 总资产为零、负数或单位不一致会导致无效比率；
- 合并报表与母公司报表混用会改变口径。

## 3. 构造控制变量：Size、LEV、ROA、ListAge、TOP1、Indep

**目的**

构造 Table 2 和 Table 3 使用的企业财务及治理控制变量。

**输入文件**

- `data/raw/financial_data/control_variables.csv`

**输出文件**

- `data/interim/control_variables.csv`

**关键字段**

- 主键：`firm_id`、`year`
- 财务字段：`total_assets`、`total_liabilities`、`net_profit`
- 上市信息：`listing_year`
- 股权与治理：`largest_shareholder_ownership`、
  `independent_directors`、`total_directors`

**构造规则**

```text
Size    = ln(total_assets)
LEV     = total_liabilities / total_assets
ROA     = net_profit / total_assets
ListAge = ln(year - listing_year + 1)
TOP1    = largest_shareholder_ownership
Indep   = independent_directors / total_directors
```

**可能风险**

- 总资产单位和净利润口径不一致；
- 上市年份、上市日期或重新上市的处理不同；
- `TOP1` 可能以 0–1 或 0–100 表示；
- 独立董事和董事总人数可能使用期末值或年度平均值；
- 总资产或董事人数非正时不能构造对应变量。

## 4. 合并成 panel_for_replication.csv

**目的**

将数字化指数、金融资产变量和控制变量合并为唯一的企业—年份面板。

**输入文件**

- `data/interim/digital_index.csv`
- `data/interim/financial_assets.csv`
- `data/interim/control_variables.csv`

**输出文件**

- `data/processed/panel_for_replication.csv`

**关键字段**

```text
firm_id, year, fin1, fin2, digital,
Size, LEV, ROA, ListAge, TOP1, Indep
```

**可能风险**

- `firm_id` 前导零丢失；
- 年报年份与财务报表年份错配；
- 任一来源存在重复 `firm_id-year`；
- 内连接造成样本损失；
- 缺失值和未匹配记录未被记录。

合并脚本采用一对一内连接，并报告每一步的样本量。它不会为未匹配企业补造记录。

## 5. 运行 Table 2

**目的**

用最终真实面板计算 `fin1`、`fin2`、`digital` 及控制变量的观测数、均值、标准差、
最小值和最大值。

**输入文件**

- `data/processed/panel_for_replication.csv`

**输出文件**

- `outputs/tables/table2_descriptive_statistics.csv`

**关键字段**

`fin1`、`fin2`、`digital`、`Size`、`LEV`、`ROA`、`ListAge`、`TOP1`、`Indep`

**可能风险**

- 各变量缺失值不同导致观测数不同；
- 比例单位或对数定义与原文不一致；
- 原文可能进行缩尾、行业剔除或样本期筛选。

## 6. 运行 Table 3

**目的**

分别以 `fin1` 和 `fin2` 为被解释变量，运行企业固定效应和年份固定效应基准回归。

**输入文件**

- `data/processed/panel_for_replication.csv`

**输出文件**

- `outputs/tables/table3_baseline_regression.txt`
- `outputs/tables/table3_baseline_coefficients.csv`

**关键字段**

`firm_id`、`year`、`fin1`、`fin2`、`digital`、`Size`、`LEV`、`ROA`、
`ListAge`、`TOP1`、`Indep`

**可能风险**

- 固定效应或聚类标准误设定与原文不同；
- 完整样本筛选导致两个模型样本量不同；
- 时间不变变量会被企业固定效应吸收；
- 变量口径差异会直接影响系数数量级。

## 7. 对比原文结果

**目的**

系统比较样本量、描述性统计、`digital` 系数方向、数量级、标准误和显著性。

**输入文件**

- 本项目真实数据生成的 Table 2 和 Table 3 输出；
- 原文对应表格、正文、附录和变量定义。

**输出文件**

- 后续建立的结果对比记录，不预填论文数值或复现结论。

**关键字段**

- 样本期与观测数；
- 变量均值、标准差和极值；
- `digital` 的回归系数、标准误和显著性；
- 固定效应、控制变量和标准误设置。

**可能风险**

- 论文版本、数据库版本或样本筛选不同；
- 原文未完整披露清洗细节；
- 数值接近不等于识别设计完全一致；
- 不应人为调整数据以追求与原文相同的结果。

