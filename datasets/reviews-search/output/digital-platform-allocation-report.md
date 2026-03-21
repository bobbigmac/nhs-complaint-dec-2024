# Named Digital Platform Allocation Across The Digitally Relevant Practice Set

This note takes the widened digital-appointment review set and asks a simpler follow-up question: for each digitally relevant practice, do the reviews ever explicitly name the platform being used?

The aim is not to prove the full appointment stack from reviews alone. It is to see how far the corpus lets us allocate practices to named systems such as `AskMyGP`, `PATCHS`, `eConsult`, `Accurx`, or `NHS App`, and how much still stays generic as just `the website`, `the online form`, `the app`, or `the system`.

## Coverage

- `295` practices have at least one digitally signalled review
- `121` of those can be allocated to at least one named platform from explicit review wording
- `174` remain `unknown only`
- `23` show more than one named platform

Put simply: this review corpus lets us allocate about `41.0%` of the digitally signalled practices to at least one named system, while about `59.0%` still stay unnamed.

## Distribution Of Known Versus Unknown

| Allocation bucket | Practices |
| --- | ---: |
| unknown only | 174 |
| NHS App | 56 |
| AskMyGP | 22 |
| PATCHS | 10 |
| eConsult | 8 |
| AskMyGP + NHS App | 7 |
| NHS App + PATCHS | 7 |
| eConsult + NHS App | 5 |
| Accurx | 2 |
| eConsult + PATCHS | 2 |
| Accurx + AskMyGP | 1 |
| Accurx + NHS App | 1 |

The biggest single bucket by far is still `unknown only`. After that, the most common named allocations are:

- `NHS App` only: `56` practices
- `AskMyGP` only: `22` practices
- `PATCHS` only: `10` practices
- `eConsult` only: `8` practices
- `Accurx` only: `2` practices

## What The Mixed Cases Look Like

Most multiple-platform cases are still small in number, but they matter because they are likely to be system changes, overlapping routes, or reviews naming both the practice front door and the `NHS App`.

Recurring combinations:

- `AskMyGP + NHS App`: `7` practices
- `NHS App + PATCHS`: `7` practices
- `eConsult + NHS App`: `5` practices
- `eConsult + PATCHS`: `2` practices
- `Accurx + AskMyGP`: `1` practice
- `Accurx + NHS App`: `1` practice

Examples of multi-platform practices in the reviews include:

- `Chorlton Family Practice`: `PATCHS` and `NHS App`
- `Culcheth Medical Centre`: `eConsult` and `NHS App`
- `Heywood Health`: `PATCHS` and `NHS App`
- `Holes Lane Medical Ltd.`: `eConsult` and `PATCHS`
- `Limelight Health and Wellbeing Hub`: `Accurx` and `AskMyGP`
- `New Bank Health`: `PATCHS` and `NHS App`

## Satisfaction By System

There are two useful ways to read the system-level numbers:

- `Any-use`: every practice where that named system appears at least once in the reviews, even if the practice also shows another named system
- `Single-only`: only practices where the reviews point to that one named system and no other named system

The single-only view is cleaner if you want a rougher software comparison without as much contamination from system changes or mixed routes.

| System | Practices any-use | Practices single-only | Positive reviews any-use | Negative reviews any-use | Weighted positive share any-use | Positive reviews single-only | Negative reviews single-only | Weighted positive share single-only |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| AskMyGP | 30 | 22 | 126 | 119 | 51.4% | 110 | 80 | 57.9% |
| PATCHS | 19 | 10 | 93 | 87 | 51.7% | 17 | 32 | 34.7% |
| eConsult | 15 | 8 | 44 | 66 | 40.0% | 20 | 40 | 33.3% |
| Accurx | 4 | 2 | 39 | 22 | 63.9% | 9 | 2 | 81.8% |
| NHS App | 76 | 56 | 425 | 353 | 54.6% | 311 | 253 | 55.1% |

## What Those System Numbers Suggest

- `NHS App` is still the most commonly allocatable named route in this dataset, but it appears in both the stronger and weaker practice groups, so it is not a clean quality marker on its own.
- `AskMyGP` looks roughly balanced overall and somewhat better in the cleaner single-only slice than in the mixed any-use slice.
- `PATCHS` looks roughly balanced in the any-use view but weaker in the single-only slice.
- `eConsult` looks weaker than the others in both any-use and single-only review balance.
- `Accurx` looks better in the tiny single-only slice, but that is based on just `2` single-only practices and should not be over-read.

## How Much Of The Ranked Set Is Still Unknown

Even inside the ranked practices, unknowns remain a huge share.

- top 50 practices with no named platform in reviews: `23`
- bottom 50 practices with no named platform in reviews: `21`

So the next manual step is still necessary. Reviews get us a long way, but they do not solve the whole allocation problem.

## Bottom Line

The reviews are good enough to allocate a substantial minority of the digitally relevant practices to named systems, but not most of them. The biggest bucket is still unnamed website/form/app language.

That means the review corpus can already support a first-pass software comparison, but only with caution:

- use `single-only` practices when you want the cleanest software read
- keep `any-use` practices when you want more coverage and more real-world messiness
- treat the `unknown only` group as a large unresolved block that still needs direct checking practice by practice

This is enough to start building a real quality or satisfaction picture by platform, but not enough to stop doing manual allocation work.
