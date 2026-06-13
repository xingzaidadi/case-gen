CREATE TABLE fin_voucher_header (
  voucher_id varchar(64),
  source_document_id varchar(64),
  legal_entity varchar(32),
  accounting_period varchar(16),
  status varchar(32)
);

CREATE TABLE fin_voucher_line (
  voucher_id varchar(64),
  account_code varchar(32),
  debit_amount decimal(18, 2),
  credit_amount decimal(18, 2),
  cost_center varchar(64)
);

CREATE TABLE finance_audit_log (
  audit_id varchar(64),
  actor varchar(64),
  action varchar(128),
  before_value text,
  after_value text,
  rule_id varchar(128),
  created_at timestamp
);

