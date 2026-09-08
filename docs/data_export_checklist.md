# 数据导出检查清单

本清单用于从 Wind、CSMAR 或合法替代来源导出数据前后核对字段，避免后续脚本因为口径不清而反复返工。

## 1. 样本基础

- 年份范围：2010-2022。
- 公司范围：先导出全部 A 股；如果能确认原文仅制造业，再另存制造业版本。
- 股票代码：保留 6 位字符串，不要让 Excel 自动去掉前导零。
- 报表类型：优先使用合并报表、年度数据。
- 筛选标记：尽量同时导出行业代码、ST/*ST 标记、退市状态。

## 2. 年报文本

准备目录：

```text
data/raw/annual_reports/
data/interim/annual_report_text/
```

每份文本建议命名为：

```text
{firm_id}_{year}.txt
```

例如：

```text
000001_2010.txt
```

## 3. 财务报表科目

保存为：

```text
data/raw/financial_data/financial_statement_items.csv
```

必须包含：

```text
firm_id
year
total_assets
monetary_funds
fair_value_through_profit_or_loss_financial_assets
interest_receivable_net
dividend_receivable_net
available_for_sale_financial_assets_net
held_to_maturity_investments_net
long_term_equity_investments_net
investment_property_net
```

## 4. 控制变量

保存为：

```text
data/raw/financial_data/control_variables.csv
```

必须包含：

```text
firm_id
year
total_assets
total_liabilities
net_profit
listing_year
tobin_q
largest_shareholder_ownership
independent_directors
total_directors
```

## 5. 导出后先检查

拿到数据后，先不要跑回归。先检查：

1. `firm_id` 是否保留前导零；
2. `firm_id-year` 是否唯一；
3. 年份是否完整覆盖 2010-2022；
4. 金额单位是否一致；
5. `TOP1` 是 0-1 还是 0-100；
6. `Indep` 的分子分母是否合理；
7. `TobinQ` 的数据库定义是否与论文一致；
8. ST、退市、行业字段是否足够支持样本筛选；
9. 缺失值是空白、0、`NULL`、`N/A` 还是特殊编码；
10. 是否有任何数据文件被 Git 跟踪。
