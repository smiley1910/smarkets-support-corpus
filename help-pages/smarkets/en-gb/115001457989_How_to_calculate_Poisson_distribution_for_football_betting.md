<!-- 
id: 115001457989
title: How to calculate Poisson distribution for football betting
product: Smarkets
region: en-gb
category: Education
section: Football-betting-strategy
url: https://help.smarkets.com/hc/en-gb/articles/115001457989-How-to-calculate-Poisson-distribution-for-football-betting
scraped: 2026-06-29
-->
Title: How to calculate Poisson distribution for football betting

URL Source: https://help.smarkets.com/hc/en-gb/articles/115001457989-How-to-calculate-Poisson-distribution-for-football-betting

Markdown Content:
![Image 1](https://help.smarkets.com/hc/en-gb/article_attachments/115001610745/helpdesk_header_750x360_22_2_2017.jpg)

By incorporating Poisson distribution with historical data, football bettors can begin to determine the probable number of goals scored in a game. This article explains how to calculate a football betting model using Poisson distribution, its limitations and how it can help you find value on a number of betting markets.

## What is Poisson distribution

Poisson distribution can be used to measure the probability of independent events occurring a certain number of times within a set period - such as the number of goals scored in a football match. It can be used to do this by converting averages into a probability for the changeable outcomes.

Basically, when you know the average number of times an event will happen, you can use Poisson to calculate how likely other outcomes deviate from this average.

## Calculating Poisson distribution for football results

Let’s analyse the Premier League game between Tottenham Hotspur and Stoke City on February 26, 2017.

The first step is to calculate the average number of goals each team is expected to score in a match. To do this each team must be assigned a value for both attacking and defensive strength.

It’s important to use a relevant date range when calculating these values - too long and the data will be irrelevant due to the meteoric changes in non-playing and playing staff in modern football, while too short leaves the data vulnerable to outliers.

For our example game, the data used to calculate attack and defence strength is for the entire 2015/16 Premier League season.

## Calculating Attack and Defence strength

Using last seasons Premier League data, the first step is to establish the average number of goals scored per game - for both home and away teams.

Average goals scored at home = total home goals scored in the season / total number of home games

Average goals scored away = total away goals scored in the season / total number of away games

For our example, the 2015/16 Premier League season average out at:

Average number of goals scored by the home team: 567/380 = 1.492 goals per game

Average number of goals scored by the away team: 459/380 = 1.208 goals per game

The next step is to determine the average number of goals conceded per game - for both home and away teams - which is the opposite to the average goals scored per game.

Average number of goals conceded by the home team: 459/380 = 1.208 goals per game

Average number of goals conceded by the away team: 567/380 = 1.492 goals per game

These numbers can be used for our example to determine the attack and defence strength for both Tottenham and Stoke.

**Calculating the home team's attack strength:**

There are two steps to calculating a home team's attack strength.

Number of goals scored at home last season by the home team / number of home games played.

For our example that’s: 35/19 = 1.842

You can now calculate the attack strength of the home team by using the following equation:

Home team's average goals per home game / average home league goals per game

For our example that’s: 1.842 / 1.492 = 1.235 (Tottenham’s attack strength)

This highlights Tottenham scored 23.5% more goals at home than the theoretical average Premier League team in 2015/16.

**Calculating an away team's defensive strength:**

Like above there are two steps to calculating an away team's defence strength.

Number of goals conceded away last season by the away team / number of away games played.

For our example that’s: 31/19 = 1.632

To calculate the defence strength of the away team use the following equation:

Away team's average goals conceded per away game / average away league goals conceded per game

For our example that’s: 1.632 / 1.492 = 1.094 (Stoke’s defence strength)

This highlights Stoke conceded 9.4% more goals away from home than the average Premier League team in 2015/16.

**Projecting expected home team goals**

You can use the following method to calculate the number of goals the home team may score:

Home team attack strength * away team defence strength * average number of home goals

For our example Tottenham are expected to score: 1.235 * 1.094 * 1.492 = 2.016 goals against Stoke.

**Calculating the away team's attack strength:**

Number of goals scored away last season by the away team / number of away games played.

For our example that’s: 19/19 = 1

You can now calculate the attack strength of the away team by using the following equation:

Away team's average goals per away game / average away league goals per game

For our example that’s: 1 / 1.208 = 0.828 (Stoke’s attack strength)

This highlights Stoke scored 17.2% fewer goals away from home than the average Premier League team in 2015/16.

**Calculating a home team's defensive strength:**

Home team's average goals conceded per home game / number of home games played.

For our example that’s: 15/19 = 0.789

To calculate the defence strength of home team use the following equation:

Home team's average goals conceded per home game / average home league goals per game

For our example that’s: 0.789/1.208 = 0.653 (Tottenham’s defence strength)

This highlights Tottenham conceded 34.7% fewer goals at home in comparison to the average Premier League team in 2015/16.

**Projecting expected away team goals**

You can use the following method to calculate the number of goals the away team may score:

Away team attack strength * home team defence strength * average number of away goals

For our example Stoke are expected to score: 0.828 * 0.653 * 1.208 = 0.653 goals against Tottenham.

## Using Poisson distribution to predict football betting

Obviously no football match ends 2.016 vs. 0.653 - this is an average. Now need to convert these averages into probability.

Poisson allows bettors to distribute the 100% probability across multiple goal outcomes for each team.

The formula for Poisson distribution is:

![Image 2: b75025fd6426768c49ec751b5327b2b996ebe221.svg](https://help.smarkets.com/hc/article_attachments/115001617429/b75025fd6426768c49ec751b5327b2b996ebe221.svg)

k represents the number of goals you want to find the probability for, and the λ parameter is the expected number of goals.

However, instead of calculating all Poisson outcomes there are numerous online calculators, such as [this from Stat Trek](http://stattrek.com/online-calculator/poisson.aspx) that will compute most of the equation.

The next step is to enter the different goal outcomes (0-5 for our example, we ignore anything above five goals as it’s highly unlikely) in the ‘Poisson Random Variable’ (k) class. Then input the projected goals for the team - for our example Tottenham at 2.016 - in the ‘average rate of success’ category. The calculator will then output the probability of each score.

To see all possible goalscoring outcomes, you can simply create a matrix as displayed below.

The blue cells are the probabilities that each team will score a specific number of goals (eg. the probability that Stoke will score 1 goal is 33.99%). By multiplying the two expected goal probabilities together, you can work out the implied probability of a specific match outcome.

![Image 3](https://help.smarkets.com/hc/en-gb/article_attachments/115001596025/poisson_matrix.png)

_Matrix key_

Grey: Potential goals for Tottenham and Stoke

Blue: Poisson probability for each specific team to score a number of goals

Green: Probabilities for all combinations of a Tottenham win

Yellow: Probabilities for all combinations of a Draw

Red: Probabilities for all combinations of a Stoke win

Therefore the most likely result based on the probability in the Matrix above is a 2-0 win for Tottenham, using the formula below.

Implied probability of a 2-0 Tottenham win = 27.07% * 52.05% = 0.141 or 14.09%

The next step it to compare your Poisson result to the odds offered by bookmakers or exchanges. If betting on the correct 2-0 score, Smarkets currently offer the 2-0 win for Tottenham at 6.68 which gives it a 14.97% chance - [learn how to calculate implied probability from betting odds](https://help.smarkets.com/hc/en-gb/articles/214058369-How-to-calculate-implied-probability-in-betting).

This suggests the Poisson analysis is accurate at assigning the implied probability when compared to the betting odds.

However, if the odds change, there may be an opportunity to identify value - if you believe your odds are more accurate than the exchange or bookmaker.

## Converting implied probability into betting odds

Poisson can be used to predict outcomes for a number of other betting markets. You can do this by using the probabilities to create your own odds and compare it to an exchange or bookmaker odds.

Let’s assume you want to bet on the 1X2 market and are looking for a [value bet](https://help.smarkets.com/hc/en-gb/articles/214554985-How-to-calculate-expected-value-in-betting). To do this, simply reuse the matrix created above, and add up the probabilities for the three individual possible results:

*   Tottenham win (green)
*   Stoke win (red)
*   Draw (yellow)

The table below shows the Poisson implied probability for the following outcomes on the 1X2 compared to the Smarkets odds - with 2% commission factored in ([read how to factor commission or a bookmaker margin into the odds](https://help.smarkets.com/hc/en-gb/articles/214180145-How-to-calculate-betting-margins)) - and their implied probability.

![Image 4](https://help.smarkets.com/hc/en-gb/article_attachments/115001596365/Screenshot_from_2017-02-22_16-52-44.png)

Therefore, if last season's form was the best indicator of this year’s results, it would appear the exchange has overvalued a Tottenham win on the back market - as the Smarkets odds show the chance of a Spurs win to be 7.61% more likely than Poisson - while the draw and a Stoke win are undervalued.

## Limitations of Poisson distribution for football betting

Unfortunately nothing is that simple, and the model does have its limitations, some of which are listed below:

*   Given the model uses past data to predict future results, it doesn’t consider squad changes or manager movement.
*   The only factor a Poisson model takes into consideration is the result. Results tell us the final score but are not always indicative of what happened in a match. For instance there are plenty of matches where teams dominate only to win 1-0.
*   We know that a number of events both pre-game and during the game can affect a result. This model doesn’t account for injuries, suspensions, fitness or weather - all of which can have an impact on a team's probability pre-game. Likewise, goal expectation can be affected once the game has started such as red cards, or an away goal - the team may then employ counter-attacking tactics etc.
*   Correlations such as the condition of the pitch are also ignored, which highlights that specific matches can have a tendency for high or low-scoring outcomes - this can certainly help when gaining an edge in the lower leagues.

## Apply this to betting

Despite having its limitations, a Poisson model is a solid starting point when trying to predict football results, or find value bets by creating your own odds.

It can offer an indication as a standalone guide - iterating as you go along, for example combining this season’s results with last season up to a maximum of 38 games per team - or it can be used as a basis, before exploring further complicated methods - perhaps calculating goal expectation by total shot ratio, or Elo ratings.

[Trade on Football Now](https://smarkets.com/sport/football?utm_campaign=20170223_best_football_odds&utm&utm_medium=post&utm_source=blog)
