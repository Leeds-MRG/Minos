Loneliness
----------

Introduction
~~~~~~~~~~~~

Prediction of ordinal loneliness state.

Methods
~~~~~~~

What methods are used? Justification due to output data type.
explanation of model output.

.. code:: r

   #discrete_barplot(obs, 'loneliness')
   order <- c(1, 2, 3)
   discrete_barplot(obs, order)

.. figure:: ./figure/loneliness_data-1.png
   :alt: plot of chunk loneliness_data

   plot of chunk loneliness_data

Data
~~~~

What variables are included? Why is this output chosen. What explanatory
variables are used and why are they chosen

Results
~~~~~~~

What are the results. Coefficients tables. diagnostic plots. measures of
goodness of fit.

.. figure:: ./figure/housing_output-1.png
   :alt: plot of chunk housing_output

   plot of chunk housing_output

.. code:: r

   plot_rfo_importance(model)

.. figure:: ./figure/unnamed-chunk-1-1.png
   :alt: plot of chunk unnamed-chunk-1

   plot of chunk unnamed-chunk-1

References
~~~~~~~~~~
