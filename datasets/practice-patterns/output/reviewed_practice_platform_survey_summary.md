# Reviewed Practice Platform vs Survey Snapshot

This is an exploratory merge of manual practice-pattern reports with per-practice GP Patient Survey metrics.
It is not causal analysis, and it only covers practices that have already been reviewed manually.

## Coverage

- reviewed reports: `18`
- reviewed reports with GPPS data: `18`
- generated_at: `2026-03-13`
- interactive relative rankings: `reviewed_practice_relative_rankings.html`

## Website Stack Groups

| website stack | n | overall_good | contact_good | website_easy | app_easy | phone_easy | google |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GTD-managed practice microsite | 10 | 63.9 | 58.4 | 40.9 | 46.3 | 43.4 | 2.5 |
| WordPress with NHS UK frontend theme and Silicon Practice plugins | 2 | 72 | 54 | 46 | 37 | 41 | 4.8 |
| WordPress with NHS UK frontend theme and Silicon Practice form layer | 1 | 73 | 80 | 71 | 54 | 70 | 4.8 |
| Standalone nhs.uk practice site with Practice365 elements | 1 | 69 | 58 | 29 | 41 | 54 | 2.7 |
| WordPress with NHS UK theme and Silicon Practice elements | 1 | 69 | 66 | 73 | 60 | 61 | 1.9 |
| Standalone legacy surgery website | 1 | 66 | 60 | 13 | 31 | 33 | 1.3 |
| Standalone WordPress practice site with Silicon Practice style NHS theme | 1 | 59 | 50 | 52 | 47 | 41 | 1.9 |
| WordPress on GPsurgery.net network theme | 1 | - | - | - | - | - | 1.5 |

## Flag Deltas

Positive `delta` means practices with the flag are scoring higher than reviewed practices without it.

| flag | n | overall delta | website delta | app delta | phone delta | notes |
| --- | --- | --- | --- | --- | --- | --- |
| PATCHS present | 13 | -6 | 0 | 6.3 | -2.6 | P89011, P89013, P89602, P89612, Y02325, Y02520, Y02586, Y02663, Y02713, Y02849, Y02875, Y02936, Y02960 |
| Shared-host patient microsite | 10 | -4.1 | -6.4 | 1.3 | -6.6 | P89011, P89013, P89602, P89612, Y02520, Y02586, Y02663, Y02713, Y02849, Y02875 |
| Accurx present | 7 | 3.4 | 11.5 | -2.3 | 3.4 | P84689, V6E6I, Y02325, Y02755001, Y02849, Y02936, Y02960 |
| WordPress public site | 6 | 3.7 | 22.9 | 4.9 | 9.8 | P84689, P87015, V6E6I, Y02325, Y02755001, Y02960 |
| Silicon Practice hosted forms present | 5 | 3.7 | 22.9 | 4.9 | 9.8 | P84689, P87015, V6E6I, Y02325, Y02960 |
| Standalone practice domain | 5 | 2.6 | 6.2 | 1.1 | 8.6 | P87015, P89020, Y02325, Y02936, Y02960 |
| Patient Access / EMIS Access present | 3 | -0.9 | -14.8 | -7.5 | -3.9 | P89020, Y02325, Y02936 |

## Top Reviewed Practices By Website Ease

- `Y02960` New Bank Health: website `73%`, vs ICS `19`, stack `WordPress with NHS UK theme and Silicon Practice elements`, requests `accurx, patchs, silicon_forms`
- `P87015` Pendleton Medical Centre: website `71%`, vs ICS `17`, stack `WordPress with NHS UK frontend theme and Silicon Practice form layer`, requests `silicon_forms`
- `Y02849` City Health Centre: website `56%`, vs ICS `2`, stack `GTD-managed practice microsite`, requests `accurx, patchs`
- `P89612` Mossley Medical Practice: website `54%`, vs ICS `0`, stack `GTD-managed practice microsite`, requests `patchs`
- `Y02325` Charlestown MD: website `52%`, vs ICS `-2`, stack `Standalone WordPress practice site with Silicon Practice style NHS theme`, requests `accurx, patchs, patient_access, silicon_forms`
- `Y02520` Simpson Medical Practice: website `52%`, vs ICS `-2`, stack `GTD-managed practice microsite`, requests `patchs`
- `P84689` Manchester Integrative Medical Practice: website `46%`, vs ICS `-8`, stack `WordPress with NHS UK frontend theme and Silicon Practice plugins`, requests `accurx, silicon_forms`
- `Y02875` Lindley House Health Centre: website `45%`, vs ICS `-9`, stack `GTD-managed practice microsite`, requests `patchs`
- `Y02586` Ashton Gp Service: website `43%`, vs ICS `-11`, stack `GTD-managed practice microsite`, requests `patchs`
- `Y02713` Guide Bridge Medical Practice: website `42%`, vs ICS `-12`, stack `GTD-managed practice microsite`, requests `patchs`

## Bottom Reviewed Practices By Website Ease

- `P89020` HT Practice: website `13%`, vs ICS `-41`, stack `Standalone legacy surgery website`, requests `patient_access`
- `P89602` The Smithy Surgery: website `21%`, vs ICS `-33`, stack `GTD-managed practice microsite`, requests `patchs`
- `P89011` Gordon Street Medical Centre: website `26%`, vs ICS `-28`, stack `GTD-managed practice microsite`, requests `patchs`
- `Y02663` Droylsden Medical Practice: website `29%`, vs ICS `-25`, stack `GTD-managed practice microsite`, requests `patchs`
- `Y02936` Millbrook Medical Practice: website `29%`, vs ICS `-25`, stack `Standalone nhs.uk practice site with Practice365 elements`, requests `accurx, patchs, patient_access`
- `P89013` Hattersley Group Practice: website `41%`, vs ICS `-13`, stack `GTD-managed practice microsite`, requests `patchs`
- `Y02713` Guide Bridge Medical Practice: website `42%`, vs ICS `-12`, stack `GTD-managed practice microsite`, requests `patchs`
- `Y02586` Ashton Gp Service: website `43%`, vs ICS `-11`, stack `GTD-managed practice microsite`, requests `patchs`
- `Y02875` Lindley House Health Centre: website `45%`, vs ICS `-9`, stack `GTD-managed practice microsite`, requests `patchs`
- `P84689` Manchester Integrative Medical Practice: website `46%`, vs ICS `-8`, stack `WordPress with NHS UK frontend theme and Silicon Practice plugins`, requests `accurx, silicon_forms`

## Top Reviewed Practices By Overall Experience

- `P89612` Mossley Medical Practice: overall `83%`, vs ICS `6`, google `3.7`, stack `GTD-managed practice microsite`
- `Y02520` Simpson Medical Practice: overall `80%`, vs ICS `3`, google `1.8`, stack `GTD-managed practice microsite`
- `P89602` The Smithy Surgery: overall `78%`, vs ICS `1`, google `4`, stack `GTD-managed practice microsite`
- `P87015` Pendleton Medical Centre: overall `73%`, vs ICS `-4`, google `4.8`, stack `WordPress with NHS UK frontend theme and Silicon Practice form layer`
- `P84689` Manchester Integrative Medical Practice: overall `72%`, vs ICS `-5`, google `4.8`, stack `WordPress with NHS UK frontend theme and Silicon Practice plugins`
- `Y02875` Lindley House Health Centre: overall `72%`, vs ICS `-5`, google `2.1`, stack `GTD-managed practice microsite`
- `Y02849` City Health Centre: overall `70%`, vs ICS `-7`, google `4.5`, stack `GTD-managed practice microsite`
- `Y02936` Millbrook Medical Practice: overall `69%`, vs ICS `-8`, google `2.7`, stack `Standalone nhs.uk practice site with Practice365 elements`
- `Y02960` New Bank Health: overall `69%`, vs ICS `-8`, google `1.9`, stack `WordPress with NHS UK theme and Silicon Practice elements`
- `P89020` HT Practice: overall `66%`, vs ICS `-11`, google `1.3`, stack `Standalone legacy surgery website`

## Bottom Reviewed Practices By Overall Experience

- `P89013` Hattersley Group Practice: overall `41%`, vs ICS `-36`, google `2.1`, stack `GTD-managed practice microsite`
- `Y02663` Droylsden Medical Practice: overall `49%`, vs ICS `-28`, google `1.8`, stack `GTD-managed practice microsite`
- `Y02586` Ashton Gp Service: overall `52%`, vs ICS `-25`, google `1.8`, stack `GTD-managed practice microsite`
- `Y02713` Guide Bridge Medical Practice: overall `53%`, vs ICS `-24`, google `1.8`, stack `GTD-managed practice microsite`
- `Y02325` Charlestown MD: overall `59%`, vs ICS `-18`, google `1.9`, stack `Standalone WordPress practice site with Silicon Practice style NHS theme`
- `P89011` Gordon Street Medical Centre: overall `61%`, vs ICS `-16`, google `1.5`, stack `GTD-managed practice microsite`
- `P89020` HT Practice: overall `66%`, vs ICS `-11`, google `1.3`, stack `Standalone legacy surgery website`
- `Y02936` Millbrook Medical Practice: overall `69%`, vs ICS `-8`, google `2.7`, stack `Standalone nhs.uk practice site with Practice365 elements`
- `Y02960` New Bank Health: overall `69%`, vs ICS `-8`, google `1.9`, stack `WordPress with NHS UK theme and Silicon Practice elements`
- `Y02849` City Health Centre: overall `70%`, vs ICS `-7`, google `4.5`, stack `GTD-managed practice microsite`
