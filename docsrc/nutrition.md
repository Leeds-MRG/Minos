# Nutrition

The nutrition module uses a composite variable comprised of the frequency and amount of the consumption of fruit and 
vegetables.

## Composite Variable

The variables available to us from Understanding Society on the quality of food consumption were
[wkfruit](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/wkfruit),
[fruitamt](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/fruitamt),
[wkvege](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/wkvege), and
[vegeamt](https://www.understandingsociety.ac.uk/documentation/mainstage/dataset-documentation/variable/vegeamt).

The equations to generate the nutrition composite are as follows:

```
fruit_intermediate = days_eating_fruit_per_week * fruit_per_day
veg_intermediate = days_eating_veg_per_week * veg_per_day

nutrition_composite = fruit_intermediate + veg_intermediate
```

This gives us a continuous nutrition score, composed of the sum of two proxy values for the amount of fruit and veg 
eaten per week. Unfortunately because the `days_eating_<>_per_week` variables are ordinal 
(levels = [Never, 1-3 days, 4-6 days, Everyday]) and not just the number of days, we can't calculate an actual value 
for `amount_per_week`.

## Transition Model

Predictor variables:
- Sex
- Age
- Education
- SF-12
- Labour state
- Ethnicity
- Household Income