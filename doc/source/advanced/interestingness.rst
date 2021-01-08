*******************************
Interestingness Scoring
*******************************

In Lux, recommended visualizations are scored and ranked based on their statistical properties. 
Lux uses various standard metrics for determining how interesting a visualization is. 
The choice of an interestingness metric is dependent on the chart type, as shown in the following table.

+----------------+---------+--------------------------------------------------------------------+
| Chart Type     | Filter? | Function                                                           |
+================+=========+====================================================================+
| Bar/Line Chart | ✔       | :func:`lux.interestingness.interestingness.unevenness`             |
|                +---------+--------------------------------------------------------------------+
|                | X       | :func:`lux.interestingness.interestingness.deviation_from_overall` |
+----------------+---------+--------------------------------------------------------------------+
| Histogram      | ✔       | :func:`lux.interestingness.interestingness.skewness`               |
|                +---------+--------------------------------------------------------------------+
|                | X       | :func:`lux.interestingness.interestingness.deviation_from_overall` |
+----------------+---------+--------------------------------------------------------------------+
| Scatterplot    | ✔/X     | :func:`lux.interestingness.interestingness.monotonicity`           |
+----------------+---------+--------------------------------------------------------------------+

Bar Chart Interestingness
=========================

.. _barNoFilter:

Bar charts without filters: Unevenness
---------------------------------------

A chart is scored higher if it is more uneven, indicating high variation 
in the individual bar values in the chart. The score is computed based 
on the difference between the value of the bar chart :math:`V` and the flat uniform distribution :math:`V_{flat}`.
The difference is captured via the Euclidean distance (L2 norm).


.. math::

    L_2[V, V_{flat}]

.. Add illustration 
.. Example: "Occurrence" recommendation

.. _barWithFilter:

Bar charts with filters: Deviation from Overall
-----------------------------------------------

A filtered chart is scored higher if it differs greatly from the 
unfiltered overall visualization, indicating that the filter 
significantly changes the shape of the visualization.
This is multiplied by a significance coefficient, which measures 
the ratio of the number of rows in the filtered v.s. unfiltered view.

.. math::

    \frac{|V_F|}{|V|}\cdot L_2(V,V_F)
.. Add illustration
.. Example: "Filter" recommendation where the intent only has 1 dimension.

Histogram Interestingness
=========================

.. _histoNoFilter:

Histogram without filters: Skewness
---------------------------------------

A histogram is scored higher if it is more skewed, 
indicating that it strongly deviates from a normal distribution.
The skewness is computed based on `scipy.stats.skew <https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.skew.html>`_.

.. math::
    \mu^3/\sigma^3

.. Add illustration
.. Example: "Distribution" recommendation


.. _histoWithFilter:

Histogram with filters: Deviation from overall
-----------------------------------------------

The interestingness score for histogram with filters is computed in a similar manner to the case of bar charts with filters.
The deviation measures how different is the filtered distribution from the overall. 

.. math::

    \frac{|V_F|}{|V|}\cdot L_2(V,V_F)

.. Add illustration
.. Example: "Filter" recommendation where the intent only has 1 measure.

Scatterplot Interestingness
==============================

.. _scatter:

Scatterplot: Monotonicity
-----------------------------------

A chart is scored higher if it exhibits a strong monotonic pattern, whether linear or not.
Monotonicity indicates a strong correlation between the two quantitative variables.
The monotonicity score is computed as the square of the Spearman correlation coefficient, refer to `this paper <https://research.tableau.com/sites/default/files/Wilkinson_Infovis-05.pdf>`_ more details.
If a filter is in the view, the monotonicity is multiplied by the significance factor to obtain the final interestingness score.

.. math::

    \frac{|V_F|}{|V|}\cdot \textrm{Spearman's coefficient}(V_x,V_y)^2

.. Add illustration
.. Example: "Correlation" recommendation
