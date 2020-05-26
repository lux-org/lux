********************************
Specifying Context of Interest
********************************

Lux provides a flexible language for communicating your analytical goals and intent to the system, so that the system can provide better and more relevant recommendations to you. In this tutorial, we will see various ways of specifying the context, including the attributes and values that you are interested or not interested in, enumeration specifiers, as well as any constraints on the visualization encoding.

The primary way to set the context is through :func:`lux.context.LuxDataframe.setContext`. :func:`lux.context.LuxDataframe.setContext` takes in a list of specification. We will first describe how context can be specified through convenient shorthand descriptions, then we will describe advance usage via the :mod:`lux.context.Spec` object.

Basic descriptions
------------------

Specifying attributes of interest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can indicate interested in a single attribute, for instance `AverageCost`.

.. code-block:: python

    df.setContext(['AverageCost'])

You might be interested in multiple attribute, for instance you might want to look at both `AverageCost` and `FundingModel`. When multiple items are specified, Lux puts all the specified items in the context.

.. code-block:: python

    df.setContext(['AverageCost','FundingModel'])

Let's say that in addition to `AverageCost`, you are interested in the looking at a list of attributes that are related to different financial measures, such as `Expenditure` or `MedianDebt`, and how they breakdown with respect to `FundingModel`. You can specify a list of desired attributes separated by the `|` symbol, which indicates an `OR` relationship. Lux automatically create combinations of the specified attributes. 

.. code-block:: python

    df.setContext(["AverageCost|Expenditure|MedianDebt|MedianEarnings","FundingModel"])

Alternatively, you could also provide the specification as a list: 

.. code-block:: python

    df.setContext([["AverageCost" 'Expenditure','MedianDebt' 'MedianEarnings'],"FundingModel"])

Specifying values of interest
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Lux, you can also specify particular values corresponding to subsets of the data that you might be interested in. For example, you may be interested in only colleges in New England. 

.. code-block:: python

    df.setContext(["MedianDebt","Region=New England"])

Multiple values 
.. code-block:: python
       'Region=New England|Southeast|Far West'
       'New England', 'Southeast', 'Far West'

Note: Difference between Pandas 

.. code-block:: python
    
    df[df["Region"]=="New England"]

Advanced usage of :mod:`lux.context.Spec`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The basic string-based descriptions provides a convenient way of specifying the context. 
However, not all specification can be expressed through the descriptions, more complex specification can be expressed through the :mod:`lux.context.Spec` object. The two modes of specification is essentially equivalent, with the :mod:`lux.compiler.Parser` parsing the string description into :mod:`lux.context.Spec` object.

