# Reviewed Practice Platform vs Survey Snapshot

This is an exploratory merge of manual practice-pattern reports with per-practice GP Patient Survey metrics.
It is not causal analysis, and it only covers practices that have already been reviewed manually.

## Coverage

- reviewed reports: `15`
- reviewed reports with GPPS data: `15`
- generated_at: `2026-03-13`

## Website Stack Groups

| website stack | n | overall_good | contact_good | website_easy | app_easy | phone_easy | google |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GTD-hosted practice microsite on concrete5 / Concrete CMS | 11 | 64.4 | 58.4 | 39.8 | 45.8 | 44.4 | 2.5 |
| My Surgery Website | 1 | 97 | 92 | 79 | 86 | 92 | 5 |
| WordPress with nhsuk-frontend-theme and Silicon Practice plugins | 1 | 69 | 66 | 73 | 60 | 61 | 1.9 |
| WordPress with NHS UK theme and Silicon Practice elements | 1 | 59 | 50 | 52 | 47 | 41 | 1.9 |

## Flag Deltas

Positive `delta` means practices with the flag are scoring higher than reviewed practices without it.

| flag | n | overall delta | website delta | app delta | phone delta | notes |
| --- | --- | --- | --- | --- | --- | --- |
| PATCHS present | 13 | -3.6 | -10.9 | 14.8 | 5.1 | P86001, P89011, P89013, P89602, P89612, Y02325, Y02520, Y02586, Y02663, Y02713, Y02875, Y02936, Y02960 |
| Concrete CMS / concrete5 public site | 11 | -10.6 | -28.2 | -18.5 | -20.3 | P89011, P89013, P89602, P89612, Y02520, Y02586, Y02663, Y02713, Y02849, Y02875, Y02936 |
| Shared-host patient microsite | 11 | -10.6 | -28.2 | -18.5 | -20.3 | P89011, P89013, P89602, P89612, Y02520, Y02586, Y02663, Y02713, Y02849, Y02875, Y02936 |
| Accurx present | 4 | -2.6 | 8.3 | -8.8 | -5.5 | P89011, Y02325, Y02849, Y02960 |
| Patient Access / EMIS Access present | 2 | 13.2 | 22.9 | 19.5 | 20.7 | P86001, Y02325 |
| WordPress public site | 2 | -3.1 | 19.4 | 4.3 | 2.7 | Y02325, Y02960 |
| Silicon Practice hosted forms present | 2 | -3.1 | 19.4 | 4.3 | 2.7 | Y02325, Y02960 |
| Standalone practice domain | 2 | -3.1 | 19.4 | 4.3 | 2.7 | Y02325, Y02960 |
| My Surgery Website public site | 1 | 32.7 | 35.7 | 39 | 46.6 | P86001 |
| Phone-first appointments wording | 1 | 32.7 | 35.7 | 39 | 46.6 | P86001 |
| PATCHS described as limited-scope, not full front door | 1 | 32.7 | 35.7 | 39 | 46.6 | P86001 |

## Top Reviewed Practices By Website Ease

- `P86001` Milnrow Village Practice: website `79%`, vs ICS `25`, stack `My Surgery Website`, requests `patchs, patient_access`
- `Y02960` New Bank Health: website `73%`, vs ICS `19`, stack `WordPress with nhsuk-frontend-theme and Silicon Practice plugins`, requests `accurx, patchs, silicon_forms`
- `Y02849` City Health Centre: website `56%`, vs ICS `2`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `accurx`
- `P89612` Mossley Medical Practice: website `54%`, vs ICS `0`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `Y02325` Charlestown Medical Practice: website `52%`, vs ICS `-2`, stack `WordPress with NHS UK theme and Silicon Practice elements`, requests `accurx, patchs, patient_access, silicon_forms`
- `Y02520` Simpson Medical Practice: website `52%`, vs ICS `-2`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `Y02875` Lindley House Health Centre: website `45%`, vs ICS `-9`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `Y02586` Ashton GP Service: website `43%`, vs ICS `-11`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `Y02713` Guide Bridge Medical Practice: website `42%`, vs ICS `-12`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `P89013` Hattersley Group Practice: website `41%`, vs ICS `-13`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`

## Bottom Reviewed Practices By Website Ease

- `P89602` The Smithy Surgery: website `21%`, vs ICS `-33`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `P89011` Gordon Street Medical Centre: website `26%`, vs ICS `-28`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `accurx, patchs`
- `Y02663` Droylsden Medical Practice: website `29%`, vs ICS `-25`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `Y02936` Millbrook Medical Practice: website `29%`, vs ICS `-25`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `P89013` Hattersley Group Practice: website `41%`, vs ICS `-13`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `Y02713` Guide Bridge Medical Practice: website `42%`, vs ICS `-12`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `Y02586` Ashton GP Service: website `43%`, vs ICS `-11`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `Y02875` Lindley House Health Centre: website `45%`, vs ICS `-9`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`
- `Y02325` Charlestown Medical Practice: website `52%`, vs ICS `-2`, stack `WordPress with NHS UK theme and Silicon Practice elements`, requests `accurx, patchs, patient_access, silicon_forms`
- `Y02520` Simpson Medical Practice: website `52%`, vs ICS `-2`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`, requests `patchs`

## Top Reviewed Practices By Overall Experience

- `P86001` Milnrow Village Practice: overall `97%`, vs ICS `20`, google `5`, stack `My Surgery Website`
- `P89612` Mossley Medical Practice: overall `83%`, vs ICS `6`, google `3.7`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02520` Simpson Medical Practice: overall `80%`, vs ICS `3`, google `1.8`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `P89602` The Smithy Surgery: overall `78%`, vs ICS `1`, google `4`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02875` Lindley House Health Centre: overall `72%`, vs ICS `-5`, google `2.1`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02849` City Health Centre: overall `70%`, vs ICS `-7`, google `4.5`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02936` Millbrook Medical Practice: overall `69%`, vs ICS `-8`, google `2.7`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02960` New Bank Health: overall `69%`, vs ICS `-8`, google `1.9`, stack `WordPress with nhsuk-frontend-theme and Silicon Practice plugins`
- `P89011` Gordon Street Medical Centre: overall `61%`, vs ICS `-16`, google `1.5`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02325` Charlestown Medical Practice: overall `59%`, vs ICS `-18`, google `1.9`, stack `WordPress with NHS UK theme and Silicon Practice elements`

## Bottom Reviewed Practices By Overall Experience

- `P89013` Hattersley Group Practice: overall `41%`, vs ICS `-36`, google `2.1`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02663` Droylsden Medical Practice: overall `49%`, vs ICS `-28`, google `1.8`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02586` Ashton GP Service: overall `52%`, vs ICS `-25`, google `1.8`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02713` Guide Bridge Medical Practice: overall `53%`, vs ICS `-24`, google `1.8`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02325` Charlestown Medical Practice: overall `59%`, vs ICS `-18`, google `1.9`, stack `WordPress with NHS UK theme and Silicon Practice elements`
- `P89011` Gordon Street Medical Centre: overall `61%`, vs ICS `-16`, google `1.5`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02936` Millbrook Medical Practice: overall `69%`, vs ICS `-8`, google `2.7`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02960` New Bank Health: overall `69%`, vs ICS `-8`, google `1.9`, stack `WordPress with nhsuk-frontend-theme and Silicon Practice plugins`
- `Y02849` City Health Centre: overall `70%`, vs ICS `-7`, google `4.5`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
- `Y02875` Lindley House Health Centre: overall `72%`, vs ICS `-5`, google `2.1`, stack `GTD-hosted practice microsite on concrete5 / Concrete CMS`
