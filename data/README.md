# 本地数据放置说明

本目录用于存放合法取得的本地研究数据。数据文件不会上传 GitHub。

## 推荐目录

```text
data/raw/annual_reports/
data/raw/financial_data/
data/interim/annual_report_text/
data/processed/
```

## 第三步需要准备的文件

```text
data/raw/financial_data/financial_statement_items.csv
data/raw/financial_data/control_variables.csv
data/interim/annual_report_text/{firm_id}_{year}.txt
```

CSV 字段模板见：

```text
templates/financial_statement_items.csv.example
templates/control_variables.csv.example
```

注意：`firm_id` 必须保留 6 位股票代码，例如 `000001`。不要把真实数据提交到 GitHub。
