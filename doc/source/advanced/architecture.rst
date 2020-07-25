********************************
System Architecture
********************************

Overview of Lux Architecture
=================================
Lux is composed of multiple modules, each with distinct responsibilities. The
architecture can be described in layers: the user interface layer, the user input validation
and parsing layer, the intent processing layer, the data execution layer, and finally the
analytics layer. The principle behind this design is to take advantage of the extensibility of loosely coupled modules.

.. image:: ../lux/doc/source/guide/Lux_Architecture.PNG
   :width: 400
   :align: center

Lux Data Structures
=================================
In this section we introduce these essential building
blocks to provide background information before going over the rest of the system.

Lux Dataframe
--------------------------------
To benefit from the convenience of Pandas dataframes,
Lux is designed with a focus on a tight integration with Pandas. 
We define the central piece to Lux's data model as the Lux Dataframe (LDF), 
a subclassed Pandas dataframe that supports all dataframe operations
while housing other variables and functions for generating visual recommendations.

Clause/Context
--------------------------------
The Clause object represents a single unit of user specification. These specifications can be
attributes that designate columns or filter values that specify rows in the dataset. The LDF
stores these objects in a list named the Context, which holds all current specifications for
generating recommendations. An essential job of the LDF is to maintain the Clauses within
the Context, so that generated visual recommendations are up to date with the user's input.

Vis/VisList
--------------------------------
Since Lux maintains sets of visualizations, we require a data structure that encapsulates
each visualization and its properties so that we can score, rank and display them later. Hence,
we define a Vis object for each visualization as a representation of all information required
for data fetching and rendering. The LDF stores multiple Vis objects in a Vis List, which 
represents a set of visualizations to display to the user. Since data fetching 
for a Vis is an expensive operation, a Vis in Lux is decoupled from the
data, making modification or transfering of Vis easier for query processing.

Lux System
=================================
Based on established definitions of the data structures used in Lux, we overview the system
with a focus on each module. The following sections describe the life cycle of 
how Lux interprets the user's analytical intent, fetches the relevant data, and performs
analytics to generate visualizations.

Widget (ipywidget)
--------------------------------
Lux outputs visualizations to Jupyter via custom widgets. These
widgets act as a framework for creating custom HTML representations of Python objects
within Jupyter. Displaying Lux's output through widgets lets us make the
visualizations interactive for users. Users can select particular visualizations of interest
and save them for later use.

Parser
--------------------------------
The Parser allows users to specify what variable relationships they are interested in exploring
without having to explicitely create Lux Specification objects.
Before any processing happens, Lux interprets user inputs to transform strings into Clause
objects for the Context. All syntax rules are applied to parse user input in this stage.

Validator
--------------------------------
Input validation catches inconsistencies between a LDF's Clauses and the dataset. With
this feature, data scientists can discover mistakes early on in their exploration and make
corrections. For example, if there is a filter specification where the attribute "Origin" is
equal to "USA", the validation stage checks whether the value "USA" exists for the attribute
"Origin" in the dataset.

Compiler
--------------------------------
Lux allows users to provide the bare minimum in terms of input specifications. Therefore,
Clause objects often require additional processing before they are used for creating Views.
Underspecified information for Clauses within the Context are inferred during the compilation
stage. The transformation of these Clauses into Views is a three-step process.

1. **Vis List generation**: The system generates list of Views for visualization. These Views are created from Clauses in the Context that are fully or partially specified. In the fully defined case, there is no ambiguity in which attributes the user wants to visualize. For partially specified instances, the system locates any Clause objects that include wildcard characters that are denoted by a question mark. These wildcard Clauses are further processed to enumerate all candidate Views that hold explicit Clauses. Ultimately, Lux creates a list of Views that correspond to each visualization that will be displayed in the frontend.
2. **Infer data type and data model information**: The system auto-fills missing details for each Vis. Each Vis holds Clauses that correspond to the attributes for a visualization. For each of the attributes, we populate the Clauses with corresponding data type information. These bits of information are necessary for encoding data into the correct visual elements.
3. **Visual Encoding**: The final step in the compilation is an automatic encoding process that determines visualization mappings. The system automatically infers type, marks, channels and additional details that can be left underspecified in the input specifications. The system implements a set of visualization encoding rules that automatically determines marks and channels of each visualization based on data properties determined in step 2, as shown in the table below. 

========================== ========================== ========================== 
Number of Dimensions       Number of Measures         Mark Type
========================== ========================== ========================== 
0                          1                          Histogram
1 (ordinal)                0, 1                       Line Chart
1 (categorical)            0, 1                       Bar Chart
2 (ordinal)                0, 1                       Line Chart
2 (categorical)            0, 1                       Line Chart
0                          2                          Scatter plot
1                          2                          Scatter plot
0                          3                          Scatter plot
========================== ========================== ========================== 

Executor
--------------------------------
The data executor populates each Vis with a subset of the dataframe based on their Vis
specifications. You can read more on the Lux Execution Engines' specifics  
`here <https://lux-api.readthedocs.io/en/dfapi/source/guide/executor.html>`_.