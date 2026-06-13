# Finance Regulatory And Professional Sources

Use these sources as traceability labels. They do not replace project-specific
finance policy, accounting policy, or legal review.

## China Finance And Internal Control

| Label | Source | Use in case generation |
| --- | --- | --- |
| `LAW-ACCOUNTING` | Accounting Law of the People's Republic of China | Authenticity, completeness, accounting vouchers, books, reports, computerized accounting records |
| `CAS-BASIC` | Accounting Standards for Business Enterprises - Basic Standard | Recognition, measurement, accounting information quality, financial reporting |
| `CIC-BASIC` | Basic Norms for Enterprise Internal Control | Compliance, asset safety, financial report reliability, risk assessment, control activities |
| `CIC-APPLICATION` | Enterprise Internal Control Application Guidelines | Funds, procurement, sales, assets, financial reporting, contracts, information systems |
| `STA-INVOICE` | State Taxation Administration invoice and e-invoice rules | VAT invoice status, red-letter invoice, identity verification, invoice use and verification |

## International Control And Security References

| Label | Source | Use in case generation |
| --- | --- | --- |
| `COSO-IC` | COSO Internal Control - Integrated Framework | Control environment, risk assessment, control activities, information/communication, monitoring |
| `SOX-ICFR` | SOX Section 404 / ICFR practice | Financial reporting control assertions and management control assessment |
| `PCAOB-AS2201` | PCAOB AS 2201 | Automated application controls, program change, program access, IT dependency for ICFR |
| `GAO-FISCAM` | GAO Federal Information System Controls Audit Manual | User controls, application controls, general controls |
| `OWASP-API-2023` | OWASP API Security Top 10 2023 | Object-level authorization, authentication, object-property authorization, function authorization |
| `PCI-DSS-4.0.1` | PCI DSS v4.0.1 | Payment card data security when cardholder data or payment card environment is involved |
| `ISTQB-CTFL-4` | ISTQB CTFL v4.x | Risk-based testing, test techniques, prioritization, traceability |
| `ISO-29119-4` | ISO/IEC/IEEE 29119-4 | Test design techniques and coverage-oriented test design |

## Source URL Notes

Prefer official URLs when adding citations in generated case docs. Good source
owners include:

- National People's Congress, State Council, Ministry of Finance, State Taxation Administration
- COSO, PCAOB, GAO, ISACA
- OWASP Foundation, PCI Security Standards Council, ISTQB, ISO

## Use Rules

- Use regulatory labels only when the generated case actually checks that rule area.
- Mark legal/regulatory interpretation as project policy or legal review needed
  when the requirement is ambiguous.
- Prefer business policy references for concrete accounting entries. Regulations
  often define duties and quality requirements, not the exact system posting rule.

